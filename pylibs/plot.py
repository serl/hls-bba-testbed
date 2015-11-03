import log
import numpy as np
import cPickle as pickle
from zipfile import PyZipFile
from tempfile import NamedTemporaryFile
from generic import is_percentage

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
	if len(session.VLClogs) == 2:
		subplot_rows += 1
	if details:
		for VLClog in session.VLClogs:
			if VLClog.algorithm.startswith('bba1') or VLClog.algorithm.startswith('bba2') or VLClog.algorithm.startswith('bba3'):
				subplot_rows += 1

	for VLClog in session.VLClogs:
		ax_bits = plt.subplot2grid((subplot_rows, 1), (i, 0), rowspan=2, sharex=ax_bits)
		ax_bits.set_ylabel('(kbit/s)')

		#session data
		for stream in session.streams:
			ax_bits.axhline(stream, alpha=0.4, color='black', linestyle='--')
		bwprofile = session.get_profile('bwprofile')
		if bwprofile is not None:
			ax_bits.step(bwprofile[0], bwprofile[1], where='post', marker='.', markersize=1, linestyle=':', color='purple', linewidth=2*thickness_factor, label='total bandwidth')
			if len(session.VLClogs) > 1:
				ax_bits.step(bwprofile[0], [v/len(session.VLClogs) for v in bwprofile[1]], where='post', linestyle='--', alpha=.6, color='purple', linewidth=thickness_factor, label='bandwidth fair share')

		#client data
		vlc_t, vlc_events = VLClog.get_events(time_relative_to=session)
		vlc_approxbuffer_t, vlc_approxbuffer_v = VLClog.get_events(time_relative_to=session, values_fn=lambda evt: evt.buffer_approx, filter_fn=lambda evt: evt.buffer_approx is not None)
		for buffering in [e for e in vlc_events if e.buffering][1:]:
			ax_bits.axvspan(buffering.t - session.start_time, buffering.end - session.start_time, alpha=0.8, linewidth=0, color='red')
		#measured bandwidth
		ax_bits.step(vlc_t, [evt.downloading_bandwidth for evt in vlc_events], where='post', color='black', label='obtained throughput', linewidth=thickness_factor)
		if vlc_events[0].avg_bandwidth is not None and max([evt.avg_bandwidth for evt in vlc_events]) != 0:
			ax_bits.step(vlc_t, [evt.avg_bandwidth for evt in vlc_events], where='post', color='#441e00', alpha=0.7, label='average throughput', linewidth=thickness_factor)
		#stream requested
		stream_requests = [VLClog.streams[evt.downloading_stream] if evt.downloading_stream is not None else None for evt in vlc_events]
		ax_bits.step(vlc_t, stream_requests, where='post', color='green', label='stream requested', linewidth=thickness_factor)
		#playout buffer
		ax_buffer = ax_bits.twinx()
		#ax_buffer.step(vlc_t, [evt.buffer for evt in vlc_events], where='post', color='#000099', alpha=0.7, linewidth=thickness_factor)
		ax_buffer.plot(vlc_approxbuffer_t, vlc_approxbuffer_v, color='blue', alpha=0.7, linewidth=thickness_factor)
		ax_buffer.set_ylabel('buffer (s)', color='blue')
		for tl in ax_buffer.get_yticklabels():
			tl.set_color('blue')
		#ax_buffer.axhline(VLClog.buffersize, color='blue', linestyle='--')

		ax_bits.axis([plot_start, plot_end, 0, session.max_display_bits*1.1])
		locs = ax_bits.get_yticks()
		ax_bits.set_yticklabels(map("{0:.0f}".format, locs/1000))
		ax_buffer.axis([plot_start, plot_end, 0, None])

		if details:
			#avg bw, bitrate and instability
			ax_buffer.text(.99, .01, 'algorithm: {4}, avg bandwidth: {0:.2f}kbit/s, avg bitrate: {1:.2f}kbit/s, avg quality: {2:.1f}%, instability: {3:.1f}%'.format(VLClog.get_avg_bandwidth()/1000, VLClog.get_avg_bitrate()/1000, VLClog.get_avg_quality(), VLClog.get_instability(), VLClog.algorithm), transform=ax_buffer.transAxes, weight='semibold', ha='right')

		handles, labels = ax_bits.get_legend_handles_labels()
		handles += [plt.Line2D((0,1),(0,0), alpha=0.4, color='black', linestyle='--'), plt.Line2D((0,1),(0,0), color='blue')]
		labels += ['nominal bitrates', 'buffer size']
		ax_bits.legend(handles, labels, fontsize='small').set_zorder(20)

		i += 2

		if details:
			if VLClog.algorithm.startswith('bba1') or VLClog.algorithm.startswith('bba2') or VLClog.algorithm.startswith('bba3'):
				#bba1 subplot
				ax_bba1bits = plt.subplot2grid((subplot_rows, 1), (i, 0), sharex=ax_bits)
				ax_bba1bits.set_ylabel('(kbit/s)')

				for stream in (session.streams[0], session.streams[-1]):
					ax_bba1bits.axhline(stream, alpha=0.4, color='black', linestyle='--')

				#bwprofile = session.get_profile('bwprofile')
				#if bwprofile is not None:
				#	ax_bba1bits.step(bwprofile[0], bwprofile[1], where='post', marker='.', markersize=1, linestyle=':', color='purple', linewidth=2*thickness_factor, label='bw limit')

				#selected stream and rates
				vlc_bba1rates_t = []
				vlc_bba1rates_v = []
				#vlc_bba1calcrate_v = []
				vlc_bba1stream_v = []
				for vlc_evt_i, t in enumerate(vlc_t):
					evt = vlc_events[vlc_evt_i]
					if not hasattr(evt, 'bba1_rates') or evt.bba1_rates is None:
						continue
					vlc_bba1rates_t.append(t)
					vlc_bba1rates_v.append(evt.bba1_rates)
					#vlc_bba1calcrate_v.append(evt.bba1_calcrate)
					vlc_bba1stream_v.append(evt.bba1_rates[evt.bba1_stream] if evt.bba1_stream is not None else None)

				#for r_id, _ in enumerate(vlc_bba1rates_v[0]):
				bba1_rates_colors = ('#58D3F7', '#0080FF')
				bba1_rates_labels = ('real bitrate, lowest quality', 'real bitrate, highest quality')
				for r_id in (0, -1):
					inst_rates = [rates[r_id] for rates in vlc_bba1rates_v]
					ax_bba1bits.step(vlc_bba1rates_t, inst_rates, where='post', color=bba1_rates_colors[r_id], linewidth=thickness_factor, label=bba1_rates_labels[r_id])
				#ax_bba1bits.step(vlc_bba1rates_t, vlc_bba1calcrate_v, where='post', color='red', linewidth=thickness_factor)
				ax_bba1bits.step(vlc_bba1rates_t, vlc_bba1stream_v, where='post', color='green', linewidth=thickness_factor, label='real bitrate requested')

				ax_bba1bits.axis([plot_start, plot_end, 0, None])
				locs = ax_bba1bits.get_yticks()
				ax_bba1bits.set_yticklabels(map("{0:.0f}".format, locs/1000))

				# reservoir and buffer
				#ax_bba1buffer = ax_bba1bits.twinx()
				#ax_bba1buffer.step(vlc_t, [evt.buffer for evt in vlc_events], where='post', color='blue', linewidth=thickness_factor)
				#vlc_bba1reservoir_t, vlc_bba1reservoir_v = VLClog.get_events(time_relative_to=session, values_fn=lambda evt: evt.bba1_reservoir, filter_fn=lambda evt: hasattr(evt, 'bba1_reservoir'))
				#ax_bba1buffer.step(vlc_bba1reservoir_t, vlc_bba1reservoir_v, where='post', color='blue', linestyle='--', linewidth=thickness_factor)
				#ax_bba1buffer.set_ylabel('buffer (s)', color='blue')
				#for tl in ax_bba1buffer.get_yticklabels():
				#	tl.set_color('blue')
				#ax_bba1buffer.axis([plot_start, plot_end, 0, None])

				# bba2 debug infos
				#if VLClog.algorithm.startswith('bba2') or VLClog.algorithm.startswith('bba3'):
				#	startup_start = None
				#	for evt in vlc_events:
				#		if evt.bba2_status == 'startup' and startup_start is None:
				#			startup_start = evt.t
				#		if evt.bba2_status == 'steady' and startup_start is not None:
				#			ax_bba1bits.axvspan(startup_start - session.start_time, evt.t - session.start_time, ymin=.9, ymax=1, alpha=.5, linewidth=0, color='green')
				#			startup_start = None

				handles, labels = ax_bba1bits.get_legend_handles_labels()
				handles += [plt.Line2D((0,1),(0,0), alpha=0.4, color='black', linestyle='--')]
				labels += ['nominal bitrates (min, max)']
				ax_bba1bits.legend(handles, labels, fontsize='small')

				i += 1

			#cwnd subplot
			ax_packets = plt.subplot2grid((subplot_rows, 1), (i, 0), sharex=ax_bits)
			ax_packets.set_ylabel('(pkts)')
			#ax_msec = ax_packets.twinx()
			#ax_msec.set_ylabel('RTT (ms)', color='green')

			#tcpprobe
			for fourtuple, tcpp in VLClog.tcpprobe.split().iteritems():
				tcpp_t, tcpp_events = tcpp.get_events(time_relative_to=session)
				cwnd = [evt.snd_cwnd for evt in tcpp_events]
				ax_packets.step(tcpp_t, cwnd, where='post', color='red', linewidth=thickness_factor)
				ssthresh = [evt.ssthresh if evt.ssthresh < 2147483647 else 0 for evt in tcpp_events]
				ax_packets.step(tcpp_t, ssthresh, where='post', color='gray', linewidth=thickness_factor)
				#rtt = [evt.srtt for evt in tcpp_events]
				#ax_msec.step(tcpp_t, rtt, color='green', alpha=0.5)

			#for tl in ax_msec.get_yticklabels():
			#	tl.set_color('green')

			for req_time in VLClog.http_requests:
				ax_packets.axvline(req_time - session.start_time, alpha=0.8, linestyle=':', linewidth=thickness_factor, color='black')

			handles = [plt.Line2D((0,1),(0,0), color='red'), plt.Line2D((0,1),(0,0), color='gray'), plt.Line2D((0,1),(0,0), alpha=0.8, color='black', linestyle=':')]
			labels = ['congestion window', 'slow start threshold', 'segment requests']
			ax_packets.legend(handles, labels, fontsize='small')

			i += 1

	if details:
		ax_packets = plt.subplot2grid((subplot_rows, 1), (i, 0), sharex=ax_bits)
		ax_packets.set_ylabel('(pkts)')

		#buffer
		ax_packets.step(bandwidth_buffer_t, bandwidth_buffer_packets, where='post', color='#0B3B0B', alpha=.8, label='bottleneck router buffer', linewidth=thickness_factor)
		buffer_profile = session.get_profile('buffer_profile')
		ax_packets.step(buffer_profile[0], buffer_profile[1], where='post', marker='.', markersize=1, linestyle=':', color='blue', linewidth=2*thickness_factor, label='bottleneck router buffer limit')
		#ax_packets.step(delay_buffer_t, delay_buffer_packets, where='post', color='purple', label='delay buffer', linewidth=thickness_factor)

		ax_packets.axis([plot_start, plot_end, 0, max(max(bandwidth_buffer_packets), max(buffer_profile[1]))*1.1])
		#handles, labels = ax_packets.get_legend_handles_labels()
		#ax_packets.legend(handles[:3], labels[:3], bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)

		#total_measured = session.get_total_measured()
		#ax_usage = ax_packets.twinx()
		#ax_usage.set_ylabel('Total BW measured (%)', color='red')
		#ax_usage.step(total_measured.keys(), total_measured.values(), where='post', color='red', linewidth=thickness_factor)
		#ax_usage.axis([plot_start, plot_end, 0, None])
		#for tl in ax_usage.get_yticklabels():
		#	tl.set_color('red')
		avg_out_rate = '-'
		avg_in_rate = '-'
		try:
			rate = session.bandwidth_eth2_toclients.get_avg_rate()
			avg_out_rate = '{0:.2f}kbit/s'.format(rate/1000)
			if len(session.bwprofile) == 1:
				avg_out_rate += ' ({0:.1f}%)'.format(rate/session.bwprofile.values()[0]*100)
			avg_in_rate = '{0:.2f}kbit/s'.format(session.bandwidth_eth1_toclients.get_avg_rate()/1000)
		except:
			pass
		ax_packets.text(.99, .02, 'policy: {}, time with empty buffer: {:.1f}%\navg in rate: {}, avg out rate: {}'.format(session.aqm_algorithm, session.get_avg_router_idle(), avg_in_rate, avg_out_rate), transform=ax_packets.transAxes, weight='semibold', ha='right')

		try:
			h_sampling_time = session.bandwidth_eth1_toclients.sampling_time/2
			bandwidth_toclients_eth1_t, bandwidth_toclients_eth1_packets = session.bandwidth_eth1_toclients.get_events(time_relative_to=session, values_fn=lambda evt: evt.packets)

			max_packets = max(bandwidth_toclients_eth1_packets)
			burst_start_idx = None
			bursts = []
			for idx, packets in enumerate(bandwidth_toclients_eth1_packets):
				time = bandwidth_toclients_eth1_t[idx]
				if burst_start_idx is not None:
					if packets != bandwidth_toclients_eth1_packets[burst_start_idx]:
						bursts.append((bandwidth_toclients_eth1_t[burst_start_idx]-h_sampling_time, bandwidth_toclients_eth1_t[idx-1]+h_sampling_time, bandwidth_toclients_eth1_packets[burst_start_idx]))
						burst_start_idx = None
						if packets > 0:
							burst_start_idx = idx
				elif packets > 0:
					burst_start_idx = idx

			for burst in bursts:
				ax_packets.axvspan(burst[0], burst[1], alpha=min(0.2+0.8*burst[2]/max_packets, 1), linewidth=0, color='red')

			#bandwidth_toclients_eth2_t, bandwidth_toclients_eth2_rate = session.bandwidth_eth2_toclients.get_events(time_relative_to=session, values_fn=lambda evt: evt.rate)
			#ax_rate = ax_packets.twinx()
			#ax_rate.set_ylabel('Out rate (bit/s)', color='red')
			#ax_rate.step(bandwidth_toclients_eth2_t, bandwidth_toclients_eth2_rate, where='post', color='red', linewidth=thickness_factor)
			#ax_rate.axis([plot_start, plot_end, 0, None])
			#for tl in ax_rate.get_yticklabels():
			#	tl.set_color('red')

		except:
			raise

		import matplotlib.patches as mpatches
		handles, labels = ax_packets.get_legend_handles_labels()
		handles += [mpatches.Patch(color='red', alpha=.5)]
		labels += ['density of data from the server']
		ax_packets.legend(handles, labels, fontsize='small')

		i += 1

	if len(session.VLClogs) == 2:
		unfairness = session.get_unfairness()
		ax_unfairness = plt.subplot2grid((subplot_rows, 1), (i, 0), sharex=ax_bits)
		ax_unfairness.set_ylabel('(kbit/s)')
		ax_unfairness.step(unfairness.keys(), unfairness.values(), where='post', color='#550000', linewidth=thickness_factor, label='unfairness')
		ax_unfairness.axis([plot_start, plot_end, 0, max(unfairness.values())*1.1])
		ax_unfairness.text(.99, .02, 'avg unfairness: {0:.2f}kbit/s, general unfairness: {1:.2f}kbit/s, quality unfairness: {2:.1f}%'.format(session.get_avg_unfairness()/1000, session.get_general_unfairness()/1000, session.get_quality_unfairness()), transform=ax_unfairness.transAxes, color='#550000', weight='semibold', ha='right')
		locs = ax_unfairness.get_yticks()
		ax_unfairness.set_yticklabels(map("{0:.0f}".format, locs/1000))
		ax_unfairness.legend(fontsize='small')

		i += 1

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
		xtickNames = ax.set_xticklabels([format_bw(s.bwprofile.values()[0]) for s in grouped_sessions[0]['sessions']])
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
	dropped_packets_t, dropped_packets_events = session.dropped_packets.get_events(time_relative_to=session)
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
		tshark = True

	fig = plt.figure()
	plot_id = 1

	ax_packets = fig.add_subplot(3 if tshark else 1, 1, plot_id)
	ax_packets.set_ylabel('packets')
	if is_percentage(session.session_infos.bandwidth_buffersize_description) is not False:
		buffersize_string = "{} BDP, {} packets".format(session.session_infos.bandwidth_buffersize_description, session.session_infos.bandwidth_buffersize)
	else:
		buffersize_string = "{} packets".format(session.session_infos.bandwidth_buffersize)
	ax_packets.set_title("{type} session, BW: {bandwidth} (buf {buffersize_string}), RTT: {delay}, policy: {aqm_algorithm}".format(buffersize_string=buffersize_string, **session.session_infos.__dict__))

	#tcpprobe
	cwnd = [evt.snd_cwnd for evt in tcpprobe_events]
	ax_packets.step(tcpprobe_t, cwnd, color='red', label='cwnd')
	ssthresh = [evt.ssthresh if evt.ssthresh < 2147483647 else 0 for evt in tcpprobe_events]
	ax_packets.step(tcpprobe_t, ssthresh, color='gray', label='ssthresh')

	#dropped_packets
	for drop in dropped_packets_t:
		ax_packets.axvline(drop, alpha=.7, linewidth=thickness_factor, color='red')

	#buffer
	ax_packets.step(bandwidth_buffer_t, bandwidth_buffer_packets, color='blue', label='bw buffer')
	ax_packets.step(delay_buffer_t, delay_buffer_packets, color='purple', alpha=.5, label='delay buffer')

	ax_packets.axis([plot_start, plot_end, 0, None])

	#RTT
	ax_msec = ax_packets.twinx()
	rtt = [evt.srtt for evt in tcpprobe_events]
	ax_msec.step(tcpprobe_t, rtt, color='green', alpha=0.7)
	ax_msec.set_ylabel('RTT (ms)', color='green')
	for tl in ax_msec.get_yticklabels():
		tl.set_color('green')
	ax_msec.axis([plot_start, plot_end, min(rtt)*0.8, max(rtt)*1.2])

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
			ax_bytes.text(plot_end*.99, max(tshark_framelen[h]), '{0} bw: {1:.1f}kbit/s'.format(h, session.__dict__['bandwidth_'+h]/1000), ha='right')
			ax_bytes.set_title(h + '.pcap')
		else:
			bw_text += '{0} bw: {1:.1f}kbit/s '.format(h, session.__dict__['bandwidth_'+h]/1000)

	if bw_text is not '':
		ax_msec.text(plot_end, max(rtt)*1.2, bw_text, ha='right')

	import matplotlib.patches as mpatches
	handles, labels = ax_packets.get_legend_handles_labels()
	handles += [plt.Line2D((0,1),(0,0), alpha=0.7, color='green'), mpatches.Patch(color='red', alpha=.7)]
	labels += ['RTT', 'dropped packets']
	ax_packets.legend(handles, labels, fontsize='small')

	show(plt, session, fig, export, plot_size)

	plt.close()

