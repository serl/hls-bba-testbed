#!/bin/bash

schedule="$(cat /dev/stdin)"

hosts=$(echo "$schedule" | grep --extended-regexp --only-matching "^[^#\\ ]+" | uniq)
hosts_count=$(echo $hosts | wc -w)
start_time=$(($hosts_count * 5 + $(date +%s)))

for host in $hosts; do
	echo "$schedule" | ssh -oStrictHostKeyChecking=no $host "/vagrant/code/scheduler.sh $start_time" &
done

