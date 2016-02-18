#!/bin/bash

if [ -z "$1" ]; then
	echo "Usage: $0 <rundir(s)...>"
	exit 1
fi

for rundir in "$@"; do
	if [ -d "$rundir" ]; then
		continue
	fi

	run=$(basename $rundir)
	if [[ $run =~ \.tar\.gz$ ]]; then
		echo "Run without .tar.gz in $rundir!" >&2
		exit 1
	fi
	if ! [[ $run =~ ^[0-9]+$ ]]; then
		echo "Invalid run: $run"
		continue
	fi

	testdir=$(dirname $rundir)
	tarfilepath="$testdir/$run.tar.gz"

	if [ ! -f "$tarfilepath" ]; then
		echo "$tarfilepath not found. Unable to decompress." >&2
		continue
	fi

	echo "Decompressing $tarfilepath..."
	mkdir -p "$rundir"
	if tar -C "$rundir" -xzf "$tarfilepath" ; then
		rm "$tarfilepath"
	else
		rm -r "$rundir"
		echo "Decompress error on $rundir" >&2
		continue
	fi
done