def plotCompareVLCRuns(sessions, export=False, thickness_factor=1, size=None):
	details = False
	if export:
		import matplotlib
		matplotlib.use('Agg')
	import matplotlib.pyplot as plt
	if size is None:
		size = (22,12)

	colors = ('red', 'green', 'blue')
	fig = plt.figure()
	i = 0
	subplot_rows = len(sessions)

	for session in sessions:
		ax_bits = plt.subplot2grid((subplot_rows, 1), (i, 0))
		ax_bits.set_ylabel('(kbit/s)')

		for stream in session.streams:
			ax_bits.axhline(stream, alpha=0.4, color='black', linestyle='--')

		bwprofile = session.get_profile('bwprofile')
		if bwprofile is not None:
			ax_bits.step(bwprofile[0], [v/len(session.VLClogs) for v in bwprofile[1]], where='post', marker='.', markersize=1, linestyle=':', color='purple', linewidth=2*thickness_factor, label='bandwidth fair share')

		VLClogs_len = len(session.VLClogs)
		for VLClog_idx, VLClog in enumerate(session.VLClogs):
			vlc_t, vlc_events = VLClog.get_events(time_relative_to=session)

			for buffering in [e for e in vlc_events if e.buffering][1:]:
				ymin = 1 - VLClog_idx * (1-.9) / VLClogs_len
				ymax = 1 - (VLClog_idx+1) * (1-.9) / VLClogs_len
				ax_bits.axvspan(buffering.t - session.start_time, buffering.end - session.start_time, ymin=ymin, ymax=ymax, alpha=.8, linewidth=0, color=colors[VLClog_idx%len(colors)])

			stream_requests = [VLClog.streams[evt.downloading_stream] if (evt.downloading_stream is not None and evt.t in VLClog.http_requests) else None for evt in vlc_events]
			ax_bits.step(vlc_t, stream_requests, where='post', label='stream requested (client {0})'.format(VLClog_idx+1), marker='+', markersize=6*thickness_factor, markeredgewidth=thickness_factor, linestyle='None', color=colors[VLClog_idx%len(colors)], alpha=.7)
			if details:
				#bandwidth
				#ax_bits.step(vlc_t, [evt.downloading_bandwidth for evt in vlc_events], where='post', color='black', linewidth=thickness_factor/2)
				if vlc_events[0].avg_bandwidth is not None:
					ax_bits.step(vlc_t, [evt.avg_bandwidth for evt in vlc_events], where='post', color=colors[VLClog_idx%len(colors)], alpha=.5, linewidth=thickness_factor/2)

		if i == 0:
			ax_bits.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=len(session.VLClogs)+1, mode="expand", borderaxespad=0.)

		if details:
			ax_bits.text(.99, .01, 'gamma: {0:.2f}, mu: {1:.2f}, instability: {2:.1f}%'.format(session.get_fraction_oneidle(), session.get_fraction_both_overestimating(), VLClog.get_instability()), transform=ax_bits.transAxes, weight='semibold', ha='right')
		if details:
			ax_bits.axis([0, session.duration, 0, session.max_display_bits*1.1])
		else:
			ax_bits.axis([0, session.duration, 0, max(bwprofile[1])*1.1/len(session.VLClogs)])
		locs = ax_bits.get_yticks()
		ax_bits.set_yticklabels(map("{0:.0f}".format, locs/1000))

		i += 1

	if export:
		fig.set_size_inches(size[0], size[1])
		fig.savefig(export, bbox_inches='tight')
	else:
		plt.show()

	plt.close()

