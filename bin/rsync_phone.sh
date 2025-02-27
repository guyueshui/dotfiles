#!/bin/bash
# author: yychi
# date: 2024-11-21

set -e # exit when error

_say_what_i_do() {
cat << COMMENT
This script is used to backup some folders from mobile phone to here (the
directory of a backup disk). To achieve this, you should

1. have \`rsync\` installed **BOTH** on your PC and phone;
2. start a ssh server on your mobile phone, i.e., SSHelper or Termux;
3. config your ssh login via .ssh/config and ssh-copy-id such that you can
   login your PC (and/or mobile) simply with \`ssh <hostname>\`.

See: https://askubuntu.com/a/343740

To configure those directories you want to backup, just modify the
\`folders_to_sync\` variable.

-------------------------------------------------------------------------------

Usage:
    $0 <backup|restore>
    
    backup  	Backup phone to remote directory.
    restore	Restore from remote to phone.

COMMENT
}

notify() {
    echo "--- $*"
}

termux_map_root=~/storage/shared
folers_to_sync=(
    Pictures
    Snapseed
    backup
    billing
    Books
    dictionary
    Download
    eudb_en
    Fonts
    GooglePinyinInput
    neo_backuped_data
    Music
    Movies
    )

# folders in this array will sync files deletion
folders_sync_delete=(
    Pictures
    Download
    neo_backuped_data
)

sync_folder_v1() {
    if [ ! -d $1 ]; then
        mkdir $1
    fi
    rsync -auh --progress --size-only --exclude=".*" \
        munch:storage/shared/$1/ $1
}

sync_folder() {
    notify "sync... folder $1 to $2"
    # use ssh -q to suppress barrier of ssh
    rsync -auhzP --size-only --exclude=".*" \
	-e "ssh -q" \
        $3 \
        $1 $2
}

# backup, excuted on phone
push_phone_to_remote() {
    cd $termux_map_root
    sync_folder $1 $remote_root $2
}

# restore, excuted on phone
pull_remote_to_phone() {
    cd $termux_map_root
    sync_folder $remote_root$1 .
}



func=
case "$1" in
    -\?|-h|--help|--usage)
        _say_what_i_do
        exit 0
        ;;
    "backup")
        notify "backup on phone"
        func=push_phone_to_remote
        ;;
    "restore")
        notify "restore on phone"
        func=pull_remote_to_phone
        ;;
    *)
        notify "input is invalid"
        _say_what_i_do
        exit 1
        ;;
esac

case "$2" in
    --to-mibook)
	    local_storage="/home/yychi/EXTRA/Android/munch/device_sdcard/"
	    remote_root="mi-book:$local_storage"
        ;;
    --to-dell-lan)
	    local_storage="/media/sdc2/android_device/Android/munch/"
	    remote_root="dell-inspiron-lan:$local_storage"
        segate=1
        ;;
    *)
	    local_storage="/srv/alist/Android/munch/"
	    remote_root="dell-inspiron-frp:$local_storage"
        ;;
esac


echo "Backup to $remote_root"
# confirm excute
read -re -p "Ready to excute? (y/n) " CHOICE
if ! [[ "${CHOICE}" =~ (Y|y) ]]; then
    notify "aborted!"
    exit 1
fi

for folder in ${folers_to_sync[*]}; do
    # test whether a string is in an array
    if printf '%s\0' "${folders_sync_delete[@]}" | grep -qxzF -- "${folder}" && \
        ((segate != 1))
    then
	    notify "$folder is delete sync"
        $func $folder --delete
	else
    
	    notify "$folder is norm sync"
        $func $folder
    fi
    echo; echo # for two newlines
done
