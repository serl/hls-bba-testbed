#!/bin/bash

if [ ! -d "$RUN_PATH" ]; then
	echo "Not a directory: $RUN_PATH"
	exit 0
fi

run=$(basename $RUN_PATH)
if ! [[ $run =~ ^[0-9]+$ ]]; then
	echo "Invalid run: $run"
	exit 0
fi

testdir=$(dirname $RUN_PATH)
tarfilepath="$testdir/$run.tar.gz"
echo "Compressing $RUN_PATH..."
if tar -czf "$tarfilepath" -C "$RUN_PATH" . ; then
	rm -r "$RUN_PATH"
else
	rm "$tarfilepath"
	echo "Compress error on $RUN_PATH" >&2
fi

exit 0
