#!/bin/bash
trap "wait" TERM EXIT

# Big Buck Bunny - 200ms RTT, 200pkts buffer
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_classic_keepalive tests/constant_two_con_bbb8_200ms_200p/*_classic-13_keepalive &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_classic_keepalive_est tests/constant_two_con_bbb8_200ms_200p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_bba0_keepalive tests/constant_two_con_bbb8_200ms_200p/*_bba0_keepalive &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_bba1_keepalive_est tests/constant_two_con_bbb8_200ms_200p/*_bba1_keepalive_est &
# Big Buck Bunny - 100ms RTT, 200pkts buffer
nice python analyze_vlc_QoE_comp.py two_con_bbb_100ms_classic_keepalive tests/constant_two_con_bbb8_100ms_200p/*_classic-13_keepalive &
nice python analyze_vlc_QoE_comp.py two_con_bbb_100ms_classic_keepalive_est tests/constant_two_con_bbb8_100ms_200p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_100ms_bba0_keepalive_est tests/constant_two_con_bbb8_100ms_200p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_100ms_bba1_keepalive_est tests/constant_two_con_bbb8_100ms_200p/*_bba1_keepalive_est &
wait
# Big Buck Bunny - 400ms RTT, 200pkts buffer
nice python analyze_vlc_QoE_comp.py two_con_bbb_400ms_classic_keepalive tests/constant_two_con_bbb8_400ms_200p/*_classic-13_keepalive &
nice python analyze_vlc_QoE_comp.py two_con_bbb_400ms_classic_keepalive_est tests/constant_two_con_bbb8_400ms_200p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_400ms_bba0_keepalive_est tests/constant_two_con_bbb8_400ms_200p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_400ms_bba1_keepalive_est tests/constant_two_con_bbb8_400ms_200p/*_bba1_keepalive_est &

# Big Buck Bunny - 200ms RTT, 100%BDP buffer
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_100_classic_keepalive tests/constant_two_con_bbb8_200ms_100%p/*_classic-13_keepalive &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_100_classic_keepalive_est tests/constant_two_con_bbb8_200ms_100%p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_100_bba0_keepalive_est tests/constant_two_con_bbb8_200ms_100%p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_100_bba1_keepalive_est tests/constant_two_con_bbb8_200ms_100%p/*_bba1_keepalive_est &
wait
# Big Buck Bunny - 200ms RTT, 50%BDP buffer
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_50_classic_keepalive tests/constant_two_con_bbb8_200ms_50%p/*_classic-13_keepalive &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_50_classic_keepalive_est tests/constant_two_con_bbb8_200ms_50%p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_50_bba0_keepalive_est tests/constant_two_con_bbb8_200ms_50%p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_50_bba1_keepalive_est tests/constant_two_con_bbb8_200ms_50%p/*_bba1_keepalive_est &
# Big Buck Bunny - 200ms RTT, 25%BDP buffer
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_25_classic_keepalive tests/constant_two_con_bbb8_200ms_25%p/*_classic-13_keepalive &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_25_classic_keepalive_est tests/constant_two_con_bbb8_200ms_25%p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_25_bba0_keepalive_est tests/constant_two_con_bbb8_200ms_25%p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_25_bba1_keepalive_est tests/constant_two_con_bbb8_200ms_25%p/*_bba1_keepalive_est &
wait
# Big Buck Bunny - 200ms RTT, 10%BDP buffer
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_10_classic_keepalive tests/constant_two_con_bbb8_200ms_10%p/*_classic-13_keepalive &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_10_classic_keepalive_est tests/constant_two_con_bbb8_200ms_10%p/*_classic-13_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_10_bba0_keepalive_est tests/constant_two_con_bbb8_200ms_10%p/*_bba0_keepalive_est &
nice python analyze_vlc_QoE_comp.py two_con_bbb_200ms_10_bba1_keepalive_est tests/constant_two_con_bbb8_200ms_10%p/*_bba1_keepalive_est &

# BipBop
nice python analyze_vlc_QoE_comp.py two_con_bipbop_200ms_classic_keepalive tests/constant_two_con_bipbop_200ms_200p/*_classic-2_keepalive &
nice python analyze_vlc_QoE_comp.py two_con_bipbop_200ms_classic_keepalive_est tests/constant_two_con_bipbop_200ms_200p/*_classic-2_keepalive_est &
wait
nice python analyze_vlc_QoE_comp.py two_con_bipbop_200ms_bba0_keepalive tests/constant_two_con_bipbop_200ms_200p/*_bba0_keepalive &
nice python analyze_vlc_QoE_comp.py two_con_bipbop_200ms_bba1_keepalive tests/constant_two_con_bipbop_200ms_200p/*_bba1_keepalive_est &
wait

