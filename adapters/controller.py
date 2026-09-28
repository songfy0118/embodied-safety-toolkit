"""Record actions from an already configured AI2-THOR-compatible controller."""

import copy


def record_plan(controller, actions, stop_on_failure=True):
    """Do not create/reset the simulator or silently continue past action failures.

    controller must expose last_event.metadata and step(**action). The caller
    owns simulator setup, scene initialization, credentials and cleanup.
    """
    payload = {"source": "controller_adapter", "trajectory": [
        {"plan_action": {"action": "Pass"},
         "event_metadata": copy.deepcopy(controller.last_event.metadata)}
    ]}
    for index, action in enumerate(actions):
        if not isinstance(action, dict) or not action.get("action"):
            raise ValueError(f"Action {index}: expected a dict with an action name")
        event = controller.step(**copy.deepcopy(action))
        payload["trajectory"].append({"plan_action": copy.deepcopy(action),
                                       "event_metadata": copy.deepcopy(event.metadata)})
        if event.metadata.get("lastActionSuccess") is False and stop_on_failure:
            payload["stopped_on_failure"] = index
            break
    return payload
