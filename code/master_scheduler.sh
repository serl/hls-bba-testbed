#!/bin/bash

schedule="$(cat /dev/stdin)"

source $(dirname $0)/colors.sh

hosts=$(echo "$schedule" | grep --extended-regexp --only-matching "^[^#\\ ]+" | sort | uniq)
hosts_count=$(echo $hosts | wc -w)
master_delay=$(($hosts_count * 2 + 2))
duration=$(echo "$schedule" | grep --invert-match '^#' | cut -f2 -d' ' | sort --numeric-sort | tail -n1)

for host in $hosts; do
	echo -ne "${IBlack}Updating $host clock..."
	ssh -oStrictHostKeyChecking=no $host "sudo ntpdate pool.ntp.org"
	echo -ne $Color_Off
done

start_time=$(($master_delay + $(date +%s)))
end=$(date --date=@$(($duration + $start_time)))
echo -e "${IBlue}Execution delayed by $master_delay seconds, expected end: $end$Color_Off"

for host in $hosts; do
	echo -e "${Green}Sending schedule to $host...$Color_Off"
	echo "$schedule" | ssh -oStrictHostKeyChecking=no $host "/vagrant/code/scheduler.sh $start_time" &
done

