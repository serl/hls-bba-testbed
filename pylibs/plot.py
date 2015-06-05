import matplotlib.pyplot as plt
import numpy as np

def plotSession(session, export = False):
	log = session.VLClogs[0]
	vlc_t, vlc_events = log.get_events(time_relative_to=session)
	tcpprobe_t, tcpprobe_events = session.tcpprobe.get_events(time_relative_to=session)
	bandwidth_buffer_t, bandwidth_buffer_packets = session.bandwidth_buffer.get_events(time_relative_to=session, values_fn=lambda evt: evt.packets)
	delay_buffer_t, delay_buffer_packets = session.delay_buffer.get_events(time_relative_to=session, values_fn=lambda evt: evt.packets)

	fig = plt.figure()

	ax_bits = fig.add_subplot(2, 1, 1)
	ax_bits.set_ylabel('(bits/s)')
	bits_limit = 0

	for stream in session.streams:
		ax_bits.plot([0, log.duration], [stream]*2, alpha=0.4, color='black', linestyle='--')
		if bits_limit < stream:
			bits_limit = stream + 100000

	if len(session.bwprofile):
		bw_t = []
		bw_values = []
		for time, value in sorted(session.bwprofile.iteritems()):
			time = time/1000
			if len(bw_t) != 0:
				bw_t.append(time - 1)
				bw_values.append(bw_values[-1])
			bw_t.append(time)
			bw_values.append(value)
		bw_t.append(log.duration)
		bw_values.append(bw_values[-1])
		ax_bits.plot(bw_t, bw_values, color='purple', linewidth=2, label='bw limit')

		if bits_limit < max(bw_values):
			bits_limit = max(bw_values) 

	for buffering in [e for e in vlc_events if e.buffering][1:]:
		ax_bits.axvline(buffering.t/1000, alpha=0.8, linewidth=3, color='red')

	obtained_bandwidth = [evt.downloading_bandwidth for evt in vlc_events]
	ax_bits.plot(vlc_t, obtained_bandwidth, marker='.', markersize=3, linestyle=':', color='black', label='obtained bw')

	if bits_limit < max(obtained_bandwidth):
		bits_limit = max(obtained_bandwidth) 

	stream_requests = [log.streams[evt.downloading_stream] if evt.downloading_stream is not None else None for evt in vlc_events]
	ax_bits.plot(vlc_t, stream_requests, marker='.', markersize=3, linestyle=':', color='green', label='stream requested')

	ax_bits.axis([0, log.duration, 0, bits_limit])

	ax_buffer = ax_bits.twinx()
	buffer_size = [evt.buffer for evt in vlc_events]
	ax_buffer.plot(vlc_t, buffer_size, color='blue', alpha=0.7)
	ax_buffer.set_ylabel('buffer (s)', color='blue')
	for tl in ax_buffer.get_yticklabels():
		tl.set_color('blue')
	ax_buffer.axis([0, log.duration, 0, max(buffer_size)+5])

	ax_bits.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)

	ax_packets = fig.add_subplot(2, 1, 2)
	ax_packets.set_ylabel('packets')

	#buffer
	ax_packets.plot(bandwidth_buffer_t, bandwidth_buffer_packets, color='blue', label='bw buffer')
	#ax_packets.plot(delay_buffer_t, delay_buffer_packets, color='purple', label='delay buffer')
	ax_packets.axis([0, log.duration, 0, None])

	#tcpprobe
	cwnd = [evt.snd_cwnd for evt in tcpprobe_events]
	ax_packets.plot(tcpprobe_t, cwnd, color='red', label='cwnd')

	#ax_msec = ax_packets.twinx()
	#rtt = [evt.srtt for evt in tcpprobe_events]
	#ax_msec.plot(tcpprobe_t, rtt, color='green', alpha=0.7)
	#ax_msec.set_ylabel('RTT (ms)', color='green')
	#for tl in ax_msec.get_yticklabels():
	#	tl.set_color('green')
	#ax_msec.axis([0, log.duration, min(rtt)*0.8, max(rtt)*1.2])

	ax_packets.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)

	if export:
		fig.set_size_inches(22,12)
		fig.savefig(export, bbox_inches='tight')
	else:
		plt.show()

	plt.close()

