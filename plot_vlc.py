import sys, os.path
#from os.path import dirname
from pylibs.log import VLCSession
from pylibs.plot import plotSession

if __name__ == "__main__":
	filenames = sys.argv[1:]
	assert len(filenames)
	export = len(filenames) > 1
	if filenames[0] == 'export':
		export = True
		filenames = sys.argv[2:]

	for filename in filenames:
		print "Reading {0}...".format(filename)
		session = VLCSession.parse(filename)
		print "Plotting {0}...".format(filename)
		plotSession(session, os.path.join('tests', session.collection, session.name + '.png') if export else False)