def plotScatters(sessions_summary, export=False, export_big=False, thickness_factor=1, plot_instability=True, plot_unfairness=False, plot_general_unfairness=True, plot_quality_unfairness=True, plot_router_rate=True, tag_points=True, colorize=True):
	if export:
		import matplotlib
		matplotlib.use('Agg')
	import matplotlib.pyplot as plt
	from matplotlib.colors import LinearSegmentedColormap

	tag_session = []
	tag_player = []
	gamma_session = []
	gamma_player = [] #the same, but dduupplliiccaattee
	mu = []
	mu_dry = []
	mu_bitrate = []
	instability = []
	fairshare_session = []
	fairshare_player = []
	lambda_session = []
	lambda_player = []
	unfairness = []
	general_unfairness = []
	quality_unfairness = []
	router_rate = []
	for summary in sessions_summary.sessions:
		tag_session.append(summary.tag)
		gamma_session.append(summary.gamma)
		mu.append(summary.mu)
		mu_dry.append(summary.mu_dry)
		mu_bitrate.append(summary.mu_bitrate)
		fairshare_session.append(summary.fairshare)
		lambda_session.append(summary.lambdap)
		unfairness.append(summary.unfairness)
		general_unfairness.append(summary.general_unfairness)
		quality_unfairness.append(summary.quality_unfairness)
		router_rate.append(summary.router_rate)
		if summary.router_rate is None:
			plot_router_rate = False
		for VLCsummary in summary.VLClogs:
			tag_player.append(summary.tag)
			gamma_player.append(summary.gamma)
			if plot_instability:
				instability.append(VLCsummary.instability)
			fairshare_player.append(summary.fairshare)
			lambda_player.append(summary.lambdap)

	if not tag_points:
		tag_session = []
		tag_player = []

	fig = plt.figure()
	plot_rows = 2 * (int(plot_instability) + int(plot_unfairness) + int(plot_general_unfairness) + int(plot_quality_unfairness) + int(plot_router_rate)) + 1

	cdict = {'red': ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)), 'green': ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)), 'blue': ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))}
	cmap = LinearSegmentedColormap('Black', cdict)
	if colorize:
		cmap = plt.get_cmap('cool')

	row = 0

	ax_gamma_mu = plt.subplot2grid((plot_rows, 2), (row, 0))
	ax_gamma_mu.set_xlabel(r'$\gamma$', labelpad=0)
	ax_gamma_mu.set_ylabel(r'$\mu$')
	ax_gamma_mu.scatter(gamma_session, mu, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
	for i, tag in enumerate(tag_session):
		ax_gamma_mu.annotate(tag, (gamma_session[i], mu[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
	ax_gamma_mu.axis([0, None, 0, None])

	if plot_instability:
		ax_gamma_inst = plt.subplot2grid((plot_rows, 2), (row, 1))
		ax_gamma_inst.set_xlabel(r'$\gamma$', labelpad=0)
		ax_gamma_inst.set_ylabel('instability (%)')
		ax_gamma_inst.scatter(gamma_player, instability, marker='x', s=50*thickness_factor, c=fairshare_player, cmap=cmap)
		for i, tag in enumerate(tag_player):
			ax_gamma_inst.annotate(tag, (gamma_player[i], instability[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_gamma_inst.axis([0, None, 0, None])
		row += 1

		ax_fairshare_inst = plt.subplot2grid((plot_rows, 2), (row, 0))
		ax_fairshare_inst.set_xlabel('fair share (kbit/s)', labelpad=0)
		ax_fairshare_inst.set_ylabel('instability (%)')
		ax_fairshare_inst.scatter(fairshare_player, instability, marker='x', s=50*thickness_factor, c=fairshare_player, cmap=cmap)
		for s in sessions_summary.streams:
			ax_fairshare_inst.axvline(s/1000, alpha=0.4, linewidth=2*thickness_factor, color='black')
		for i, tag in enumerate(tag_player):
			ax_fairshare_inst.annotate(tag, (fairshare_player[i], instability[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_fairshare_inst.axis([0, None, 0, None])

		ax_lambda_inst = plt.subplot2grid((plot_rows, 2), (row, 1))
		ax_lambda_inst.set_xlabel(r'$\lambda$', labelpad=0)
		ax_lambda_inst.set_ylabel('instability (%)')
		ax_lambda_inst.scatter(lambda_player, instability, marker='x', s=50*thickness_factor, c=fairshare_player, cmap=cmap)
		for i, tag in enumerate(tag_player):
			ax_lambda_inst.annotate(tag, (lambda_player[i], instability[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_lambda_inst.axis([0, None, 0, None])
		row += 1

	if plot_unfairness:
		ax_gamma_unfairness = plt.subplot2grid((plot_rows, 2), (row, 1))
		ax_gamma_unfairness.set_xlabel(r'$\gamma$', labelpad=0)
		ax_gamma_unfairness.set_ylabel('unfairness (kbit/s)')
		ax_gamma_unfairness.scatter(gamma_session, unfairness, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for i, tag in enumerate(tag_session):
			ax_gamma_unfairness.annotate(tag, (gamma_session[i], unfairness[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_gamma_unfairness.axis([0, None, 0, None])
		row += 1

		ax_fairshare_unfairness = plt.subplot2grid((plot_rows, 2), (row, 0))
		ax_fairshare_unfairness.set_xlabel('fair share (kbit/s)', labelpad=0)
		ax_fairshare_unfairness.set_ylabel('unfairness (kbit/s)')
		ax_fairshare_unfairness.scatter(fairshare_session, unfairness, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for s in sessions_summary.streams:
			ax_fairshare_unfairness.axvline(s/1000, alpha=0.4, linewidth=2*thickness_factor, color='black')
		for i, tag in enumerate(tag_session):
			ax_fairshare_unfairness.annotate(tag, (fairshare_session[i], unfairness[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_fairshare_unfairness.axis([0, None, 0, None])

		ax_lambda_unfairness = plt.subplot2grid((plot_rows, 2), (row, 1))
		ax_lambda_unfairness.set_xlabel(r'$\lambda$', labelpad=0)
		ax_lambda_unfairness.set_ylabel('unfairness (kbit/s)')
		ax_lambda_unfairness.scatter(lambda_session, unfairness, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for i, tag in enumerate(tag_session):
			ax_lambda_unfairness.annotate(tag, (lambda_session[i], unfairness[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_lambda_unfairness.axis([0, None, 0, None])
		row += 1

	if plot_general_unfairness:
		ax_gamma_gunfairness = plt.subplot2grid((plot_rows, 2), (row, 1))
		ax_gamma_gunfairness.set_xlabel(r'$\gamma$', labelpad=0)
		ax_gamma_gunfairness.set_ylabel('general unfairness (kbit/s)')
		ax_gamma_gunfairness.scatter(gamma_session, general_unfairness, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for i, tag in enumerate(tag_session):
			ax_gamma_gunfairness.annotate(tag, (gamma_session[i], general_unfairness[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_gamma_gunfairness.axis([0, None, 0, None])
		row += 1

		ax_fairshare_gunfairness = plt.subplot2grid((plot_rows, 2), (row, 0))
		ax_fairshare_gunfairness.set_xlabel('fair share (kbit/s)', labelpad=0)
		ax_fairshare_gunfairness.set_ylabel('general unfairness (kbit/s)')
		ax_fairshare_gunfairness.scatter(fairshare_session, general_unfairness, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for s in sessions_summary.streams:
			ax_fairshare_gunfairness.axvline(s/1000, alpha=0.4, linewidth=2*thickness_factor, color='black')
		for i, tag in enumerate(tag_session):
			ax_fairshare_gunfairness.annotate(tag, (fairshare_session[i], general_unfairness[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_fairshare_gunfairness.axis([0, None, 0, None])

		ax_lambda_gunfairness = plt.subplot2grid((plot_rows, 2), (row, 1))
		ax_lambda_gunfairness.set_xlabel(r'$\lambda$', labelpad=0)
		ax_lambda_gunfairness.set_ylabel('general unfairness (kbit/s)')
		ax_lambda_gunfairness.scatter(lambda_session, general_unfairness, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for i, tag in enumerate(tag_session):
			ax_lambda_gunfairness.annotate(tag, (lambda_session[i], general_unfairness[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_lambda_gunfairness.axis([0, None, 0, None])
		row += 1

	if plot_quality_unfairness:
		ax_gamma_qunfairness = plt.subplot2grid((plot_rows, 2), (row, 1))
		ax_gamma_qunfairness.set_xlabel(r'$\gamma$', labelpad=0)
		ax_gamma_qunfairness.set_ylabel('quality unfairness (%)')
		ax_gamma_qunfairness.scatter(gamma_session, quality_unfairness, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for i, tag in enumerate(tag_session):
			ax_gamma_qunfairness.annotate(tag, (gamma_session[i], quality_unfairness[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_gamma_qunfairness.axis([0, None, 0, None])
		row += 1

		ax_fairshare_qunfairness = plt.subplot2grid((plot_rows, 2), (row, 0))
		ax_fairshare_qunfairness.set_xlabel('fair share (kbit/s)', labelpad=0)
		ax_fairshare_qunfairness.set_ylabel('quality unfairness (%)')
		ax_fairshare_qunfairness.scatter(fairshare_session, quality_unfairness, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for s in sessions_summary.streams:
			ax_fairshare_qunfairness.axvline(s/1000, alpha=0.4, linewidth=2*thickness_factor, color='black')
		for i, tag in enumerate(tag_session):
			ax_fairshare_qunfairness.annotate(tag, (fairshare_session[i], quality_unfairness[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_fairshare_qunfairness.axis([0, None, 0, None])

		ax_lambda_qunfairness = plt.subplot2grid((plot_rows, 2), (row, 1))
		ax_lambda_qunfairness.set_xlabel(r'$\lambda$', labelpad=0)
		ax_lambda_qunfairness.set_ylabel('quality unfairness (%)')
		ax_lambda_qunfairness.scatter(lambda_session, quality_unfairness, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for i, tag in enumerate(tag_session):
			ax_lambda_qunfairness.annotate(tag, (lambda_session[i], quality_unfairness[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_lambda_qunfairness.axis([0, None, 0, None])
		row += 1

	if plot_router_rate:
		ax_gamma_rrate = plt.subplot2grid((plot_rows, 2), (row, 1))
		ax_gamma_rrate.set_xlabel(r'$\gamma$', labelpad=0)
		ax_gamma_rrate.set_ylabel('router output rate (%)')
		ax_gamma_rrate.scatter(gamma_session, router_rate, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for i, tag in enumerate(tag_session):
			ax_gamma_rrate.annotate(tag, (gamma_session[i], router_rate[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_gamma_rrate.axis([0, None, 0, None])
		row += 1

		ax_fairshare_rrate = plt.subplot2grid((plot_rows, 2), (row, 0))
		ax_fairshare_rrate.set_xlabel('fair share (kbit/s)', labelpad=0)
		ax_fairshare_rrate.set_ylabel('router output rate (%)')
		ax_fairshare_rrate.scatter(fairshare_session, router_rate, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for s in sessions_summary.streams:
			ax_fairshare_rrate.axvline(s/1000, alpha=0.4, linewidth=2*thickness_factor, color='black')
		for i, tag in enumerate(tag_session):
			ax_fairshare_rrate.annotate(tag, (fairshare_session[i], router_rate[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_fairshare_rrate.axis([0, None, 0, None])

		ax_lambda_rrate = plt.subplot2grid((plot_rows, 2), (row, 1))
		ax_lambda_rrate.set_xlabel(r'$\lambda$', labelpad=0)
		ax_lambda_rrate.set_ylabel('router output rate (%)')
		ax_lambda_rrate.scatter(lambda_session, router_rate, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
		for i, tag in enumerate(tag_session):
			ax_lambda_rrate.annotate(tag, (lambda_session[i], router_rate[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
		ax_lambda_rrate.axis([0, None, 0, None])
		row += 1

	ax_gamma_mu_dry = plt.subplot2grid((plot_rows, 2), (row, 0))
	ax_gamma_mu_dry.set_xlabel(r'$\gamma$', labelpad=0)
	ax_gamma_mu_dry.set_ylabel(r'$\mu$ dry')
	ax_gamma_mu_dry.scatter(gamma_session, mu_dry, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
	for i, tag in enumerate(tag_session):
		ax_gamma_mu_dry.annotate(tag, (gamma_session[i], mu_dry[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
	ax_gamma_mu_dry.axis([0, None, 0, None])

	ax_gamma_mu_bitrate = plt.subplot2grid((plot_rows, 2), (row, 1))
	ax_gamma_mu_bitrate.set_xlabel(r'$\gamma$', labelpad=0)
	ax_gamma_mu_bitrate.set_ylabel(r'$\mu$ bitrate')
	ax_gamma_mu_bitrate.scatter(gamma_session, mu_bitrate, marker='x', s=50*thickness_factor, c=fairshare_session, cmap=cmap)
	for i, tag in enumerate(tag_session):
		ax_gamma_mu_bitrate.annotate(tag, (gamma_session[i], mu_bitrate[i]), size=thickness_factor*5, xytext=(0, 0), textcoords='offset points', horizontalalignment='center', verticalalignment='center')
	ax_gamma_mu_bitrate.axis([0, None, 0, None])

	if export:
		fig.set_size_inches(22,4*plot_rows)
		fig.savefig(export, bbox_inches='tight')
		if export_big:
			fig.set_size_inches(88,16*plot_rows)
			fig.savefig(export_big, bbox_inches='tight')
	else:
		plt.show()

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

