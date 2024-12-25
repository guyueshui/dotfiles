#!/bin/bash

_say_what_i_do() {
    cat << COMMENT
This script backup termux packages and configurations which allow you to
restore on a fresh-installed termux to get your effort back.

This script just follows the steps in termux wiki on how to backup it:

    https://wiki.termux.com/wiki/Backing_up_Termux

-------------------------------------------------------------------------------

Usage:
    $0 <backup|restore>

    backup      Backup termux config as tar in sdcard.
    restore     Restore from the previous backuped tar ball.

COMMENT
}

msg() {
    echo "--- $*"
}

backup() {
    mkdir -p /sdcard/backup
    local tarball=termux-backup-$(date +%F).tar.gz
    # use termux tar for it's newer than system default
    local tarbin=$PREFIX/bin/tar
    msg "tarbin is $tarbin"
    msg "start excute backup..."
    su sh -c \
    $tarbin -cavf /sdcard/backup/$tarball \
        -C /data/data/com.termux/files \
	    --exclude-caches \
	    --exclude=.zsh_history \
	    --exclude=.cache \
	    --exclude=usr/var \
	    --exclude=usr/tmp \
	    ./home ./usr
    msg "done generate $tarball."
}

restore() {
    local tarball=$1
    msg "start restore..."
    su sh -c \
    tar -zxf $tarball -C /data/data/com.termux/files \
        --recursive-unlink --preserve-permissions
    msg "done restored $tarball."
}

func=
case "$1" in
    -\?|-h|--help|--usage)
        _say_what_i_do
        exit 0
        ;;
    "backup")
        msg "Backup termux configurations..."
        func=backup
        ;;
    "restore")
        msg "restore from a perviously backuped tar ball..."
        func=restore
        ;;
    *)
        _say_what_i_do
        exit 1
        ;;
esac

# confirm excute
read -re -p "Ready to excute? (y/n) " CHOICE
if ! [[ "${CHOICE}" =~ (Y|y) ]]; then
    msg "aborted!"
    exit 1
fi

$func
