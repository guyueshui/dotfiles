#!/bin/bash

_usage() {
    cat << COMMENT
This script is used for a crontab scheduling. You should use the rsync_phone.sh
at most time.
COMMENT
}

start_frp() {
    local logfile=$HOME/frpc.log
    echo "starting frp tunnel..."
    frpc -c $HOME/bin/frp_0.61.0_linux_amd64/frpc_visitor.toml \
        >> $logfile 2>&1 &
    my_frp_pid=$!
    echo "my frp pid is $my_frp_pid"
}

start_frp_tunnel() {
    pgrep -x frpc || {
        start_frp
        sleep 3
    }
    for i in $(seq 3); do
        if ssh -q dell-inspiron-frp exit; then
            echo "$FUNCNAME return 0"
            return 0
        else
            echo "wait 2s, seq=$i"
            sleep 2
        fi
    done
    echo "$FUNCNAME return 1"
    return 1
}

backup() {
    local logfile=$HOME/rsync_phone_backup.log
    cat >> $logfile << _HEADER
========================================
auto start backup at $(date +'%F %T')
========================================
_HEADER
    # answer 'y' to the prompt question
    bash $HOME/bin/rsync_phone.sh backup >> $logfile 2>&1 << EOF
y
EOF
}

ret=1
if start_frp_tunnel; then
    backup
    ret=0
fi
[ -n "${my_frp_pid}" ] && kill $my_frp_pid
exit $ret
