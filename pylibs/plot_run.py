import sys, os, re, os.path
from getopt import getopt, GetoptError
from log import Session
from plot import plotSession

targz_re = re.compile('^(\d+).tar.gz$')
if __name__ == "__main__":
	try:
		opts, args = getopt(sys.argv[1:], 'se:o:d:', ('silent', 'nodetails', 'details', 'export=', 'output_dir=', 'size=', 'boundaries='))
		rundir = args[0].rstrip(os.sep)
		if not os.path.exists(rundir):
			raise IndexError()
	except (GetoptError, IndexError):
		print 'Usage: {} [OPTIONS] <run_directory|run.tar.gz>\n\n-s, --silent suppresses the debugging output\n--nodetails do a less detailed plot\n--details do a more detailed plot (default)\n-e, --export=FORMAT saves the plot in the requested format(s), comma delimited (pyz, png, ...)\n-o, --output_dir=DIR saves the plot in the requested directory, instead of in the parent directory of the run_directory\n-d, --size=WIDTHxHEIGHT use these dimensions in inches for the export (defaults to 22x12)\n--boundaries=START:END cut plot between START and END seconds'.format(sys.argv[0])
		sys.exit(1)

	details = True
	silent = False
	export = False
	outdir = None
	plot_size = (22, 6)
	plot_start = 0
	plot_end = None
	for opt, arg in opts:
		if opt in ("-s", "--silent"):
			silent = True
		elif opt in ("--nodetails"):
			details = False
		elif opt in ("--details"):
			details = True
		elif opt in ("-e", "--export"):
			export = arg.split(',')
		elif opt in ("-o", "--output_dir"):
			outdir = arg
		elif opt in ("-d", "--size"):
			plot_size = tuple(arg.split('x'))
		elif opt in ("--boundaries"):
			(plot_start, plot_end) = map(float, arg.split(':'))

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
	testname = os.path.basename(testdir)
	if outdir is None:
		outdir = os.path.dirname(testdir)

	try:
		if not silent:
			print "Reading {}...".format(rundir)
		session = Session.read(rundir)
		boundaries = '_{}-{}'.format(plot_start, plot_end) if plot_end is not None else ''
		export_files = [os.path.join(outdir, '{}_{}{}.{}'.format(testname, run, boundaries, fmt)) for fmt in export] if export else False
		if not silent:
			export_string = " on {}".format(' and '.join(export_files)) if export_files else ''
			print "Plotting {}{}...".format(rundir, export_string)
		plotSession(session, export_files, plot_size=plot_size, details=details, plot_start=plot_start, plot_end=plot_end)
	except:
		print "for run {}".format(rundir)
		raise

