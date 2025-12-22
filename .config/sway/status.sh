#!/bin/bash

battery_status=$(upower -i $(upower -e | grep BAT) | grep percentage | awk '{print $2}')
datetime_status=$(date '+%F %X')

echo BAT $battery_status '|' $datetime_status
