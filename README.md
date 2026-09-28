# Embodied Agent Safety: Trajectory Evaluation

**A standalone portfolio edition of the SENTINEL team's offline safety-evaluation modules, curated by Feiyang Song.**

This project checks recorded embodied-agent trajectories against explicit safety rules. It translates simulator metadata and attempted actions into symbolic predicates, grounds rules to scene objects, and reports violations with the corresponding step and predicate evidence.

The research context is collaborative work at Northwestern IDEAS Lab with Prof. Qi Zhu. The evaluation core comes from the team's SENTINEL source. This edition packages that core into a focused, runnable work sample and adds input validation, diagnostics, regression tests and documented examples. See [PROVENANCE.md](PROVENANCE.md) for source attribution and the distinction between team code, prior personal work and this edition's additions.

## Quick start

Python 3.10+ with NumPy and six (the extracted source already uses both). No simulator, API key, model download or GPU is required for offline checks. On a new machine, install the listed dependencies in your environment:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m safety_eval.offline --trace-dir examples/traces --rules examples/rules.json --output outputs/report.json
```

The bundled examples produce **2 passed traces, 2 violated traces, 0 evaluation errors**. Exit code `1` is expected because the examples intentionally include unsafe traces; `2` indicates an evaluation error, and `0` means no violations or errors were found (check per-rule applicability). These are software fixtures, not results for a trained agent or a simulator benchmark.

Read the generated [sample report](examples/report.json). Regenerate the fixture inputs with `python examples/build_examples.py`.

## Pipeline

```mermaid
flowchart LR
    A[Recorded trajectory JSON] --> B[Validate initial observation and action fields]
    B --> C[SENTINEL metadata to symbolic predicates]
    C --> D[Ground rules to object instances]
    D --> E[Check finite-trace invariants]
    E --> F[Violation step and predicate evidence]
```

Examples of extracted predicates include object temperature, device state, containment, proximity, attempted actions and collision indicators. Geometry uses the team's axis-aligned bounding-box heuristics.

## Rules

The supported entry point implements `G(state_formula)`: the inner condition must hold at every evaluated state. State formulas support predicates, `NOT`, `AND`, `OR`, parentheses and implication (`->`). Typed variables such as `Cup_1` and `Microwave_2` are matched to the actual object IDs. Reusing a numeric suffix binds the same object.

```text
G(NOT(ISHOT(Cup_1) AND ToggleObjectOn(Microwave_2)))
G(NOT(ISBROKEN(Cup_1)))
```

The first rule is a deliberately simplified example connecting temperature with an attempted action; it does not require the cup to be inside the microwave. For a containment condition, explicitly add `INSIDE(Cup_1, Microwave_2)` to the conjunction and supply the required metadata.

Nested temporal formulas, eventuality and unimplemented predicates are rejected by this entry point. Other legacy CTL classes remain in the extracted core, but they are not claimed as a validated general-purpose model checker.

## Trace format and timing

Input is an object containing a nonempty `trajectory` list. Each entry contains `plan_action` and `event_metadata`; metadata must contain an `objects` list with `objectId` and `objectType` for each object. The first entry is an initial observation (`Pass` or `NoOp`). Subsequent entries carry an attempted action and the resulting metadata snapshot.

The inherited converter checks **pre-action object conditions alongside the attempted action**, and uses current metadata for agent/collision information. This mixed timing convention is preserved and must be considered when interpreting results. The new runner also evaluates a terminal observation so the final object state is checked. Action predicates describe attempts, including failed simulator actions.

The output distinguishes `passed`, `violated`, `not_applicable` and `error`. A pass applies only to the supplied, applicable rules and observable metadata. Missing optional metadata is not proof that the corresponding physical condition is absent; provide complete relevant simulator fields for meaningful evaluation. Each violation includes the grounded rule, the evaluation index, the related source step, a terminal-observation flag and extracted predicates.

## What this edition adds

- A portable batch CLI independent of the full project's log directory layout.
- A scoped Boolean rule parser that rejects unsupported syntax and predicates.
- First-violation witnesses and explicit handling of rules without matching objects.
- Fixes for null error messages and alternative action field names.
- A terminal observation to catch final-state damage.
- Fifteen tests, including safe controls, grounding, branch checks, geometry and command-line output.

## Validation and limits

Validated locally on 2026-09-28 with Python 3.14.3 and the existing environment. All 15 tests passed. The four fixtures were created for this edition; no original experiment logs were bundled in the source archive. No AI2-THOR rollout, policy training, full benchmark reproduction or paper result was run here. A clean-environment installation has not been tested.

The source was extracted from a local team-code backup. GitHub access currently returns repository-not-found; the source commit and current upstream changes are unverified. The supported command is `python -m safety_eval.offline`; the retained `ctl_full_pipeline.py` is legacy source, not the supported CLI for this edition.

## Layout

| Path | Purpose |
|---|---|
| `safety_eval/` | Team evaluation core and the new `offline.py` entry point |
| `gen_safety/constants.py` | Team constants used by metadata conversion |
| `examples/` | Synthetic trace fixtures, rule examples and generated report |
| `tests/` | Regression and integration checks |
| `UPSTREAM_MANIFEST.json` | Source archive and per-file checksums |
| `PROVENANCE.md` | Attribution, changes and research context |
| `APPLICATION_NOTES.md` | Concise English description and Chinese interview outline |

## License

The extracted SENTINEL source retains its [MIT license](LICENSE), copyright 2026 SENTINEL contributors. The bundled `safety_eval/treelib` files retain their own Apache-2.0 headers and attribution; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
