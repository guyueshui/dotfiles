#!/bin/bash
#
# Provide some utilities.

notify()
{
    echo "--- $*"
}

log_time()
{
    # output like: 2024-11-15 18:12:19.404
    date +"%F %T.%3N"
}

# get the base directory of the give path
get_base_dir()
{
    dirname $(readlink -f $1)
}

get_excute_dir()
{
    dirname $(readlink -f $0)
}

get_excute_dir2()
{
    cd $(dirname $0); pwd
}

clean_mem_cache()
{
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

sync_folder()
{
    notify "sync... $1 to $2"
    rsync -auh --progress --size-only --exclude=".*" \
        $1 $2
}
