import sys, os, os.path
from pylibs.log import Session
from pylibs.parallelize import Parallelize
from pylibs.generic import mkdir_p, mean_confidence, PlainObject
import numpy as np

if __name__ == "__main__":
	outfile = sys.argv[1]
	filenames = sys.argv[2:]
	assert len(filenames)

	sessions_summary = PlainObject()
	sessions_summary.runs = []
	for filename in filenames:
		try:
			filename = filename.rstrip(os.sep)
			run = 1
			funcs = []
			while True:
				runpath = os.path.join(filename, str(run))
				if not os.path.isdir(runpath):
					runpath += '.tar.gz'
					if not os.path.isfile(runpath):
						break
				#print "Reading {0} run {1}...".format(filename, run)
				funcs.append({'args': (runpath,)})
				run += 1
			p = Parallelize(funcs, fn=Session.read)
			p.run()
			if len(p.results) == 0:
				#print "No runs in {0}".format(filename)
				continue
			#print "Analyzing {0}...".format(filename)
			for i, session in enumerate(p.results):
				for VLClog in session.VLClogs:
					summary = PlainObject()
					summary.buffering_fraction = VLClog.get_buffering_fraction()
					summary.avg_bitrate = VLClog.get_avg_bitrate()
					summary.avg_bitrate_ratio = summary.avg_bitrate / session.get_fairshare() * 100
					summary.avg_quality = VLClog.get_avg_quality()
					summary.instability = VLClog.get_instability()

					summary.link_utilization = -1
					if len(session.bwprofile) == 1:
						summary.link_utilization = session.bandwidth_eth2_toclients.get_avg_rate() / session.bwprofile.values()[0] * 100

					summary.avg_router_queue_len = session.bandwidth_buffer.get_avg_queue_len()
					if len(set(session.buffer_profile.values())) != 1:
						raise Exception("More to code if router buffer size is not constant!")
					summary.avg_relative_router_queue_len = summary.avg_router_queue_len / session.buffer_profile.values()[0] * 100

					if len(set(session.delay_profile.values())) != 1:
						raise Exception("More to code if RTT is not constant!")
					summary.avg_relative_rtt = VLClog.tcpprobe.get_avg_srtt() / session.delay_profile.values()[0] * 100

					if len(session.VLClogs) > 1:
						summary.general_unfairness = session.get_general_unfairness()
						summary.quality_unfairness = session.get_quality_unfairness()

					if len(sessions_summary.runs) < i+1:
						sessions_summary.runs.append([])
					sessions_summary.runs[i].append(summary)
		except:
			print "in {}".format(filename)
			raise

	result = []
	for index in ('buffering_fraction', 'avg_bitrate', 'avg_bitrate_ratio', 'avg_quality', 'instability', 'link_utilization', 'avg_router_queue_len', 'avg_relative_router_queue_len', 'avg_relative_rtt', 'general_unfairness', 'quality_unfairness'):
		run_means = []
		for run in sessions_summary.runs:
			try:
				run_means.append(np.array([s.__dict__[index] for s in run]).mean())
			except KeyError:
				continue
		if len(run_means):
			result.extend(mean_confidence(run_means))

	if os.path.dirname(outfile) is not '':
		mkdir_p(os.path.dirname(outfile))
	with open(outfile, 'w') as f:
		f.write("{0},{1}\n".format(os.path.basename(outfile), ','.join(map(str, result))))

