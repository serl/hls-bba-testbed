#!/bin/bash

source code/colors.sh

for schedule_file in "$@"; do
	if [ -d $schedule_file ]; then
		schedule_file="$schedule_file/jobs.sched"
	fi
	echo -e "${IBlue}Running $schedule_file...${Color_Off}"
	vagrant ssh server --command '/vagrant/code/master_scheduler.sh' < $schedule_file
	sleep 1
	echo
done

