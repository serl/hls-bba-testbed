#!/bin/bash

# could be useful to add this to sudoers:
# (sudo visudo)
# yourusername ALL=(ALL) NOPASSWD: /sbin/tc *

SUDO='sudo -n'
DEV='eth1'

function destroy {
  echo "Deleting root qdisc"
  $SUDO tc qdisc del dev $DEV root
}

function set_bw {
  packets=200
  if [ "$2" ]; then
    packets="$2"
  fi
  delay=200ms
  if [ "$3" ]; then
    delay="$3"
  fi
  bw="$1"
  echo "Adding/replacing netem qdisc with rate $bw, delay $delay (buffer of $packets packets)"
  $SUDO tc qdisc replace dev $DEV root netem rate "$bw" limit "$packets" delay "$delay"
}

function set_delay {
  delay="$1"
  echo "Adding/replacing netem qdisc with delay $delay"
  $SUDO tc qdisc replace dev $DEV root netem delay "$delay"
}

function show {
  $SUDO tc -s qdisc show dev $DEV
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
esac

