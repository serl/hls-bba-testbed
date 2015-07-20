#!/bin/bash
trap "wait" TERM EXIT

nice python plot_vlc_scatters.py two_con_scatters_bipbop_classic.png tests/constant_two_con_bipbop_200ms_200p/*_classic &
nice python plot_vlc_scatters.py two_con_scatters_bipbop_bba0.png tests/constant_two_con_bipbop_200ms_200p/*_bba0 &
wait

nice python plot_vlc_scatters.py two_con_scatters_bbb_classic.png tests/constant_two_con_bbb_200ms_200p/*_classic &
nice python plot_vlc_scatters.py two_con_scatters_bbb_bba0.png tests/constant_two_con_bbb_200ms_200p/*_bba0 &
wait

