"""Auditable offline checks using the SENTINEL trajectory evaluation core.

Supports G(state_formula) on finite recorded traces. This entry point deliberately
rejects temporal nesting rather than implying a complete CTL implementation.
"""

import argparse
import copy
import json
import re
from itertools import product
from pathlib import Path

from .ctl import CTLAllAlways, CTLAnd, CTLNot, CTLOr, CTLPrimitive
from .ctl_full_pipeline import (
    _build_suffix_candidates, _collect_object_ids, _extract_suffix_bases,
    _ground_rule_string,
)
from .ctl_parser import CTLParser
from .trace_to_ctl import trace_to_ctl_sequence
from .tree_traj import Proposition


# Predicate coverage is explicit: unimplemented predicates must not silently pass.
PREDICATES = {
    "ISON": 1, "ISOFF": 1, "ISHOT": 1, "ISCOLD": 1, "ISOPEN": 1,
    "ISCLOSED": 1, "ISDIRTY": 1, "ISBROKEN": 1, "ISMICROWAVESAFE": 1,
    "ISFILLEDWITHLIQUID": 1, "HELD": 1, "INSIDE": 2, "ABOVE": 2,
    "NEAR": 2, "BELOW": 2, "COLLISION": 1, "ToggleObjectOn": 1, "ToggleObjectOff": 1,
    "OpenObject": 1, "CloseObject": 1, "PickupObject": 1, "PutObject": 2,
}


def _split_top_level(text, separator):
    depth = 0
    parts, start = [], 0
    for i, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if depth < 0:
            raise ValueError("Unbalanced parentheses")
        if depth == 0 and text.startswith(separator, i):
            parts.append(text[start:i].strip())
            start = i + len(separator)
    if depth:
        raise ValueError("Unbalanced parentheses")
    parts.append(text[start:].strip())
    return parts


def parse_state_formula(text):
    """Parse NOT, AND, OR, implication and parentheses with explicit precedence."""
    text = text.strip()
    for separator, operator in [("->", None), (" OR ", CTLOr), (" AND ", CTLAnd)]:
        parts = _split_top_level(text, separator)
        if len(parts) > 1:
            if not all(parts):
                raise ValueError("Missing operand")
            if operator is None:
                if len(parts) != 2:
                    raise ValueError("Parenthesize chained implications")
                return CTLOr([CTLNot(parse_state_formula(parts[0])), parse_state_formula(parts[1])])
            return operator([parse_state_formula(part) for part in parts])
    if text.startswith("(") and text.endswith(")"):
        return parse_state_formula(text[1:-1])
    if text.startswith("NOT(") and text.endswith(")"):
        return CTLNot(parse_state_formula(text[4:-1]))
    match = re.fullmatch(r"([A-Za-z_]+)\(([^()]*)\)", text)
    if not match:
        raise ValueError(f"Unsupported state formula: {text}")
    name, raw_args = match.groups()
    args = [arg.strip().strip("'\"") for arg in raw_args.split(",")]
    if name not in PREDICATES:
        raise ValueError(f"Unsupported predicate: {name}")
    if len(args) != PREDICATES[name] or not all(args):
        raise ValueError(f"Invalid arguments for {name}")
    return CTLPrimitive(Proposition(name, args))


def parse_rule(text):
    if not isinstance(text, str):
        raise ValueError("Rules must be strings")
    for word in ["NOT", "AND", "OR"]:
        text = re.sub(r"\b" + word + r"\b", word, text, flags=re.IGNORECASE)
    text = text.strip()
    if not text.startswith("G(") or not text.endswith(")"):
        raise ValueError("Supported rule form: G(state_formula)")
    return text, CTLAllAlways(parse_state_formula(text[2:-1]))


