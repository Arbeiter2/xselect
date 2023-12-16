#!/bin/sh

# while 
# do
#     rm -rf /var/lock/scrape_pid
#     echo $USER
#     nohup python user.py -u ${USER} -i /home/delano/of0.json 2>&1 > /home/delano/logs/twitter/${USER} &
#     echo $! > /var/lock/scrape_pid
#     tput sgr0
#     killall -q chrome chromedriver firefox geckodriver
#     sleep 65
# done

echo $@
while :
do
    python batch.py -v $1 -b $2
    if [ $? -eq 0 ]
    then
        exit 0
    fi
    tput sgr0
    ORPHAN_PID=`pgrep -laP 1 | egrep  -e '(driver|chrome|firefox)' | cut -f1 -d' '`
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
