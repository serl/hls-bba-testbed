import sys, os
from pylibs.log import VLCSession
from pylibs.plot import plotScatters
from pylibs.parallelize import Parallelize

class EmptyObject(object): pass

if __name__ == "__main__":
	filenames = sys.argv[1:]
	assert len(filenames)
	export = False
	export_big = False
	if filenames[0].endswith('.png'):
		export = filenames[0]
		export_big = filenames[0].replace('.png', '_big.png')
		filenames = sys.argv[2:]

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
		for session in p.results:
			if 'streams' not in sessions_summary.__dict__:
				sessions_summary.streams = session.streams
			summary = EmptyObject()
			summary.tag = "{0}_{1}".format(session.name.split('_')[0], session.run)
			summary.gamma = session.get_fraction_oneidle()
			summary.mu = session.get_fraction_both_overestimating()
			summary.mu_dry = session.get_fraction_both_overestimating(what='downloading_bandwidth')
			summary.mu_bitrate = session.get_fraction_both_overestimating(what='downloading_bitrate')
			summary.fairshare = session.get_fairshare()/1000
			summary.lambdap = session.get_fraction_both_on()
			summary.unfairness = session.get_avg_unfairness()/1000
			summary.VLClogs = []
			for VLClog in session.VLClogs:
				VLCsummary = EmptyObject()
				VLCsummary.instability = VLClog.get_instability()
				summary.VLClogs.append(VLCsummary)

			sessions_summary.sessions.append(summary)

	print "Plotting..."
	plotScatters(sessions_summary, export, export_big=export_big, thickness_factor=2)

