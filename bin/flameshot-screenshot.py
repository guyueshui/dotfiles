#!/usr/bin/env python

import subprocess
import os

env = os.environ.copy()
# env["QT_QPA_PLATFORM"] = "wayland"

subprocess.run(
        ["flameshot", "gui"],
        env=env,
        shell=False,
        )
