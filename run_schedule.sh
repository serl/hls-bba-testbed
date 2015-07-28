#!/bin/bash

pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null

source "$SCRIPTPATH/code/colors.sh"

repeat=1
dry_run="false"
if [[ $1 =~ ^-?[0-9]+$ ]]; then
	if [ $1 -lt 0 ]; then
		repeat=$((-$1))
		dry_run="true"
	else
		repeat=$1
	fi
	shift
fi

if [ "$dry_run" == "false" ]; then
	vagrant up
fi

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
		mkdir -p "$log_dir"

		if [ "$dry_run" == "false" ]; then
			echo -e "${IBlue}Running $schedule_file (run index: $run_index)...${Color_Off}"
			vagrant ssh server --command "/vagrant/code/master_scheduler.sh /vagrant/$log_dir" -- -T < $schedule_file
			sleep 1
			echo
		else
			echo -e "${IBlue}Dry run of $schedule_file (run index: $run_index).${Color_Off}"
		fi
		let repetition+=1
	done
done

mailaddress="$(cat "$SCRIPTPATH/.mail" 2>/dev/null)"
if [ "$mailaddress" ]; then
	echo "" | mail -s "Tests ran on $SCRIPTPATH" "$mailaddress"
fi

if [ "$dry_run" == "false" ]; then
	vagrant halt
fi

