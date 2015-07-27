import sys, os
from pylibs.log import VLCSession
from pylibs.plot import plotScatters
from pylibs.parallelize import Parallelize

if __name__ == "__main__":
	filenames = sys.argv[1:]
	assert len(filenames)
	export = False
	export_big = False
	if filenames[0].endswith('.png'):
		export = filenames[0]
		export_big = filenames[0].replace('.png', '_big.png')
		filenames = sys.argv[2:]

	sessions = []
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
			sessions.append(session)

	print "Plotting..."
	plotScatters(sessions, export, export_big=export_big, thickness_factor=2)

