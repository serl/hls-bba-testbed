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
mkdir -p "$TESTDIR/QoE_metrics_variable/"

# Big Buck Bunny
for algo in classic-13_keepalive classic-13_keepalive_est classic-119_keepalive classic-119_keepalive_est bba0_keepalive_est bba1_keepalive_est bba2_keepalive_est bba3_keepalive_est bba3-a_keepalive_est; do
	delaybuffer="200ms_200p"
	for num in single two_con; do
		for testnum in 01 02; do
			outfile="$TESTDIR/QoE_metrics_variable/v${testnum}_${num}_bbb_${delaybuffer}_${algo}.csv"
			tests=$TESTDIR/variable_${num}_bbb8_${delaybuffer}/v${testnum}_*_$algo
			if [ ! -f "$outfile" ] && exists $tests; then
				echo python analyze_vlc_QoE_variable.py $outfile $tests
			fi
		done
	done
done | parallel --gnu --eta -j16
echo
echo "$? jobs failed."

single_files="$TESTDIR/QoE_metrics_variable/v01_single_bbb_200ms_200p_* $TESTDIR/QoE_metrics_variable/v02_single_bbb_200ms_200p_*"
if exists $single_files; then
	echo "label,rebuffering_ratio,,avg_bitrate,,avg_quality_level,,instability,,avg_router_queue_len,,avg_relative_router_queue_len,,avg_relative_rtt" > $TESTDIR/QoE_metrics_variable/single_all.csv
	for f in $single_files; do
		tail -n1 $f >> $TESTDIR/QoE_metrics_variable/single_all.csv
	done
	sed -i '/^$/d' $TESTDIR/QoE_metrics_variable/single_all.csv
fi

two_con_files="$TESTDIR/QoE_metrics_variable/v01_two_con_bbb_200ms_200p_* $TESTDIR/QoE_metrics_variable/v02_two_con_bbb_200ms_200p_*"
if exists $two_con_files; then
	echo "label,rebuffering_ratio,,avg_bitrate,,avg_quality_level,,instability,,avg_router_queue_len,,avg_relative_router_queue_len,,avg_relative_rtt,,general_unfairness,,quality_unfairness" > $TESTDIR/QoE_metrics_variable/two_con_all.csv
	for f in $two_con_files; do
		tail -n1 $f >> $TESTDIR/QoE_metrics_variable/two_con_all.csv
	done
	sed -i '/^$/d' $TESTDIR/QoE_metrics_variable/two_con_all.csv
fi

