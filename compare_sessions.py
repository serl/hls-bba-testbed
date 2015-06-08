import sys
from pylibs.log import VLCSession
from pylibs.plot import plotCompareSessions

def algo_key(algo):
	if algo == 'classic':
		return 0
	if algo == 'bba0':
		return 1
	return 10

if __name__ == "__main__":
	filenames = sys.argv[1:]
	assert len(filenames)
	export = False
	if filenames[0] == 'export':
		filenames = sys.argv[2:]
		export = 'comparison.svg'

	sessions = [VLCSession.parse(f) for f in filenames]
	sessions.sort(key=lambda s: (s.bwprofile[0], algo_key(s.VLClogs[0].algorithm)))
	sessions_by_algo = []
	for s in sessions:
		algo = s.VLClogs[0].algorithm
		obj = next((o for o in sessions_by_algo if o['algo'] == algo), None)
		if not obj:
			obj = {'algo': algo, 'sessions': []}
			sessions_by_algo.append(obj)
		obj['sessions'].append(s)

	plotCompareSessions(sessions_by_algo, export)

