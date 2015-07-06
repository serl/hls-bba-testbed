from pylibs.test import Test, Player, BwChange, DelayChange

server_url = 'http://192.168.100.10:3000/static'
bipbop_url = server_url + '/bb/bipbop_4x3_variant_onlyvideo.m3u8' # rates: 232370 649879 991714 1927833, duration (s): ~1800
tearsofsteel_url = server_url + '/ts/vM7nH0Kl.m3u8' # rates: 380000 670000 1710000 3400000, duration (s): ~734
bigbuckbunny_url = server_url + '/bbb/bigbuckbunny.m3u8' # rates: 290400 510400 1170400 2820400, duration (s): ~597


if __name__ == "__main__":
	delay = '200ms'
	buffer_size = 200

	algorithms = ('classic', 'bba0')
	bandwidths = ('300kbit', '650kbit', '950kbit', '1mbit', '1.5mbit', '2mbit', '5mbit', '10mbit')
	collection = 'constant_single_bipbop_{0}_{1}p'.format(delay, buffer_size)
	for algo in algorithms:
		player = Player(delay=1, host='client0', algo=algo, url=bipbop_url, kill_after=2330)
		num = 1
		for bw in bandwidths:
			bwchange = BwChange(bw=bw, buffer_size=buffer_size)
			t = Test(name='c{0:02d}_bipbop_{1}_{2}'.format(num, bw, algo), collection=collection, player=player, init_bw=bwchange, packet_delay=delay)
			t.generate_schedule()
			num += 1

	#bandwidths = ('950kbit', '1mbit', '1.5mbit', '3mbit', '5mbit', '10mbit')
	#collection = 'constant_single_tearsofsteel_{0}_{1}p'.format(delay, buffer_size)
	#for algo in algorithms:
	#	player = Player(delay=1, host='client0', algo=algo, url=tearsofsteel_url, kill_after=1130)
	#	num = 1
	#	for bw in bandwidths:
	#		bwchange = BwChange(bw=bw, buffer_size=buffer_size)
	#		t = Test(name='c{0:02d}_tearsofsteel_{1}_{2}'.format(num, bw, algo), collection=collection, player=player, init_bw=bwchange, packet_delay=delay)
	#		t.generate_schedule()
	#		num += 1

	algorithms = ('classic', 'classic-2', 'bba0')
	bandwidths = ('650kbit', '950kbit', '1mbit', '1.5mbit', '2mbit', '2.5mbit', '3mbit', '3.5mbit', '4mbit', '5mbit', '10mbit')
	collection = 'constant_two_con_bipbop_{0}_{1}p'.format(delay, buffer_size)
	for algo in algorithms:
		player1 = Player(delay=1, host='client0', algo=algo, url=bipbop_url, kill_after=2330)
		player2 = Player(delay=1, host='client1', algo=algo, url=bipbop_url, kill_after=2330)
		num = 1
		for bw in bandwidths:
			bwchange = BwChange(bw=bw, buffer_size=buffer_size)
			t = Test(name='c{0:02d}_two_con_bipbop_{1}_{2}'.format(num, bw, algo), collection=collection, init_bw=bwchange, packet_delay=delay)
			t.add_event(player1)
			t.add_event(player2)
			t.generate_schedule()
			num += 1

	algorithms = ('classic', 'bba0')
	collection = 'constant_two_del_bipbop_{0}_{1}p'.format(delay, buffer_size)
	for algo in algorithms:
		player1 = Player(delay=1, host='client0', algo=algo, url=bipbop_url, kill_after=2330)
		player2 = Player(delay=300, host='client1', algo=algo, url=bipbop_url, kill_after=2330)
		num = 1
		for bw in bandwidths:
			bwchange = BwChange(bw=bw, buffer_size=buffer_size)
			t = Test(name='c{0:02d}_two_del_bipbop_{1}_{2}'.format(num, bw, algo), collection=collection, init_bw=bwchange, packet_delay=delay)
			t.add_event(player1)
			t.add_event(player2)
			t.generate_schedule()
			num += 1

	algorithms = ('classic', 'bba0')
	bandwidths_coll = [
		{0: '5mbit', 200: '2mbit', 500: '5mbit', 800: '1mbit', 1100: '5mbit'},
		{0: '5mbit', 250: '4mbit', 500: '3mbit', 750: '2mbit', 1000: '1mbit', 1250: '5mbit'},
	]
	num = 1
	for bandwidths in bandwidths_coll:
		collection = 'variable_single_bipbop_{0}_{1}p'.format(delay, buffer_size)
		for algo in algorithms:
			player = Player(delay=1, host='client0', algo=algo, url=bipbop_url, kill_after=2330)

			t = Test(name='v{0:02d}_bipbop_{1}'.format(num, algo), collection=collection, player=player, packet_delay=delay)
			for d, bw in bandwidths.iteritems():
				t.add_event(BwChange(delay=d, bw=bw, buffer_size=buffer_size))
			t.generate_schedule()

		collection = 'variable_two_con_bipbop_{0}_{1}p'.format(delay, buffer_size)
		for algo in algorithms:
			player1 = Player(delay=1, host='client0', algo=algo, url=bipbop_url, kill_after=2330)
			player2 = Player(delay=1, host='client1', algo=algo, url=bipbop_url, kill_after=2330)

			t = Test(name='v{0:02d}_two_con_bipbop_{1}'.format(num, algo), collection=collection, packet_delay=delay)
			t.add_event(player1)
			t.add_event(player2)
			for d, bw in bandwidths.iteritems():
				t.add_event(BwChange(delay=d, bw=bw, buffer_size=buffer_size))
			t.generate_schedule()

		collection = 'variable_two_del_bipbop_{0}_{1}p'.format(delay, buffer_size)
		for algo in algorithms:
			player1 = Player(delay=1, host='client0', algo=algo, url=bipbop_url, kill_after=2330)
			player2 = Player(delay=300, host='client1', algo=algo, url=bipbop_url, kill_after=2330)

			t = Test(name='v{0:02d}_two_del_bipbop_{1}'.format(num, algo), collection=collection, packet_delay=delay)
			t.add_event(player1)
			t.add_event(player2)
			for d, bw in bandwidths.iteritems():
				t.add_event(BwChange(delay=d, bw=bw, buffer_size=buffer_size))
			t.generate_schedule()

		num += 1

