import log
import matplotlib.pyplot as plt
import numpy as np
import cPickle as pickle
from zipfile import PyZipFile
from tempfile import NamedTemporaryFile

def show(session, fig, export):
	if export:
		if isinstance(export, basestring):
			export = [export]
		for filename in export:
			if filename.endswith('.pickle'):
				with open(filename, 'w') as f:
					pickle.dump(session, f)
			elif filename.endswith('.pyz'):
				with PyZipFile(filename, mode='w') as zf:
					zf.writepy('pylibs')
					with NamedTemporaryFile() as f:
						pickle.dump(session, f.file)
						f.seek(0, 0)
						zf.write(f.name, 'pylibs/pickle')
					zf.writestr('__main__.py', "from pylibs.plot import plotSession\nimport cPickle as pickle\nfrom pkg_resources import resource_stream\nplotSession(pickle.load(resource_stream('pylibs', 'pickle')))")
			else:
				fig.set_size_inches(22,12)
				fig.savefig(filename, bbox_inches='tight')
	else:
		plt.show()

def plotVLCSession(session, export = False, plot_start=0, plot_end=None):
	log = session.VLClogs[0]
	if plot_end is None:
		plot_end = log.duration
	vlc_t, vlc_events = log.get_events(time_relative_to=session)
	tcpprobe_t, tcpprobe_events = session.tcpprobe.get_events(time_relative_to=session)
	bandwidth_buffer_t, bandwidth_buffer_packets = session.bandwidth_buffer.get_events(time_relative_to=session, values_fn=lambda evt: evt.packets)
	delay_buffer_t, delay_buffer_packets = session.delay_buffer.get_events(time_relative_to=session, values_fn=lambda evt: evt.packets)

	fig = plt.figure()

	ax_bits = fig.add_subplot(2, 1, 1)
	ax_bits.set_ylabel('(bit/s)')
	bits_limit = 0

	for stream in session.streams:
		ax_bits.plot([plot_start, plot_end], [stream]*2, alpha=0.4, color='black', linestyle='--')
		if bits_limit < stream:
			bits_limit = stream*1.1

	if len(session.bwprofile):
		bwprofile = sorted(session.bwprofile.iteritems())
		bwprofile.append((plot_end, bwprofile[-1][1]))
		bwprofile_t = [t for t, v in bwprofile]
		bwprofile_v = [v for t, v in bwprofile]
		bwprofile_v = [bwprofile_v[0]] + bwprofile_v[:-1]
		ax_bits.step(bwprofile_t, bwprofile_v, marker='.', markersize=3, linestyle=':', color='purple', linewidth=2, label='bw limit')
		max_bw = max(bwprofile_v)
		if bits_limit < max_bw:
			bits_limit = max_bw*1.1

	for buffering in [e for e in vlc_events if e.buffering][1:]:
		ax_bits.axvline(buffering.t/1000, alpha=0.8, linewidth=3, color='red')

	obtained_bandwidth = [evt.downloading_bandwidth for evt in vlc_events]
	ax_bits.step(vlc_t, obtained_bandwidth, marker='.', markersize=3, linestyle=':', color='black', label='obtained bw')

	if bits_limit < max(obtained_bandwidth):
		bits_limit = max(obtained_bandwidth)*1.1

	stream_requests = [log.streams[evt.downloading_stream] if evt.downloading_stream is not None else None for evt in vlc_events]
	ax_bits.step(vlc_t, stream_requests, marker='.', markersize=3, linestyle=':', color='green', label='stream requested')

	ax_bits.axis([plot_start, plot_end, 0, bits_limit])

	ax_buffer = ax_bits.twinx()
	buffer_size = [evt.buffer for evt in vlc_events]
	ax_buffer.step(vlc_t, buffer_size, color='blue', alpha=0.7)
	ax_buffer.set_ylabel('buffer (s)', color='blue')
	for tl in ax_buffer.get_yticklabels():
		tl.set_color('blue')
	ax_buffer.axis([plot_start, plot_end, 0, None])

	ax_bits.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)

	ax_packets = fig.add_subplot(2, 1, 2, sharex=ax_bits)
	ax_packets.set_ylabel('packets')

	#buffer
	ax_packets.step(bandwidth_buffer_t, bandwidth_buffer_packets, color='blue', label='bw buffer')
	#ax_packets.step(delay_buffer_t, delay_buffer_packets, color='purple', label='delay buffer')

	for fourtuple, tcpp in log.tcpprobe.split().iteritems():
		tcpp_t, tcpp_events = tcpp.get_events(time_relative_to=session)
		#tcpprobe
		cwnd = [evt.snd_cwnd for evt in tcpp_events]
		ax_packets.step(tcpp_t, cwnd, color='red', label='cwnd')
		ssthresh = [evt.ssthresh if evt.ssthresh < 2147483647 else 0 for evt in tcpp_events]
		ax_packets.step(tcpp_t, ssthresh, color='gray', label='ssthresh')

	#ax_msec = ax_packets.twinx()
	#rtt = [evt.srtt for evt in tcpprobe_events]
	#ax_msec.step(tcpprobe_t, rtt, color='green', alpha=0.7)
	#ax_msec.set_ylabel('RTT (ms)', color='green')
	#for tl in ax_msec.get_yticklabels():
	#	tl.set_color('green')
	#ax_msec.axis([plot_start, plot_end, min(rtt)*0.8, max(rtt)*1.2])

	ax_packets.axis([plot_start, plot_end, 0, None])
	handles, labels = ax_packets.get_legend_handles_labels()
	ax_packets.legend(handles[:3], labels[:3], bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)

	show(session, fig, export)

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
	exclude_segments = 40
	
	plots = [
			{
				'title': 'Average bitrate',
				'fn': lambda s: s.VLClogs[0].get_avg_bitrate(),
				'show_bitrates': True
			},
			{
				'title': 'Average bitrate (excl. first {0} segments)'.format(exclude_segments),
				'fn': lambda s: s.VLClogs[0].get_avg_bitrate(skip=exclude_segments),
				'show_bitrates': True
			},
			{
				'title': 'Bitrate changes',
				'fn': lambda s: s.VLClogs[0].count_bitrate_changes(),
				'show_bitrates': False
			},
			{
				'title': 'Bitrate changes (excl. first {0} segments)'.format(exclude_segments),
				'fn': lambda s: s.VLClogs[0].count_bitrate_changes(skip=exclude_segments),
				'show_bitrates': False
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
#			},
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

def plotIperfSession(session, export = False, plot_start=0, plot_end=None):
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
	ax_packets.step(tcpprobe_t, cwnd, color='red', label='cwnd')
	ssthresh = [evt.ssthresh if evt.ssthresh < 2147483647 else 0 for evt in tcpprobe_events]
	ax_packets.step(tcpprobe_t, ssthresh, color='gray', label='ssthresh')

	#buffer
	ax_packets.step(bandwidth_buffer_t, bandwidth_buffer_packets, color='blue', label='bw buffer')
	ax_packets.step(delay_buffer_t, delay_buffer_packets, color='purple', label='delay buffer')

	ax_packets.axis([plot_start, plot_end, 0, None])

	#RTT
	ax_msec = ax_packets.twinx()
	rtt = [evt.srtt for evt in tcpprobe_events]
	ax_msec.step(tcpprobe_t, rtt, color='green', alpha=0.7)
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
			ax_bytes = fig.add_subplot(3, 1, plot_id, sharex=ax_packets)
			ax_bytes.step(tshark_framelen_t[h], tshark_framelen[h], marker='.', markersize=2, linestyle=':', color='blue', alpha=0.7)
			ax_bytes.set_ylabel('packet size (B)', color='blue')
			for tl in ax_bytes.get_yticklabels():
				tl.set_color('blue')
			ax_bytes.axis([plot_start, plot_end, min(tshark_framelen[h])*0.8, max(tshark_framelen[h])*1.2])

			#RTT
			ax_msec = ax_bytes.twinx()
			ax_msec.step(tshark_rtt_t[h], tshark_rtt[h], marker='.', markersize=2, linestyle=':', color='green', alpha=0.7)
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

	show(session, fig, export)

	plt.close()

def plotSession(session, export = False, plot_start=0, plot_end=None):
	plot_fn = None
	if type(session) is log.IperfSession:
		plot_fn = plotIperfSession
	elif type(session) is log.VLCSession:
		plot_fn = plotVLCSession
	if plot_fn is None:
		print type(session), session, dir(session)
		raise Exception('Not implemented')
	return plot_fn(session, export, plot_start, plot_end)

def open_pickle(filename):
	with open(filename, 'r') as f:
		plotSession(pickle.load(f))

if __name__ == '__main__':
	import sys
	sys.modules['pylibs.log'] = log #bad hack
	open_pickle(sys.argv[1])

