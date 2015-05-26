#!/bin/bash

me=$(hostname)
if [ "$2" ]; then
	me=$2
fi

start_time="$1"
now=$(date +%s)
if [ $start_time == 0 ]; then
	start_time=$now
fi

function run_delayed {
	delay=$(($1 + $start_time - $now))
	shift
	sleep $delay 2>/dev/null
	echo $(date +%s.%N) $me RUN $@
	eval "$@ &"
}

while read -r line; do
	if [[ $line =~ $me[[:space:]]+([0-9]+)[[:space:]]+(.*) ]]; then
		delay=${BASH_REMATCH[1]}
		command=${BASH_REMATCH[2]}
		run_delayed $delay "$command" &
	elif [[ $line =~ \#eval[[:space:]]+(.*) ]]; then
		command=${BASH_REMATCH[1]}
		eval $command
	fi
done < /dev/stdin

