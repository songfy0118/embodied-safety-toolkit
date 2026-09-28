# Reproduce this release

Run commands from the repository root with Python 3.10+. Dependencies are NumPy and six; the test runner is Python's standard-library unittest.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m pipeline --output outputs/run-seed7 --seed 7 --variants 2
```

Expected suite summary: total 24, matched_expectations 24, passed 12, violated 12, error 0, not_applicable 0. Output includes trace checksums and the rule-catalog checksum. A fixed seed reproduces the same generated JSON. Variants change selected object types within the supported family, not entire physical scenes.

## Individual trace evaluator

```bash
python -m safety_eval.offline --trace-dir examples/traces --rules examples/rules.json --output outputs/offline.json
```

Expected counts: passed 2, violated 2, error 0, not_applicable 0. This command returns 1 intentionally.

| Command | Exit 0 | Exit 1 | Exit 2 |
|---|---|---|---|
| `python -m pipeline` | All fixture expectations match | A fixture differs from its expectation | Invalid input or run configuration |
| `python -m safety_eval.offline` | No detected violations/errors; inspect applicability | At least one violation | Evaluation/input error |

An invariant pass is limited to the supplied rules, object bindings and observed metadata. A missing object is reported as not applicable. Missing optional simulator fields are not evidence of physical safety.

## Simulator extension

See [adapters/README.md](adapters/README.md). Simulator installation and scene setup are owned by the calling application; no simulator or remote model is launched by the demo. Run the saved result through `safety_eval.offline` with rules appropriate to that scene.

Local validation used the existing Windows Python 3.14.3 environment. CI defines fresh Python 3.10/3.12 runs; their current outcome is visible in GitHub Actions, not inferred from this document.
