import sys, os, re, os.path
from log import Session
from plot import plotSession


#TODO should be added a silent parameter so to substitute plot_vlc.py in plot_vlc.sh

targz_re = re.compile('^(\d+).tar.gz$')
if __name__ == "__main__":
	rundir = sys.argv[1]

	export = False
	if rundir in ('png', 'pyz'):
		export = rundir
		rundir = sys.argv[2]

	rundir = rundir.rstrip(os.sep)

	run = 0
	try:
		run = int(os.path.basename(rundir))
	except:
		match = targz_re.match(os.path.basename(rundir))
		try:
			run = int(match.group(1))
		except:
			pass

	testdir = os.path.dirname(rundir)

	try:
		print "Reading {0}...".format(rundir)
		session = Session.read(rundir)
		print "Plotting {0}...".format(rundir)
		plotSession(session, '{}_{}.{}'.format(testdir, run, export) if export else False)
	except:
		print "for run {}".format(filename)
		raise

