import sys, os
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
		filename = filename.rstrip(os.sep)
		run = ''
		try:
			run = '_' + str(int(filename.split(os.sep)[-1]))
		except:
			pass
		print "Reading {0}...".format(filename)
		session = VLCSession.parse(filename)
		print "Plotting {0}...".format(filename)
		plotSession(session, [os.path.join('tests', session.collection, session.name + run + '.' + ext) for ext in ('pyz', 'png')] if export else False)
		#plotSession(session, os.path.join('tests', session.collection, session.name + run + '_slides.png'), plot_size=(11,7), thickness_factor=2, details=False)
		#plotSession(session, os.path.join('tests', session.collection, session.name + run + '_pdf.png'), plot_size=(18,5), thickness_factor=2, details=False)
		#plotSession(session, os.path.join('tests', session.collection, session.name + run + '_detail.png'), details=False, plot_start=450, plot_end=700, plot_size=(11,7), thickness_factor=2)

