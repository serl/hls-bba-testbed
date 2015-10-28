import sys, os, re, os.path
from getopt import getopt, GetoptError
from log import Session
from plot import plotSession

targz_re = re.compile('^(\d+).tar.gz$')
if __name__ == "__main__":
	try:
		opts, args = getopt(sys.argv[1:], 'se:', ('silent', 'export='))
		rundir = args[0].rstrip(os.sep)
		if not os.path.exists(rundir):
			raise IndexError()
	except (GetoptError, IndexError):
		print 'Usage: {} [OPTIONS] <run_directory|run.tar.gz>\n\n-s, --silent suppresses the debugging output\n-e, --export=FORMAT saves the plot in the requested format (pyz, png, ...)'.format(sys.argv[0])
		sys.exit(1)

	silent = False
	export = False
	for opt, arg in opts:
		if opt in ("-s", "--silent"):
			silent = True
		elif opt in ("-e", "--export"):
			export = arg

	run = 0
	try:
		run = int(os.path.basename(rundir))
	except:
		match = targz_re.match(os.path.basename(rundir))
		try:
			run = int(match.group(1))
		except:
			raise Exception("Unable to understand run id, for run {}".format(rundir))
			pass

	testdir = os.path.dirname(rundir)

	try:
		if not silent:
			print "Reading {0}...".format(rundir)
		session = Session.read(rundir)
		if not silent:
			print "Plotting {0}...".format(rundir)
		plotSession(session, '{}_{}.{}'.format(testdir, run, export) if export else False)
	except:
		print "for run {}".format(rundir)
		raise

