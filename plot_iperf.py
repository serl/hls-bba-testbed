import sys, re
from pylibs.log import IperfSession
from pylibs.plot import plotIperf

if __name__ == "__main__":
	filenames = sys.argv[1:]
	assert len(filenames)
	export = len(filenames) > 1
	if filenames[0] == 'export':
		export = True
		filenames = sys.argv[2:]

	for dirname in filenames:
		if dirname[-1] == '/':
			dirname = dirname[:-1]
		print "Reading {0}...".format(dirname)
		session = IperfSession.parse(dirname, tshark=False)
		print "Plotting {0}...".format(dirname)
		plotIperf(session, dirname+'.png' if export else False)#, 15, 30)

