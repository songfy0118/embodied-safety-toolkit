# Source and contributions

## Source

- Upstream: https://github.com/NU-IDEAS-Lab/SENTINEL_code
- Material used: the user's local `SENTINEL项目.zip` team-code backup.
- Extraction date: 2026-09-28.
- Commit: unknown; this archive has no verified commit reference.
- Public source located during release preparation: https://github.com/NU-IDEAS-Lab/SENTINEL, branch `ai2thor`, commit `0cfa2739f0783f0f058a62d2334d8b49a5d66cf1`. The old `_code` URL returned repository-not-found. `PUBLIC_UPSTREAM.json` records a file-by-file comparison with the newly downloaded public source.
- Reuse context: Feiyang reports that the supervising team authorized participants to reuse project components in personal portfolios. The archive also includes the MIT license reproduced here.

`UPSTREAM_MANIFEST.json` records the archive hash and original per-file hashes. Source line endings were normalized to LF. The extracted modules retain their original attribution; the code is not presented as solely written by Feiyang.

## Contribution context

This is collaborative embodied-agent safety research with Northwestern IDEAS Lab and Prof. Qi Zhu. Feiyang's prior work includes reusable AI2-THOR safety-scenario templates, scene initialization and object-type fixes, and local task-generation checks. A template generates multiple cases across scene/object choices; template count is not a count of all tested instances.

The selected evaluation subsystem gives a reviewer the wider technical context in which that work operates: simulated observations become predicates, predicates feed rule evaluation, and violations inform debugging and test design. Packaging this subsystem does not retroactively establish authorship of all its implementation or reproduce earlier experiments.

## New work in this portfolio edition

- Extracted a focused offline evaluation subsystem, its constants and its bundled tree utility.
- Added `safety_eval/offline.py` for validation, scoped rule parsing, object grounding, batch execution, terminal-state checking and violation witnesses.
- Added the complete seeded scenario-to-report workflow, a requirement catalog, six scenario families with safe controls, a controller adapter, JSON/CSV/HTML reports and 23 tests. The default suite generates 24 synthetic trajectories.
- Added setup instructions, architecture explanation, validation results and application wording.

## Changes to extracted files

- `safety_eval/tree_traj.py`: import the tree library already bundled in the source using a relative package import.
- `safety_eval/trace_to_ctl.py`: handle a null error message; accept camelCase as well as snake_case object/receptacle action IDs; add a documented bounding-box BELOW predicate for the shower scenario.
- All other extracted Python files remain unchanged apart from line endings. The original files' checksums are preserved in the manifest.

The original six-case independent demo remains in the neighboring `embodied-safety-scenarios` directory; it is a separate teaching example. This directory contains the team-derived portfolio edition.

## Publication source audit

The public `ai2thor` branch contains the same twelve extracted safety-evaluation Python modules as the archive baseline (apart from this edition's two adapted files). Its MIT notice identifies IDEAS Lab and is retained in `LICENSE-UPSTREAM`. The archive notice remains in `LICENSE`. The checked public branch imports `gen_safety.constants` but does not include that directory; this edition preserves the needed archive-derived constants instead of silently dropping that dependency. New code is identified in `LICENSE-TOOLKIT`.

The generated cases, tests and reports are new portfolio engineering. They are not reconstructed historical logs or claims of individual authorship of the full SENTINEL system.
