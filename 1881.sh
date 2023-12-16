#!/bin/bash 

ARCH=`uname -m`
if [ ${ARCH} == "armv7l" ]
then
    LOG_PATH=/mnt/chronos
else
    LOG_PATH=/home/delano
fi
RAW="/home/delano/tmp/bbn"
JSON="/home/delano/tmp/bbn.json"

while :
do
    #egrep -a -e "`date +%Y%m`.*__dump_linktree_url" ${LOG_PATH}/logs/batch_*.log | cut -f5- -d' ' | tr '[:upper:]' '[:lower:]' | tr -d '\r' | sort -u | egrep -e "\}" 2>&1 1> ${RAW}
    egrep -a -e "*20230[56].*__dump_linktree_url" ${LOG_PATH}/logs/batch_*.log | cut -f5- -d' ' | tr '[:upper:]' '[:lower:]' | tr -d '\r' | sort -u | egrep -e "\}" 2>&1 1> ${RAW}
    perl -0777 -e 'my $lines = <>; $lines =~ s/\n$//g; $lines =~ s/\n/,\n/g; print "[\n" . lc($lines) . "\n]";' < ${RAW} 1> ${JSON}
    python 1881.py ${JSON}
    sleep 1800
    if [ $? -ne 0 ]
    then
        break
    fi
done
