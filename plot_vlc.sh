#!/bin/bash

if [ "$1" == "force" ]; then
	force=1
	shift
fi

sessiondirs="$@"

function scandirs {
	for sessiondir in $sessiondirs; do
		sessiondir=${sessiondir%/}
		if [ ! -d $sessiondir ]; then
			continue
		fi
		pushd $sessiondir >/dev/null || continue
		runs=$(echo */)
		popd >/dev/null
		for d in $runs; do
			run=${d%/}
			rundir=${sessiondir}/${run}
			png_path=${sessiondir}_${run}.png
			if [ "$force" == "1" ] || [ ! -f "$png_path" ]; then
				echo $rundir
			fi
		done
	done
}

scandirs | parallel --progress -j5 python plot_vlc.py export
echo "$? jobs failed."

