#!/bin/bash

cap=`eww get EWW_BATTERY | jq .BAT1.capacity`
st=`eww get EWW_BATTERY | jq -r .BAT1.status`
if (( $cap >= 95 )) && [[ "$st" =~ Charging ]]; then
    dunstify \
        -i battery-090-charging \
        -a system -t 5000 \
        Battery \
        "Battery is near charged($cap%), consider unplugging the power cable."
    echo "pls unplug"
elif (( $cap <= 10 )) && [ x$st == "xDischarging" ]; then
    dunstify \
        -u critical
        -i battery-caution \
        -a system -t 5000 \
        Battery \
        "Battery is near dried($cap%), consider plugging the power cable!"
    echo "pls plug"
else
    echo 0
fi
exit 0

