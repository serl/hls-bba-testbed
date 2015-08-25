import sys, re, json, subprocess, os.path, traceback, collections
from parallelize import Parallelize

class LogEvent(object):
	def __repr__(self):
		return repr(self.__dict__)

class Log(object):
	def __init__(self):
		self.events = {}
		self.start_time = None
		self.end_time = None
		self.duration = 0
	def adjust_time(self):
		self.start_time = min(self.events)
		self.end_time = max(self.events)
		self.duration = self.end_time - self.start_time
	def get_events(self, values_fn=lambda evt: evt, filter_fn=lambda evt: True, time_relative_to=0, time_fn=None):
		if time_fn is None:
			if Session in type(time_relative_to).__bases__:
				time_relative_to = time_relative_to.start_time
			time_fn = lambda evt: evt.t - time_relative_to
		events = [evt for t, evt in sorted(self.events.iteritems()) if filter_fn(evt)]
		return ([time_fn(evt) for evt in events], [values_fn(evt) for evt in events])
	def get_value_at(self, time, values_fn=lambda evt: evt, compare_fn=None):
		if compare_fn is None:
			compare_fn = lambda a, b: values_fn(a) == values_fn(b)
		value = None
		try:
			value = values_fn(self.events[time])
		except KeyError:
			try:
				before_t = max([t for t in self.events.keys() if t <= time])
				after_t = min([t for t in self.events.keys() if t >= time])
				value = values_fn(self.events[before_t]) if compare_fn(self.events[before_t], self.events[after_t]) else None
			except ValueError:
				pass
		return value
	def get_step_value_at(self, time, values_fn=lambda evt: evt):
		value = None
		try:
			value = values_fn(self.events[time])
		except KeyError:
			try:
				before_t = max([t for t in self.events.keys() if t <= time])
				value = values_fn(self.events[before_t])
			except ValueError:
				pass
		return value
	@classmethod
	def parse(cls, *args, **kwargs):
		raise Exception('Not implemented')

class Session(object):
	def __init__(self):
		self.logs = []
		self.start_time = None
		self.end_time = None
		self.duration = 0
	def add_log(self, log):
		if log is None:
			return
		self.logs.append(log)
		self.adjust_time()
	def adjust_time(self):
		for log in filter(self.__class__.logs_filter, self.logs):
			if self.start_time is None or self.start_time > log.start_time:
				self.start_time = log.start_time
			if self.end_time is None or self.end_time < log.end_time:
				self.end_time = log.end_time
		try:
			self.duration = self.end_time - self.start_time
		except:
			pass
	@staticmethod
	def logs_filter(log):
		return True
	@classmethod
	def parse(cls, *args, **kwargs):
		raise Exception('Not implemented')

