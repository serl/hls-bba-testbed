#!/bin/bash

if [ -z "$1" -o ! -d "$1" ]; then
	echo "Usage: $0 <testdir>"
	exit 1
fi

TESTDIR="$1"

trap "wait" TERM EXIT

# Big Buck Bunny - 200ms RTT, 200pkts buffer
nice python analyze_vlc_QoE.py two_con_bbb_200ms_200p_classic_keepalive $TESTDIR/constant_two_con_bbb8_200ms_200p/*_classic-13_keepalive &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_200p_classic_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_200p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_200p_bba0_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_200p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_200p_bba1_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_200p/*_bba1_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_200p_bba2_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_200p/*_bba2_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_200p_bba3_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_200p/*_bba3_keepalive_est &
wait
# Big Buck Bunny - 100ms RTT, 200pkts buffer
nice python analyze_vlc_QoE.py two_con_bbb_100ms_200p_classic_keepalive $TESTDIR/constant_two_con_bbb8_100ms_200p/*_classic-13_keepalive &
nice python analyze_vlc_QoE.py two_con_bbb_100ms_200p_classic_keepalive_est $TESTDIR/constant_two_con_bbb8_100ms_200p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_100ms_200p_bba0_keepalive_est $TESTDIR/constant_two_con_bbb8_100ms_200p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_100ms_200p_bba1_keepalive_est $TESTDIR/constant_two_con_bbb8_100ms_200p/*_bba1_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_100ms_200p_bba2_keepalive_est $TESTDIR/constant_two_con_bbb8_100ms_200p/*_bba2_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_100ms_200p_bba3_keepalive_est $TESTDIR/constant_two_con_bbb8_100ms_200p/*_bba3_keepalive_est &
wait
# Big Buck Bunny - 400ms RTT, 200pkts buffer
nice python analyze_vlc_QoE.py two_con_bbb_400ms_200p_classic_keepalive $TESTDIR/constant_two_con_bbb8_400ms_200p/*_classic-13_keepalive &
nice python analyze_vlc_QoE.py two_con_bbb_400ms_200p_classic_keepalive_est $TESTDIR/constant_two_con_bbb8_400ms_200p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_400ms_200p_bba0_keepalive_est $TESTDIR/constant_two_con_bbb8_400ms_200p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_400ms_200p_bba1_keepalive_est $TESTDIR/constant_two_con_bbb8_400ms_200p/*_bba1_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_400ms_200p_bba2_keepalive_est $TESTDIR/constant_two_con_bbb8_400ms_200p/*_bba2_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_400ms_200p_bba3_keepalive_est $TESTDIR/constant_two_con_bbb8_400ms_200p/*_bba3_keepalive_est &
wait
# Big Buck Bunny - 200ms RTT, 100%BDP buffer
nice python analyze_vlc_QoE.py two_con_bbb_200ms_100%_classic_keepalive $TESTDIR/constant_two_con_bbb8_200ms_100%p/*_classic-13_keepalive &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_100%_classic_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_100%p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_100%_bba0_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_100%p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_100%_bba1_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_100%p/*_bba1_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_100%_bba2_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_100%p/*_bba2_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_100%_bba3_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_100%p/*_bba3_keepalive_est &
wait
# Big Buck Bunny - 200ms RTT, 50%BDP buffer
nice python analyze_vlc_QoE.py two_con_bbb_200ms_50%_classic_keepalive $TESTDIR/constant_two_con_bbb8_200ms_50%p/*_classic-13_keepalive &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_50%_classic_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_50%p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_50%_bba0_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_50%p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_50%_bba1_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_50%p/*_bba1_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_50%_bba2_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_50%p/*_bba2_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_50%_bba3_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_50%p/*_bba3_keepalive_est &
wait
# Big Buck Bunny - 200ms RTT, 25%BDP buffer
nice python analyze_vlc_QoE.py two_con_bbb_200ms_25%_classic_keepalive $TESTDIR/constant_two_con_bbb8_200ms_25%p/*_classic-13_keepalive &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_25%_classic_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_25%p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_25%_bba0_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_25%p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_25%_bba1_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_25%p/*_bba1_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_25%_bba2_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_25%p/*_bba2_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_25%_bba3_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_25%p/*_bba3_keepalive_est &
wait
# Big Buck Bunny - 200ms RTT, 10%BDP buffer
nice python analyze_vlc_QoE.py two_con_bbb_200ms_10%_classic_keepalive $TESTDIR/constant_two_con_bbb8_200ms_10%p/*_classic-13_keepalive &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_10%_classic_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_10%p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_10%_bba0_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_10%p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_10%_bba1_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_10%p/*_bba1_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_10%_bba2_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_10%p/*_bba2_keepalive_est &
nice python analyze_vlc_QoE.py two_con_bbb_200ms_10%_bba3_keepalive_est $TESTDIR/constant_two_con_bbb8_200ms_10%p/*_bba3_keepalive_est &
wait

# BipBop
nice python analyze_vlc_QoE.py two_con_bipbop_200ms_200p_classic_keepalive $TESTDIR/constant_two_con_bipbop_200ms_200p/*_classic-2_keepalive
nice python analyze_vlc_QoE.py two_con_bipbop_200ms_200p_classic_keepalive_est $TESTDIR/constant_two_con_bipbop_200ms_200p/*_classic-2_keepalive_est
nice python analyze_vlc_QoE.py two_con_bipbop_200ms_200p_bba0_keepalive_est $TESTDIR/constant_two_con_bipbop_200ms_200p/*_bba0_keepalive_est
nice python analyze_vlc_QoE.py two_con_bipbop_200ms_200p_bba1_keepalive_est $TESTDIR/constant_two_con_bipbop_200ms_200p/*_bba1_keepalive_est
nice python analyze_vlc_QoE.py two_con_bipbop_200ms_200p_bba2_keepalive_est $TESTDIR/constant_two_con_bipbop_200ms_200p/*_bba2_keepalive_est
nice python analyze_vlc_QoE.py two_con_bipbop_200ms_200p_bba3_keepalive_est $TESTDIR/constant_two_con_bipbop_200ms_200p/*_bba3_keepalive_est

echo "label,rebuffering_ratio,,avg_bitrate,,avg_relative_bitrate,,avg_quality_level,,instability,,link_utilization,,avg_router_queue_len,,general_unfairness,,quality_unfairness" > $TESTDIR/QoE_metrics/two_con_all
cat $TESTDIR/QoE_metrics/two_con_bipbop_200ms_200p_* $TESTDIR/QoE_metrics/two_con_bbb_100ms_200p_* $TESTDIR/QoE_metrics/two_con_bbb_200ms_200p_* $TESTDIR/QoE_metrics/two_con_bbb_400ms_200p_* $TESTDIR/QoE_metrics/two_con_bbb_200ms_100%_* $TESTDIR/QoE_metrics/two_con_bbb_200ms_50%_* $TESTDIR/QoE_metrics/two_con_bbb_200ms_25%_* $TESTDIR/QoE_metrics/two_con_bbb_200ms_10%_* >> $TESTDIR/QoE_metrics/two_con_all
sed -i '/^$/d' $TESTDIR/QoE_metrics/two_con_all

