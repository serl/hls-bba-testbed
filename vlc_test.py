import sys
from pylibs.test import Test, Player, BwChange, DelayChange, TcpDump

server_url = 'http://192.168.100.10:3000/static'
bipbop_url = server_url + '/bb/bipbop_4x3_variant_onlyvideo_size.m3u8' # rates: 232370 649879 991714 1927833, duration (s): ~1800
tearsofsteel_url = server_url + '/ts/vM7nH0Kl_size.m3u8' # rates: 380000 670000 1710000 3400000, duration (s): ~734
bigbuckbunny_url = server_url + '/bbb/bigbuckbunny_size.m3u8' # rates: 290400 510400 1170400 2820400, duration (s): ~597
bigbuckbunny8_url = server_url + '/bbb8/play_size.m3u8' # rates: 350k 470k 630k 845k 1130k 1520k 2040k 2750k, duration (s): ~600

def curl_signature(curl):
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
	return tuples

def add_tcpdump(t):
	t.add_event(TcpDump(host='bandwidth', iface='eth1'))
	t.add_event(TcpDump(host='bandwidth', iface='eth2'))

if __name__ == "__main__" and 'const' in sys.argv[1:]:
	for buffer_size in (200, '2%', '5%', '10%', '25%', '50%', '100%'):
		for rtt in ('200ms', '100ms', '400ms'):
			algorithms = ('classic-13', 'bba0', 'bba1')
			bandwidths = ('400kbit', '500kbit', '600kbit', '700kbit', '800kbit', '900kbit', '1000kbit', '1100kbit', '1200kbit', '1300kbit', '1400kbit', '1500kbit', '1600kbit', '1700kbit', '1800kbit', '1900kbit', '2000kbit', '2100kbit', '2200kbit', '2300kbit', '2400kbit', '2500kbit', '2600kbit', '2700kbit', '2800kbit', '2900kbit', '3000kbit')
			collection = 'constant_single_bbb8_{0}_{1}p'.format(rtt, buffer_size)
			for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
				player = Player(delay=1, host='client0', algo=algo, curl=curl, url=bigbuckbunny8_url, kill_after=700)
				num = 1
				for bw in bandwidths:
					bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
					t = Test(name='c{0:02d}_single_bbb8_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, player=player, init_bw=bwchange, packet_delay=rtt)
					add_tcpdump(t)
					t.generate_schedule()
					num += 1

			algorithms = ('classic-13', 'bba0', 'bba1')
			bandwidths = ('800kbit', '1000kbit', '1200kbit', '1400kbit', '1600kbit', '1800kbit', '2000kbit', '2200kbit', '2400kbit', '2600kbit', '2800kbit', '3000kbit', '3200kbit', '3400kbit', '3600kbit', '3800kbit', '4000kbit', '4200kbit', '4400kbit', '4600kbit', '4800kbit', '5000kbit', '5200kbit', '5400kbit', '5600kbit', '5800kbit', '6000kbit')
			collection = 'constant_two_con_bbb8_{0}_{1}p'.format(rtt, buffer_size)
			for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
				player1 = Player(delay=1, host='client0', algo=algo, curl=curl, url=bigbuckbunny8_url, kill_after=700)
				player2 = Player(delay=1, host='client1', algo=algo, curl=curl, url=bigbuckbunny8_url, kill_after=700)
				num = 1
				for bw in bandwidths:
					bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
					t = Test(name='c{0:02d}_two_con_bbb8_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, init_bw=bwchange, packet_delay=rtt)
					t.add_event(player1)
					t.add_event(player2)
					add_tcpdump(t)
					t.generate_schedule()
					num += 1


			algorithms = ('classic-2', 'bba0', 'bba1')
			bandwidths = ('300kbit', '400kbit', '500kbit', '600kbit', '700kbit', '800kbit', '900kbit', '1000kbit', '1100kbit', '1200kbit', '1300kbit', '1400kbit', '1500kbit', '1600kbit', '1700kbit', '1800kbit', '1900kbit', '2000kbit', '2100kbit', '2200kbit')
			collection = 'constant_single_bipbop_{0}_{1}p'.format(rtt, buffer_size)
			for (algo, curl) in get_algocurl_tuples(algorithms, ('no', 'yes', 'bandwidth')):
				player = Player(delay=1, host='client0', algo=algo, curl=curl, url=bipbop_url, kill_after=2000)
				num = 1
				for bw in bandwidths:
					bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
					t = Test(name='c{0:02d}_bipbop_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, player=player, init_bw=bwchange, packet_delay=rtt)
					add_tcpdump(t)
					t.generate_schedule()
					num += 1

			algorithms = ('classic-2', 'bba0', 'bba1')
			bandwidths = ('600kbit', '800kbit', '1000kbit', '1200kbit', '1400kbit', '1600kbit', '1800kbit', '2000kbit', '2200kbit', '2400kbit', '2600kbit', '2800kbit', '3000kbit', '3200kbit', '3400kbit', '3600kbit', '3800kbit', '4000kbit', '4200kbit', '4400kbit')
			collection = 'constant_two_con_bipbop_{0}_{1}p'.format(rtt, buffer_size)
			for (algo, curl) in get_algocurl_tuples(algorithms, ('no', 'yes', 'bandwidth')):
				player1 = Player(delay=1, host='client0', algo=algo, curl=curl, url=bipbop_url, kill_after=2000)
				player2 = Player(delay=1, host='client1', algo=algo, curl=curl, url=bipbop_url, kill_after=2000)
				num = 1
				for bw in bandwidths:
					bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
					t = Test(name='c{0:02d}_two_con_bipbop_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, init_bw=bwchange, packet_delay=rtt)
					t.add_event(player1)
					t.add_event(player2)
					add_tcpdump(t)
					t.generate_schedule()
					num += 1


if __name__ == "__main__" and 'var' in sys.argv[1:]:
	rtt = '200ms'
	buffer_size = 200
	algorithms = ('classic-13', 'bba0', 'bba1')
	bandwidths_coll = [ # actually: fairshare - it will be multiplied by 2 for two-clients tests
		{0: 4000000, 120: 1000000, 240: 4000000, 360: 600000, 480: 4000000},
		{0: 4000000, 100: 2800000, 200: 1500000, 300: 1000000, 400: 600000, 500: 4000000},
	]
	num = 1
	for bandwidths in bandwidths_coll:
		collection = 'variable_single_bbb8_{0}_{1}p'.format(rtt, buffer_size)
		for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
			player = Player(delay=1, host='client0', algo=algo, curl=curl, url=bigbuckbunny8_url, kill_after=700)

			t = Test(name='v{0:02d}_single_bbb8_{1}_{2}'.format(num, algo, curl_signature(curl)), collection=collection, player=player, packet_delay=rtt)
			for d, bw in bandwidths.iteritems():
				t.add_event(BwChange(delay=d, bw=bw, buffer_size=buffer_size, rtt=rtt))
			add_tcpdump(t)
			t.generate_schedule()

		collection = 'variable_two_con_bbb8_{0}_{1}p'.format(rtt, buffer_size)
		for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
			player1 = Player(delay=1, host='client0', algo=algo, curl=curl, url=bigbuckbunny8_url, kill_after=700)
			player2 = Player(delay=1, host='client1', algo=algo, curl=curl, url=bigbuckbunny8_url, kill_after=700)

			t = Test(name='v{0:02d}_two_con_bbb8_{1}_{2}'.format(num, algo, curl_signature(curl)), collection=collection, packet_delay=rtt)
			t.add_event(player1)
			t.add_event(player2)
			for d, bw in bandwidths.iteritems():
				t.add_event(BwChange(delay=d, bw=bw*2, buffer_size=buffer_size, rtt=rtt))
			add_tcpdump(t)
			t.generate_schedule()

		num += 1

sys.exit()

if False:
	rtt = '200ms'
	buffer_size = 200
	algorithms = ('classic', 'bba0')
	bandwidths = ('650kbit', '950kbit', '1mbit', '1.5mbit', '2mbit', '2.5mbit', '3mbit', '3.5mbit', '4mbit', '5mbit', '10mbit')
	collection = 'constant_two_del_bipbop_{0}_{1}p'.format(rtt, buffer_size)
	for algo in algorithms:
		player1 = Player(delay=1, host='client0', algo=algo, url=bipbop_url, kill_after=2000)
		player2 = Player(delay=300, host='client1', algo=algo, url=bipbop_url, kill_after=2000)
		num = 1
		for bw in bandwidths:
			bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
			t = Test(name='c{0:02d}_two_del_bipbop_{1}_{2}'.format(num, bw, algo), collection=collection, init_bw=bwchange, packet_delay=rtt)
			t.add_event(player1)
			t.add_event(player2)
			add_tcpdump(t)
			t.generate_schedule()
			num += 1

	algorithms = ('classic', 'bba0')
	bandwidths_coll = [
		{0: '5mbit', 200: '2mbit', 500: '5mbit', 800: '1mbit', 1100: '5mbit'},
		{0: '5mbit', 250: '4mbit', 500: '3mbit', 750: '2mbit', 1000: '1mbit', 1250: '5mbit'},
	]
	num = 1
	for bandwidths in bandwidths_coll:
		collection = 'variable_single_bipbop_{0}_{1}p'.format(rtt, buffer_size)
		for algo in algorithms:
			player = Player(delay=1, host='client0', algo=algo, url=bipbop_url, kill_after=2000)

			t = Test(name='v{0:02d}_bipbop_{1}'.format(num, algo), collection=collection, player=player, packet_delay=rtt)
			for d, bw in bandwidths.iteritems():
				t.add_event(BwChange(delay=d, bw=bw, buffer_size=buffer_size, rtt=rtt))
			add_tcpdump(t)
			t.generate_schedule()

		collection = 'variable_two_con_bipbop_{0}_{1}p'.format(rtt, buffer_size)
		for algo in algorithms:
			player1 = Player(delay=1, host='client0', algo=algo, url=bipbop_url, kill_after=2000)
			player2 = Player(delay=1, host='client1', algo=algo, url=bipbop_url, kill_after=2000)

			t = Test(name='v{0:02d}_two_con_bipbop_{1}'.format(num, algo), collection=collection, packet_delay=rtt)
			t.add_event(player1)
			t.add_event(player2)
			for d, bw in bandwidths.iteritems():
				t.add_event(BwChange(delay=d, bw=bw, buffer_size=buffer_size, rtt=rtt))
			add_tcpdump(t)
			t.generate_schedule()

		collection = 'variable_two_del_bipbop_{0}_{1}p'.format(rtt, buffer_size)
		for algo in algorithms:
			player1 = Player(delay=1, host='client0', algo=algo, url=bipbop_url, kill_after=2000)
			player2 = Player(delay=300, host='client1', algo=algo, url=bipbop_url, kill_after=2000)

			t = Test(name='v{0:02d}_two_del_bipbop_{1}'.format(num, algo), collection=collection, packet_delay=rtt)
			t.add_event(player1)
			t.add_event(player2)
			for d, bw in bandwidths.iteritems():
				t.add_event(BwChange(delay=d, bw=bw, buffer_size=buffer_size, rtt=rtt))
			add_tcpdump(t)
			t.generate_schedule()

		num += 1