class VLCLog(Log):
	def __init__(self):
		super(VLCLog, self).__init__()
		self.algorithm = 'unknown'
		self.streams = ()
		self._composition_streams_id = ()
		self.composition = ()
		self.http_requests = []
		self.tcpprobe = None
		self.buffersize = 240

	def _fill_composition(self):
		self.composition = tuple(self.streams[n] for n in self._composition_streams_id)

	def _fill_bandwidths(self):
		bandwidths = {}
		previous_segment = 0
		for t in sorted(self.events):
			evt = self.events[t]
			if evt.downloading_segment is not previous_segment:
				bandwidths[previous_segment] = evt.previous_bandwidth
				if evt.downloading_segment is not None:
					previous_segment = evt.downloading_segment
		for t, evt in self.events.iteritems():
			try:
				evt.downloading_bandwidth = bandwidths[evt.downloading_segment] if evt.downloading_segment is not None else None
			except:
				evt.downloading_bandwidth = None #missing data! :(
			del evt.previous_bandwidth

	def count_buffering_events(self):
		return len([t for t, evt in self.events.iteritems() if evt.buffering])

	def get_avg_bitrate(self, skip=0):
		return float(sum(self.composition[skip:]))/len(self.composition[skip:])

	def get_avg_quality(self, skip=0):
		return 100*float(sum(self._composition_streams_id[skip:]))/len(self._composition_streams_id[skip:])/len(self.streams)

	def get_avg_buffer(self, skip=0):
		events = [evt for t, evt in self.events.iteritems() if evt.playing_time >= skip*1000]
		return float(sum([evt.buffer for evt in events]))/len(events)

	def get_avg_bandwidth(self, skip=0):
		samples = [evt.downloading_bandwidth for evt in self.events.values()[skip:] if evt.downloading_bandwidth is not None]
		return float(sum(samples))/len(samples)

	def count_bitrate_changes(self, skip=0):
		count = 0
		last = self.composition[skip]
		for b in self.composition[skip+1:]:
			if b != last:
				count += 1
				last = b
		return count

	def get_instability(self):
		if not hasattr(self, '_instability_cache'):
			skip = 0 #or break caching system
			self._instability_cache = float(self.count_bitrate_changes(skip)) / len(self.composition[skip:]) * 100
		return self._instability_cache

	@classmethod
	def parse(cls, filename):
		inst = cls()
		algorithm_re = re.compile('^ALGORITHM: (.+)$')
		streams_re = re.compile('^STREAMS: ([\d\s]*)$')
		composition_re = re.compile('^DOWNLOAD COMPOSITION: (\d*)$')
		event_re = re.compile('^T: ([\d\.]+), PLAYING TIME: (-?\d+)ms, BUFFER: (-?\d+)s \((-?\d+)\), PLAY STR/SEG \(buffering\): (\d+)/(\d+) \((\d+)\), DOWNLOAD STR/SEG \(active\): (\d+)/(\d+) \((\d+)\), BANDWIDTH: (\d+)(, AVG BANDWIDTH: (\d+))?$')
		bba1_re = re.compile('BBA1_debug. reservoir: (\d+)s, calculated rate: (\d+), selected_stream: (-?\d+), instant rates: ([\d\s]+)')
		past_evt = None
		with open(filename, "r") as contents:
			for line in contents:
				#event line
				match = event_re.match(line)
				if match:
					evt = LogEvent()
					evt.t = float(match.group(1))
					evt.playing_time = int(match.group(2))
					evt.buffer = int(match.group(3))
					evt.buffer_segments = int(match.group(4))
					evt.playing_stream = int(match.group(5))
					evt.playing_segment = int(match.group(6))
					evt.buffering = int(match.group(7)) == 1
					evt.downloading_active = int(match.group(10)) == 1
					evt.downloading_stream = int(match.group(8)) if evt.downloading_active else None
					evt.downloading_bitrate = inst.streams[evt.downloading_stream] if evt.downloading_stream is not None else None
					evt.downloading_segment = int(match.group(9)) if evt.downloading_active else None
					evt.previous_bandwidth = int(match.group(11))
					evt.avg_bandwidth = int(match.group(13)) if match.group(13) is not None else None

					if evt.buffering:
						evt.end = evt.t+1 #initialization
					evt.buffer_approx = None
					if past_evt is not None:
						if (not evt.downloading_active and not past_evt.downloading_active) or past_evt.buffer < evt.buffer or evt.buffer == 0:
							evt.buffer_approx = evt.buffer
						if (not past_evt.downloading_active and evt.downloading_active) or (past_evt.downloading_active and evt.downloading_active and past_evt.downloading_segment < evt.downloading_segment):
							inst.http_requests.append(evt.t)
						if past_evt.buffering:
							past_evt.end = evt.t

					#print line.strip()
					#print evt.t, evt.playing_time, evt.buffer, evt.buffer_segments, evt.playing_stream, evt.playing_segment, evt.rebuffering, evt.downloading_stream, evt.downloading_segment, evt.downloading_active, evt.previous_bandwidth
					inst.events[evt.t] = evt
					past_evt = evt
					continue

				#bba1 debug line
				match = bba1_re.match(line)
				if match:
					if past_evt is not None:
						past_evt.bba1_reservoir = int(match.group(1))
						past_evt.bba1_calcrate = int(match.group(2))
						past_evt.bba1_stream = int(match.group(3))
						if past_evt.bba1_stream < 0:
							past_evt.bba1_stream = None
						past_evt.bba1_rates = tuple(map(int, match.group(4).split(" ")))
						if all(r == 0 for r in past_evt.bba1_rates):
							past_evt.bba1_rates = None
					continue

				#download composition line
				match = composition_re.match(line)
				if match:
					inst._composition_streams_id = tuple(int(c) for c in match.group(1))
					continue

				#algorithm line
				match = algorithm_re.match(line)
				if match:
					inst.algorithm = match.group(1)
					continue

				#streams line
				match = streams_re.match(line)
				if match:
					inst.streams = tuple(int(bitrate) for bitrate in match.group(1).split())
					continue

				#unknown line
				raise Exception("UNKNOWN LINE: " + line.strip())
		inst._fill_composition()
		inst._fill_bandwidths()
		inst.adjust_time()
		return inst

