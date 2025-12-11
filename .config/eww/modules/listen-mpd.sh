#!/bin/bash

song=$(mpc current)
state=$(mpc status | grep -q playing && echo 1 || echo 0)

echo "{\"song\": \"$song\", \"playing\": $state}"

listen_mpd() {
    mpc idleloop | while read -r line; do
        song=$(mpc current)
        state=$(mpc status | grep -q playing && echo 1 || echo 0)
        echo "{\"song\": \"$song\", \"playing\": $state}"
    done
}

listen_mpd
