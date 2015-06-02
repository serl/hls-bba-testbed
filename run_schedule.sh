#!/bin/bash

for schedule_file in "$@"; do
	if [ -d $schedule_file ]; then
		schedule_file="$schedule_file/jobs.sched"
	fi
	vagrant ssh server --command '/vagrant/code/master_scheduler.sh' < $schedule_file
	sleep 2
done

