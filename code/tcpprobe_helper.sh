#!/bin/bash

if [ -z "$1" ]; then
	echo "Usage: $0 <port>"
	exit 1
fi

sudo rmmod tcp_probe 2>/dev/null
sudo modprobe tcp_probe port=$1 full=1
sleep 1
echo "$(date +%s.%N) BOOT $(grep 'CONFIG_HZ=' /boot/config-$(uname -r))"
exec sudo cat /proc/net/tcpprobe

