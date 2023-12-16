#!/bin/sh

for pid in `pgrep -laP 1 | egrep  -e '(driver|chrome|firefox)' | cut -f1 -d' '`
do
    kill $pid
done
