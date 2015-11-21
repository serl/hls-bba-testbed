#!/bin/bash

if [ -z "$1" -o ! -e "$1" ]; then
	echo "Usage: $0 <rundir|run.tar.gz> [parameters to plot_run.py]"
	exit 1
fi
rundir="$1"
shift

python pylibs/plot_run.py --export=svg --output_dir="./" --size=7x3 --nodetails "$@" "$rundir"

