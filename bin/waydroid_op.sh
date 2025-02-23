#!/bin/bash

source utils.sh

WAYLAND_SOCK=wayland-1

_usage() {
    cat << COMMENT
This script is handy for start waydroid in X11 session.
CREDITS: https://unix.stackexchange.com/a/734975

Usage:
    $0 <start|stop>

    start   Check the wayland env and start waydroid in show-full-ui.
    stop    Stop the current waydroid session.

COMMENT
}


check_wayland_env() {
    [ -S "/run/user/$UID/${WAYLAND_SOCK}" ] && {
        notify "wayland session is ready"
    } || {
        killall -q weston
        while pgrep -u $UID -x weston >/dev/null; do sleep 1; done
        weston --xwayland &
        sleep 2
    }
    export WAYLAND_DISPLAY=wayland-1
}


case "$1" in
    "start")
        # use `waydroid` log to see the log
        check_wayland_env && waydroid show-full-ui &
        ;;
    "stop")
        waydroid session stop
        ;;
    *)
        _usage
        exit 1
        ;;
esac
