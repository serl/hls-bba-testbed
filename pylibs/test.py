import os, re, json, errno, string, random
from generic import mkdir_p, is_percentage

class Test(object):
	save_dir = 'tests'

	def __init__(self, name, collection='', player=None, init_bw=None, packet_delay=None, log_cwnd=True, log_routerbuffer=True, aqm_algorithm='droptail'):
		self._events = []
		self.name = name
		self.collection = collection
		self.bw_profile = {}
		self.buffer_profile = {}
		self.delay_profile = {}
		self.clients = []
		self.log_cwnd = log_cwnd
		self.log_routerbuffer = log_routerbuffer
		self.aqm_algorithm = aqm_algorithm

		if player is not None:
			self._events.append(player)
		if init_bw is not None:
			self._events.append(init_bw)
		if packet_delay is not None:
			self._events.append(DelayChange(packet_delay=packet_delay))

		if self.log_cwnd:
			self._events.append(CwndLogger(delay=0, host='server'))
		if self.log_routerbuffer:
			self._events.append(RouterBufferLogger(delay=0, host='bandwidth'))
			self._events.append(RouterBufferLogger(delay=0, host='delay'))
		self._events.append(TrafficControlCleanup(host='bandwidth'))
		self._events.append(TrafficControlCleanup(host='delay'))

	def add_event(self, e):
		self._events.append(e)

	def generate_schedule(self, echo=False):
		last_moment = 2
		for evt in self._events:
			if KilledEvent in type(evt).__bases__ and 'kill_after' in evt.__dict__ and evt.kill_after + evt.delay > last_moment:
				last_moment = evt.kill_after + evt.delay
		for evt in self._events:
			if KilledEvent in type(evt).__bases__ and not 'kill_after' in evt.__dict__:
				evt.kill_after = last_moment - evt.delay
			if CleanupEvent in type(evt).__bases__:
				evt.delay = last_moment

		events = sorted(self._events, key=lambda evt: evt.delay)
		#scheduler_commands = '#eval LOGDIR=/vagrant/tests/'+self.collection+'/'+self.name+'\n' now injected from the scheduler
		scheduler_commands = ''
		for evt in events:
			scheduler_commands += evt.commands(self) + '\n'
		scheduler_commands = '#SESSION' + json.dumps({'name': self.name, 'collection': self.collection, 'bwprofile': self.bw_profile, 'aqm_algorithm': self.aqm_algorithm, 'buffer_profile': self.buffer_profile, 'delay_profile': self.delay_profile, 'clients': self.clients}) + '\n' + scheduler_commands

		if echo:
			print scheduler_commands
		else:
			mkdir_p(os.path.join(self.save_dir, self.collection, self.name))
			with open(os.path.join(self.save_dir, self.collection, self.name, 'jobs.sched'), 'w') as f:
				f.write(scheduler_commands)

num_unit_re = re.compile('^(\d+(\.\d+)?)(\w*)$')
def bw_convert(bw): #read tc style, convert to bits/s (hope so)
	match = num_unit_re.match(str(bw))
	if not match:
		raise Exception('Malformed bandwidth, see tc docs.')
	value = float(match.group(1))
	unit = match.group(3).lower()
	if unit == 'kbps':
		return int(value*8000)
	if unit == 'mbps':
		return int(value*8000000)
	if unit == 'kbit':
		return int(value*1000)
	if unit == 'mbit':
		return int(value*1000000)
	if unit == 'bit' or unit == '':
		return int(value)
	raise Exception('Malformed bandwidth, see tc docs.')
def delay_convert(delay): #read tc style, convert to ms
	match = num_unit_re.match(str(delay))
	if not match:
		raise Exception('Malformed delay, see tc docs.')
	value = float(match.group(1))
	unit = match.group(3).lower()
	if unit == 's':
		return int(value*1000)
	if unit == 'ms':
		return int(value)
	raise Exception('Malformed delay, see tc docs.')
def router_buffer_convert(buffer_size, bw, rtt, mss=1500):
	try:
		real_size = int(buffer_size)
	except ValueError:
		percentage = is_percentage(buffer_size)
		if percentage is False:
			raise
		real_size = int(bw_convert(bw) * delay_convert(rtt) * percentage / 8 / mss / 100000)
	if real_size <= 0:
		return 1
	return real_size


class Event(object):
	delay=0
	def __init__(self, **kwds):
		self.__dict__.update(kwds)
	def commands(self, test):
		raise Exception('Not implemented')
	def __repr__(self):
		return repr(self.__dict__)

class KilledEvent(Event):
	def commands(self, test):
		if not 'kill_after' in self.__dict__:
			raise Exception('Missing kill_after in KilledEvent')
		rndstr = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
		up = '%s %d %s & echo $! >/tmp/pid_%s' % (self.host, self.delay, self.killed_command(test), rndstr)
		down = '%s %d sudo kill -SIGTERM $(cat /tmp/pid_%s)' % (self.host, self.kill_after + self.delay, rndstr)
		return up + '\n' + down
	def killed_command(self, test):
		raise Exception('Unimplemented')

class CleanupEvent(Event):
	pass

class Player(KilledEvent):
	curl='no'
	def killed_command(self, test):
		test.clients.append({'delay': self.delay, 'host': self.host})
		return 'export HTTPLIVE_ALGORITHM={0} HTTPLIVE_CURL={3} ; /vagrant/code/vlc/vlc -I "dummy" -V "dummy" -A "dummy" "{1}" >$LOGDIR/{2}_vlc.log 2>$LOGDIR/{2}_vlc.err'.format(self.algo.upper(), self.url, self.host, self.curl)

class CwndLogger(KilledEvent):
	def killed_command(self, test):
		return '/vagrant/code/tcpprobe_helper.sh 3000 &>$LOGDIR/cwnd.log'

class RouterBufferLogger(KilledEvent):
	def killed_command(self, test):
		return '/vagrant/code/tc_helper.sh watch_buffer_size &>$LOGDIR/{0}_buffer.log'.format(self.host)

class TcpDump(KilledEvent):
	snaplen=96
	def killed_command(self, test):
		return 'sudo tcpdump -tt -v -i{1} -s{2} -w $LOGDIR/dump_{0}_{1}.pcap &>$LOGDIR/dump_{0}_{1}.log'.format(self.host, self.iface, self.snaplen)

class BwChange(Event):
	buffer_size=200
	rtt=0
	host='bandwidth'
	def commands(self, test):
		test.bw_profile[self.delay] = bw_convert(self.bw)
		test.buffer_profile[self.delay] = router_buffer_convert(self.buffer_size, self.bw, self.rtt)
		if test.aqm_algorithm == 'droptail':
			return '{0} {1} /vagrant/code/tc_helper.sh set_bw {2} {3} {4} 2>&1'.format(self.host, self.delay, self.bw, self.buffer_size, self.rtt)
		else:
			return '{0} {1} /vagrant/code/tc_helper.sh set_bw_aqm {5} {2} {3} {4} 2>&1'.format(self.host, self.delay, self.bw, self.buffer_size, self.rtt, test.aqm_algorithm)

class TrafficControlCleanup(CleanupEvent):
	def commands(self, test):
		return '{0} {1} /vagrant/code/tc_helper.sh destroy 2>&1'.format(self.host, self.delay)

class DelayChange(Event):
	packet_delay='200ms'
	host='delay'
	def commands(self, test):
		test.delay_profile[self.delay] = delay_convert(self.packet_delay)
		return '{0} {1} /vagrant/code/tc_helper.sh set_delay {2} 2>&1'.format(self.host, self.delay, self.packet_delay)
