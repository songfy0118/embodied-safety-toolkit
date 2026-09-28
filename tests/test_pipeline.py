import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from adapters.controller import record_plan
from gen_safety.scenarios import build_cases, FAMILIES
from pipeline.__main__ import load_catalog, run_suite
from safety_eval.offline import evaluate_payload
from examples.build_examples import trace


CATALOG = Path(__file__).resolve().parents[1] / "configs/rules.json"


class PipelineTests(unittest.TestCase):
    def test_all_families_and_safe_controls(self):
        catalog = load_catalog(CATALOG)
        cases = build_cases(seed=19, variants=3)
        self.assertEqual(len(cases), 36)
        self.assertEqual({c["family"] for c in cases}, set(FAMILIES))
        for case in cases:
            with self.subTest(case=case["case_id"]):
                formula = catalog[case["family"]]["formula"]
                self.assertEqual(evaluate_payload({"trajectory": case["trajectory"][:1]}, [formula])["status"], "passed")
                self.assertEqual(evaluate_payload(case, [formula])["status"], case["expected_status"])

    def test_seed_is_repeatable(self):
        self.assertEqual(build_cases(7, 3), build_cases(7, 3))
        self.assertNotEqual(build_cases(7, 3), build_cases(11, 3))

    def test_invalid_variant_count(self):
        for value in (0, -1, 101, True, "2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_cases(variants=value)

    def test_reports_and_output_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "run"
            report = run_suite(output, CATALOG, variants=1)
            self.assertEqual(report["summary"]["matched_expectations"], 12)
            self.assertEqual(len(list((output / "traces").glob("*.json"))), 12)
            self.assertEqual(json.loads((output / "report.json").read_text())["summary"], report["summary"])
            self.assertEqual(len((output / "summary.csv").read_text().splitlines()), 13)
            self.assertIn("Inspect evidence", (output / "report.html").read_text())
            with self.assertRaisesRegex(ValueError, "must be empty"):
                run_suite(output, CATALOG)

    def test_catalog_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "catalog.json"
            entry = {"id": "a", "requirement": "example", "formula": "G(NOT(ISHOT(Cup_1)))"}
            path.write_text(json.dumps([entry, entry]))
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                load_catalog(path)

    def test_long_trace_does_not_recurse(self):
        payload = trace("RoomTemp")
        payload["trajectory"] += [copy.deepcopy(payload["trajectory"][-1]) for _ in range(1100)]
        self.assertEqual(evaluate_payload(payload, ["G(NOT(ISBROKEN(Cup_1)))"])["status"], "passed")

    def test_controller_records_copies_and_stops_on_failure(self):
        class Controller:
            def __init__(self):
                self.last_event = SimpleNamespace(metadata={"objects": [], "lastActionSuccess": True})
                self.calls = []

            def step(self, **action):
                self.calls.append(action)
                self.last_event.metadata["lastActionSuccess"] = False
                self.last_event.metadata["errorMessage"] = "Blocked"
                return self.last_event

        controller = Controller()
        actions = [{"action": "MoveAhead"}, {"action": "MoveAhead"}]
        result = record_plan(controller, actions)
        self.assertEqual(len(controller.calls), 1)
        self.assertEqual(result["stopped_on_failure"], 0)
        self.assertTrue(result["trajectory"][0]["event_metadata"]["lastActionSuccess"])
        self.assertFalse(result["trajectory"][1]["event_metadata"]["lastActionSuccess"])

    def test_controller_exception_is_not_hidden(self):
        class Broken:
            last_event = SimpleNamespace(metadata={"objects": []})
            def step(self, **action):
                raise RuntimeError("Simulator disconnected")
        with self.assertRaisesRegex(RuntimeError, "disconnected"):
            record_plan(Broken(), [{"action": "MoveAhead"}])


if __name__ == "__main__":
    unittest.main()
