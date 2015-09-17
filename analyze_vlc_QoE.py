import sys, os
from pylibs.log import VLCSession
from pylibs.plot import plotScatters
from pylibs.parallelize import Parallelize
from pylibs.generic import mkdir_p

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
			VLClog = session.VLClogs[0]

			summary = EmptyObject()
			summary.buffering_fraction = VLClog.get_buffering_fraction()
			summary.avg_bitrate = VLClog.get_avg_bitrate()
			summary.avg_bitrate_ratio = summary.avg_bitrate/session.get_fairshare()*100
			summary.avg_quality = VLClog.get_avg_quality()
			summary.instability = VLClog.get_instability()

			sessions_summary.sessions.append(summary)

	result = []
	for index in ('buffering_fraction', 'avg_bitrate', 'avg_bitrate_ratio', 'avg_quality', 'instability'):
		result.append(sum([s.__dict__[index] for s in sessions_summary.sessions])/len(sessions_summary.sessions))

	mkdir_p('tests/QoE_metrics')
	with open(os.path.join('tests/QoE_metrics', label), 'w') as f:
		f.write("{0},{1}".format(label, ','.join(map(str, result))))

