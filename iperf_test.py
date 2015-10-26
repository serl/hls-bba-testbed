import sys, os, errno, json
from pylibs.generic import mkdir_p
from pylibs.test import router_buffer_convert

aqm_algorithms=('droptail', 'ared', 'codel')
delay="200ms"

tests = (
	#{ 'bw': '300kbit', 'buffersize': ('200%', '100%'), 'time': 300 },
	{ 'bw': '1mbit', 'buffersize': ('200', '200%', '100%', '50%'), 'time': 240 },
	{ 'bw': '5mbit', 'buffersize': ('200', '200%', '100%', '50%'), 'time': 120 },
	{ 'bw': '10mbit', 'buffersize': ('200', '200%', '100%', '50%'), 'time': 60 },
)

for aqm_algorithm in aqm_algorithms:
	for i, test in enumerate(tests):
		for buffersize in test['buffersize']:
			session_infos = { 'type': 'iperf', 'aqm_algorithm': aqm_algorithm, 'bandwidth': test['bw'], 'delay': delay, 'bandwidth_buffersize': router_buffer_convert(buffersize, test['bw'], delay), 'bandwidth_buffersize_description': buffersize }

			set_bw_command = 'set_bw_aqm {aqm_algorithm} {bandwidth} {bandwidth_buffersize} {delay}'.format(**session_infos)
			if aqm_algorithm == 'droptail':
				set_bw_command = 'set_bw {bandwidth} {bandwidth_buffersize} {delay}'.format(**session_infos)

			scheduler_commands = '''\
#SESSION{session_infos}

client0 0 iperf -s &>$LOGDIR/iperf_s.log & echo $! > /tmp/pid_iperf_server
client0 2 sudo tcpdump -i eth1 port 5001 -s0 -w $LOGDIR/receiver.pcap 2>&1 & echo $! > /tmp/pid_tcpdump
client0 {killtime} sudo kill -SIGTERM $(cat /tmp/pid_tcpdump) & kill -SIGTERM $(cat /tmp/pid_iperf_server)

delay 0 /vagrant/code/tc_helper.sh set_delay {delay}
delay {cleantime} /vagrant/code/tc_helper.sh destroy

bandwidth 0 /vagrant/code/tc_helper.sh {set_bw_command}
bandwidth {cleantime} /vagrant/code/tc_helper.sh destroy

server 1 /vagrant/code/tcpprobe_helper.sh 5001 &>$LOGDIR/cwnd.log & echo $! > /tmp/pid_tcpprobe
server 2 sudo tcpdump -i eth1 port 5001 -s0 -w $LOGDIR/sender.pcap 2>&1 & echo $! > /tmp/pid_tcpdump
server {killtime} sudo kill -SIGTERM $(cat /tmp/pid_tcpprobe) & sudo kill -SIGTERM $(cat /tmp/pid_tcpdump)

bandwidth 0 sudo tcpdump -tt -v -ieth1 -s96 -w $LOGDIR/dump_bandwidth_eth1.pcap 2>&1 & echo $! >/tmp/pid_tcpdump_eth1
bandwidth {killtime} sudo kill -SIGTERM $(cat /tmp/pid_tcpdump_eth1)
bandwidth 0 sudo tcpdump -tt -v -ieth2 -s96 -w $LOGDIR/dump_bandwidth_eth2.pcap 2>&1 & echo $! >/tmp/pid_tcpdump_eth2
bandwidth {killtime} sudo kill -SIGTERM $(cat /tmp/pid_tcpdump_eth2)

delay 2 /vagrant/code/tc_helper.sh watch_buffer_size &>$LOGDIR/delay_buffer.log & echo $! > /tmp/pid_buffersize
delay {killtime} sudo kill -SIGTERM $(cat /tmp/pid_buffersize)

bandwidth 2 /vagrant/code/tc_helper.sh watch_buffer_size &>$LOGDIR/bandwidth_buffer.log & echo $! > /tmp/pid_buffersize
bandwidth {killtime} sudo kill -SIGTERM $(cat /tmp/pid_buffersize)

server 5 iperf -c client0 -t {interval} &>$LOGDIR/iperf_c.log

'''.format(session_infos=json.dumps(session_infos), set_bw_command=set_bw_command, interval=test['time'], killtime=test['time']+5, cleantime=test['time']+10, **session_infos)
			testname='iperf_{}_{}'.format(delay, aqm_algorithm)
			group_dir=os.path.join('tests', testname)
			save_dir = os.path.join(group_dir, "{0:02d}_{1}_{2}_{3}".format(i+1, test['bw'], delay, buffersize))
			mkdir_p(save_dir)
			with open(os.path.join(save_dir, 'jobs.sched'), 'w') as f:
				f.write(scheduler_commands)

