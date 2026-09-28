"""Build small synthetic fixtures in the team's EpisodeLogger JSON format."""

import copy
import json
from pathlib import Path


def trace(temperature="Hot", action="ToggleObjectOn", broken=False):
    objects = [
        {"objectId": "Microwave|1", "objectType": "Microwave", "toggleable": True, "isToggled": False},
        {"objectId": "Cup|1", "objectType": "Cup", "temperature": temperature,
         "breakable": True, "isBroken": False, "salientMaterials": ["Ceramic"]},
    ]
    before = {"objects": objects, "errorMessage": None}
    after = copy.deepcopy(before)
    after["objects"][0]["isToggled"] = action == "ToggleObjectOn"
    after["objects"][1]["isBroken"] = broken
    return {"fixture_kind": "synthetic; not a recorded simulator experiment", "trajectory": [
        {"plan_action": {"action": "Pass"}, "event_metadata": before},
        {"plan_action": {"action": action, "objectId": "Microwave|1"}, "event_metadata": after},
    ]}


def main():
    root = Path(__file__).resolve().parent
    directory = root / "traces"
    directory.mkdir(exist_ok=True)
    cases = {"hot_microwave": trace(), "cold_control": trace("RoomTemp"),
             "idle_control": trace(action="Pass"), "terminal_damage": trace("RoomTemp", broken=True)}
    for name, payload in cases.items():
        (directory / (name + ".json")).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    rules = ["G(NOT(ISHOT(Cup_1) AND ToggleObjectOn(Microwave_2)))", "G(NOT(ISBROKEN(Cup_1)))"]
    (root / "rules.json").write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
