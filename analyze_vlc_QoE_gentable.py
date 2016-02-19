import sys, itertools, os.path
from vlc_test import settings, get_algocurl_tuples, get_curl_label

metrics = ('rebuffering_ratio', 'avg_bitrate', 'avg_relative_bitrate', 'avg_quality_level', 'instability', 'link_utilization', 'avg_router_queue_len', 'avg_relative_router_queue_len', 'avg_relative_rtt', 'dropped_burst', 'dropped_clocking', 'dropped_trailing', 'general_unfairness', 'general_relative_unfairness', 'quality_unfairness', 'total_clients')
def get_cell(file_path, column):
	try:
		with open(file_path, 'r') as f:
			for last in f: pass
			return last.rstrip().split(',')[column:column+2]
	except IOError:
		return ('', '')

def generate_subtable(n_client, rtt, metricsdir, prefix):
	rtt_label = str(rtt).zfill(settings.rtt_zfill)

	#label
	output = 'Clients: {},RTT: {}\n'.format(n_client, rtt)

	#metrics header
	output += ','
	for metric in metrics:
		output += '{}{}'.format(metric, ','*len(settings.aqm)*len(settings.buffer_size)*2)
	output += '\n'

	#aqm/buffer_size header
	submetric_header = ''
	for (aqm, buffer_size) in itertools.product(settings.aqm, settings.buffer_size):
		submetric_header += '{}-{},,'.format(aqm, buffer_size)
	output += 'algo,{}\n'.format(submetric_header*len(metrics))

	algocurls = sorted(['{}_{}'.format(algo, get_curl_label(curl)) for (algo, curl) in get_algocurl_tuples(settings.algorithms, settings.curl)])
	for algocurl in algocurls:
		output += algocurl + ','
		for ((metric_i, metric), aqm, buffer_size) in itertools.product(enumerate(metrics), settings.aqm, settings.buffer_size):
			buffer_size_label = str(buffer_size).zfill(settings.buffer_size_zfill)
			output += ','.join(get_cell(os.path.join(metricsdir, '{}{}_bbb_{}_{}BDP_{}_{}.csv'.format(prefix, n_client, rtt_label, buffer_size_label, algocurl, aqm)), (2*metric_i)+1)) + ','
		output += '\n'

	return output


if __name__ == "__main__":
	metricsdir = sys.argv[1]
	prefix = ''
	try:
		prefix = sys.argv[2]
	except:
		pass
	outfile = os.path.join(metricsdir, prefix + 'summary.csv')
	with open(outfile, 'w') as f:
		for (n_client, rtt) in itertools.product(settings.clients, settings.rtt):
			subtable = generate_subtable(n_client, rtt, metricsdir, prefix)
			f.write(subtable+'\n')
