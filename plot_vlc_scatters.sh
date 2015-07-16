#!/bin/bash
trap "wait" TERM EXIT

nice python plot_vlc_scatters.py two_con_scatters_classic.png tests/constant_two_con_bipbop_200ms_200p/*_classic &
nice python plot_vlc_scatters.py two_con_scatters_classic-2.png tests/constant_two_con_bipbop_200ms_200p/*_classic-2 &
wait
nice python plot_vlc_scatters.py two_con_scatters_classic-2-8.png tests/constant_two_con_bipbop_200ms_200p/*_classic-2-8 &
nice python plot_vlc_scatters.py two_con_scatters_bba0.png tests/constant_two_con_bipbop_200ms_200p/*_bba0 &
wait

nice python plot_vlc_scatters.py two_range_con_scatters_classic-2.png tests/constant_range_two_con_bipbop_200ms_200p/*_classic-2 &
nice python plot_vlc_scatters.py two_range_con_scatters_classic-2-8.png tests/constant_range_two_con_bipbop_200ms_200p/*_classic-2-8 &
wait

