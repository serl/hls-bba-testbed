import sys, os, os.path
from pylibs.log import Session
from pylibs.plot import plotScatters
from pylibs.parallelize import Parallelize
from pylibs.generic import mkdir_p

class EmptyObject(object): pass

if __name__ == "__main__":
	filenames = sys.argv[1:]
	assert len(filenames)
	export = False
	if filenames[0].endswith('.png'):
		export = filenames[0]
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
				runpath += '.tar.gz'
				if not os.path.isfile(runpath):
					break
			print "Reading {0} run {1}...".format(filename, run)
			funcs.append({'args': (runpath,)})
			run += 1
		p = Parallelize(funcs, fn=Session.read)
		p.run()
		if len(p.results) == 0:
			print "No runs in {0}".format(filename)
			continue
		print "Analyzing {0}...".format(filename)
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
			summary.general_unfairness = session.get_general_unfairness()/1000
			summary.quality_unfairness = session.get_quality_unfairness()
			summary.router_rate = None
			try:
				if len(session.bwprofile) == 1:
					summary.router_rate = session.bandwidth_eth2_toclients.get_avg_rate()/session.bwprofile.values()[0]*100
			except:
				pass
			summary.VLClogs = []
			for VLClog in session.VLClogs:
				VLCsummary = EmptyObject()
				VLCsummary.instability = VLClog.get_instability()
				summary.VLClogs.append(VLCsummary)

			sessions_summary.sessions.append(summary)

	if len(sessions_summary.sessions):
		if not export:
			print "Plotting..."
			plotScatters(sessions_summary, thickness_factor=2, tag_points=True)
		else:
			mkdir_p('tests/scatterplots')
			export_bw = os.path.join('tests/scatterplots', export)
			mkdir_p(os.path.join('tests/scatterplots', 'tag'))
			export_tag = os.path.join('tests/scatterplots', 'tag', export.replace('.png', '_tag.png'))
			export_big = os.path.join('tests/scatterplots', 'tag', export.replace('.png', '_big.png'))
			mkdir_p(os.path.join('tests/scatterplots', 'color'))
			export_color = os.path.join('tests/scatterplots', 'color', export.replace('.png', '_color.png'))

			print "Plotting {0} with tags...".format(export)
			plotScatters(sessions_summary, export=export_tag, export_big=export_big, thickness_factor=2, tag_points=True)
			print "Plotting {0} without tags...".format(export)
			plotScatters(sessions_summary, export=export_color, thickness_factor=2, tag_points=False)
			print "Plotting {0} without colors...".format(export)
			plotScatters(sessions_summary, export=export_bw, thickness_factor=2, tag_points=False, colorize=False)

