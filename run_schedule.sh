#!/bin/bash

source code/colors.sh

repeat=1
if [[ $1 =~ ^[0-9]+$ ]]; then
	repeat=$1
	shift
fi

vagrant up

for schedule_file in "$@"; do
	if [ -d $schedule_file ]; then
		schedule_file="$schedule_file/jobs.sched"
	fi
	if [ ! -e $schedule_file ]; then
		echo -e "${IRed}File $schedule_file does not exist${Color_Off}"
		continue
	fi
	repetition=0
	schedule_dir="$(dirname "$schedule_file")"

	while [ $repetition -lt $repeat ]; do
		run_index=1
		log_dir="$schedule_dir/$run_index"
		while [ -d $log_dir ]; do
			let run_index+=1
			log_dir="$schedule_dir/$run_index"
		done

		echo -e "${IBlue}Running $schedule_file (run index: $run_index)...${Color_Off}"
		vagrant ssh server --command "/vagrant/code/master_scheduler.sh /vagrant/$log_dir" -- -T < $schedule_file
		sleep 1
		echo
		let repetition+=1
	done
done

vagrant suspend

