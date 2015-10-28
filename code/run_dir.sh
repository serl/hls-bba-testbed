#!/bin/bash

if [ -z "$1" ]; then
	echo "Usage $0 <dir>"
	exit 1
fi

for f in $1/*; do
	if ! ([ -x "$f" ] && "$f"); then
		echo "Error executing $f, aborting." >&2
		exit 1
	fi
done
