#!/bin/bash

if [ "$1" == "force" ]; then
	force=1
	shift
fi

if [ -z "$1" -o ! -d "$1" ]; then
	echo "Usage: $0 <sessiondir> [sessiondir...]"
	exit 1
fi

shopt -s nullglob

sessiondirs="$@"

for sessiondir in $sessiondirs; do
	sessiondir=${sessiondir%/}
	if [ ! -d $sessiondir ]; then
		continue
	fi
	pushd $sessiondir >/dev/null || continue
	runs=$(echo */ *.tar.gz)
	popd >/dev/null
	if [ -z "$runs" ]; then
		continue
	fi
	for d in $runs; do
		run=${d%/}
		run=${run%.tar.gz}
		rundir=${sessiondir}/${d}
		png_path=${sessiondir}_${run}.png
		if [ "$force" == "1" ] || [ ! -f "$png_path" ]; then
			echo $rundir
		fi
	done
done | parallel --gnu --eta -j10 nice python pylibs/autoplot.py --silent --export=png
echo "$? jobs failed."

