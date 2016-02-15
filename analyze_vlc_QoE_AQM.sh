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
RESULTSDIR="$TESTDIR/QoE_metrics_AQM"
mkdir -p "$RESULTSDIR"

# Big Buck Bunny
for algo in classic-13_keepalive classic-13_keepalive_est classic-119_keepalive classic-119_keepalive_est bba0_keepalive_est bba1_keepalive_est bba2_keepalive_est bba3_keepalive_est bba3-a_keepalive_est; do
	for delaybuffer in 100ms_200p 200ms_200p 400ms_200p 200ms_100%p 200ms_50%p 200ms_25%p 200ms_10%p; do
		for num in single two_con three_con; do
			for aqm in droptail ared codel; do
				outfile="$RESULTSDIR/${num}_bbb_${delaybuffer}_${algo}_${aqm}.csv"
				tests=$TESTDIR/constant_${num}_bbb8_${delaybuffer}
				if [ "$aqm" != "droptail" ]; then
					tests="${tests}_${aqm}/c01_*_$algo ${tests}_${aqm}/c02_*_$algo"
				else
					tests="${tests}/c17_*_$algo ${tests}/c27_*_$algo"
				fi
				if [ ! -f "$outfile" ] && exists $tests; then
					echo python analyze_vlc_QoE.py $outfile $tests
				fi
			done
		done
	done
done | parallel --gnu --eta -j24
echo -e "\n$? jobs failed."

# BipBop
for algo in classic-2_keepalive classic-2_keepalive_est classic-23_keepalive classic-23_keepalive_est bba0_keepalive_est bba1_keepalive_est bba2_keepalive_est bba3_keepalive_est bba3-a_keepalive_est; do
	for num in single two_con; do
		for aqm in droptail ared codel; do
			outfile="$RESULTSDIR/${num}_bipbop_200ms_200p_${algo}_${aqm}.csv"
			tests=$TESTDIR/constant_${num}_bipbop_200ms_200p
			if [ "$aqm" != "droptail" ]; then
				tests="${tests}_${aqm}/c01_*_$algo"
			else
				tests="${tests}/c20_*_$algo"
			fi
			if [ ! -f "$outfile" ] && exists $tests; then
				echo python analyze_vlc_QoE.py $outfile $tests
			fi
		done
	done
done | parallel --gnu --eta -j16
echo -e "\n$? jobs failed."

single_files="$RESULTSDIR/single_bipbop_200ms_200p_* $RESULTSDIR/single_bbb_100ms_200p_* $RESULTSDIR/single_bbb_200ms_200p_* $RESULTSDIR/single_bbb_400ms_200p_* $RESULTSDIR/single_bbb_200ms_100%p_* $RESULTSDIR/single_bbb_200ms_50%p_* $RESULTSDIR/single_bbb_200ms_25%p_* $RESULTSDIR/single_bbb_200ms_10%p_*"
if exists $single_files; then
	echo "label,rebuffering_ratio,,avg_bitrate,,avg_relative_bitrate,,avg_quality_level,,instability,,link_utilization,,avg_router_queue_len,,avg_relative_router_queue_len,,avg_relative_rtt" > $RESULTSDIR/single_all.csv
	for f in $single_files; do
		tail -n1 $f >> $RESULTSDIR/single_all.csv
	done
	sed -i '/^$/d' $RESULTSDIR/single_all.csv
fi

two_con_files="$RESULTSDIR/two_con_bipbop_200ms_200p_* $RESULTSDIR/two_con_bbb_100ms_200p_* $RESULTSDIR/two_con_bbb_200ms_200p_* $RESULTSDIR/two_con_bbb_400ms_200p_* $RESULTSDIR/two_con_bbb_200ms_100%p_* $RESULTSDIR/two_con_bbb_200ms_50%p_* $RESULTSDIR/two_con_bbb_200ms_25%p_* $RESULTSDIR/two_con_bbb_200ms_10%p_*"
if exists $two_con_files; then
	echo "label,rebuffering_ratio,,avg_bitrate,,avg_relative_bitrate,,avg_quality_level,,instability,,link_utilization,,avg_router_queue_len,,avg_relative_router_queue_len,,avg_relative_rtt,,general_unfairness,,general_relative_unfairness,,quality_unfairness" > $RESULTSDIR/two_con_all.csv
	for f in $two_con_files; do
		tail -n1 $f >> $RESULTSDIR/two_con_all.csv
	done
	sed -i '/^$/d' $RESULTSDIR/two_con_all.csv
fi

three_con_files="$RESULTSDIR/three_con_bbb_200ms_100%p_*"
if exists $three_con_files; then
	echo "label,rebuffering_ratio,,avg_bitrate,,avg_relative_bitrate,,avg_quality_level,,instability,,link_utilization,,avg_router_queue_len,,avg_relative_router_queue_len,,avg_relative_rtt,,general_unfairness,,general_relative_unfairness,,quality_unfairness" > $RESULTSDIR/three_con_all.csv
	for f in $three_con_files; do
		tail -n1 $f >> $RESULTSDIR/three_con_all.csv
	done
	sed -i '/^$/d' $RESULTSDIR/three_con_all.csv
fi

