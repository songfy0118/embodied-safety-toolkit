# Trace schema and timing

A trace is a JSON object with a nonempty `trajectory` list. Every entry contains `plan_action` and `event_metadata`. Metadata has an `objects` list; each object needs `objectId` and `objectType`. Entry zero is an initial observation with Pass/NoOp (or no action); subsequent entries contain the attempted action and the resulting snapshot.

Provide all fields needed by the rule: temperature, toggleable/isToggled, breakable/isBroken, openable/isOpen, dirtyable/isDirty, salientMaterials, liquid flags, inventory and bounding boxes as appropriate. AABB cornerPoints must contain eight 3D points. Agent geometry uses the upstream approximate agent box. Missing optional metadata does not prove safety.

## Timing convention

The inherited converter combines pre-action object conditions and attempted actions with current agent/collision metadata. The toolkit preserves this convention. It adds a terminal observation so the final post-action object state is also checked. A violation's `source_step` identifies the related trace entry; `terminal_observation` identifies the added terminal check. `evaluation_index` is the internal check index, not a physical timestamp.

Actions indicate attempts, including failed actions. An invariant is evaluated over observed finite states. A passed result is limited to applicable supplied rules and observed metadata. `not_applicable` means a variable has no matching object; `error` means the rule or trace could not be evaluated.

## Geometry limitations

NEAR uses upstream box distance. INSIDE uses containment and simulator receptacle metadata. ABOVE uses a surface-contact heuristic. The new BELOW predicate requires vertical separation and horizontal overlap. These approximations do not model fluids, heat transfer, flexible geometry or full contact dynamics.

Do not infer task success from an absence of rule violations. Use separate task outcomes from a simulator or independent evaluator.
