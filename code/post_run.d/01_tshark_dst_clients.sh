#!/bin/bash

for pcap in $RUN_PATH/*.pcap; do
	[ -e "$pcap" ] || break
	if [ -e "$pcap.toclients" ]; then
		echo "Skipping $pcap."
	else
		(echo "Processing $pcap..." && \
		tshark -r "$pcap" -Y 'ip.dst == 192.168.200.0/24 and tcp.len > 0' -T fields -E separator=, -e frame.time_epoch -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e tcp.len > "$pcap.toclients") &
	fi
done

wait
exit 0
