import sys, itertools
from pylibs.test import Test, Player, BwChange, DelayChange, TcpDump
from pylibs.generic import PlainObject

server_url = 'http://192.168.100.10:3000/static'
bigbuckbunny8_url = server_url + '/bbb8/play_size.m3u8' # rates: 350k 470k 630k 845k 1130k 1520k 2040k 2750k, duration (s): ~600

settings = PlainObject()
settings.video_label = 'bbb8'
settings.video_url = bigbuckbunny8_url
settings.kill_after = 700
settings.rtt = ('20ms', '80ms')
settings.rtt_zfill = 4
settings.buffer_size = ('25%', '50%', '100%', '600%')
settings.buffer_size_zfill = 4
settings.fairshare = range(600, 3001, 300)
settings.aqm = ('droptail', 'ared', 'codel')
settings.clients = (1, 2, 3)
settings.algorithms = ('classic-119', 'bba2', 'bba3')
settings.curl = ('yes', 'bandwidth')

def get_curl_label(curl):
	if curl == 'yes':
		return 'keepalive'
	if curl == 'bandwidth':
		return 'keepalive_est'
	return 'close'

def get_algocurl_tuples(algorithms, curl_tuple):
	tuples = []
	for curl in curl_tuple:
		for algo in algorithms:
			if algo.startswith('bba') and curl == 'yes':
				tuples.append((algo, 'bandwidth'))
				continue
			tuples.append((algo, curl))
	return set(tuples)

def add_tcpdump(t):
	t.add_event(TcpDump(host='bandwidth', iface='eth1'))
	t.add_event(TcpDump(host='bandwidth', iface='eth2'))

# for buffer_size in settings.buffer_size:
# 	for rtt in settings.rtt:
# 		for (algo, curl) in get_algocurl_tuples(settings.algorithms, settings.curl):
# 			for n_clients in settings.clients:

if __name__ == "__main__":
	for (buffer_size, rtt, (algo, curl), n_clients, aqm) in itertools.product(settings.buffer_size, settings.rtt, get_algocurl_tuples(settings.algorithms, settings.curl), settings.clients, settings.aqm):
		if (aqm == 'ared' or (algo == 'classic-119' and curl == 'yes')) and n_clients > 1:
			continue
		rtt_label = str(rtt).zfill(settings.rtt_zfill)
		buffer_size_label = str(buffer_size).zfill(settings.buffer_size_zfill)

		#constant
		collection = 'constant_{}_{}_{}_{}BDP_{}'.format(n_clients, settings.video_label, rtt_label, buffer_size_label, aqm)
		num = 1
		for bw_kbits in settings.fairshare:
			bw = str(bw_kbits*n_clients)+'kbit'
			bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
			t = Test(name='c{:02d}_{}_{}_{}_{}_{}'.format(num, n_clients, settings.video_label, bw, algo, get_curl_label(curl)), collection=collection, init_bw=bwchange, packet_delay=rtt, aqm_algorithm=aqm)
			t.add_event(TcpDump(host='bandwidth', iface='eth1'))
			t.add_event(TcpDump(host='bandwidth', iface='eth2'))
			for client_id in range(n_clients):
				player = Player(delay=1, host='client{}'.format(client_id), algo=algo, curl=curl, url=settings.video_url, kill_after=settings.kill_after)
				t.add_event(player)
			t.generate_schedule()
			num += 1

		#variable
		bandwidths_coll = [ # actually: fairshare - it will be multiplied by the number of clients
			{0: 4000000, 120: 1000000, 240: 4000000, 360: 600000, 480: 4000000},
			{0: 4000000, 100: 2800000, 200: 1500000, 300: 1000000, 400: 600000, 500: 4000000},
		]
		collection = 'variable_{}_{}_{}_{}BDP_{}'.format(n_clients, settings.video_label, rtt_label, buffer_size_label, aqm)
		num = 1
		for bandwidths in bandwidths_coll:
			t = Test(name='v{:02d}_{}_{}_{}_{}'.format(num, n_clients, settings.video_label, algo, get_curl_label(curl)), collection=collection, packet_delay=rtt, aqm_algorithm=aqm)
			for d, bw in bandwidths.iteritems():
				t.add_event(BwChange(delay=d, bw=bw*n_clients, buffer_size=buffer_size, rtt=rtt))
			t.add_event(TcpDump(host='bandwidth', iface='eth1'))
			t.add_event(TcpDump(host='bandwidth', iface='eth2'))
			for client_id in range(n_clients):
				player = Player(delay=1, host='client{}'.format(client_id), algo=algo, curl=curl, url=settings.video_url, kill_after=settings.kill_after)
				t.add_event(player)
			t.generate_schedule()
			num += 1
