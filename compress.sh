#!/bin/bash

if [ -z "$1" ] || [ ! -d "$1" ]; then
	echo "Usage: $0 <rundir(s)...>"
	exit 1
fi

for rundir in "$@"; do
	if [ ! -d "$rundir" ]; then
		echo "Not a directory: $rundir"
		continue
	fi
	run=$(basename $rundir)
	if ! [[ $run =~ ^[0-9]+$ ]]; then
		echo "Invalid run: $run"
		continue
	fi
	testdir=$(dirname $rundir)
	tarfilepath="$testdir/$run.tar.gz"
	echo "Compressing $rundir..."
	tar -czf "$tarfilepath" -C "$rundir" .
	success=$?
	if [ "$success" == "0" ]; then
		rm -r "$rundir"
	else
		rm "$tarfilepath"
	fi
done

