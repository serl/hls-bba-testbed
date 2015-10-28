#!/bin/bash

IN_PCAP="$RUN_PATH/dump_bandwidth_eth1.pcap"
OUT_PCAP="$RUN_PATH/dump_bandwidth_eth2.pcap"
TSHARK_FILTER='ip.dst == 192.168.200.0/24 and tcp.len > 0 and tcp.seq'
TSHARK_FIELDS="-e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e tcp.len -e tcp.seq"
OUT_FILE="$RUN_PATH/dropped_packets"

unsorted_out_file="$RUN_PATH/dropped_packets_unsorted"
rm $unsorted_out_file &>/dev/null

for pcap in "$IN_PCAP" "$OUT_PCAP"; do
	[ -e "$pcap" ] || exit 0
done

in_temp_time="$RUN_PATH/in_tempfile_time.txt"
in_temp="$RUN_PATH/in_tempfile.txt"
(echo "Processing IN interface..." && \
tshark -r "$IN_PCAP" -Y "$TSHARK_FILTER" -T fields -E separator=, -e frame.time_epoch $TSHARK_FIELDS > "$in_temp_time" && \
cut -d',' -f2- "$in_temp_time" | sort > "$in_temp") &

out_temp="$RUN_PATH/out_tempfile.txt"
(echo "Processing OUT interface..." && \
tshark -r "$OUT_PCAP" -Y "$TSHARK_FILTER" -T fields -E separator=, $TSHARK_FIELDS | sort > "$out_temp") &

wait

diff "$in_temp" "$out_temp" | grep '^<' | cut -d' ' -f2- | \
while IFS= read -r line; do
	grep -E "^[0-9.]+,$line\$" "$in_temp_time" | head -n-1 >>"$unsorted_out_file" || echo "Error calculating dropped packets on $RUN_PATH" >&2
done

sort "$unsorted_out_file" > "$OUT_FILE"

rm "$in_temp_time" "$in_temp" "$out_temp" "$unsorted_out_file"

exit 0
