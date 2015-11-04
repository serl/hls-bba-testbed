import sys
from pylibs.test import Test, Player, BwChange, DelayChange, TcpDump

server_url = 'http://192.168.100.10:3000/static'
bipbop_url = server_url + '/bb/bipbop_4x3_variant_onlyvideo_size.m3u8' # rates: 232370 649879 991714 1927833, duration (s): ~1800
tearsofsteel_url = server_url + '/ts/vM7nH0Kl_size.m3u8' # rates: 380000 670000 1710000 3400000, duration (s): ~734
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
	return set(tuples)

def add_tcpdump(t):
	t.add_event(TcpDump(host='bandwidth', iface='eth1'))
	t.add_event(TcpDump(host='bandwidth', iface='eth2'))

if __name__ == "__main__" and 'const' in sys.argv[1:]:

	video_url = bigbuckbunny8_url
	kill_after = 700
	algorithms = ('classic-13', 'classic-119', 'bba0', 'bba1', 'bba2', 'bba3', 'bba3-a')
	fairshares_kbits = range(400, 3001, 100)
	for buffer_size in (200, '10%', '25%', '50%', '100%'):
		for rtt in ('200ms', '100ms', '400ms'):
			if buffer_size != 200 and rtt != '200ms':
				continue # with percentage of bdp use only 200ms RTT

			collection = 'constant_single_bbb8_{0}_{1}p'.format(rtt, buffer_size)
			for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
				player = Player(delay=1, host='client0', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
				num = 1
				for bw_kbits in fairshares_kbits:
					bw = str(bw_kbits)+'kbit'
					bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
					t = Test(name='c{0:02d}_single_bbb8_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, player=player, init_bw=bwchange, packet_delay=rtt)
					add_tcpdump(t)
					t.generate_schedule()
					num += 1

			collection = 'constant_two_con_bbb8_{0}_{1}p'.format(rtt, buffer_size)
			for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
				player1 = Player(delay=1, host='client0', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
				player2 = Player(delay=1, host='client1', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
				num = 1
				for bw_kbits in fairshares_kbits:
					bw = str(bw_kbits*2)+'kbit'
					bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
					t = Test(name='c{0:02d}_two_con_bbb8_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, init_bw=bwchange, packet_delay=rtt)
					t.add_event(player1)
					t.add_event(player2)
					add_tcpdump(t)
					t.generate_schedule()
					num += 1

	buffer_size = '100%'
	rtt = '200ms'
	collection = 'constant_three_con_bbb8_{0}_{1}p'.format(rtt, buffer_size)
	for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
		player1 = Player(delay=1, host='client0', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
		player2 = Player(delay=1, host='client1', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
		player3 = Player(delay=1, host='client2', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
		num = 1
		for bw_kbits in fairshares_kbits:
			bw = str(bw_kbits*3)+'kbit'
			bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
			t = Test(name='c{0:02d}_three_con_bbb8_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, init_bw=bwchange, packet_delay=rtt)
			t.add_event(player1)
			t.add_event(player2)
			t.add_event(player3)
			add_tcpdump(t)
			t.generate_schedule()
			num += 1

	video_url = bipbop_url
	kill_after = 2000
	algorithms = ('classic-2', 'classic-23', 'bba0', 'bba1', 'bba2', 'bba3', 'bba3-a')
	fairshares_kbits = range(300, 2201, 100)
	buffer_size = '200'
	rtt = '200ms'

	collection = 'constant_single_bipbop_{0}_{1}p'.format(rtt, buffer_size)
	for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
		player = Player(delay=1, host='client0', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
		num = 1
		for bw_kbits in fairshares_kbits:
			bw = str(bw_kbits)+'kbit'
			bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
			t = Test(name='c{0:02d}_single_bipbop_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, player=player, init_bw=bwchange, packet_delay=rtt)
			add_tcpdump(t)
			t.generate_schedule()
			num += 1

	collection = 'constant_two_con_bipbop_{0}_{1}p'.format(rtt, buffer_size)
	for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
		player1 = Player(delay=1, host='client0', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
		player2 = Player(delay=1, host='client1', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
		num = 1
		for bw_kbits in fairshares_kbits:
			bw = str(bw_kbits*2)+'kbit'
			bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
			t = Test(name='c{0:02d}_two_con_bipbop_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, init_bw=bwchange, packet_delay=rtt)
			t.add_event(player1)
			t.add_event(player2)
			add_tcpdump(t)
			t.generate_schedule()
			num += 1


if __name__ == "__main__" and 'aqm' in sys.argv[1:]:

	for aqm_algorithm in ('ared', 'codel'):
		video_url = bigbuckbunny8_url
		kill_after = 700
		algorithms = ('classic-13', 'classic-119', 'bba0', 'bba1', 'bba2', 'bba3', 'bba3-a')
		fairshares_kbits = range(2000, 3001, 1000)
		for buffer_size in (200, '10%', '25%', '50%', '100%'):
			for rtt in ('200ms', '100ms', '400ms'):
				if buffer_size != 200 and rtt != '200ms':
					continue # with percentage of bdp use only 200ms RTT

				collection = 'constant_single_bbb8_{0}_{1}p_{2}'.format(rtt, buffer_size, aqm_algorithm)
				for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
					player = Player(delay=1, host='client0', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
					num = 1
					for bw_kbits in fairshares_kbits:
						bw = str(bw_kbits)+'kbit'
						bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
						t = Test(name='c{0:02d}_single_bbb8_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, player=player, init_bw=bwchange, packet_delay=rtt, aqm_algorithm=aqm_algorithm)
						add_tcpdump(t)
						t.generate_schedule()
						num += 1

				collection = 'constant_two_con_bbb8_{0}_{1}p_{2}'.format(rtt, buffer_size, aqm_algorithm)
				for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
					player1 = Player(delay=1, host='client0', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
					player2 = Player(delay=1, host='client1', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
					num = 1
					for bw_kbits in fairshares_kbits:
						bw = str(bw_kbits*2)+'kbit'
						bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
						t = Test(name='c{0:02d}_two_con_bbb8_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, init_bw=bwchange, packet_delay=rtt, aqm_algorithm=aqm_algorithm)
						t.add_event(player1)
						t.add_event(player2)
						add_tcpdump(t)
						t.generate_schedule()
						num += 1

		buffer_size = '100%'
		rtt = '200ms'
		collection = 'constant_three_con_bbb8_{0}_{1}p_{2}'.format(rtt, buffer_size, aqm_algorithm)
		for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
			player1 = Player(delay=1, host='client0', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
			player2 = Player(delay=1, host='client1', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
			player3 = Player(delay=1, host='client2', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
			num = 1
			for bw_kbits in fairshares_kbits:
				bw = str(bw_kbits*3)+'kbit'
				bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
				t = Test(name='c{0:02d}_three_con_bbb8_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, init_bw=bwchange, packet_delay=rtt, aqm_algorithm=aqm_algorithm)
				t.add_event(player1)
				t.add_event(player2)
				t.add_event(player3)
				add_tcpdump(t)
				t.generate_schedule()
				num += 1

		video_url = bipbop_url
		kill_after = 2000
		algorithms = ('classic-2', 'classic-23', 'bba0', 'bba1', 'bba2', 'bba3', 'bba3-a')
		fairshares_kbits = (2200,)
		buffer_size = '200'
		rtt = '200ms'

		collection = 'constant_single_bipbop_{0}_{1}p_{2}'.format(rtt, buffer_size, aqm_algorithm)
		for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
			player = Player(delay=1, host='client0', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
			num = 1
			for bw_kbits in fairshares_kbits:
				bw = str(bw_kbits)+'kbit'
				bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
				t = Test(name='c{0:02d}_single_bipbop_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, player=player, init_bw=bwchange, packet_delay=rtt, aqm_algorithm=aqm_algorithm)
				add_tcpdump(t)
				t.generate_schedule()
				num += 1

		collection = 'constant_two_con_bipbop_{0}_{1}p_{2}'.format(rtt, buffer_size, aqm_algorithm)
		for (algo, curl) in get_algocurl_tuples(algorithms, ('yes', 'bandwidth')):
			player1 = Player(delay=1, host='client0', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
			player2 = Player(delay=1, host='client1', algo=algo, curl=curl, url=video_url, kill_after=kill_after)
			num = 1
			for bw_kbits in fairshares_kbits:
				bw = str(bw_kbits*2)+'kbit'
				bwchange = BwChange(bw=bw, buffer_size=buffer_size, rtt=rtt)
				t = Test(name='c{0:02d}_two_con_bipbop_{1}_{2}_{3}'.format(num, bw, algo, curl_signature(curl)), collection=collection, init_bw=bwchange, packet_delay=rtt, aqm_algorithm=aqm_algorithm)
				t.add_event(player1)
				t.add_event(player2)
				add_tcpdump(t)
				t.generate_schedule()
				num += 1


if __name__ == "__main__" and 'var' in sys.argv[1:]:
	rtt = '200ms'
	buffer_size = 200
	algorithms = ('classic-13', 'classic-119', 'bba0', 'bba1', 'bba2', 'bba3', 'bba3-a')
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

