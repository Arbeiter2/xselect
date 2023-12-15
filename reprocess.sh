#!/bin/sh

while :
do
    python linktree_reprocess.py
    if [ $? -eq 0 ]
    then
        exit 0
    fi
    ORPHAN_PID=`pgrep -laP 1 | egrep -e '(firefox|driver|chrome)' | cut -f1 -d' '`
    if [ -z "${ORPHAN_PID}" ]
    then
        pkill -P ${ORPHAN_PID}
    fi
done
