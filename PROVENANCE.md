# Source and contributions

## Source

- Upstream: https://github.com/NU-IDEAS-Lab/SENTINEL_code
- Material used: the user's local `SENTINEL项目.zip` team-code backup.
- Extraction date: 2026-09-28.
- Commit: unknown; this archive has no verified commit reference.
- Current remote: a read-only GitHub attempt returned repository-not-found. This is not represented as a fresh upstream checkout.
- Reuse context: Feiyang reports that the supervising team authorized participants to reuse project components in personal portfolios. The archive also includes the MIT license reproduced here.

`UPSTREAM_MANIFEST.json` records the archive hash and original per-file hashes. Source line endings were normalized to LF. The extracted modules retain their original attribution; the code is not presented as solely written by Feiyang.

## Contribution context

This is collaborative embodied-agent safety research with Northwestern IDEAS Lab and Prof. Qi Zhu. Feiyang's prior work includes reusable AI2-THOR safety-scenario templates, scene initialization and object-type fixes, and local task-generation checks. A template generates multiple cases across scene/object choices; template count is not a count of all tested instances.

The selected evaluation subsystem gives a reviewer the wider technical context in which that work operates: simulated observations become predicates, predicates feed rule evaluation, and violations inform debugging and test design. Packaging this subsystem does not retroactively establish authorship of all its implementation or reproduce earlier experiments.

## New work in this portfolio edition

- Extracted a focused offline evaluation subsystem, its constants and its bundled tree utility.
- Added `safety_eval/offline.py` for validation, scoped rule parsing, object grounding, batch execution, terminal-state checking and violation witnesses.
- Added four explicitly synthetic example traces and fifteen tests.
- Added setup instructions, architecture explanation, validation results and application wording.

## Changes to extracted files

- `safety_eval/tree_traj.py`: import the tree library already bundled in the source using a relative package import.
- `safety_eval/trace_to_ctl.py`: handle a null error message; accept camelCase as well as snake_case object/receptacle action IDs.
- All other extracted Python files remain unchanged apart from line endings. The original files' checksums are preserved in the manifest.

The original six-case independent demo remains in the neighboring `embodied-safety-scenarios` directory; it is a separate teaching example. This directory contains the team-derived portfolio edition.
