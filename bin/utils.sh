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

# Get the base directory of the give path.
get_base_dir() {
    dirname $(readlink -f $1)
}

get_excute_dir() {
    dirname $(readlink -f $0)
}

get_excute_dir2() {
    cd $(dirname $0); pwd
}

# Test if an array contains an element.
# CREDITS: https://stackoverflow.com/a/47541882
#
# Pass the correct the arguments like this (mind the double-quotes):
# is_array_element "$elem" "${array[@]}"
is_array_element() {
    local elem="$1"
    shift
    # use the command exit value as the return value
    printf '%s\0' "$@" | grep -qxzF -- "${elem}"
    return

    # or use alias
    local array=("$@")
    printf '%s\0' "${array[@]}" | grep -qxzF -- "${elem}"
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

# Check if a ssh connection can be established.
check_ssh_connection() {
    local username=$1
    local host=$2
    # This execute a command after a ssh connection established, the command
    # could be:
    #   - true or /bin/true or /usr/bin/true
    #   - exit
    # Exit with 0 indicates the connection is ok.
    ssh -q "${username}@${host}" true
}

# Convert video to gif using ffmpeg.
# cf. https://askubuntu.com/a/837574
convert_to_gif() {
    set -x
    local input=$1
    local output="${input%.*}"
    local options=(
        -r 30
# See https://superuser.com/a/556031 for explaination of parameters
# if you want scale, uncomment the following line.
#        -vf "fps=15,scale=300:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
        -vf "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
        -loop 0
    )
    case "$2" in
        --speed)
            ffmpeg -r 60 -i "$input" -r 40 \
                -vf "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
                "${output}.gif"
            ;;
        --quality)
            # NOTE: this option generates high-quality gif with a larger file size.
            ffmpeg -i "$input" "${options[@]}" "${output}.gif"
            ;;
        --scale)
            ffmpeg -i "$input" -r 15 \
                -vf "scale=512:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
                "${output}.gif"
            ;;
        *)
            ffmpeg -i "$input" "${output}.gif"
            ;;
    esac
}

sync_folder() {
    notify "sync... $1 to $2"
    rsync -auh --progress --size-only --exclude=".*" \
        $1 $2
}

# Find a desktop entry.
find_desktop_app() {
    local query="$1"
    find ~/.local/share/applications -iname "*${query}*"
    find /usr/share/applications/ -iname "*${query}*"
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

# An easy way to test microphone.
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

# List function names of a script.
# https://unix.stackexchange.com/a/260659
function list_my_scripts() {
    bash -c '. ~/bin/utils.sh; typeset -F' | cut -d' ' -f3
}

# Download bdy files via alist link.
download_from_bdy() {
    echo "Download bdy files via alist link.\n"
    curl -LX GET "$1" \
        -H 'User-Agent:pan.baidu.com' \
        -O \
        -C -
}

# Handy way to proxy in terminal.
proxydo() {
    export ALL_PROXY=http://127.0.0.1:8080
    $@
    unset ALL_PROXY
}
