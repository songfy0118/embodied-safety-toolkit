# Simulator recording adapter

`record_plan(controller, actions)` accepts an existing controller with `last_event.metadata` and `step(**action)`. It records an initial observation followed by actions and returned metadata. Snapshots are copied so later simulator mutation cannot corrupt previous steps. By default it stops after `lastActionSuccess == False`; exceptions propagate with their diagnostics.

```python
import json
from pathlib import Path
from adapters.controller import record_plan

# controller must already be initialized in your own environment.
actions = [{"action": "MoveAhead"}]
payload = record_plan(controller, actions)
Path("episode.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
```

The caller owns reset, scene setup, reachable positions, object selection and cleanup. The toolkit does not import/install AI2-THOR or call paid models. Contract tests use a fake controller. A live simulator integration remains unverified.

The trace evaluator accepts both `objectId` and `object_id`. For `PutObject`, provide an unambiguous object ID and receptacle ID (`receptacleObjectId` or `receptacle_id`); raw controller formats may need application-specific normalization before evaluation.
