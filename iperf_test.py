import sys, os, errno
from pylibs.generic import mkdir_p

bandwidth_buffersize=int(sys.argv[1])
delay=sys.argv[2]

testname='iperf_%s_%dp' % (delay, bandwidth_buffersize)
group_dir=os.path.join('tests', testname)

tests = (
	{ 'bw': '300kbit', 'time': 300 },
	{ 'bw': '1mbit', 'time': 240 },
	{ 'bw': '5mbit', 'time': 120 },
	{ 'bw': '10mbit', 'time': 60 },
)

for i, test in enumerate(tests):
	scheduler_commands = '''\
client0 0 iperf -s &>$LOGDIR/iperf_s.log & echo $! > /tmp/pid_iperf_server
delay 0 /vagrant/code/tc_helper.sh set_delay {delay}
bandwidth 0 /vagrant/code/tc_helper.sh set_bw {bandwidth} {bandwidth_buffersize}
server 1 /vagrant/code/tcpprobe_helper.sh 5001 &>$LOGDIR/cwnd.log & echo $! > /tmp/pid_tcpprobe
server 2 sudo tcpdump -i eth1 port 5001 -s0 -w $LOGDIR/sender.pcap 2>&1 & echo $! > /tmp/pid_tcpdump
client0 2 sudo tcpdump -i eth1 port 5001 -s0 -w $LOGDIR/receiver.pcap 2>&1 & echo $! > /tmp/pid_tcpdump
delay 2 /vagrant/code/tc_helper.sh watch_buffer_size &>$LOGDIR/delay_buffer.log & echo $! > /tmp/pid_buffersize
bandwidth 2 /vagrant/code/tc_helper.sh watch_buffer_size &>$LOGDIR/bandwidth_buffer.log & echo $! > /tmp/pid_buffersize
server 5 iperf -c client0 -t {interval} &>$LOGDIR/iperf_c.log
server {killtime} sudo kill -SIGTERM $(cat /tmp/pid_tcpprobe) & sudo kill -SIGTERM $(cat /tmp/pid_tcpdump)
client0 {killtime} sudo kill -SIGTERM $(cat /tmp/pid_tcpdump) & kill -SIGTERM $(cat /tmp/pid_iperf_server)
delay {killtime} sudo kill -SIGTERM $(cat /tmp/pid_buffersize)
bandwidth {killtime} sudo kill -SIGTERM $(cat /tmp/pid_buffersize)

delay {cleantime} /vagrant/code/tc_helper.sh destroy
bandwidth {cleantime} /vagrant/code/tc_helper.sh destroy

'''.format(bandwidth=test['bw'], delay=delay, bandwidth_buffersize=bandwidth_buffersize, interval=test['time'], killtime=test['time']+5, cleantime=test['time']+10)
	save_dir = os.path.join(group_dir, "{0:02d}_{1}".format(i+1, test['bw']))
	mkdir_p(save_dir)
	with open(os.path.join(save_dir, 'jobs.sched'), 'w') as f:
		f.write(scheduler_commands)

