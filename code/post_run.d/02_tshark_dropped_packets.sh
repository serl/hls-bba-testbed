#!/bin/bash

pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null
IN_PCAP="$RUN_PATH/dump_bandwidth_eth1.pcap"
OUT_PCAP="$RUN_PATH/dump_bandwidth_eth2.pcap"
TSHARK_FILTER='ip.dst == 192.168.200.0/24 and tcp.len > 0 and tcp.seq'
TSHARK_FIELDS="-e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e tcp.len -e tcp.seq" #changing this will break the python script!
OUT_FILE="$RUN_PATH/dropped_packets"
PACKETGROUPS_OUT_FILE="$RUN_PATH/packet_groups.csv"

if [ -e "$OUT_FILE" ] && [ -e "$PACKETGROUPS_OUT_FILE" ]; then
	echo "Skipping dropped packet analysis"
	exit 0
fi

unsorted_out_file="$RUN_PATH/dropped_packets_unsorted"
rm $unsorted_out_file &>/dev/null

for pcap in "$IN_PCAP" "$OUT_PCAP"; do
	[ -e "$pcap" ] || exit 0
done

in_temp_complete="$RUN_PATH/in_tempfile_complete.txt"
in_temp_acks="$RUN_PATH/in_tempfile_acks."
in_temp_time="$RUN_PATH/in_tempfile_time.txt"
in_temp="$RUN_PATH/in_tempfile.txt"
(echo "Processing IN interface..." && \
tshark -r "$IN_PCAP" -Y 'ip.addr == 192.168.200.0/24 and tcp.port == 3000' -T fields -E separator=, -e frame.time_epoch -e tcp.stream $TSHARK_FIELDS -e tcp.ack > "$in_temp_complete" && \
awk -F, '{print > ("'$in_temp_acks'"$2)}' "$in_temp_complete" && \
python $SCRIPTPATH/02_process.py --in_tempfile="$in_temp" --in_tempfile_time="$in_temp_time" --packetgroups="$PACKETGROUPS_OUT_FILE" "$in_temp_acks"* && \
sort -o "$in_temp" "$in_temp" && \
echo "Done processing IN interface.") &

out_temp="$RUN_PATH/out_tempfile.txt"
(echo "Processing OUT interface..." && \
tshark -r "$OUT_PCAP" -Y "$TSHARK_FILTER" -T fields -E separator=, $TSHARK_FIELDS | sort > "$out_temp" && \
echo "Done processing OUT interface.") &

wait

diff "$in_temp" "$out_temp" | grep '^<' | cut -d' ' -f2- | \
while IFS= read -r line; do
	grep -E "^[0-9.]+,$line,[BCT]\$" "$in_temp_time" | head -n-1 >>"$unsorted_out_file" || echo "Error calculating dropped packets on $RUN_PATH" >&2
done

sort "$unsorted_out_file" > "$OUT_FILE"

rm "$in_temp_complete" "$in_temp_acks"* "$in_temp_time" "$in_temp" "$out_temp" "$unsorted_out_file"

exit 0
