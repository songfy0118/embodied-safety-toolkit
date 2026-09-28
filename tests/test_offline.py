import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from examples.build_examples import trace
from safety_eval.offline import evaluate_payload, parse_rule, parse_state_formula
from safety_eval.ctl import CTLAllAlways, CTLPrimitive
from safety_eval.trace_to_ctl import _collision_from_error, _state_from_metadata
from safety_eval.tree_traj import State, Proposition, TrajectoryTree


HOT_RULE = "G(NOT(ISHOT(Cup_1) AND ToggleObjectOn(Microwave_2)))"


class OfflineTests(unittest.TestCase):
    def test_hot_trigger_and_grounded_witness(self):
        result = evaluate_payload(trace(), [HOT_RULE])
        self.assertEqual(result["status"], "violated")
        witness = result["rules"][0]["witness"]
        self.assertEqual(witness["source_step"], 1)
        self.assertIn("Cup|1", witness["grounded_rule"])
        self.assertIn("ToggleObjectOn(Microwave|1)", witness["evidence"])

    def test_safe_controls(self):
        for payload in [trace("RoomTemp"), trace(action="Pass")]:
            with self.subTest(payload=payload):
                self.assertEqual(evaluate_payload(payload, [HOT_RULE])["status"], "passed")

    def test_final_state_is_checked(self):
        result = evaluate_payload(trace("RoomTemp", broken=True), ["G(NOT(ISBROKEN(Cup_1)))"])
        self.assertEqual(result["status"], "violated")
        self.assertTrue(result["rules"][0]["witness"]["terminal_observation"])

    def test_null_error_message(self):
        self.assertIsNone(_collision_from_error(None))
        self.assertEqual(_collision_from_error("object failed to open"), "OPEN")

    def test_action_naming_conventions(self):
        snake = trace()
        snake["trajectory"][1]["plan_action"] = {"action": "ToggleObjectOn", "object_id": "Microwave|1"}
        self.assertEqual(evaluate_payload(snake, [HOT_RULE]), evaluate_payload(trace(), [HOT_RULE]))

    def test_nested_boolean_precedence(self):
        expression = parse_state_formula("ISHOT(Cup|1) OR ISBROKEN(Cup|1) AND ISON(Microwave|1)")
        state = State({}, [Proposition("ISHOT", ["Cup|1"])])
        self.assertTrue(expression.eval_state(state, None, {}))
        expression = parse_state_formula("NOT(ISHOT(Cup|1) OR (ISBROKEN(Cup|1) AND ISON(Microwave|1)))")
        self.assertFalse(expression.eval_state(state, None, {}))

    def test_implication(self):
        _, expression = parse_rule("G(ISHOT(Cup_1) -> NOT(ToggleObjectOn(Microwave_2)))")
        self.assertIsInstance(expression, CTLAllAlways)
        result = evaluate_payload(trace(), ["G(ISHOT(Cup_1) -> NOT(ToggleObjectOn(Microwave_2)))"])
        self.assertEqual(result["status"], "violated")

    def test_unsupported_or_invalid_rules_are_errors(self):
        for rule in ["G(F(ISHOT(Cup_1)))", "G(NOT(OVERLOAD(Cup_1)))", "G(NOT(ISHOT(Cup_1))garbage)", "G(NOT(NEAR(Cup_1)))"]:
            with self.subTest(rule=rule):
                self.assertEqual(evaluate_payload(trace(), [rule])["status"], "error")

    def test_absent_objects_are_not_applicable(self):
        result = evaluate_payload(trace(), ["G(NOT(ISBROKEN(Laptop_1)))"])
        self.assertEqual(result["status"], "not_applicable")

    def test_input_validation(self):
        cases = [{}, {"trajectory": []}, {"trajectory": [{}]}]
        missing_initial = trace()
        missing_initial["trajectory"] = missing_initial["trajectory"][1:]
        cases.append(missing_initial)
        for payload in cases:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                evaluate_payload(payload, [HOT_RULE])

    def test_input_unchanged(self):
        payload = trace()
        expected = copy.deepcopy(payload)
        evaluate_payload(payload, [HOT_RULE])
        self.assertEqual(payload, expected)

    def test_multiple_objects_are_grounded(self):
        payload = trace("RoomTemp")
        for step in payload["trajectory"]:
            extra = copy.deepcopy(step["event_metadata"]["objects"][1])
            extra.update(objectId="Cup|2", temperature="Hot")
            step["event_metadata"]["objects"].append(extra)
        result = evaluate_payload(payload, [HOT_RULE])
        self.assertIn("Cup|2", result["rules"][0]["witness"]["grounded_rule"])

    def test_branching_invariant_checks_every_branch(self):
        safe = State({}, [])
        unsafe = State({}, [Proposition("ISBROKEN", ["Cup|1"])])
        tree = TrajectoryTree(safe)
        tree.add_node(tree.root.node_id, safe)
        tree.add_node(tree.root.node_id, unsafe)
        _, expression = parse_rule("G(NOT(ISBROKEN(Cup|1)))")
        self.assertFalse(expression.eval(tree, {}).rv)

    def test_explicit_containment_with_bounding_boxes(self):
        outer = [[x, y, z] for x in (0, 2) for y in (0, 2) for z in (0, 2)]
        inner = [[x, y, z] for x in (.5, 1) for y in (.5, 1) for z in (.5, 1)]
        metadata = {"objects": [
            {"objectId": "Cup|1", "objectType": "Cup", "axisAlignedBoundingBox": {"cornerPoints": inner}},
            {"objectId": "Microwave|1", "objectType": "Microwave", "axisAlignedBoundingBox": {"cornerPoints": outer}},
        ]}
        self.assertIn("INSIDE(Cup|1, Microwave|1)", _state_from_metadata(metadata)["edges"])

    def test_batch_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            result = subprocess.run([sys.executable, "-m", "safety_eval.offline", "--trace-dir", "examples/traces", "--rules", "examples/rules.json", "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(output.read_text())
            self.assertEqual(report["counts"], {"passed": 2, "violated": 2, "not_applicable": 0, "error": 0})


if __name__ == "__main__":
    unittest.main()
