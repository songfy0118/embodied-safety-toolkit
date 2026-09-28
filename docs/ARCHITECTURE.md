# Architecture and research coverage

The SENTINEL research framework considers semantic interpretation, action plans and execution trajectories. This toolkit organizes a working subset around explicit rule catalogs, scenario construction, trace adapters, grounded invariant checks and inspectable reports.

| Research layer | Implementation here | Remaining integration |
|---|---|---|
| Semantic | Human-reviewed requirement/formula catalog and syntax checks | Automatic NL-to-LTL translation and formal equivalence testing |
| Plan | Explicit action sequences accepted by the controller recorder | Pre-execution plan verification and model-generated plans |
| Trajectory | Metadata extraction, object grounding, finite invariants, violation evidence | Comprehensive temporal/branching validation and real simulator experiments |
| Experiment workflow | Reproducible seeded fixture suite and reports | Dataset splits, independent ground truth and calibrated model comparisons |

## Data flow

1. `configs/rules.json` defines the test requirement and its executable rule.
2. `gen_safety/scenarios.py` generates independent control/unsafe traces.
3. `pipeline` confirms that each initial state satisfies its rule.
4. `safety_eval.trace_to_ctl` extracts predicates using upstream conversion logic.
5. `safety_eval.offline` binds object variables and checks each finite invariant.
6. `pipeline.reporting` exports outcomes and first-violation evidence.

Alternatively, `adapters.controller.record_plan` records an existing simulator controller and the offline CLI consumes its saved JSON. The adapter does not initialize a simulator or translate a model's free-form instructions.

The fixture generator and controller adapter share the trace schema; the fixture generator does not pretend to be a simulator. Unimplemented research layers have documented contracts and milestones rather than silent placeholder results.
