#!/usr/bin/env python3
# Original Author: Elkowar https://github.com/elkowar/dots-of-war/blob/master/eww-bar/.config/eww-bar/swayspaces.py

import subprocess
import json

def get_workspace_icon(index):
    # you need install Font Awesome font to display these symbols
    # see: https://fontawesome.com/download
    icons = {
        1:' ',
        2:' ',
        3:' ',
        4:' ',
        5:' ',
        8:' ',
    }
    return icons.get(index, icons[8])


def get_workspaces():
    output = subprocess.check_output(["swaymsg", "-t", "get_workspaces"])
    return json.loads(output.decode("utf-8")) 


def generate_workspace_data() -> dict:
    data = {}
    for wsp in get_workspaces():
        if wsp["output"] not in data:
            data[wsp["output"]] = []
        n_n = wsp["name"].split(':')
        assert len(n_n) == 2, "invalid workspace name: %s" % wsp["name"]
        has_name = n_n[-1] != ""
        name = n_n[-1] if has_name else n_n[0]
        if not wsp["focused"]:
            name = "%s %s" % (wsp['num'], name) if has_name else wsp["name"]
        else:
            name = "%s %s" % (get_workspace_icon(wsp['num']), name)
        i = {
            "display_name": name,
            "name": wsp["name"],
            "monitor": wsp["output"],
            "focused": wsp["focused"],
            "visible": wsp["visible"],
            "index": wsp["num"],
        }
        if wsp["focused"]:
            i["class"] = "focused"
            i["icon"] = ""
        elif wsp["visible"]:
            i["class"] = "visible"
            i["icon"] = ""
        else:
            i["class"] = "hidden"
            i["icon"] = ""
        data[wsp["output"]].append(i)

    return data


if __name__ == "__main__":
    process = subprocess.Popen(
        ["swaymsg", "-t", "subscribe", "-m", '["workspace"]', "--raw"],
        stdout=subprocess.PIPE,
    )
    if process.stdout is None:
        print("Error: could not subscribe to sway events")
        exit(1)
    while True:
        print(json.dumps(generate_workspace_data()), flush=True)
        line = process.stdout.readline().decode("utf-8")
        if line == "":
            break
