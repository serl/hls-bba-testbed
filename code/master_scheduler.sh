#!/bin/bash

schedule="$(cat /dev/stdin)"
lockdir="/tmp/testrunning"

source $(dirname $0)/colors.sh

if ! mkdir "$lockdir" &>/dev/null; then
	echo -e "${Red}Another test is running... Abort!$Color_Off"
	exit 1
fi

hosts=$(echo "$schedule" | grep --extended-regexp --only-matching "^[^#\\ ]+" | sort | uniq)
hosts_count=$(echo $hosts | wc -w)
master_delay=$(($hosts_count * 2 + 2))
duration=$(echo "$schedule" | grep --invert-match '^#' | cut -f2 -d' ' | sort --numeric-sort | tail -n1)

echo -e "${IBlack}Clearing SSH keys...$Color_Off"
rm /home/vagrant/.ssh/known_hosts &>/dev/null

for host in $hosts; do
	echo -ne "${IBlack}Updating $host clock..."
	ssh -oLogLevel=quiet -oStrictHostKeyChecking=no $host "sudo ntpdate pool.ntp.org"
	echo -ne $Color_Off
done

start_time=$(($master_delay + $(date +%s)))
end=$(date --date=@$(($duration + $start_time)))
echo -e "${IBlue}Execution delayed by $master_delay seconds, expected end: $end$Color_Off"

for host in $hosts; do
	echo -e "${Green}Sending schedule to $host...$Color_Off"
	echo "$schedule" | ssh -oStrictHostKeyChecking=no $host "/vagrant/code/scheduler.sh $start_time" &
done

sleep $(($duration + $master_delay + 2))
rmdir "$lockdir" &>/dev/null || echo "${Red}Unclean exit!$Color_Off"

