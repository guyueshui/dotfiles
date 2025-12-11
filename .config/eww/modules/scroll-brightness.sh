#!/bin/bash -x

signal=$1
cur_brightness=$(brightnessctl info | grep -i 'current brightness' | awk '{print $4}' | tr -d '()%')
echo "$cur_brightness"

[ "$signal" == 'up' ] && {
    brightnessctl set 1%+
} || {
    brightnessctl set 1%-
}