class VLCSession(Session):
	def __init__(self):
		super(VLCSession, self).__init__()
		self.VLClogs = []
		self.bwprofile = {}
		self.clients = []
		self.streams = ()
		self.tcpprobe = None
		self.bandwidth_buffer = None
		self.delay_buffer = None
		self.name = ''
		self.run = ''
		self.collection = ''
		self.max_display_bits = 0

	def get_unfairness(self, time_relative_to=None):
		if time_relative_to is None:
			time_relative_to = self
		if Session in type(time_relative_to).__bases__:
			time_relative_to = time_relative_to.start_time
		if len(self.VLClogs) != 2:
			raise Exception('No sense in trying to measure unfairness. Need exactly 2 clients.')
		all_t = sorted(list(set(self.VLClogs[0].events.keys()) | set(self.VLClogs[1].events.keys())))
		unfairness = collections.OrderedDict()
		for t in all_t:
			client0_bw = self.VLClogs[0].get_step_value_at(t, lambda evt: self.VLClogs[0].streams[evt.downloading_stream] if evt.downloading_stream is not None else None)
			client1_bw = self.VLClogs[1].get_step_value_at(t, lambda evt: self.VLClogs[1].streams[evt.downloading_stream] if evt.downloading_stream is not None else None)
			#unfairness[t - time_relative_to] = None
			if client0_bw is not None and client1_bw is not None:
				unfairness[t - time_relative_to] = abs(client0_bw - client1_bw)
		return unfairness

	def get_avg_unfairness(self):
		last_t = None
		last_value = None
		wsum = 0.0
		wlen = 0.0
		for t, value in self.get_unfairness().iteritems():
			if last_t is None:
				last_t = t
				last_value = value
				continue
			weight = t - last_t
			wlen += weight
			wsum += weight * last_value
			last_t = t
			last_value = value
		return wsum/wlen

	def get_general_unfairness(self):
		if len(self.VLClogs) != 2:
			raise Exception('No sense in trying to measure unfairness. Need exactly 2 clients.')
		return abs(self.VLClogs[0].get_avg_bitrate() - self.VLClogs[1].get_avg_bitrate())

	def get_quality_unfairness(self):
		if len(self.VLClogs) != 2:
			raise Exception('No sense in trying to measure unfairness. Need exactly 2 clients.')
		return abs(self.VLClogs[0].get_avg_quality() - self.VLClogs[1].get_avg_quality())

	def get_total_measured(self):
		if not hasattr(self, '_total_measured_cache'):
			time_relative_to = self.start_time

			all_t = set()
			for VLClog in self.VLClogs:
				all_t = all_t | set(VLClog.events.keys())
			all_t = sorted(list(all_t))

			usage = collections.OrderedDict()
			for t in all_t:
				u = 0.0
				for VLClog in self.VLClogs:
					bw = VLClog.get_step_value_at(t, lambda evt: evt.downloading_bandwidth)
					if bw is not None:
						u += bw
				usage[t - time_relative_to] = u/self.get_bottleneck_at(t)*100
			self._total_measured_cache = usage
		return self._total_measured_cache

	def get_avg_total_measured(self):
		last_t = None
		last_value = None
		wsum = 0.0
		wlen = 0.0
		for t, value in self.get_total_measured().iteritems():
			if last_t is None:
				last_t = t
				last_value = value
				continue
			weight = t - last_t
			wlen += weight
			wsum += weight * last_value
			last_t = t
			last_value = value
		return wsum/wlen

	def get_avg_router_idle(self):
		total = len(self.bandwidth_buffer.events)
		count = 0.0
		for t, evt in self.bandwidth_buffer.events.iteritems():
			packets = evt.packets[0]
			if packets == 0:
				count += 1
		return count/total*100

	def get_fraction_oneidle(self): #nossdav-akhshabi gamma: fraction of time with exactly one client off
		if not hasattr(self, '_fraction_oneidle_cache'):
			if len(self.VLClogs) != 2:
				raise Exception('No sense in trying to measure gamma. Need exactly 2 clients.')
			all_t = sorted(list(set(self.VLClogs[0].events.keys()) | set(self.VLClogs[1].events.keys())))
			one_idle_time = 0
			last_t = all_t[0]
			last_activity = (False, False)
			for t in all_t:
				client0_on = self.VLClogs[0].get_step_value_at(t, lambda evt: evt.downloading_active)
				if client0_on is None:
					client0_on = False
				client1_on = self.VLClogs[1].get_step_value_at(t, lambda evt: evt.downloading_active)
				if client1_on is None:
					client1_on = False

				if client0_on ^ client1_on and last_activity == (client0_on, client1_on):
					one_idle_time += t - last_t

				last_t = t
				last_activity = (client0_on, client1_on)

			self._fraction_oneidle_cache = one_idle_time/self.duration

		return self._fraction_oneidle_cache

	def get_bottleneck_at(self, time):
		k = max([t for t in self.bwprofile.keys() if t <= time])
		return self.bwprofile[k]

	def get_fairshare(self):
		return max(self.bwprofile.values()) / len(self.clients)

	def get_fraction_both_overestimating(self, what='avg_bandwidth'): #nossdav-akhshabi mu
		if not hasattr(self, '_fraction_both_overestimating_cache'):
			self._fraction_both_overestimating_cache = {}

		if not self._fraction_both_overestimating_cache.has_key(what):
			if len(self.VLClogs) != 2:
				raise Exception('No sense in trying to measure gamma. Need exactly 2 clients.')
			fairshare = self.get_fairshare()
			all_t = sorted(list(set(self.VLClogs[0].events.keys()) | set(self.VLClogs[1].events.keys())))
			both_overestimating_time = 0.0
			last_t = all_t[0]
			last_activity = (False, False)
			for t in all_t:
				client0_bw = self.VLClogs[0].get_step_value_at(t, lambda evt: evt.__dict__[what])
				if client0_bw is None:
					client0_overestimating = False
				else:
					client0_overestimating = client0_bw > fairshare

				client1_bw = self.VLClogs[1].get_step_value_at(t, lambda evt: evt.__dict__[what])
				if client1_bw is None:
					client1_overestimating = False
				else:
					client1_overestimating = client1_bw > fairshare

				current_activity = (client0_overestimating, client1_overestimating)
				if current_activity == (True, True) and last_activity == (True, True):
					both_overestimating_time += t - last_t

				last_t = t
				last_activity = current_activity

			self._fraction_both_overestimating_cache[what] = both_overestimating_time/self.duration

		return self._fraction_both_overestimating_cache[what]

	def get_fraction_both_on(self): #nossdav-akhshabi lambda
		if not hasattr(self, '_fraction_both_on'):
			if len(self.VLClogs) != 2:
				raise Exception('No sense in trying to measure gamma. Need exactly 2 clients.')
			all_t = sorted(list(set(self.VLClogs[0].events.keys()) | set(self.VLClogs[1].events.keys())))
			c0_active = 0.0
			c1_active = 0.0
			both_active = 0.0
			last_t = all_t[0]
			last_activity = (False, False)
			for t in all_t:
				client0_on = self.VLClogs[0].get_step_value_at(t, lambda evt: evt.downloading_active)
				if client0_on is None:
					client0_on = False
				client1_on = self.VLClogs[1].get_step_value_at(t, lambda evt: evt.downloading_active)
				if client1_on is None:
					client1_on = False

				if client0_on and last_activity[0]:
					c0_active += t - last_t

				if client1_on and last_activity[1]:
					c1_active += t - last_t

				if client0_on and last_activity[0] and client1_on and last_activity[1]:
					both_active += t - last_t

				last_t = t
				last_activity = (client0_on, client1_on)

			fraction_c0 = both_active/c0_active
			fraction_c1 = both_active/c1_active
			self._fraction_both_on = max(fraction_c0, fraction_c1)

		return self._fraction_both_on

	def get_bwprofile(self, time_relative_to=None):
		if not len(self.bwprofile):
			return None

		if time_relative_to is None:
			time_relative_to = self
		if Session in type(time_relative_to).__bases__:
			time_relative_to = time_relative_to.start_time

		bwprofile_t = []
		bwprofile_v = []
		for rel_t, v in sorted(self.bwprofile.iteritems()):
			bwprofile_t.append(rel_t - time_relative_to)
			bwprofile_v.append(v)
		bwprofile_t.append(self.duration)
		bwprofile_v.append(bwprofile_v[-1])
		return (bwprofile_t, bwprofile_v)

	@classmethod
	def parse(cls, dirname):
		inst = cls()
		funcs = []
		funcs.append({'fn': TcpProbeLog.parse, 'args': (os.path.join(dirname, 'cwnd.log'),), 'return_attr': 'tcpprobe'})
		for h in ('bandwidth', 'delay'):
			funcs.append({'fn': RouterBufferLog.parse, 'args': (os.path.join(dirname, h+'_buffer.log'),), 'return_attr': h+'_buffer'})
			for iface in ('eth1', 'eth2'):
				toclients_file = os.path.join(dirname, 'dump_'+h+'_'+iface+'.pcap.toclients')
				if os.path.isfile(toclients_file):
					funcs.append({'fn': TsharkPacketsToClients.parse, 'args': (toclients_file,), 'return_attr': h+'_'+iface+'_toclients'})

		Parallelize(funcs, return_obj=inst).run()
		inst.add_log(inst.tcpprobe)
		inst.add_log(inst.bandwidth_buffer)
		inst.add_log(inst.delay_buffer)

		sched_file = os.path.join(dirname, 'jobs.sched')
		if not os.path.isfile(sched_file):
			sched_file = os.path.normpath(os.path.join(dirname, '..', 'jobs.sched'))
			inst.run = dirname.rstrip(os.path.sep).split(os.path.sep)[-1]
		session_re = re.compile('^#SESSION(.+)$')
		with open(sched_file, "r") as contents:
			for line in contents:
				#session line
				match = session_re.match(line)
				if match:
					session = json.loads(match.group(1))
					inst.name = session['name']
					inst.collection = session['collection']
					inst.bwprofile = {int(k)+inst.bandwidth_buffer.start_time: v for k,v in session['bwprofile'].iteritems()}
					inst.max_display_bits = max(inst.bwprofile.values())
					inst.clients = session['clients']
					for client in inst.clients:
						log_filename = os.path.join(dirname, client['host'] + '_vlc.log')
						try:
							log = inst._addvlclog(log_filename)
							log.tcpprobe = inst.tcpprobe.filter_by_ip(client['host'])
						except Exception, e:
							print traceback.format_exc()
					continue

				#skipping unknown lines
		return inst

	def _addvlclog(self, filename):
		log = VLCLog.parse(filename)

		if len(self.streams) == 0:
			self.streams = log.streams
		elif self.streams != log.streams:
			raise Exception("Logs of different videos!")

		max_stream = max(log.streams)
		if max_stream > self.max_display_bits:
			self.max_display_bits = max_stream

		max_bw = max([evt.downloading_bandwidth for t, evt in log.events.iteritems()])
		if max_bw > self.max_display_bits:
			self.max_display_bits = max_bw

		self.VLClogs.append(log)
		self.add_log(log)
		return log

	@staticmethod
	def logs_filter(log):
		return log.__class__ == VLCLog

