#!/bin/bash

signal=$1
cur_vol=$(pactl get-sink-volume @DEFAULT_SINK@ | awk '{print $5}' | tr -d '%\n')

[ "$signal" == 'up' ] && {
    (( ++cur_vol > 100 )) && cur_vol=100 || true
} || {
    (( --cur_vol < 0 )) && cur_vol=0
    #pactl set-sink-volume @DEFAULT_SINK@ -1%
}
#echo "set vol to $cur_vol %"
pactl set-sink-mute @DEFAULT_SINK@ $((cur_vol <= 0))
pactl set-sink-volume @DEFAULT_SINK@ ${cur_vol}%
