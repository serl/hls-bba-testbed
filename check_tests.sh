#!/bin/bash

if [ -z "$1" -o ! -d "$1" ]; then
	echo "Usage: $0 <testdir>"
	exit 1
fi

TESTDIR="$1"

function check
{
	GROUP_S="$1" #constant variable
	CLIENTS="$2"
	VIDEO="$3"
	NETS="$4"
	ALGORITHMS="$5"
	MAX_TEST="$6"
	RUNS="$7"

	TMPFILE=$(mktemp)
	for group in $GROUP_S; do
		for clients in $CLIENTS; do
			for net in $NETS; do
				grouptestdir="$TESTDIR/${group}_${clients}_${VIDEO}_${net}"
				if [ ! -d "$grouptestdir" ]; then
					echo "$grouptestdir missing completely"
					continue
				fi

				for algorithm in $ALGORITHMS; do
					: >"$TMPFILE"
					for num in $(seq -f "%02g" 1 $MAX_TEST); do
						ptestdir=""
						if [ "$group" == "constant" ]; then
							ptestdir="${grouptestdir}/c${num}_${clients}_${VIDEO}_*_${algorithm}"
						elif [ "$group" == "variable" ]; then
							ptestdir="${grouptestdir}/v${num}_${clients}_${VIDEO}_${algorithm}"
						fi

						for run in $(seq 1 $RUNS); do
							rundir="$ptestdir/$run"
							runtarfile="$ptestdir/$run.tar.gz"
							if [ ! -d $rundir ] && [ ! -f $runtarfile ]; then
								echo "Missing $rundir" >>"$TMPFILE"
							fi
							if [ -d $rundir ]; then
								filesize=$(stat --printf="%s" $rundir/client0_vlc.log)
								if [ "$filesize" -lt 10000 ]; then
									echo $rundir corrupted
								fi
							fi
						done
					done
					missing=$(wc -l "$TMPFILE" | awk '{print $1}')
					if [ "$missing" -gt 0 ]; then
						if [ "$missing" -eq $((MAX_TEST * RUNS)) ]; then
							echo "Missing $algorithm in $grouptestdir"
						else
							echo "$(cat "$TMPFILE")"
						fi
					fi
				done
			done
		done
	done
	rm -f $TMPFILE
}

check "constant" "single" "bbb8" "100ms_200p 200ms_200p 400ms_200p 200ms_100%p 200ms_50%p 200ms_25%p 200ms_10%p" "bba0_keepalive_est bba1_keepalive_est bba2_keepalive_est bba3_keepalive_est bba3-a_keepalive_est classic-13_keepalive classic-13_keepalive_est classic-119_keepalive classic-119_keepalive_est" 27 2
check "constant" "two_con" "bbb8" "100ms_200p 200ms_200p 400ms_200p 200ms_100%p 200ms_50%p 200ms_25%p 200ms_10%p" "bba0_keepalive_est bba1_keepalive_est bba2_keepalive_est bba3_keepalive_est bba3-a_keepalive_est classic-13_keepalive classic-13_keepalive_est classic-119_keepalive classic-119_keepalive_est" 27 4
check "constant" "single" "bipbop" "200ms_200p" "bba0_keepalive_est bba1_keepalive_est bba2_keepalive_est bba3_keepalive_est bba3-a_keepalive_est classic-2_keepalive classic-2_keepalive_est classic-23_keepalive classic-23_keepalive_est" 20 2
check "constant" "two_con" "bipbop" "200ms_200p" "bba0_keepalive_est bba1_keepalive_est bba2_keepalive_est bba3_keepalive_est bba3-a_keepalive_est classic-2_keepalive classic-2_keepalive_est  classic-23_keepalive classic-23_keepalive_est" 20 4

check "variable" "single" "bbb8" "200ms_200p" "bba0_keepalive_est bba1_keepalive_est bba2_keepalive_est bba3_keepalive_est classic-13_keepalive classic-13_keepalive_est" 2 2
check "variable" "two_con" "bbb8" "200ms_200p" "bba0_keepalive_est bba1_keepalive_est bba2_keepalive_est bba3_keepalive_est classic-13_keepalive classic-13_keepalive_est" 2 4


