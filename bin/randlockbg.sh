#!/bin/bash

# This script use i3lock with a random background image.
# use the following to glasp the effect
# convert Pictures/Aragaki_Yui.JPG RGB:- | i3lock -e --raw 1920x1080:rgb -i /dev/stdin

IMAGE_DIR=~/Pictures

cd $IMAGE_DIR

files=()
for i in *.jpg *.png; do
    [[ -f $i ]] && files+=("$i")
done
range=${#files[@]}
echo "range is $range"
echo ${files[RANDOM % range]}

#((range)) && convert "${files[RANDOM % range]}" RGB:- | i3lock -e --raw 1920x1080:rgb -i /dev/stdin 
