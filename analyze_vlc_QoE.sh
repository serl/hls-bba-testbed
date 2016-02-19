#!/bin/bash

if [ -z "$1" -o ! -d "$1" ]; then
	echo "Usage: $0 <testdir>"
	exit 1
fi

shopt -s nullglob
exists() {
	[ -e "$1" ] || [ -L "$1" ]
}

TESTDIR="$1"

RESULTSDIR="$TESTDIR/QoE_metrics"
mkdir -p "$RESULTSDIR"

# Big Buck Bunny, constant
for algo in classic-119_keepalive classic-119_keepalive_est bba2_keepalive_est bba3_keepalive_est; do
	for delay in 20ms 80ms; do
		for buffer in 600%BDP 100%BDP 050%BDP 025%BDP; do
			for num in 1 2 3; do
				for aqm in droptail ared codel; do
					outfile="$RESULTSDIR/${num}_bbb_${delay}_${buffer}_${algo}_${aqm}.csv"
					tests=$TESTDIR/constant_${num}_bbb8_${delay}_${buffer}_${aqm}/c*_$algo
					if [ ! -f "$outfile" ] && exists $tests; then
						echo python analyze_vlc_QoE.py $outfile $tests
					fi
				done
			done
		done
	done
done | parallel --gnu --eta -j10
echo -e "\n$? jobs failed."

python analyze_vlc_QoE_gentable.py $RESULTSDIR

RESULTSDIR="$TESTDIR/QoE_metrics_variable"
mkdir -p "$RESULTSDIR"

# Big Buck Bunny, variable
for algo in classic-119_keepalive classic-119_keepalive_est bba2_keepalive_est bba3_keepalive_est; do
	for delay in 20ms 80ms; do
		for buffer in 600%BDP 100%BDP 050%BDP 025%BDP; do
			for num in 1 2 3; do
				for aqm in droptail ared codel; do
					for testnum in 01 02; do
						outfile="$RESULTSDIR/v${testnum}_${num}_bbb_${delay}_${buffer}_${algo}_${aqm}.csv"
						tests=$TESTDIR/variable_${num}_bbb8_${delay}_${buffer}_${aqm}/v${testnum}_*_$algo
						if [ ! -f "$outfile" ] && exists $tests; then
							echo python analyze_vlc_QoE_variable.py $outfile $tests
						fi
					done
				done
			done
		done
	done
done | parallel --gnu --eta -j15
echo -e "\n$? jobs failed."

python analyze_vlc_QoE_gentable.py $RESULTSDIR v01_
python analyze_vlc_QoE_gentable.py $RESULTSDIR v02_
