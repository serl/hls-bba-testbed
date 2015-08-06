#!/bin/bash

if [ -z "$1" ]; then
	echo "Usage $0 <dir>"
	exit 1
fi

for f in $1/*; do
	[ -x "$f" ] && "$f"
done

