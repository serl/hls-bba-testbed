import sys, os, math
from pylibs.log import VLCSession
from pylibs.parallelize import Parallelize
from pylibs.generic import mkdir_p
from scipy.stats import t
import numpy as np

class EmptyObject(object): pass

if __name__ == "__main__":
	label = sys.argv[1]
	filenames = sys.argv[2:]
	assert len(filenames)

	sessions_summary = EmptyObject()
	sessions_summary.sessions = []
	for filename in filenames:
		filename = filename.rstrip(os.sep)
		run = 1
		funcs = []
		while True:
			runpath = os.path.join(filename, str(run))
			if not os.path.isdir(runpath):
				break
			print "Reading {0} run {1}...".format(filename, run)
			funcs.append({'args': (runpath,)})
			run += 1
		p = Parallelize(funcs, fn=VLCSession.parse)
		p.run()
		if len(p.results) == 0:
			print "No runs in {0}".format(filename)
			continue
		print "Analyzing {0}...".format(filename)
		for session in p.results:
			for VLClog in session.VLClogs:
				summary = EmptyObject()
				summary.buffering_fraction = VLClog.get_buffering_fraction()
				summary.avg_bitrate = VLClog.get_avg_bitrate()
				summary.avg_bitrate_ratio = summary.avg_bitrate/session.get_fairshare()*100
				summary.avg_quality = VLClog.get_avg_quality()
				summary.instability = VLClog.get_instability()
				summary.link_utilization = -1
				if len(session.bwprofile) == 1:
					summary.link_utilization = session.bandwidth_eth2_toclients.get_avg_rate()/session.bwprofile.values()[0]*100
				summary.avg_router_queue_len = session.bandwidth_buffer.get_avg_queue_len()
				if len(session.VLClogs) > 1:
					summary.general_unfairness = session.get_general_unfairness()
					summary.quality_unfairness = session.get_quality_unfairness()

				sessions_summary.sessions.append(summary)

	result = []
	for index in ('buffering_fraction', 'avg_bitrate', 'avg_bitrate_ratio', 'avg_quality', 'instability', 'link_utilization', 'avg_router_queue_len', 'general_unfairness', 'quality_unfairness'):
		try:
			values = np.array([s.__dict__[index] for s in sessions_summary.sessions])
		except:
			print "{0} not present.".format(index)
			continue
		mean = values.mean()
		#confidence = t.interval(0.95, values.size-1, loc=mean, scale=values.std()/math.sqrt(values.size))
		h = values.std() / math.sqrt(values.size) * t.ppf((1+0.95)/2., values.size-1)
		result.extend((mean, h))

	mkdir_p('tests/QoE_metrics')
	with open(os.path.join('tests/QoE_metrics', label), 'w') as f:
		f.write("{0},{1}\n".format(label, ','.join(map(str, result))))

