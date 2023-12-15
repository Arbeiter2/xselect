#!/bin/sh

while :
do
    python reconfirm.py
    if [ $? -eq 0 ]
    then
        exit 0
    fi
    tput sgr0
    ORPHAN_PID=`pgrep -laP 1 | grep chrome | cut -f1 -d' '`
    if [ -z "${ORPHAN_PID}" ]
    then
        for pid in ${ORPHAN_PID}
        do
            pkill -P ${pid}
            kill ${pid}
        done
    fi
    sleep 65
done
