from pylibs.test import Test, Player, BwChange, DelayChange

server_url = 'http://192.168.100.10:3000/static'
bipbop_url = server_url + '/bb/bipbop_4x3_variant_onlyvideo.m3u8'
tearsofsteel_url = server_url + '/ts/vM7nH0Kl.m3u8'
bigbuckbunny_url = server_url + '/bbb/bigbuckbunny.m3u8'

if __name__ == "__main__":
	algorithms = ('classic', 'bba0')
	bandwidths = ('300kbit', '650kbit', '950kbit', '1mbit', '2mbit', '100mbit')
	delay = '200ms'
	buffer_size = 200
	
	collection = 'constant_single_{0}_{1}p'.format(delay, buffer_size)
	for algo in algorithms:
		player = Player(delay=1, host='client0', algo=algo, url=bipbop_url, kill_after=2330)
		num = 1
		for bw in bandwidths:
			bwchange = BwChange(bw=bw, buffer_size=buffer_size)
			t = Test(name='c{0:02d}_bipbop_{1}_{2}'.format(num, bw, algo), collection=collection, player=player, init_bw=bwchange)
			t.add_event(DelayChange(packet_delay=delay))
			t.generate_schedule()
			num += 1

