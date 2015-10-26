#!/bin/bash

# could be useful to add this to sudoers:
# (sudo visudo)
# yourusername ALL=(ALL) NOPASSWD: /sbin/tc *

SUDO='sudo -n'
DEVS='eth2'

function get_bits {
	if [ -z "$1" ]; then
		>&2 echo "Missing value"
		exit 1
	fi
	if [[ $1 =~ ^[0-9]+$ ]]; then
		echo $1
		exit 0
	fi
	if [[ $1 =~ ^([0-9]+)kbit$ ]]; then
		naked_value=${BASH_REMATCH[1]}
		echo $((naked_value * 1000))
		exit 0
	fi
	if [[ $1 =~ ^([0-9]+)mbit$ ]]; then
		naked_value=${BASH_REMATCH[1]}
		echo $((naked_value * 1000000))
		exit 0
	fi
	>&2 echo "Invalid value: $1"
	exit 2
}
function get_ms {
	if [ -z "$1" ]; then
		>&2 echo "Missing value"
		exit 1
	fi
	if [[ $1 =~ ^([0-9]+)ms$ ]]; then
		echo ${BASH_REMATCH[1]}
		exit 0
	fi
	if [[ $1 =~ ^([0-9]+)s$ ]]; then
		naked_value=${BASH_REMATCH[1]}
		echo $((naked_value * 1000))
		exit 0
	fi
	>&2 echo "Invalid value: $1"
	exit 2
}

function check_success {
	exit_value=$?
	if [ $exit_value -gt 0 ]; then
		exit $exit_value
	fi
}

function run_command {
	type=$1
	shift
	command=$1
	shift
	arguments=$@
	for dev in $DEVS; do
		$SUDO tc -s $type $command dev $dev $arguments
	done
}

function destroy {
	run_command qdisc del root 2>&1 && \
	echo "Deleted root qdisc"
}

function set_bw {
	bw_bits=$(get_bits "$1")
	check_success

	buffer=200
	if [ "$2" ]; then
		buffer="$2"
	fi
	if [[ $buffer =~ ^([0-9]+)%$ ]]; then
		percentage=${BASH_REMATCH[1]}
		rtt="$3"
		mss=1500
		if [ -z $rtt ]; then
			echo "RTT needed to calculate percentage of BDP."
			exit 1
		fi
		rtt_ms=$(get_ms "$rtt")
		check_success
		buffer_echo=": $percentage% BDP"
		buffer=$((bw_bits * rtt_ms * percentage / 8 / mss / 100000))
		if [ "$buffer" -le "0" ]; then
			buffer=1
		fi
	fi

	run_command qdisc replace root netem rate "$bw_bits" limit "$buffer" 2>&1 && \
	echo "Added/replaced netem qdisc with rate ${bw_bits}bits/s (buffer of $buffer packets$buffer_echo)"
}

function set_bw_aqm {
	aqm=$1
	bw_bits=$(get_bits "$2")
	check_success
	mss=1500

	buffer="$3"
	if [[ $buffer =~ ^([0-9]+)%$ ]]; then
		percentage=${BASH_REMATCH[1]}
		rtt="$4"
		if [ -z $rtt ]; then
			echo "RTT needed to calculate percentage of BDP."
			exit 1
		fi
		rtt_ms=$(get_ms "$rtt")
		check_success
		buffer_echo=": $percentage% BDP"
		buffer=$((bw_bits * rtt_ms * percentage / 8 / mss / 100000))
		if [ "$buffer" -le "0" ]; then
			buffer=1
		fi
	fi

	("$0" show | grep htb >/dev/null || run_command qdisc replace root handle 1: htb default 1) && \
	run_command class replace parent 1: classid 1:1 htb rate "$bw_bits" && \
	echo "Added/replaced hbf qdisc with rate ${bw_bits}bits/s" || \
	return

	case "$aqm" in
		ared)
			buffer=$((buffer * mss))
			run_command qdisc replace parent 1:1 handle 20:0 red limit $buffer avpkt 1000 adaptive bandwidth "$bw_bits" && \
			echo "Added $aqm AQM to hbf qdisc (buffer of $buffer bytes)"
			;;
		codel)
			run_command qdisc replace parent 1:1 handle 20:0 codel limit $buffer noecn && \
			echo "Added $aqm AQM to hbf qdisc (buffer of $buffer packets)"
			;;
		*)
			echo "$aqm AQM not supported."
			;;
	esac
}

function set_delay {
	delay="$1"
	run_command qdisc replace root netem delay "$delay" 2>&1 && \
	echo "Added/replaced netem qdisc with delay $delay"
}

function show {
	run_command qdisc show
}

function watch_buffer_size {
	oldline=''
	while true; do
		line=$("$0" show | grep backlog)
		if [ -z "$line" ]; then
			continue
		fi
		if [ "$line" != "$oldline" ]; then
			echo $(date +%s.%N) $line
		fi
		sleep 0.001
		oldline=$line
	done
}

function usage {
	echo "Usage: $0 {set_bw <bw> [max_buffer_size] [rtt]|set_bw_aqm <algorithm> <bw> <max_buffer_size> [rtt]|set_delay <rtt>|destroy|show|watch_buffer_size}"
	exit 1
}

case "$1" in
	destroy)
		destroy
		;;
	show)
		show
		;;
	set_bw)
		if [ -z "$2" ]; then
			usage
		else
			set_bw "$2" "$3" "$4"
		fi
		;;
	set_bw_aqm)
		if [ -z "$2" ] || [ -z "$3" ]; then
			usage
		else
			shift
			set_bw_aqm "$@"
		fi
		;;
	set_delay)
		if [ -z "$2" ]; then
			usage
		else
			set_delay "$2"
		fi
		;;
	watch_buffer_size)
		watch_buffer_size
		;;
	*)
		usage
		exit
esac

