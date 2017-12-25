#!/bin/sh
while true
do
    /usr/bin/python /home/huy/syncDatabase/syncDatabase.py 
    /usr/bin/python /home/huy/syncDatabase/syncJobparam.py
    sleep 1s
done
