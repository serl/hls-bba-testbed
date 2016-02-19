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
	DELAYS="$4"
	BUFFER_SIZES="$5"
	AQMS="$6"
	ALGORITHMS="$7"
	MAX_TEST="$8"
	RUNS="$9"

	TMPFILE=$(mktemp)
	for group in $GROUP_S; do
		for clients in $CLIENTS; do
			for delay in $DELAYS; do
				for buffer_size in $BUFFER_SIZES; do
					for aqm in $AQMS; do
						net="${delay}_${buffer_size}_${aqm}"
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
		done
	done
	rm -f $TMPFILE
}

check "constant" "1" "bbb8" "20ms 80ms" "025%BDP 050%BDP 100%BDP 600%BDP" "ared codel droptail" "bba2_keepalive_est bba3_keepalive_est classic-119_keepalive classic-119_keepalive_est" 9 1
check "constant" "2" "bbb8" "20ms 80ms" "025%BDP 050%BDP 100%BDP 600%BDP" "codel droptail" "bba2_keepalive_est bba3_keepalive_est classic-119_keepalive_est" 9 1
check "constant" "3" "bbb8" "20ms 80ms" "025%BDP 050%BDP 100%BDP 600%BDP" "codel droptail" "bba2_keepalive_est bba3_keepalive_est classic-119_keepalive_est" 9 1

check "variable" "1" "bbb8" "20ms 80ms" "025%BDP 050%BDP 100%BDP 600%BDP" "ared codel droptail" "bba2_keepalive_est bba3_keepalive_est classic-119_keepalive classic-119_keepalive_est" 2 1
check "variable" "2" "bbb8" "20ms 80ms" "025%BDP 050%BDP 100%BDP 600%BDP" "codel droptail" "bba2_keepalive_est bba3_keepalive_est classic-119_keepalive_est" 2 1
check "variable" "3" "bbb8" "20ms 80ms" "025%BDP 050%BDP 100%BDP 600%BDP" "codel droptail" "bba2_keepalive_est bba3_keepalive_est classic-119_keepalive_est" 2 1
