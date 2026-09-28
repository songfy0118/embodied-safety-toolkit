import argparse
import hashlib
import json
from pathlib import Path

from gen_safety.scenarios import build_cases
from safety_eval.offline import evaluate_payload, parse_rule
from .reporting import write_reports


def load_catalog(path):
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(catalog, list) or not catalog:
        raise ValueError("Rule catalog must be a nonempty list")
    result = {}
    for entry in catalog:
        if not isinstance(entry, dict) or not all(isinstance(entry.get(k), str) and entry[k].strip() for k in ("id", "requirement", "formula")):
            raise ValueError("Each catalog entry requires id, requirement and formula strings")
        if entry["id"] in result:
            raise ValueError(f"Duplicate rule ID: {entry['id']}")
        parse_rule(entry["formula"])
        result[entry["id"]] = entry
    return result


def run_suite(output, catalog_path, seed=7, variants=2):
    catalog = load_catalog(catalog_path)
    cases = build_cases(seed, variants)
    missing = {case["family"] for case in cases} - catalog.keys()
    if missing:
        raise ValueError(f"Missing catalog families: {sorted(missing)}")
    # Prevent stale traces or reports from masquerading as the current run.
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError(f"Output directory must be empty: {output}")
    trace_dir = output / "traces"
    trace_dir.mkdir()
    results = []
    for case in cases:
        rule = catalog[case["family"]]["formula"]
        # Initial scene must satisfy its rule, including unsafe test cases.
        initial = {"trajectory": case["trajectory"][:1]}
        setup = evaluate_payload(initial, [rule])
        if setup["status"] != "passed":
            raise ValueError(f"Invalid initial setup: {case['case_id']}: {setup['status']}")
        raw = json.dumps(case, indent=2) + "\n"
        filename = case["case_id"] + ".json"
        (trace_dir / filename).write_text(raw, encoding="utf-8")
        outcome = evaluate_payload(case, [rule])
        results.append({"case_id": case["case_id"], "family": case["family"],
                        "expected_status": case["expected_status"],
                        "matches_expected": outcome["status"] == case["expected_status"],
                        "trace_sha256": hashlib.sha256(raw.encode()).hexdigest(),
                        **outcome})
    report = {"schema_version": 1, "synthetic": True, "seed": seed, "variants": variants,
              "catalog_sha256": hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
              "summary": {"total": len(results),
                          "matched_expectations": sum(r["matches_expected"] for r in results),
                          **{s: sum(r["status"] == s for r in results) for s in ("passed", "violated", "error", "not_applicable")}},
              "results": results}
    write_reports(report, output)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the synthetic embodied-safety regression suite")
    parser.add_argument("--output", type=Path, required=True, help="An empty run directory")
    parser.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] / "configs/rules.json")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--variants", type=int, default=2)
    args = parser.parse_args(argv)
    try:
        report = run_suite(args.output, args.catalog, args.seed, args.variants)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Pipeline error: {exc}\n")
    print(json.dumps(report["summary"]))
    return 0 if report["summary"]["matched_expectations"] == report["summary"]["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
