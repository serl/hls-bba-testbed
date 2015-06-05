#!/bin/bash

# could be useful to add this to sudoers:
# (sudo visudo)
# yourusername ALL=(ALL) NOPASSWD: /sbin/tc *

SUDO='sudo -n'
DEVS='eth2'

function run_command {
  command=$1
  shift
  arguments=$@
  for dev in $DEVS; do
  	$SUDO tc -s qdisc $command dev $dev $arguments
  done
}

function destroy {
  echo "Deleting root qdisc"
  run_command del root
}

function set_bw {
  packets=200
  if [ "$2" ]; then
    packets="$2"
  fi
  bw="$1"
  echo "Adding/replacing netem qdisc with rate $bw (buffer of $packets packets)"
  run_command replace root netem rate "$bw" limit "$packets"
}

function set_delay {
  delay="$1"
  echo "Adding/replacing netem qdisc with delay $delay"
  run_command replace root netem delay "$delay"
}

function show {
  run_command show
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
  echo "Usage: $0 {set_bw [bw]|set_delay [delay]|destroy|show|watch_buffer_size}"
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
      set_bw "$2" "$3"
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