def format_bw(bits):
	if not bits % 1000000:
		return str(bits / 1000000) + 'mbit'
	if not bits % 1000:
		return str(bits / 1000) + 'kbit'
	return str(bits)+'bit'

def plotCompareSessions(grouped_sessions, export = False):
	fig = plt.figure()
	colors = ('blue', 'red')
	
	plots = [ 
			{
				'title': 'Average bitrate',
				'fn': lambda s: s.VLClogs[0].get_avg_bitrate(),
				'show_bitrates': True
			},
			{
				'title': 'Average bitrate (excl. first 25 segments)',
				'fn': lambda s: s.VLClogs[0].get_avg_bitrate(skip=25),
				'show_bitrates': True
			},
#			{
#				'title': 'Average buffer size',
#				'fn': lambda s: s.logs[0].get_avg_buffer(),
#				'show_bitrates': False
#			},
#			{
#				'title': 'Average buffer size (excl. first 240 seconts)',
#				'fn': lambda s: s.logs[0].get_avg_buffer(skip=240),
#				'show_bitrates': False
#			}
		]

	ind = np.arange(len(grouped_sessions[0]['sessions']))
	width = 0.35

	plot_id = 0
	for plot_dict in plots:
		plot_id += 1
		ax = fig.add_subplot(len(plots), 1, plot_id)
		rects = []
		i = 0
		for s in grouped_sessions:
			bitrates = [plot_dict['fn'](session) for session in s['sessions']]
			rects.append(ax.bar(ind+(width*i), bitrates, width, color=colors[i%len(colors)]))
			i += 1

		if plot_dict['show_bitrates']:
			for stream in grouped_sessions[0]['sessions'][0].streams:
				ax.axhline(stream, alpha=0.4, color='black', linestyle='--')

		ax.set_xlim(-width,len(ind)+width)
		#ax.set_ylim(0,45)
		#ax.set_ylabel('Scores')
		ax.set_title(plot_dict['title'])
		ax.set_xticks(ind+width)
		xtickNames = ax.set_xticklabels([format_bw(s.bwprofile[0]) for s in grouped_sessions[0]['sessions']])
		plt.setp(xtickNames, rotation=45, fontsize=10)

		ax.legend([r[0] for r in rects], [s['algo'] for s in grouped_sessions], loc=2)

	if export:
		fig.set_size_inches(10,6*len(plots))
		fig.savefig(export, bbox_inches='tight')
	else:
		plt.show()

	plt.close()

