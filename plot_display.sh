#!/bin/bash

if [ -z "$1" -o ! -e "$1" ]; then
	echo "Usage: $0 <rundir|run.tar.gz>"
	exit 1
fi

python pylibs/plot_run.py "$1"
