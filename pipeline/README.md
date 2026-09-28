# Suite orchestration and reporting

```bash
python -m pipeline --output outputs/my-run --seed 7 --variants 2
```

The output directory must be empty. `__main__.py` validates the catalog, generates cases, checks initial setups, evaluates each case, saves trace checksums and compares observed results with expected fixture labels. Variants must be an integer from 1 to 100.

`reporting.py` writes JSON details, CSV summaries and a self-contained HTML report with filtering and expandable evidence. External content is HTML-escaped. The report has no remote scripts, network requests or analytics.

The suite is a regression harness. Its expectation-match count is not a model evaluation metric. Use actual controller logs and an independently designed evaluation protocol before reporting agent safety or task-success rates.
