#!/bin/bash

source code/colors.sh

exitcode=0
for schedule_file in "$@"; do
	if [ -d $schedule_file ]; then
		schedule_file="$schedule_file/jobs.sched"
	fi
	echo -e "${IBlue}Running $schedule_file...${Color_Off}"
	vagrant ssh server --command '/vagrant/code/master_scheduler.sh' -- -T < $schedule_file
	exitcode=$?
	sleep 1
	echo
done
exit $exitcode

