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
mkdir -p "$TESTDIR/QoE_metrics/"

# Big Buck Bunny
for algo in classic-13_keepalive classic-13_keepalive_est classic-119_keepalive classic-119_keepalive_est bba0_keepalive_est bba1_keepalive_est bba2_keepalive_est bba3_keepalive_est bba3-a_keepalive_est; do
	for delaybuffer in 100ms_200p 200ms_200p 400ms_200p 200ms_100%p 200ms_50%p 200ms_25%p 200ms_10%p; do
		for num in single two_con; do
			outfile="$TESTDIR/QoE_metrics/${num}_bbb_${delaybuffer}_$algo"
			tests=$TESTDIR/constant_${num}_bbb8_${delaybuffer}/c*_$algo
			if [ ! -f "$outfile" ] && exists $tests; then
				echo python analyze_vlc_QoE.py $outfile $tests
			fi
		done
	done
done | parallel --gnu --eta -j5
echo
echo "$? jobs failed."


# BipBop
for algo in classic-2_keepalive classic-2_keepalive_est classic-23_keepalive classic-23_keepalive_est bba0_keepalive_est bba1_keepalive_est bba2_keepalive_est bba3_keepalive_est bba3-a_keepalive_est; do
	for num in single two_con; do
		outfile="$TESTDIR/QoE_metrics/${num}_bipbop_200ms_200p_$algo"
		tests=$TESTDIR/constant_${num}_bipbop_200ms_200p/c*_$algo
		if [ ! -f "$outfile" ] && exists $tests; then
			echo python analyze_vlc_QoE.py $outfile $tests
		fi
	done
done | parallel --gnu --eta -j1
echo
echo "$? jobs failed."


single_files="$TESTDIR/QoE_metrics/single_bipbop_200ms_200p_* $TESTDIR/QoE_metrics/single_bbb_100ms_200p_* $TESTDIR/QoE_metrics/single_bbb_200ms_200p_* $TESTDIR/QoE_metrics/single_bbb_400ms_200p_* $TESTDIR/QoE_metrics/single_bbb_200ms_100%p_* $TESTDIR/QoE_metrics/single_bbb_200ms_50%p_* $TESTDIR/QoE_metrics/single_bbb_200ms_25%p_* $TESTDIR/QoE_metrics/single_bbb_200ms_10%p_*"
if exists $single_files; then
	echo "label,rebuffering_ratio,,avg_bitrate,,avg_relative_bitrate,,avg_quality_level,,instability,,link_utilization,,avg_router_queue_len,,avg_relative_router_queue_len,,avg_relative_rtt" > $TESTDIR/QoE_metrics/single_all
	cat $single_files >> $TESTDIR/QoE_metrics/single_all
	sed -i '/^$/d' $TESTDIR/QoE_metrics/single_all
fi

two_con_files="$TESTDIR/QoE_metrics/two_con_bipbop_200ms_200p_* $TESTDIR/QoE_metrics/two_con_bbb_100ms_200p_* $TESTDIR/QoE_metrics/two_con_bbb_200ms_200p_* $TESTDIR/QoE_metrics/two_con_bbb_400ms_200p_* $TESTDIR/QoE_metrics/two_con_bbb_200ms_100%p_* $TESTDIR/QoE_metrics/two_con_bbb_200ms_50%p_* $TESTDIR/QoE_metrics/two_con_bbb_200ms_25%p_* $TESTDIR/QoE_metrics/two_con_bbb_200ms_10%p_*"
if exists $two_con_files; then
	echo "label,rebuffering_ratio,,avg_bitrate,,avg_relative_bitrate,,avg_quality_level,,instability,,link_utilization,,avg_router_queue_len,,avg_relative_router_queue_len,,avg_relative_rtt,,general_unfairness,,quality_unfairness" > $TESTDIR/QoE_metrics/two_con_all
	cat $two_con_files >> $TESTDIR/QoE_metrics/two_con_all
	sed -i '/^$/d' $TESTDIR/QoE_metrics/two_con_all
fi

