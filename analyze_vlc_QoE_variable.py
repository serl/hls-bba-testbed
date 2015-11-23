import sys, os, os.path
from collections import OrderedDict
from pylibs.log import Session
from pylibs.parallelize import Parallelize
from pylibs.generic import mkdir_p, mean_confidence, PlainObject
import numpy as np

if __name__ == "__main__":
	outfile = sys.argv[1]
	filenames = sys.argv[2:]
	assert len(filenames)

	sessions_summary = OrderedDict()
	for filename in filenames:
		try:
			filename = filename.rstrip(os.sep)
			run = 1
			sessions = []
			while True:
				runpath = os.path.join(filename, str(run))
				if not os.path.isdir(runpath):
					runpath += '.tar.gz'
					if not os.path.isfile(runpath):
						break
				#print "Reading {0} run {1}...".format(filename, run)
				sessions.append(Session.read(runpath))
				run += 1
			if len(sessions) == 0:
				#print "No runs in {0}".format(filename)
				continue
			#print "Analyzing {0}...".format(filename)
			for run_zerobased, session in enumerate(sessions):
				for VLClog in session.VLClogs:
					summary = PlainObject()
					summary.rebuffering_ratio = VLClog.get_buffering_fraction()
					summary.avg_bitrate = VLClog.get_avg_bitrate()
					summary.avg_quality_level = VLClog.get_avg_quality()
					summary.instability = VLClog.get_instability()

					summary.avg_router_queue_len = session.bandwidth_buffer.get_avg_queue_len()
					if len(set(session.buffer_profile.values())) != 1:
						raise Exception("More to code if router buffer size is not constant!")
					summary.avg_relative_router_queue_len = float(summary.avg_router_queue_len) / session.buffer_profile.values()[0] * 100

					if len(set(session.delay_profile.values())) != 1:
						raise Exception("More to code if RTT is not constant!")
					summary.avg_relative_rtt = float(VLClog.tcpprobe.get_avg_srtt()) / session.delay_profile.values()[0] * 100

					if len(session.VLClogs) > 1:
						summary.general_unfairness = session.get_general_unfairness()
						summary.quality_unfairness = session.get_quality_unfairness()

					if filename not in sessions_summary:
						sessions_summary[filename] = []
					if len(sessions_summary[filename]) < run_zerobased+1:
						sessions_summary[filename].append([])
					sessions_summary[filename][run_zerobased].append(summary)
		except:
			print "in {}".format(filename)
			raise

	try:
		headers = ('rebuffering_ratio', 'avg_bitrate', 'avg_quality_level', 'instability', 'avg_router_queue_len', 'avg_relative_router_queue_len', 'avg_relative_rtt', 'general_unfairness', 'quality_unfairness')
		columns = dict([(h,[]) for h in headers])
		if os.path.dirname(outfile) is not '':
			mkdir_p(os.path.dirname(outfile))
		with open(outfile, 'w') as f:
			f.write("label,{}\n".format(",,".join(headers)))
			for filename, runs in sessions_summary.iteritems():
				for run_zerobased, summaries in enumerate(runs):
					for summary in summaries:
						values = [summary.__dict__[index] if index in summary.__dict__ else '' for index in headers]
						f.write("{}/{},{}\n".format(filename, run_zerobased+1, ",,".join(map(str, values))))
						for h in headers:
							try:
								columns[h].append(summary.__dict__[h])
							except KeyError:
								continue
			result = []
			for h in headers:
				if len(columns[h]):
					result.extend(mean_confidence(columns[h]))
				else:
					result.extend(['',''])
			f.write("\n{0},{1}\n".format(os.path.basename(outfile), ','.join(map(str, result))))
	except:
		print "in {}".format(outfile)
		raise

