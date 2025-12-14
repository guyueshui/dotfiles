#!/bin/bash

is_mpd_running() {
    mpc > /dev/null 2>&1
}

init() {
    song=$(is_mpd_running && mpc current || echo "mpd not running")
    state=$(mpc status | grep -q playing && echo 1 || echo 0)
    
    echo "{\"song\": \"$song\", \"playing\": $state}"
}

listen_mpd() {
    mpc idleloop | while read -r line; do
        song=$(is_mpd_running && mpc current || echo "mpd not running")
        state=$(mpc status | grep -q playing && echo 1 || echo 0)
        echo "{\"song\": \"$song\", \"playing\": $state}"
    done
}

single() {
    init
    listen_mpd
}

while true; do
    is_mpd_running && {
        single || {
            echo "{\"song\": \"mpd not running\", \"playing\": 0}"
        }
    } || {
        echo "{\"song\": \"mpd not running\", \"playing\": 0}"
        sleep 3
    }
done
