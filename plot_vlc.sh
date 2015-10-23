#!/bin/bash

if [ "$1" == "force" ]; then
	force=1
	shift
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
	for run in $runs; do
		run=${run%/}
		run=${run%.tar.gz}
		rundir=${sessiondir}/${run}
		png_path=${sessiondir}_${run}.png
		if [ "$force" == "1" ] || [ ! -f "$png_path" ]; then
			echo $rundir
		fi
	done
done | nice parallel --gnu --eta -j10 python plot_vlc.py export
echo "$? jobs failed."

