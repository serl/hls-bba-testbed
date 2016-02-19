# python hls-size-helper.py <hls_playlist>
# it will add the custom EXT-X-SIZE header on the playlist
# output on stdout

import re, os

def add_size(filename):
	hash_re = re.compile('^#')
	dirname = os.path.dirname(filename)
	out = ''
	with open(filename, 'r') as contents:
		for line in contents:
			if not hash_re.match(line):
				out += '#EXT-X-SIZE:' + str(os.path.getsize(os.path.join(dirname, line.rstrip()))) + '\n'
			out += line
	return out

if __name__ == '__main__':
	import sys
	filename = sys.argv[1]
	print add_size(filename)
