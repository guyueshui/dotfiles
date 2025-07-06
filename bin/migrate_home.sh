#!/bin/bash

source "utils.sh"

sync_folder() {
    notify "sync... folder $1 to $2"
    # use ssh -q to suppress barrier of ssh
    # rsync -auhzP --size-only --exclude=".*" \
    rsync -auhzP --size-only \
	-e "ssh -q" \
        $1 $2
}


main() {
    cd $HOME
    for line in $(cat ~/folders.lst); do
        sync_folder "$line" 192.168.0.104:/home/yychi/
    done
}

migrate_l1_files() {
    cd $HOME
    for line in $(cat files.lst); do
        sync_folder "$line" 192.168.0.104:/home/yychi/
    done
}

main
