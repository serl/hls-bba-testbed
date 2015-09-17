#!/bin/bash
trap "wait" TERM EXIT

# Big Buck Bunny - 200ms RTT, 200pkts buffer
nice python analyze_vlc_QoE.py bbb_200ms_classic_keepalive tests/constant_single_bbb8_200ms_200p/*_classic-13_keepalive &
nice python analyze_vlc_QoE.py bbb_200ms_classic_keepalive_est tests/constant_single_bbb8_200ms_200p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py bbb_200ms_bba0_keepalive tests/constant_single_bbb8_200ms_200p/*_bba0_keepalive &
nice python analyze_vlc_QoE.py bbb_200ms_bba1_keepalive_est tests/constant_single_bbb8_200ms_200p/*_bba1_keepalive_est &
# Big Buck Bunny - 100ms RTT, 200pkts buffer
nice python analyze_vlc_QoE.py bbb_100ms_classic_keepalive tests/constant_single_bbb8_100ms_200p/*_classic-13_keepalive &
nice python analyze_vlc_QoE.py bbb_100ms_classic_keepalive_est tests/constant_single_bbb8_100ms_200p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py bbb_100ms_bba0_keepalive_est tests/constant_single_bbb8_100ms_200p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py bbb_100ms_bba1_keepalive_est tests/constant_single_bbb8_100ms_200p/*_bba1_keepalive_est &
wait
# Big Buck Bunny - 400ms RTT, 200pkts buffer
nice python analyze_vlc_QoE.py bbb_400ms_classic_keepalive tests/constant_single_bbb8_400ms_200p/c*_classic-13_keepalive &
nice python analyze_vlc_QoE.py bbb_400ms_classic_keepalive_est tests/constant_single_bbb8_400ms_200p/c*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py bbb_400ms_bba0_keepalive_est tests/constant_single_bbb8_400ms_200p/c*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py bbb_400ms_bba1_keepalive_est tests/constant_single_bbb8_400ms_200p/c*_bba1_keepalive_est &

# Big Buck Bunny - 200ms RTT, 100%BDP buffer
nice python analyze_vlc_QoE.py bbb_200ms_100_classic_keepalive tests/constant_single_bbb8_200ms_100%p/c*_classic-13_keepalive &
nice python analyze_vlc_QoE.py bbb_200ms_100_classic_keepalive_est tests/constant_single_bbb8_200ms_100%p/c*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py bbb_200ms_100_bba0_keepalive_est tests/constant_single_bbb8_200ms_100%p/c*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py bbb_200ms_100_bba1_keepalive_est tests/constant_single_bbb8_200ms_100%p/c*_bba1_keepalive_est &
wait
# Big Buck Bunny - 200ms RTT, 50%BDP buffer
nice python analyze_vlc_QoE.py bbb_200ms_50_classic_keepalive tests/constant_single_bbb8_200ms_50%p/c*_classic-13_keepalive &
nice python analyze_vlc_QoE.py bbb_200ms_50_classic_keepalive_est tests/constant_single_bbb8_200ms_50%p/c*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py bbb_200ms_50_bba0_keepalive_est tests/constant_single_bbb8_200ms_50%p/c*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py bbb_200ms_50_bba1_keepalive_est tests/constant_single_bbb8_200ms_50%p/c*_bba1_keepalive_est &
# Big Buck Bunny - 200ms RTT, 25%BDP buffer
nice python analyze_vlc_QoE.py bbb_200ms_25_classic_keepalive tests/constant_single_bbb8_200ms_25%p/c*_classic-13_keepalive &
nice python analyze_vlc_QoE.py bbb_200ms_25_classic_keepalive_est tests/constant_single_bbb8_200ms_25%p/c*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py bbb_200ms_25_bba0_keepalive_est tests/constant_single_bbb8_200ms_25%p/c*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py bbb_200ms_25_bba1_keepalive_est tests/constant_single_bbb8_200ms_25%p/c*_bba1_keepalive_est &
wait
# Big Buck Bunny - 200ms RTT, 10%BDP buffer
nice python analyze_vlc_QoE.py bbb_200ms_10_classic_keepalive tests/constant_single_bbb8_200ms_10%p/c*_classic-13_keepalive &
nice python analyze_vlc_QoE.py bbb_200ms_10_classic_keepalive_est tests/constant_single_bbb8_200ms_10%p/c*_classic-13_keepalive_est &
nice python analyze_vlc_QoE.py bbb_200ms_10_bba0_keepalive_est tests/constant_single_bbb8_200ms_10%p/c*_bba0_keepalive_est &
nice python analyze_vlc_QoE.py bbb_200ms_10_bba1_keepalive_est tests/constant_single_bbb8_200ms_10%p/c*_bba1_keepalive_est &

# BipBop
nice python analyze_vlc_QoE.py bipbop_200ms_classic_keepalive tests/constant_single_bipbop_200ms_200p/c*_classic-2_keepalive &
wait
nice python analyze_vlc_QoE.py bipbop_200ms_bba0_keepalive tests/constant_single_bipbop_200ms_200p/c*_bba0_keepalive &
nice python analyze_vlc_QoE.py bipbop_200ms_bba1_keepalive tests/constant_single_bipbop_200ms_200p/c*_bba1_keepalive_est &
wait

