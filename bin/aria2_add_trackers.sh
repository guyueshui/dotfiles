#!/bin/bash

# This script used to add trackers from
# https://github.com/ngosang/trackerslist.git
# to aria2 conf.

CONF_FILE="$HOME/.aria2/aria2.conf"
SOURCE_URL='https://github.com/ngosang/trackerslist.git'
CHOSEN_FILE="trackers_best_ip.txt"

# see: http://c.biancheng.net/view/1120.html
tmp_str=${SOURCE_URL##*/}
foler_name=${tmp_str%.git}
SOURCE_PATH="/tmp/$foler_name"

notify()
{
    echo "--- $*"
}

check_aria2_conf()
{
    if [ ! -f $CONF_FILE ]; then
        notify "$CONF_FILE not exists!"
        exit 1
    else
        notify "found $CONF_FILE"
    fi
}

download_trackers()
{
    git clone $SOURCE_URL $SOURCE_PATH
    cd $SOURCE_PATH
    out=$(echo $(grep . $CHOSEN_FILE) | sed 's/ /,/g')
    echo "# auto added trackers at $(date)" >> $CONF_FILE
    echo "bt-tracker=$out" >> $CONF_FILE
}

check_aria2_conf
download_trackers
notify "update trackers of file: $CONF_FILE, done"