def plotIperf(session, export = False, plot_start=0, plot_end=None):
	if plot_end is None:
		plot_end = session.duration
	tcpprobe_t, tcpprobe_events = session.tcpprobe.get_events(time_relative_to=session)
	bandwidth_buffer_t, bandwidth_buffer_packets = session.bandwidth_buffer.get_events(time_relative_to=session, values_fn=lambda evt: evt.packets)
	delay_buffer_t, delay_buffer_packets = session.delay_buffer.get_events(time_relative_to=session, values_fn=lambda evt: evt.packets)
	thark = True
	tshark_framelen_t = {}
	tshark_framelen = {}
	tshark_rtt_t = {}
	tshark_rtt = {}
	for h in ('sender', 'receiver'):
		if session.__dict__['tshark_'+h] is None:
			tshark = False
			break
		tshark_framelen_t[h], tshark_framelen[h] = session.__dict__['tshark_'+h].get_events(time_relative_to=session, values_fn=lambda evt: evt.frame_len, filter_fn=lambda evt: not evt.sent)
		tshark_rtt_t[h], tshark_rtt[h] = session.__dict__['tshark_'+h].get_events(time_relative_to=session, values_fn=lambda evt: evt.rtt, filter_fn=lambda evt: evt.rtt is not None and evt.sent)

	fig = plt.figure()
	plot_id = 1

	ax_packets = fig.add_subplot(3 if tshark else 1, 1, plot_id)
	ax_packets.set_ylabel('packets')

	#tcpprobe
	cwnd = [evt.snd_cwnd for evt in tcpprobe_events]
	ax_packets.plot(tcpprobe_t, cwnd, color='red', label='cwnd')
	ssthresh = [evt.ssthresh if evt.ssthresh < 2147483647 else 0 for evt in tcpprobe_events]
	ax_packets.plot(tcpprobe_t, ssthresh, color='gray', label='ssthresh')

	#buffer
	ax_packets.plot(bandwidth_buffer_t, bandwidth_buffer_packets, color='blue', label='bw buffer')
	ax_packets.plot(delay_buffer_t, delay_buffer_packets, color='purple', label='delay buffer')

	ax_packets.axis([plot_start, plot_end, 0, None])

	#RTT
	ax_msec = ax_packets.twinx()
	rtt = [evt.srtt for evt in tcpprobe_events]
	ax_msec.plot(tcpprobe_t, rtt, color='green', alpha=0.7)
	ax_msec.set_ylabel('RTT (ms)', color='green')
	for tl in ax_msec.get_yticklabels():
		tl.set_color('green')
	ax_msec.axis([plot_start, plot_end, min(rtt)*0.8, max(rtt)*1.2])

	ax_packets.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0.)

	bw_text = ''
	for h in ('sender', 'receiver'):
		plot_id += 1
		if tshark:
			#packet size
			ax_bytes = fig.add_subplot(3, 1, plot_id)
			#ax_bytes.plot(tshark_framelen_t[h], tshark_framelen[h], color='blue', alpha=0.7)
			ax_bytes.plot(tshark_framelen_t[h], tshark_framelen[h], marker='.', markersize=2, linestyle=':', color='blue', alpha=0.7)
			ax_bytes.set_ylabel('packet size (B)', color='blue')
			for tl in ax_bytes.get_yticklabels():
				tl.set_color('blue')
			ax_bytes.axis([plot_start, plot_end, min(tshark_framelen[h])*0.8, max(tshark_framelen[h])*1.2])

			#RTT
			ax_msec = ax_bytes.twinx()
			#ax_msec.plot(tshark_rtt_t[h], tshark_rtt[h], color='green', alpha=0.7)
			ax_msec.plot(tshark_rtt_t[h], tshark_rtt[h], marker='.', markersize=2, linestyle=':', color='green', alpha=0.7)
			ax_msec.set_ylabel('RTT (ms)', color='green')
			for tl in ax_msec.get_yticklabels():
				tl.set_color('green')
			ax_msec.axis([plot_start, plot_end, min(tshark_rtt[h])*0.8, max(tshark_rtt[h])*1.2])

			#bw
			ax_bytes.text(plot_end*.99, max(tshark_framelen[h]), h+' bw: '+str(session.__dict__['bandwidth_'+h])+'bit/s', ha='right')
		else:
			bw_text += h+' bw: '+str(session.__dict__['bandwidth_'+h])+'bit/s '

	if bw_text is not '':
		ax_msec.text(plot_end, max(rtt)*1.2, bw_text, ha='right')

	if export:
		fig.set_size_inches(22,12)
		fig.savefig(export, bbox_inches='tight')
	else:
		plt.show()

	plt.close()

if __name__ == "__main__":
	import sys
	from log import Session
	filenames = sys.argv[1:]
	export = len(filenames) > 1
	if filenames[0] == 'export':
		export = True
		filenames = filenames[1:]

	for filename in filenames:
		session = Session()
		session.addlog(filename)
		plotSession(session, filename+'.svg' if export else None)

