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
  echo "Deleting root qdisc"
  run_command qdisc del root
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
  fi

  echo "Adding/replacing netem qdisc with rate ${bw_bits}bits/s (buffer of $buffer packets$buffer_echo)"
  run_command qdisc replace root netem rate "$bw_bits" limit "$buffer"
}

function set_delay {
  delay="$1"
  echo "Adding/replacing netem qdisc with delay $delay"
  run_command qdisc replace root netem delay "$delay"
}

function show {
  run_command qdisc show
}

function watch_buffer_size {
  oldline=''
  while true; do
    line=$("$0" show | grep backlog)
    if [ "$line" != "$oldline" ]; then
      echo $(date +%s.%N) $line
    fi
    sleep 0.001
    oldline=$line
  done
}

function usage {
  echo "Usage: $0 {set_bw <bw> [buffer] [rtt]|set_delay <delay>|destroy|show|watch_buffer_size}"
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

