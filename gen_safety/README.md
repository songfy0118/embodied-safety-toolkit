# Scenario generation

`scenarios.py` creates safe/unsafe metadata trace pairs for six families. `build_cases(seed=7, variants=2)` returns independent JSON-serializable cases. Each case records its family, seed, expected status and synthetic provenance. The suite validates its initial state against the corresponding catalog rule before evaluating the action.

`constants.py` is retained from the team's local source archive because the published upstream converter imports it but the checked public branch omits `gen_safety`. Its source hash is preserved in `UPSTREAM_MANIFEST.json`.

The fixtures model metadata and bounding boxes directly. They do not execute physics, generate ALFRED tasks, or claim that arbitrary placements are realizable in AI2-THOR. Add a new family by extending the generator, adding its explicit rule to `configs/rules.json`, and covering both the trigger and a safe control in tests.
