#!/bin/bash

if [ -d "$RUN_PATH" ]; then
	exit 0
fi

run=$(basename $RUN_PATH)
if [[ $run =~ \.tar\.gz$ ]]; then
	echo "Run without .tar.gz in $RUN_PATH!" >&2
	exit 1
fi
if ! [[ $run =~ ^[0-9]+$ ]]; then
	echo "Invalid run: $run"
	exit 0
fi

testdir=$(dirname $RUN_PATH)
tarfilepath="$testdir/$run.tar.gz"

if [ ! -f "$tarfilepath" ]; then
	echo "$tarfilepath not found. Unable to decompress." >&2
	exit 1
fi

echo "Decompressing $tarfilepath..."
mkdir -p "$RUN_PATH"
if tar -C "$RUN_PATH" -xzf "$tarfilepath" ; then
	rm "$tarfilepath"
else
	rm -r "$RUN_PATH"
	echo "Decompress error on $RUN_PATH" >&2
	exit 1
fi

exit 0
