import os, re, json, errno, string, random

class Test(object):
	save_dir = 'tests'

	def __init__(self, name, collection='', player=None, init_bw=None, packet_delay=None, log_cwnd=True, log_routerbuffer=True):
		self._events = []
		self.name = name
		self.collection = collection
		self.bw_profile = {}
		self.clients = []
		self.log_cwnd = log_cwnd
		self.log_routerbuffer = log_routerbuffer

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

	def add_event(self, e):
		self._events.append(e)

	def generate_schedule(self, echo=False):
		last_moment = 2
		for evt in self._events:
			if KilledEvent in type(evt).__bases__ and 'kill_after' in evt.__dict__ and evt.kill_after > last_moment:
				last_moment = evt.kill_after + evt.delay
		for evt in self._events:
			if KilledEvent in type(evt).__bases__ and not 'kill_after' in evt.__dict__:
				evt.kill_after = last_moment - evt.delay

		events = sorted(self._events, key=lambda evt: evt.delay)
		scheduler_commands = '#eval LOGDIR=/vagrant/tests/'+self.collection+'/'+self.name+'\n'
		for evt in events:
			scheduler_commands += evt.commands() + '\n'
			evt.add_test_infos(self)
		scheduler_commands = '#SESSION' + json.dumps({'name': self.name, 'collection': self.collection, 'bwprofile': self.bw_profile, 'clients': self.clients}) + '\n' + scheduler_commands

		if echo:
			print scheduler_commands
		else:
			mkdir_p(os.path.join(self.save_dir, self.collection, self.name))
			with open(os.path.join(self.save_dir, self.collection, self.name, 'jobs.sched'), 'w') as f:
				f.write(scheduler_commands)

bw_re = re.compile('^(\d+(\.\d+)?)(\w*)$')
def bw_convert(bw): #read tc style, convert to bits/s (hope so)
	match = bw_re.match(bw)
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
	if unit == 'bps' or unit == '':
		return int(value*8)
	raise Exception('Malformed bandwidth, see tc docs.')

def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc:
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else: raise

class Event(object):
	delay=0
	def __init__(self, **kwds):
		self.__dict__.update(kwds)
	def commands(self):
		raise Exception('Not implemented')
	def add_test_infos(self, test):
		pass
	def __repr__(self):
		return repr(self.__dict__)

class KilledEvent(Event):
	def commands(self):
		if not 'kill_after' in self.__dict__:
			raise Exception('Missing kill_after in KilledEvent')
		rndstr = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
		up = '%s %d %s & echo $! >/tmp/pid_%s' % (self.host, self.delay, self.killed_command(), rndstr)
		down = '%s %d sudo kill -SIGTERM $(cat /tmp/pid_%s)' % (self.host, self.kill_after + self.delay, rndstr)
		return up + '\n' + down
	def killed_command(self):
		raise Exception('Unimplemented')
	
class Player(KilledEvent):
	def killed_command(self):
		return 'export HTTPLIVE_ALGORITHM=%s ; /vagrant/code/vlc/vlc -I "dummy" -V "dummy" -A "dummy" "%s" >$LOGDIR/%s_vlc.log' % (self.algo.upper(), self.url, self.host)
	def add_test_infos(self, test):
		test.clients.append({'delay': self.delay, 'host': self.host})

class CwndLogger(KilledEvent):
	def killed_command(self):
		return '/vagrant/code/tcpprobe_helper.sh 3000 &>$LOGDIR/cwnd.log'

class RouterBufferLogger(KilledEvent):
	def killed_command(self):
		return '/vagrant/code/tc_helper.sh watch_buffer_size &>$LOGDIR/{0}_buffer.log'.format(self.host)

class BwChange(Event):
	buffer_size=200
	host='bandwidth'
	def commands(self):
		return '%s %d /vagrant/code/tc_helper.sh set_bw %s %d' % (self.host, self.delay, self.bw, self.buffer_size)
	def add_test_infos(self, test):
		test.bw_profile[self.delay] = bw_convert(self.bw)

class DelayChange(Event):
	packet_delay='200ms'
	host='delay'
	def commands(self):
		return '%s %d /vagrant/code/tc_helper.sh set_delay %s' % (self.host, self.delay, self.packet_delay)

