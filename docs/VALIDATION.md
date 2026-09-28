# Validation record

Local validation on 2026-09-28, Windows, Python 3.14.3, using existing NumPy/six packages:

- `python -m unittest discover -s tests -v`: **23 tests passed**.
- `python -m pipeline --output outputs/first-suite --seed 7 --variants 2`: **24/24 fixture expectations matched**; 12 passed traces, 12 violated traces, zero errors or inapplicable cases.
- The test suite separately covers 36 generated traces with a different seed.
- The legacy four-fixture offline command returned two passes and two violations, as expected.
- Public source comparison: all 12 extracted safety_eval Python modules matched the public commit before local adaptation, except the two documented adapted files. See `PUBLIC_UPSTREAM.json`.

No live AI2-THOR execution, paid model call, policy training, semantic-equivalence evaluation or full paper benchmark was run. Controller tests use a fake controller. The fixture suite demonstrates execution and regression coverage, not performance on real agents.

The GitHub Actions configuration requests clean Python 3.10/3.12 tests. Consult the remote workflow result for its actual status.
