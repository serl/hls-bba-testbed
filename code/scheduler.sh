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
	eval "$@"
}

while read -r line; do
	if [[ $line =~ $me[[:space:]]+([0-9]+)[[:space:]]+(.*) ]]; then
		delay=${BASH_REMATCH[1]}
		command=${BASH_REMATCH[2]}
		run_delayed $delay "$command" &
	fi
done < <(grep -E "^$me +[0-9]+" /dev/stdin)

