import sys, os
from pylibs.log import VLCSession
from pylibs.plot import plotScatters

if __name__ == "__main__":
	filenames = sys.argv[1:]
	assert len(filenames)
	export = False
	if filenames[0].endswith('.png'):
		export = filenames[0]
		filenames = sys.argv[2:]

	sessions = []
	for filename in filenames:
		filename = filename.rstrip(os.sep)
		run = 1
		while True:
			runpath = os.path.join(filename, str(run))
			if not os.path.isdir(runpath):
				break
			print "Reading {0} run {1}...".format(filename, run)
			session = VLCSession.parse(runpath)
			sessions.append(session)
			run += 1
		if len(sessions) == 0:
			print "No runs in {0}".format(filename)
			continue

	print "Plotting..."
	plotScatters(sessions, export, thickness_factor=2)

