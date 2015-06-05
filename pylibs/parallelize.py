from multiprocessing import Process, Pipe
import time

class AsyncFunction(object):
	def __init__(self, fn, args=(), kwargs={}, return_obj=None, return_attr=None):
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.return_obj = return_obj
		self.return_attr = return_attr
		self._conn = None
		self._process = None

	def _call(self, conn):
		result = self.fn(*self.args, **self.kwargs)
		conn.send(result)
		conn.close()

	def run(self):
		self._conn, child_conn = Pipe(duplex=False)
		self._process = Process(target=AsyncFunction._call, args=(self, child_conn))
		self._process.start()

	def poll(self, timeout=0):
		if self._conn.poll(timeout):
			result = self._conn.recv()
			self.return_obj.__dict__[self.return_attr] = result
			self._process.join()
			return True
		return False

class Parallelize(object):
	def __init__(self, collection, **kwargs):
		self._functions = []
		for custom_kwargs in collection:
			for k in kwargs:
				custom_kwargs[k] = kwargs[k]
			self._functions.append(AsyncFunction(**custom_kwargs))
	def run(self, polltime=0.5):
		done = 0
		for fn in self._functions:
			fn.run()
		while done is not len(self._functions):
			for fn in self._functions:
				if fn.poll(polltime):
					done += 1

if __name__ == '__main__':
	def sleepy(t):
		time.sleep(t)
		return "after {0}s".format(t)

	class resultclass:
		pass

	result=resultclass()

	coll = [
		{'args': (3,), 'return_attr': 'a'},
		{'args': (1,), 'return_attr': 'b'}
	]
	Parallelize(coll, fn=sleepy, return_obj=result).run()

	print result.__dict__

