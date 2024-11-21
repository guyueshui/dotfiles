#!/bin/bash

# 将vob格式（占用较多空间）转为mp4格式。
# cf. http://www.ruhuamtv.com/thread-9782-1-1.html

INPUT_DIR=$1
OUTPUT_DIR=$2

notify()
{
    echo "--- $1"
}


_say_what_i_do()
{
    cat << EOF
Usage: $0 <INPUT_DIR> <OUTPUT_DIR>

Convert vob files in <INPUT_DIR> to mp4 files in <OUTPUT_DIR>.
EOF
}

_convert()
{
    cd $INPUT_DIR
    for line in $(find $INPUT_DIR -iname "*.vob" -printf "%f\n"); do
        out_basename=${line%.[vV][oO][bB]}.mp4
        notify "converting $line to $OUTPUT_DIR/$out_basename"
        ffmpeg -i $line -c:v libx264 -vf yadif -crf 18 "$OUTPUT_DIR/$out_basename"
    done
}


if [[ $# != 2 ]]; then
    _say_what_i_do
else 
    _convert $1 $2
fi
