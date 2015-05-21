#!/bin/bash

# could be useful to add this to sudoers:
# (sudo visudo)
# yourusername ALL=(ALL) NOPASSWD: /sbin/tc *

SUDO='sudo -n'
DEV='eth1'
DEFAULT_BW=10Gbit

function setup {
  set_bw $DEFAULT_BW
}

function destroy {
  echo "Deleting root qdisc"
  $SUDO tc qdisc del dev $DEV root
}

function set_bw {
  packets=10
  if [ "$2" ]; then
    packets="$2"
  fi
  bw="$1"
  echo "Adding/replacing bw qdisc with rate $bw (buffer of $packets packets)"
  #$NETNS_EXEC $S_NS tc qdisc replace dev $S_IF root tbf rate $bw burst 2k latency 1ms
  #$NETNS_EXEC $S_NS tc qdisc replace dev $S_IF root tbf rate $bw burst 2k limit 100k
  $SUDO tc qdisc replace dev $DEV root netem rate "$bw" limit "$packets"
}

function show {
  $SUDO tc -s qdisc show dev $DEV
}

function watch_buffer_size {
  oldline=''
  while true; do
    line=$($SUDO tc -s qdisc show dev $DEV | grep backlog)
    if [ "$line" != "$oldline" ]; then
      echo $(date +%s.%N) $line
    fi
    sleep 0.001
    oldline=$line
  done
}

function usage {
  echo "Usage: $0 {setup|destroy|show|watch_buffer_size|set_bw [bw]}"
  exit 1
}

case "$1" in
  setup)
    setup
    ;;
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
  watch_buffer_size)
    watch_buffer_size
    ;;
  *)
    usage
esac