class TcpProbeLog(Log):
	def split(self):
		instances = {}
		for t, evt in self.events.iteritems():
			if (evt.src, evt.src_port, evt.dst, evt.dst_port) not in instances:
				instances[(evt.src, evt.src_port, evt.dst, evt.dst_port)] = self.__class__()
			instances[(evt.src, evt.src_port, evt.dst, evt.dst_port)].events[t] = evt
		return instances

	def filter_by_ip(self, ip):
		ip_re = re.compile('^\d+\.\d+\.\d+\.\d+$')
		client_re = re.compile('^client(\d+)$')
		if not ip_re.match(ip):
			match = client_re.match(ip)
			if match:
				ip = '192.168.200.' + str(10 + int(match.group(1)))
		inst = self.__class__()
		inst.events = {t: evt for t, evt in self.events.iteritems() if evt.dst == ip}
		inst.adjust_time()
		return inst

	@classmethod
	def parse(cls, filename):
		inst = cls()
		boot_re = re.compile('^([\d\.]+) BOOT CONFIG_HZ=(\d+)$')
		line_re = re.compile('^([\d\.]+) ([\d\.:a-f\[\]]+):(\d+) ([\d\.:a-f\[\]]+):(\d+) (\d+) (0x[\da-f]+) (0x[\da-f]+) (\d+) (\d+) (\d+) (\d+) (\d+)$')
		ip4_re = re.compile('^\[::ffff:([\.\d]+)\]$')
		start_time = None
		hz_value = 1
		past_evt = None
		with open(filename, "r") as contents:
			for line in contents:
				match = boot_re.match(line)
				if match:
					start_time = float(match.group(1))
					hz_value = int(match.group(2))
					continue

				match = line_re.match(line)
				if match:
					evt = LogEvent()
					evt.t = float(match.group(1)) + start_time
					match_ip4 = ip4_re.match(match.group(2))
					evt.src = match_ip4.group(1) if match_ip4 else match.group(2)
					evt.src_port = int(match.group(3))
					match_ip4 = ip4_re.match(match.group(4))
					evt.dst = match_ip4.group(1) if match_ip4 else match.group(4)
					evt.dst_port = int(match.group(5))
					evt.packet_len = int(match.group(6))
					evt.next_seq = int(match.group(7), 16)
					evt.unack_seq = int(match.group(8), 16)
					evt.inflight = evt.next_seq - evt.unack_seq
					evt.snd_cwnd = int(match.group(9))
					evt.ssthresh = int(match.group(10))
					evt.snd_wnd = int(match.group(11))
					evt.srtt = int(match.group(12))*1000/hz_value
					evt.rcv_wnd = int(match.group(13))
					evt.sending = True
					if past_evt is not None:
						evt.sending = past_evt.next_seq != evt.next_seq
					inst.events[evt.t] = evt
					past_evt = evt
					continue

		inst.adjust_time()
		return inst

