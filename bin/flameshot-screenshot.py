#!/usr/bin/env python

import subprocess
import os

env = os.environ.copy()
env["QT_SCALE_FACTOR"] = '1.2'

subprocess.run(
        ["flameshot", "gui"],
        env=env,
        shell=False,
        )
