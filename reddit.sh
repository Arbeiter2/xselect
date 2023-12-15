#!/bin/bash 

while :
do
    python reddit.py
    if [ $? -ne 0 ]
    then
        break
    fi
    sleep 10
done