def validated_steps(payload):
    steps = payload.get("trajectory") if isinstance(payload, dict) else None
    if not isinstance(steps, list) or not steps:
        raise ValueError("trajectory must be a nonempty list with an initial observation")
    steps = copy.deepcopy(steps)
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            raise ValueError(f"Step {index}: expected an object")
        metadata = step.get("event_metadata")
        if not isinstance(metadata, dict) or not isinstance(metadata.get("objects"), list):
            raise ValueError(f"Step {index}: event_metadata.objects must be a list")
        for obj in metadata["objects"]:
            if not isinstance(obj, dict) or not obj.get("objectId") or not obj.get("objectType"):
                raise ValueError(f"Step {index}: each object needs objectId and objectType")
        action = step.get("plan_action") or {}
        if not isinstance(action, dict):
            raise ValueError(f"Step {index}: plan_action must be an object")
        if index == 0 and action.get("action") not in (None, "Pass", "NoOp"):
            raise ValueError("Step 0 must be an initial observation (Pass or NoOp)")
        if index > 0 and not action.get("action"):
            raise ValueError(f"Step {index}: missing action")
        # Upstream relational predicates describe attempted actions, even failures.
        if action.get("action") in ("ToggleObjectOn", "ToggleObjectOff", "OpenObject", "CloseObject", "PickupObject"):
            if not (action.get("object_id") or action.get("objectId")):
                raise ValueError(f"Step {index}: action is missing object ID")
        if action.get("action") == "PutObject":
            if not (action.get("object_id") or action.get("objectId")) or not (action.get("receptacle_id") or action.get("receptacleObjectId")):
                raise ValueError(f"Step {index}: PutObject needs object and receptacle IDs")
    # The upstream converter pairs each action with the preceding object state.
    # Add an observation to expose the final post-action object state as well.
    steps.append({"plan_action": {"action": "NoOp"}, "event_metadata": copy.deepcopy(steps[-1]["event_metadata"])})
    return steps


def evaluate_payload(payload, rules):
    if not isinstance(rules, list) or not rules:
        raise ValueError("rules must be a nonempty list")
    sequence = trace_to_ctl_sequence(validated_steps(payload))
    tree = CTLParser().to_tree_traj(sequence)
    object_ids, id_to_type = _collect_object_ids(tree)
    # Include objects with no active unary predicate or spatial relation.
    for step in payload["trajectory"]:
        for obj in step["event_metadata"]["objects"]:
            object_id = str(obj["objectId"]).strip()
            object_ids.add(object_id)
            id_to_type[object_id] = obj["objectType"]
    outcomes = []
    for raw_rule in rules:
        try:
            rule, expression = parse_rule(raw_rule)
            bases = _extract_suffix_bases(rule)
            candidates = _build_suffix_candidates(bases, object_ids, id_to_type)
            if any(not values for values in candidates.values()):
                outcomes.append({"rule": rule, "status": "not_applicable", "reason": "No matching objects for rule variables"})
                continue
            suffixes = sorted(candidates, key=int)
            assignments = product(*(candidates[key] for key in suffixes))
            violation = None
            checked = 0
            for assignment in assignments:
                mapping = dict(zip(suffixes, assignment))
                checked += 1
                # Iterate finite invariants to avoid recursion failure on long logs.
                index = next((i for i, (state, action) in enumerate(tree.iter_sa_pairs())
                              if not expression.child.eval_state(state, action, mapping)), None)
                if index is not None:
                    violation = {"grounded_rule": _ground_rule_string(rule, mapping),
                                 "evaluation_index": index,
                                 "source_step": min(index, len(payload["trajectory"]) - 1),
                                 "terminal_observation": index == len(payload["trajectory"]),
                                 "evidence": sequence[2 * index]["edges"]}
                    break
            outcome = {"rule": rule, "status": "violated" if violation else "passed", "assignments_checked": checked}
            if violation:
                outcome["witness"] = violation
            outcomes.append(outcome)
        except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
            outcomes.append({"rule": raw_rule, "status": "error", "message": str(exc)})
    statuses = {item["status"] for item in outcomes}
    status = ("error" if "error" in statuses else "violated" if "violated" in statuses
              else "not_applicable" if statuses == {"not_applicable"} else "passed")
    return {"status": status, "source_steps": len(payload["trajectory"]), "rules": outcomes}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-dir", required=True, type=Path)
    parser.add_argument("--rules", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    rules = json.loads(args.rules.read_text(encoding="utf-8"))
    if not isinstance(rules, list) or not rules:
        parser.error("Rules JSON must be a nonempty list")
    paths = sorted(p for p in args.trace_dir.rglob("*.json") if p.resolve() not in {args.output.resolve(), args.rules.resolve()})
    if not paths:
        parser.error("No JSON traces found")
    results = []
    for path in paths:
        try:
            result = evaluate_payload(json.loads(path.read_text(encoding="utf-8")), rules)
        except (ValueError, TypeError, KeyError) as exc:
            result = {"status": "error", "message": str(exc)}
        results.append({"trace": path.relative_to(args.trace_dir).as_posix(), **result})
    counts = {status: sum(r["status"] == status for r in results)
              for status in ("passed", "violated", "not_applicable", "error")}
    report = {"scope": "Offline finite-trace checks; passed means no violations of applicable supplied rules.",
              "counts": counts, "results": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts))
    return 2 if counts["error"] else 1 if counts["violated"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
