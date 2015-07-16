import sys, os
from pylibs.log import VLCSession
from pylibs.plot import plotCompareVLCRuns
from pylibs.parallelize import Parallelize

if __name__ == "__main__":
	filenames = sys.argv[1:]
	assert len(filenames)
	export = len(filenames) > 1
	if filenames[0] == 'export':
		export = True
		filenames = sys.argv[2:]

	for filename in filenames:
		filename = filename.rstrip(os.sep)
		sessions = []
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
		sessions = p.results
		if len(sessions) == 0:
			print "No runs in {0}".format(filename)
			continue

		print "Plotting {0}...".format(filename)
		plotCompareVLCRuns(sessions, os.path.join('tests', sessions[0].collection, 'compare_runs_' + sessions[0].name + '.png') if export else False, thickness_factor=2, size=(12,9))

