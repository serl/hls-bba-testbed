import sys
from pylibs.test import Test, Player, BwChange, DelayChange

server_url = 'http://192.168.100.10:3000/static'
bipbop_url = server_url + '/bb/bipbop_4x3_variant_onlyvideo_size.m3u8' # rates: 232370 649879 991714 1927833, duration (s): ~1800
tearsofsteel_url = server_url + '/ts/vM7nH0Kl_size.m3u8' # rates: 380000 670000 1710000 3400000, duration (s): ~734
bigbuckbunny_url = server_url + '/bbb/bigbuckbunny_size.m3u8' # rates: 290400 510400 1170400 2820400, duration (s): ~597
bigbuckbunny8_url = server_url + '/bbb8/play_size.m3u8' # rates: 350k 470k 630k 845k 1130k 1520k 2040k 2750k, duration (s): ~600


if __name__ == "__main__":
	delay = '200ms'
	buffer_size = 200

	algorithms = ('classic-13', 'bba0', 'bba1')
	bandwidths = ('400kbit', '500kbit', '600kbit', '700kbit', '800kbit', '900kbit', '1000kbit', '1100kbit', '1200kbit', '1300kbit', '1400kbit', '1500kbit', '1600kbit', '1700kbit', '1800kbit', '1900kbit', '2000kbit', '2100kbit', '2200kbit', '2300kbit', '2400kbit', '2500kbit', '2600kbit', '2700kbit', '2800kbit', '2900kbit', '3000kbit')
	collection = 'constant_single_bbb8_{0}_{1}p'.format(delay, buffer_size)
	for curl in (False, True):
		for algo in algorithms:
			player = Player(delay=1, host='client0', algo=algo, curl=curl, url=bigbuckbunny8_url, kill_after=700)
			num = 1
			for bw in bandwidths:
				bwchange = BwChange(bw=bw, buffer_size=buffer_size)
				t = Test(name='c{0:02d}_single_bbb8_{1}_{2}_{3}'.format(num, bw, algo, 'keepalive' if curl else 'close'), collection=collection, player=player, init_bw=bwchange, packet_delay=delay)
				t.generate_schedule()
				num += 1

	algorithms = ('classic-13', 'bba0')
	bandwidths = ('800kbit', '1000kbit', '1200kbit', '1400kbit', '1600kbit', '1800kbit', '2000kbit', '2200kbit', '2400kbit', '2600kbit', '2800kbit', '3000kbit', '3200kbit', '3400kbit', '3600kbit', '3800kbit', '4000kbit', '4200kbit', '4400kbit', '4600kbit', '4800kbit', '5000kbit', '5200kbit', '5400kbit', '5600kbit', '5800kbit', '6000kbit')
	collection = 'constant_two_con_bbb8_{0}_{1}p'.format(delay, buffer_size)
	for curl in (False, True):
		for algo in algorithms:
			player1 = Player(delay=1, host='client0', algo=algo, curl=curl, url=bigbuckbunny8_url, kill_after=700)
			player2 = Player(delay=1, host='client1', algo=algo, curl=curl, url=bigbuckbunny8_url, kill_after=700)
			num = 1
			for bw in bandwidths:
				bwchange = BwChange(bw=bw, buffer_size=buffer_size)
				t = Test(name='c{0:02d}_two_con_bbb8_{1}_{2}_{3}'.format(num, bw, algo, 'keepalive' if curl else 'close'), collection=collection, init_bw=bwchange, packet_delay=delay)
				t.add_event(player1)
				t.add_event(player2)
				t.generate_schedule()
				num += 1


	algorithms = ('classic-2', 'bba0', 'bba1')
	bandwidths = ('300kbit', '400kbit', '500kbit', '600kbit', '700kbit', '800kbit', '900kbit', '1000kbit', '1100kbit', '1200kbit', '1300kbit', '1400kbit', '1500kbit', '1600kbit', '1700kbit', '1800kbit', '1900kbit', '2000kbit', '2100kbit', '2200kbit')
	collection = 'constant_single_bipbop_{0}_{1}p'.format(delay, buffer_size)
	for curl in (False, True):
		for algo in algorithms:
			player = Player(delay=1, host='client0', algo=algo, curl=curl, url=bipbop_url, kill_after=2000)
			num = 1
			for bw in bandwidths:
				bwchange = BwChange(bw=bw, buffer_size=buffer_size)
				t = Test(name='c{0:02d}_bipbop_{1}_{2}_{3}'.format(num, bw, algo, 'keepalive' if curl else 'close'), collection=collection, player=player, init_bw=bwchange, packet_delay=delay)
				t.generate_schedule()
				num += 1

	algorithms = ('classic-2', 'bba0')
	bandwidths = ('600kbit', '800kbit', '1000kbit', '1200kbit', '1400kbit', '1600kbit', '1800kbit', '2000kbit', '2200kbit', '2400kbit', '2600kbit', '2800kbit', '3000kbit', '3200kbit', '3400kbit', '3600kbit', '3800kbit', '4000kbit', '4200kbit', '4400kbit')
	collection = 'constant_two_con_bipbop_{0}_{1}p'.format(delay, buffer_size)
	for curl in (False, True):
		for algo in algorithms:
			player1 = Player(delay=1, host='client0', algo=algo, curl=curl, url=bipbop_url, kill_after=2000)
			player2 = Player(delay=1, host='client1', algo=algo, curl=curl, url=bipbop_url, kill_after=2000)
			num = 1
			for bw in bandwidths:
				bwchange = BwChange(bw=bw, buffer_size=buffer_size)
				t = Test(name='c{0:02d}_two_con_bipbop_{1}_{2}_{3}'.format(num, bw, algo, 'keepalive' if curl else 'close'), collection=collection, init_bw=bwchange, packet_delay=delay)
				t.add_event(player1)
				t.add_event(player2)
				t.generate_schedule()
				num += 1


	sys.exit()

	algorithms = ('classic', 'bba0')
	bandwidths = ('650kbit', '950kbit', '1mbit', '1.5mbit', '2mbit', '2.5mbit', '3mbit', '3.5mbit', '4mbit', '5mbit', '10mbit')
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

