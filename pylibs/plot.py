import log
import numpy as np
import cPickle as pickle
from zipfile import PyZipFile
from tempfile import NamedTemporaryFile

def show(plt, session, fig, export, size=None):
	if export:
		if size is None:
			size = (22,12)
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
				fig.set_size_inches(size[0], size[1])
				fig.savefig(filename, bbox_inches='tight')
	else:
		plt.show()

def plotVLCSession(plt, session, export=False, details=True, plot_start=0, plot_end=None, plot_size=None, thickness_factor=1):
	if plot_end is None:
		plot_end = session.duration
	bandwidth_buffer_t, bandwidth_buffer_packets = session.bandwidth_buffer.get_events(time_relative_to=session, values_fn=lambda evt: evt.packets)
	#delay_buffer_t, delay_buffer_packets = session.delay_buffer.get_events(time_relative_to=session, values_fn=lambda evt: evt.packets)

	fig = plt.figure()
	ax_bits = None
	i = 0
	subplot_rows = len(session.VLClogs)*3+1 if details else len(session.VLClogs)*2
	for VLClog in session.VLClogs:
		ax_bits = plt.subplot2grid((subplot_rows, 1), (i, 0), rowspan=2, sharex=ax_bits)
		ax_bits.set_ylabel('(bit/s)')

		#session data
		for stream in session.streams:
			ax_bits.axhline(stream, alpha=0.4, color='black', linestyle='--')
		if len(session.bwprofile):
			bwprofile = sorted(session.bwprofile.iteritems())
			bwprofile.append((plot_end, bwprofile[-1][1]))
			bwprofile_t = [t for t, v in bwprofile]
			bwprofile_v = [v for t, v in bwprofile]
			bwprofile_v = [bwprofile_v[0]] + bwprofile_v[:-1]
			ax_bits.step(bwprofile_t, bwprofile_v, marker='.', markersize=1, linestyle=':', color='purple', linewidth=2*thickness_factor, label='bw limit')

		#client data
		vlc_t, vlc_events = VLClog.get_events(time_relative_to=session)
		vlc_approxbuffer_t, vlc_approxbuffer_v = VLClog.get_events(time_relative_to=session, values_fn=lambda evt: evt.buffer_approx, filter_fn=lambda evt: evt.buffer_approx is not None)
		for buffering in [e for e in vlc_events if e.buffering][1:]:
			ax_bits.axvline(buffering.t - session.start_time, alpha=0.8, linewidth=3*thickness_factor, color='red')
		#measured bandwidth
		ax_bits.step(vlc_t, [evt.downloading_bandwidth for evt in vlc_events], where='post', color='black', label='obtained bw', linewidth=thickness_factor)
		#stream requested
		stream_requests = [VLClog.streams[evt.downloading_stream] if evt.downloading_stream is not None else None for evt in vlc_events]
		ax_bits.step(vlc_t, stream_requests, where='post', color='green', label='stream requested', linewidth=thickness_factor)
		#playout buffer
		ax_buffer = ax_bits.twinx()
		#ax_buffer.step(vlc_t, [evt.buffer for evt in vlc_events], where='post', color='blue', alpha=0.7, linewidth=thickness_factor)
		ax_buffer.plot(vlc_approxbuffer_t, vlc_approxbuffer_v, color='blue', alpha=0.7, linewidth=thickness_factor)
		ax_buffer.set_ylabel('buffer (s)', color='blue')
		for tl in ax_buffer.get_yticklabels():
			tl.set_color('blue')
		ax_buffer.axhline(VLClog.buffersize, color='blue', linestyle='--')

		ax_bits.axis([plot_start, plot_end, 0, session.max_display_bits*1.1])
		ax_buffer.axis([plot_start, plot_end, 0, None])

		if details:
			#avg bitrate
			ax_buffer.text(plot_end*.99, 5, 'avg bandwidth: {0:.2f}kbit/s, avg bitrate: {1:.2f}kbit/s'.format(VLClog.get_avg_bandwidth()/1000, VLClog.get_avg_bitrate()/1000), weight='semibold', ha='right')

		if i == 0:
			handles, labels = ax_bits.get_legend_handles_labels()
			if details:
				handles += [plt.Line2D((0,1),(0,0), color='red'), plt.Line2D((0,1),(0,0), color='gray')]
				labels += ['cwnd', 'ssthresh']
			ax_bits.legend(handles, labels, bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)

		i += 2

		if details:
			#cwnd subplot
			ax_packets = plt.subplot2grid((subplot_rows, 1), (i, 0), sharex=ax_bits)
			ax_packets.set_ylabel('packets')

			for fourtuple, tcpp in VLClog.tcpprobe.split().iteritems():
				tcpp_t, tcpp_events = tcpp.get_events(time_relative_to=session)
				#tcpprobe
				cwnd = [evt.snd_cwnd for evt in tcpp_events]
				ax_packets.step(tcpp_t, cwnd, where='post', color='red', label='cwnd', linewidth=thickness_factor)
				ssthresh = [evt.ssthresh if evt.ssthresh < 2147483647 else 0 for evt in tcpp_events]
				ax_packets.step(tcpp_t, ssthresh, where='post', color='gray', label='ssthresh', linewidth=thickness_factor)

			for req_time in VLClog.http_requests:
				ax_packets.axvline(req_time - session.start_time, alpha=0.8, linestyle=':', linewidth=thickness_factor, color='black')

			i += 1

	if details:
		ax_packets = plt.subplot2grid((subplot_rows, 1), (i, 0), sharex=ax_bits)
		ax_packets.set_ylabel('router buffer (packets)')

		#buffer
		ax_packets.step(bandwidth_buffer_t, bandwidth_buffer_packets, where='post', color='black', label='bw buffer', linewidth=thickness_factor)
		#ax_packets.step(delay_buffer_t, delay_buffer_packets, where='post', color='purple', label='delay buffer', linewidth=thickness_factor)

		ax_packets.axis([plot_start, plot_end, 0, max(bandwidth_buffer_packets)*1.1])
		#handles, labels = ax_packets.get_legend_handles_labels()
		#ax_packets.legend(handles[:3], labels[:3], bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)

	show(plt, session, fig, export, plot_size)

	plt.close()

def format_bw(bits):
	if not bits % 1000000:
		return str(bits / 1000000) + 'mbit'
	if not bits % 1000:
		return str(bits / 1000) + 'kbit'
	return str(bits)+'bit'

def plotCompareSessions(grouped_sessions, export=False):
	if export:
		import matplotlib
		matplotlib.use('Agg')
	import matplotlib.pyplot as plt

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

def plotIperfSession(plt, session, export=False, details=None, plot_start=0, plot_end=None, plot_size=None, thickness_factor=None): #details and thickness_factor not implemented
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

	show(plt, session, fig, export, plot_size)

	plt.close()

def plotSession(session, export=False, details=True, plot_start=0, plot_end=None, plot_size=None, thickness_factor=1):
	plot_fn = None
	if type(session) is log.IperfSession:
		plot_fn = plotIperfSession
	elif type(session) is log.VLCSession:
		plot_fn = plotVLCSession
	if plot_fn is None:
		print type(session), session, dir(session)
		raise Exception('Not implemented')
	if export:
		import matplotlib
		matplotlib.use('Agg')
	import matplotlib.pyplot as plt
	return plot_fn(plt, session, export, details, plot_start, plot_end, plot_size, thickness_factor)

def open_pickle(filename):
	with open(filename, 'r') as f:
		plotSession(pickle.load(f))

if __name__ == '__main__':
	import sys
	sys.modules['pylibs.log'] = log #bad hack
	open_pickle(sys.argv[1])

