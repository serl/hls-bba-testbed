import sys, re, json, subprocess, os.path, traceback
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
			evt.downloading_bandwidth = bandwidths[evt.downloading_segment] if evt.downloading_segment is not None else None
			del evt.previous_bandwidth

	def count_buffering_events(self):
		return len([t for t, evt in self.events.iteritems() if evt.buffering])

	def get_avg_bitrate(self, skip=0):
		return float(sum(self.composition[skip:]))/len(self.composition[skip:])

	def get_avg_buffer(self, skip=0):
		events = [evt for t, evt in self.events.iteritems() if evt.playing_time >= skip*1000]
		return float(sum([evt.buffer for evt in events]))/len(events)

	def get_avg_bandwidth(self, skip=0):
		samples = [evt.downloading_bandwidth for evt in self.events.values()[skip:] if evt.downloading_bandwidth is not None]
		return float(sum(samples))/len(samples)

	def count_bitrate_changes(self, skip=0):
		count = 0
		last = self.composition[skip]
		for b in self.composition[skip:]:
			if b != last:
				count += 1
				last = b
		return count

	@classmethod
	def parse(cls, filename):
		inst = cls()
		algorithm_re = re.compile('^ALGORITHM: (.+)$')
		streams_re = re.compile('^STREAMS: ([\d\s]*)$')
		composition_re = re.compile('^DOWNLOAD COMPOSITION: (\d*)$')
		event_re = re.compile('^T: ([\d\.]+), PLAYING TIME: (-?\d+)ms, BUFFER: (-?\d+)s \((-?\d+)\), PLAY STR/SEG \(buffering\): (\d+)/(\d+) \((\d+)\), DOWNLOAD STR/SEG \(active\): (\d+)/(\d+) \((\d+)\), BANDWIDTH: (\d+)$')
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
					evt.downloading_segment = int(match.group(9)) if evt.downloading_active else None
					evt.previous_bandwidth = int(match.group(11))

					evt.buffer_approx = None
					if (not evt.downloading_active and not past_evt.downloading_active) or (past_evt is not None and past_evt.buffer < evt.buffer):
						evt.buffer_approx = evt.buffer
					last_buffer_size = evt.buffer

					#print line.strip()
					#print evt.t, evt.playing_time, evt.buffer, evt.buffer_segments, evt.playing_stream, evt.playing_segment, evt.rebuffering, evt.downloading_stream, evt.downloading_segment, evt.downloading_active, evt.previous_bandwidth
					inst.events[evt.t] = evt
					past_evt = evt
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
		self.collection = ''
		self.max_display_bits = 0

	@classmethod
	def parse(cls, dirname):
		inst = cls()
		funcs = []
		funcs.append({'fn': TcpProbeLog.parse, 'args': (os.path.join(dirname, 'cwnd.log'),), 'return_attr': 'tcpprobe'})
		for h in ('bandwidth', 'delay'):
			funcs.append({'fn': RouterBufferLog.parse, 'args': (os.path.join(dirname, h+'_buffer.log'),), 'return_attr': h+'_buffer'})

		Parallelize(funcs, return_obj=inst).run()
		inst.add_log(inst.tcpprobe)
		inst.add_log(inst.bandwidth_buffer)
		inst.add_log(inst.delay_buffer)

		session_re = re.compile('^#SESSION(.+)$')
		with open(os.path.join(dirname, 'jobs.sched'), "r") as contents:
			for line in contents:
				#session line
				match = session_re.match(line)
				if match:
					session = json.loads(match.group(1))
					inst.name = session['name']
					inst.collection = session['collection']
					inst.bwprofile = {int(k): v for k,v in session['bwprofile'].iteritems()}
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
					evt.next_seq = match.group(7)
					evt.unack_seq = match.group(8)
					evt.snd_cwnd = int(match.group(9))
					evt.ssthresh = int(match.group(10))
					evt.snd_wnd = int(match.group(11))
					evt.srtt = int(match.group(12))*1000/hz_value
					evt.rcv_wnd = int(match.group(13))
					inst.events[evt.t] = evt
					continue

		inst.adjust_time()
		return inst

class RouterBufferLog(Log):
	@classmethod
	def parse(cls, filename):
		inst = cls()
		first_instant = -1
		line_re = re.compile('^([\d\.]+) backlog ([\dKM]+)b (\d+)p requeues (\d+)')
		with open(filename, "r") as contents:
			for line in contents:
				match = line_re.match(line)
				if match:
					evt = LogEvent()
					evt.t = float(match.group(1))
					if first_instant == -1:
						first_instant = evt.t
					#evt.rtime = evt.t - first_instant
					evt.bytes = match.group(2)
					evt.packets = int(match.group(3))
					evt.requeues = int(match.group(4))
					inst.events[evt.t] = evt
					continue
		inst.adjust_time()
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

