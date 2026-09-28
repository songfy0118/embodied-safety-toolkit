# Remaining work

The offline workflow is implemented; the following extensions are not claimed as completed.

1. **Real traces:** import authorized simulator logs, validate metadata completeness, and compare rule outcomes with manually reviewed events.
2. **Simulator integration:** run the controller adapter against the intended AI2-THOR version and reproduce scene initialization, including reachable positions and object affordances.
3. **Semantic evaluation:** define natural-language/formula pair inputs, connect a separately configured model client, and compare formulas using a formal equivalence checker. Catalog syntax checks alone are insufficient.
4. **Plan verification:** translate grounded plans and expected state transitions into a formal input representation, then validate plan properties before controller execution.
5. **Temporal coverage:** extend beyond finite invariants only with tested temporal semantics, branching cases and clear treatment of truncated traces.
6. **Experiment protocol:** define task success, applicable-rule coverage and independent reference outcomes before comparing agents.

No fake metrics or empty success-returning modules stand in for these stages.
