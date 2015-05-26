#!/bin/bash

schedule="$(cat /dev/stdin)"

hosts=$(echo "$schedule" | grep --extended-regexp --only-matching "^[^#\\ ]+" | sort | uniq)
hosts_count=$(echo $hosts | wc -w)
master_delay=$(($hosts_count * 2 + 2))
start_time=$(($master_delay + $(date +%s)))
echo "Execution delayed by $master_delay seconds"

for host in $hosts; do
	echo "Sending schedule to $host..."
	echo "$schedule" | ssh -oStrictHostKeyChecking=no $host "/vagrant/code/scheduler.sh $start_time" &
done

