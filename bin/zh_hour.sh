#!/bin/bash

zh_hours=("子" "丑" "寅" "卯" "辰" "巳" "午" "未" "申" "酉" "戌" "亥")
# echo ${zh_hours[@]}

get_now_zh_hour() {
    local h=$([ -z "$1" ] && echo $(date +%k) || echo $1)
    local i=$(( ((h + 1) / 2) % 12 ))
    echo ${zh_hours[i]}
}

get_now_zh_hour $1
