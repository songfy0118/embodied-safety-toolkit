# Rule catalog

`rules.json` is a list of objects with unique `id`, natural-language `requirement`, and logical `formula`. The suite maps each scenario family to the rule with that ID. The text/formula pairs are human-authored; no semantic-equivalence claim is made.

A variable such as `Cup_1` binds matching Cup objects. The same suffix refers to the same object across a formula. Different suffixes do not enforce distinct objects. `Object_1` matches the available object domain; constrain object types or relations to prevent unintended bindings.

Supported form is `G(state_formula)`. The predicate list and argument counts are defined in `safety_eval/offline.py`. Missing families, duplicate IDs, malformed formulas and unsupported predicates fail validation.

The standalone `safety_eval.offline` command takes a plain JSON list of formula strings, as shown in `examples/rules.json`; the suite takes this richer catalog.
