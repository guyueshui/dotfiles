#!/bin/bash
#
# Provide some utilities.

notify() {
    echo "--- $*"
}

log_time() {
    # output like: 2024-11-15 18:12:19.404
    date +"%F %T.%3N"
}

# get the base directory of the give path
get_base_dir() {
    dirname $(readlink -f $1)
}

get_excute_dir() {
    dirname $(readlink -f $0)
}

get_excute_dir2() {
    cd $(dirname $0); pwd
}

clean_mem_cache() {
    free -wm
    sync
    sudo sh -c 'echo 1 >/proc/sys/vm/drop_caches'
    local ret=$?
    free -wm
    if [ $ret -ne 0 ]; then
        notify failed
    else
        notify succeed
    fi
}

sync_folder() {
    notify "sync... $1 to $2"
    rsync -auh --progress --size-only --exclude=".*" \
        $1 $2
}

transfer_0x0() {
    ~/bin/0x0.st.sh $*
}

transfer_file_io() {
    ~/bin/file.io.sh $*
}

transferwee() {
    ~/bin/transferwee.py $*
}

function rsync_phone {
    ~/bin/rsync_phone.sh $*
}

# an easy way to test microphone
# cf. https://bbs.archlinux.org/viewtopic.php?id=196525
function test-microphone() {
    arecord -vv -f dat /dev/null
}

#: here you see three ways for define a shell function
#: - function <func_name> { <func_body> }
#: - <func_name>() { <func_body> }
#: - function <func_name>() { <func_body> }

# add tools from gitignore.io
function gi() { curl -sLw n https://www.toptal.com/developers/gitignore/api/$@ ;}

cht() {
    ~/bin/cht.sh $*
}

copy_as_hugo_post() {
    ~/bin/copy_as_hugo_post.py $*
}

# list function names of a script
# https://unix.stackexchange.com/a/260659
function list_my_scripts() {
    bash -c '. ~/bin/utils.sh; typeset -F' | cut -d' ' -f3
}
