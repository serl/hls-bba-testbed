from multiprocessing import Process, Pipe
import sys, time

class AsyncFunction(object):
	def __init__(self, fn, args=(), kwargs={}, return_obj=None, return_attr=None):
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.result = None
		self.return_obj = return_obj
		self.return_attr = return_attr
		self._conn = None
		self._process = None

	def _call(self, conn):
		result = None
		exception = None
		try:
			result = self.fn(*self.args, **self.kwargs)
		except Exception as e:
			import traceback
			exception = "".join(traceback.format_exception(*sys.exc_info()))
		finally:
			conn.send((result, exception))
			conn.close()

	def run(self):
		self._conn, child_conn = Pipe(duplex=False)
		self._process = Process(target=AsyncFunction._call, args=(self, child_conn))
		self._process.start()

	def poll(self, timeout=0):
		if self._conn.poll(timeout):
			self.result, exception = self._conn.recv()
			if exception is not None:
				raise InnerException(exception)
			if self.return_obj is not None and self.return_attr is not None:
				self.return_obj.__dict__[self.return_attr] = self.result
			self._process.join()
			return True
		return False

	def terminate(self):
		if self._process.is_alive():
			self._process.terminate()

class InnerException(Exception): pass

class Parallelize(object):
	def __init__(self, collection, **kwargs):
		self._functions = []
		for custom_kwargs in collection:
			for k in kwargs:
				custom_kwargs[k] = kwargs[k]
			self._functions.append(AsyncFunction(**custom_kwargs))
		self.results = [None] * len(self._functions)
	def run(self, polltime=0.5):
		done = 0
		for fn in self._functions:
			fn.run()
		while done is not len(self._functions):
			for idx, fn in enumerate(self._functions):
				try:
					if fn.poll(polltime):
						self.results[idx] = fn.result
						done += 1
				except:
					[fn.terminate() for fn in self._functions]
					raise

if __name__ == '__main__':
	def sleepy(t):
		time.sleep(t)
		if t == 2:
			raise Exception('ciao!')
		return "after {0}s".format(t)

	class resultclass:
		pass

	result=resultclass()
	coll = [
		{'args': (3,), 'return_attr': 'a'},
		{'args': (1,), 'return_attr': 'b'}
	]
	p = Parallelize(coll, fn=sleepy, return_obj=result)
	p.run()
	print(result.__dict__)
	print(p.results)

	result=resultclass()
	coll = [
		{'args': (300,), 'return_attr': 'a'},
		{'args': (2,), 'return_attr': 'b'}
	]
	p = Parallelize(coll, fn=sleepy, return_obj=result)
	p.run()
	print(result.__dict__)
	print(p.results)

