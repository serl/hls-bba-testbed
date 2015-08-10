#!/bin/bash
trap "wait" TERM EXIT

# Big Buck Bunny
nice python plot_vlc_scatters.py two_con_scatters_bbb_classic_keepalive.png tests/constant_two_con_bbb8_200ms_200p/*_classic-13_keepalive &
nice python plot_vlc_scatters.py two_con_scatters_bbb_classic_keepalive_est.png tests/constant_two_con_bbb8_200ms_200p/*_classic-13_keepalive_est &
nice python plot_vlc_scatters.py two_con_scatters_bbb_bba0_keepalive.png tests/constant_two_con_bbb8_200ms_200p/*_bba0_keepalive &
wait

# BipBop
nice python plot_vlc_scatters.py two_con_scatters_bipbop_classic_keepalive.png tests/constant_two_con_bipbop_200ms_200p/*_classic-2_keepalive &
nice python plot_vlc_scatters.py two_con_scatters_bipbop_bba0_keepalive.png tests/constant_two_con_bipbop_200ms_200p/*_bba0_keepalive &
wait

