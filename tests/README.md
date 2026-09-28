# Tests

```bash
python -m unittest discover -s tests -v
```

`test_offline.py` covers rule grounding, safe controls, terminal-state damage, field aliases, parser precedence, unsupported syntax, missing objects, input validation, immutability, branching invariants, containment and CLI output.

`test_pipeline.py` covers all six generated families, seed reproducibility, invalid configuration, output protection, report files, long traces and controller failure behavior.

The tests are offline and use synthetic metadata or fake controllers. They do not establish physics fidelity or benchmark/model performance. The GitHub Actions workflow runs the tests and default suite on Python 3.10 and 3.12.
