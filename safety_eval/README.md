# Safety evaluation

Supported CLI: `python -m safety_eval.offline --trace-dir ... --rules ... --output ...`.

`offline.py` validates trace shape, parses `G(state_formula)`, grounds typed variables and reports the first violation. Boolean expressions support NOT, AND, OR, parentheses and implication. Unsupported predicates and temporal nesting produce explicit errors. Invariants are evaluated iteratively so long saved logs do not exhaust Python recursion.

`trace_to_ctl.py` derives object and action predicates. The portfolio adds null-message handling, action-ID aliases and a BELOW relation defined by non-overlapping vertical bounds with horizontal overlap. Geometry remains a coarse AABB approximation.

`ctl.py`, `ctl_parser.py`, `tree_traj.py`, `collision.py` and `ctl_full_pipeline.py` are attributed upstream modules. The latter retains a legacy CLI and is not the supported command for this release. Retained temporal classes beyond finite state invariants have not been comprehensively verified. `treelib` is the original bundled tree utility with its Apache-2.0 notices.

See [trace schema](../docs/TRACE_SCHEMA.md) for pre-action/current-state timing and metadata coverage limitations.
