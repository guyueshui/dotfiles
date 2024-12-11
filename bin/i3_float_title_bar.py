#!/usr/bin/env python

"""
Whenever a window becomes floating, draw a title bar on it.
See https://github.com/Airblader/i3/issues/48#issuecomment-225631964
"""

import i3ipc
i3 = i3ipc.Connection()

def border_on_floating(i3, e):
    ws = i3.get_tree().find_focused().workspace()
    if (e.container.floating=='user_off'):
        e.container.command('border none')
    elif (e.container.floating=='user_on'):
        e.container.command('border normal')

i3.on('window::floating', border_on_floating)
i3.main()