class RouterBufferLog(Log):
	@classmethod
	def parse(cls, filename):
		inst = cls()
		first_instant = -1
		start_re = re.compile('^([\d\.]+)')
		backlog_pattern = ' backlog ([\dKM]+)b (\d+)p requeues (\d+)'
		with open(filename, "r") as contents:
			for line in contents:
				match = start_re.match(line)
				if match:
					evt = LogEvent()
					evt.t = float(match.group(1))
					bytes = []
					packets = []
					requeues = []
					for m in re.finditer(backlog_pattern, line[match.end(1):]):
						bytes.append(m.group(1))
						packets.append(int(m.group(2)))
						requeues.append(int(m.group(3)))
					#evt.bytes = tuple(bytes)
					evt.packets = tuple(packets)
					#evt.requeues = tuple(requeues)
					inst.events[evt.t] = evt
					continue
		inst.adjust_time()
		return inst

class TsharkPacketsToClients(Log):
	def get_avg_rate(self):
		return self.avg_rate

	@classmethod
	def parse(cls, filename):
		inst = cls()
		inst.sampling_time = 0.01 #if you change the sampling_time you'll break the line below!
		line_re = re.compile('^([\d\.]+),([\d\.]+),(\d+),([\d\.]+),(\d+),(\d+)$')
		with open(filename, "r") as contents:
			for line in contents:
				match = line_re.match(line)
				if match:
					rounded_time = round(float(match.group(1)), 2) #this one!
					evt = None
					try:
						evt = inst.events[rounded_time]
					except:
						evt = LogEvent()
						evt.t = rounded_time
						evt.packets = 0
						evt.bytes = 0
						evt.rate = 0
						inst.events[evt.t] = evt
					evt.packets += 1
					evt.bytes += int(match.group(6))
					evt.rate = float(evt.bytes)*8/inst.sampling_time

					#make sure the plot will have zeros where needed!
					if rounded_time-inst.sampling_time not in inst.events:
						evt = LogEvent()
						evt.t = rounded_time-inst.sampling_time
						evt.packets = 0
						evt.bytes = 0
						evt.rate = 0
						inst.events[evt.t] = evt

					evt = LogEvent()
					evt.t = rounded_time+inst.sampling_time
					evt.packets = 0
					evt.bytes = 0
					evt.rate = 0
					inst.events[evt.t] = evt

					#evt = LogEvent()
					#evt.t = float(match.group(1))
					#evt.src = match.group(2)
					#evt.src_port = int(match.group(3))
					#evt.dst = match.group(4)
					#evt.dst_port = int(match.group(5))
					#evt.tcp_len = int(match.group(6))
					#inst.events[evt.t] = evt

					continue
		inst.adjust_time()
		rate_sum = sum([evt.rate for evt in inst.events.values()])
		total_values = int((inst.end_time-inst.start_time)/inst.sampling_time)+1
		inst.avg_rate = float(rate_sum)/total_values
		return inst

