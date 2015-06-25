#!/bin/bash

source $(dirname $0)/colors.sh

start_time="$1"
now=$(date +%s)
if [ $start_time == 0 ]; then
	start_time=$now
fi

LOGDIR="$2"

me=$(hostname)
if [ "$3" ]; then
	me=$3
fi

function run_delayed {
	delay=$(($1 + $start_time - $now))
	shift
	sleep $delay 2>/dev/null
	echo -e "${IBlack}$(date +%s.%N) $me RUN $@${Color_Off}"
	eval "$@ &"
}

while read -r line; do
	if [[ $line =~ ^$me[[:space:]]+([0-9]+)[[:space:]]+(.*)$ ]]; then
		if [ -z "$LOGDIR" ]; then
			echo "Missing LOGDIR (usage $0 start_time log_dir [hostname] or hardcode it into .sched file)"
			exit 1
		fi
		mkdir -p "$LOGDIR"
		delay=${BASH_REMATCH[1]}
		command=${BASH_REMATCH[2]}
		run_delayed $delay "$command" &
	elif [[ $line =~ ^\#eval[[:space:]]+(.*) ]]; then
		command=${BASH_REMATCH[1]}
		eval $command
	fi
done < /dev/stdin

