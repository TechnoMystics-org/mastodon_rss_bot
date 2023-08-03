#!/bin/bash
if [ "$1" = "i" ];
then
	echo "Initializing"
	./rssbot.py --initialize
elif [ "$1" = "c" ];
then
	echo "Purging entries older than 15 days"
	while true
	do
		./rssbot.py --cleanup
		echo "Sleeping for 1 minute"
		sleep 1m
	done
else
	echo "Running every 1 minute"
	while true
	do
		./rssbot.py
		echo "Sleeping for 1 minute"
		sleep 1m
	done
fi

