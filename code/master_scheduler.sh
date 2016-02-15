#!/bin/bash

schedule="$(cat /dev/stdin)"
logdir="$1"
lockdir="/tmp/testrunning"

source $(dirname $0)/colors.sh
ssh="ssh -oLogLevel=quiet -oStrictHostKeyChecking=no"

if ! mkdir "$lockdir" &>/dev/null; then
	echo -e "${Red}Another test is running... Abort!$Color_Off"
	exit 1
fi

hosts=$(echo "$schedule" | grep --extended-regexp --only-matching "^[^#\\ ]+" | sort -u)
hosts_count=$(echo $hosts | wc -w)
master_delay=$(($hosts_count + 2))
duration=$(echo "$schedule" | grep --invert-match '^#' | cut -f2 -d' ' | sort --numeric-sort | tail -n1)

for host in $hosts; do
	echo -ne "${IBlack}Updating $host clock..."
	$ssh $host "sudo ntpdate pool.ntp.org"
	echo -ne $Color_Off
done

start_time=$(($master_delay + $(date +%s)))
end=$(date --date=@$(($duration + $start_time)))
echo -e "${IBlue}Execution delayed by $master_delay seconds, expected end: $end$Color_Off"

for host in $hosts; do
	echo -e "${Green}Sending schedule to $host...$Color_Off"
	echo "$schedule" | $ssh $host "/vagrant/code/scheduler.sh $start_time $logdir" &
done

wait
/vagrant/code/post_run.sh "$logdir"
rmdir "$lockdir" &>/dev/null || echo -e "${Red}Unclean exit!$Color_Off"
