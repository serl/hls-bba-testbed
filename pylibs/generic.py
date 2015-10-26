class PlainObject(object): pass

import os, errno
def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc:
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else: raise

import math
import numpy as np
from scipy.stats import t
def mean_confidence(data, confidence=.95):
	values = np.array(data)
	mean = values.mean()
	#confidence_interval = t.interval(confidence, values.size-1, loc=mean, scale=values.std()/math.sqrt(values.size))
	h = values.std() / math.sqrt(values.size) * t.ppf((1+confidence)/2., values.size-1)
	return (mean, h)

import re
percentage_re = re.compile('^(\d+)%$')
def is_percentage(value):
	match = percentage_re.match(value)
	if match:
		return int(match.group(1))
	return False