class TsharkAnalysis(Log):
	@classmethod
	def parse(cls, filename, ip_addr):
		inst = cls()
		line_re = re.compile('^([\d\.]+),([\d\.]+),([\d\.]+),(\d+),([\d\.]*)$')
		out = subprocess.check_output("tshark -r '{0}' -Y 'ip.addr=={1}' -T fields -E separator=, -e frame.time_epoch -e frame.time_relative -e ip.src -e frame.len -e tcp.analysis.ack_rtt".format(filename, ip_addr), shell=True)
		for line in out.split('\n'):
			match = line_re.match(line)
			if match:
				evt = LogEvent()
				evt.t = float(match.group(1))
				#evt.rtime = float(match.group(2))
				evt.sent = match.group(3) == ip_addr
				evt.frame_len = int(match.group(4))
				evt.rtt = float(match.group(5))*1000 if match.group(5) else None
				inst.events[evt.t] = evt
				continue
		inst.adjust_time()
		return inst

class IperfSession(Session):
	def __init__(self):
		super(IperfSession, self).__init__()
		self.tcpprobe = None
		self.bandwidth_buffer = None
		self.delay_buffer = None
		self.bandwidth_sender = None
		self.bandwidth_receiver = None
		self.tshark_sender = None
		self.tshark_receiver = None

	@staticmethod
	def get_bandwidth(filename):
		tcptrace_re = re.compile('^\s*throughput:\s*(\d+)\s+Bps')
		try:
			out = subprocess.check_output('tcptrace -l '+filename+' | grep throughput', shell=True)
			match = tcptrace_re.match(out)
			if match:
				return int(match.group(1))*8
		except Exception:
			print 'tcptrace error. Is that installed?'
			raise

	@classmethod
	def parse(cls, dirname, tshark=True):
		inst = cls()
		funcs = []
		funcs.append({'fn': TcpProbeLog.parse, 'args': (os.path.join(dirname, 'cwnd.log'),), 'return_attr': 'tcpprobe'})
		for h in ('bandwidth', 'delay'):
			funcs.append({'fn': RouterBufferLog.parse, 'args': (os.path.join(dirname, h+'_buffer.log'),), 'return_attr': h+'_buffer'})
		for h in ('sender', 'receiver'):
			funcs.append({'fn': IperfSession.get_bandwidth, 'args': (os.path.join(dirname, h+'.pcap'),), 'return_attr': 'bandwidth_'+h})
			if tshark:
				funcs.append({'fn': TsharkAnalysis.parse, 'args': (os.path.join(dirname, h+'.pcap'), '192.168.200.10'), 'return_attr': 'tshark_'+h})

		Parallelize(funcs, return_obj=inst).run()
		inst.add_log(inst.tcpprobe)
		inst.add_log(inst.bandwidth_buffer)
		inst.add_log(inst.delay_buffer)
		inst.add_log(inst.tshark_sender)
		inst.add_log(inst.tshark_receiver)

		return inst

