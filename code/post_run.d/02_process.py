import sys, os, os.path
from getopt import getopt, GetoptError

class PlainObject(object):
	def __repr__(self):
		return self.__dict__.__repr__()

class Packet(PlainObject):
	def __init__(self, line):
		(self.time, self.stream, self.src_ip, self.src_port, self.dst_ip, self.dst_port, self.len, self.seq, self.ack) = line.rstrip().split(',')
		self.f_time = float(self.time)
		self.i_seq = int(self.seq)
		self.i_len = int(self.len)
		try:
			self.i_ack = int(self.ack)
		except:
			self.i_ack = None
	def is_packet(self):
		return self.src_port == '3000' and self.len != '0'
	def is_ack(self):
		return self.dst_port == '3000' and self.len == '0' and self.ack != ''
	def get_wo_time(self):
		return ','.join((self.src_ip, self.src_port, self.dst_ip, self.dst_port, self.len, self.seq))

class PacketGroup(PlainObject):
	def set_stream(self, packet):
		if packet.is_packet():
			(self.src_ip, self.src_port, self.dst_ip, self.dst_port) = (packet.src_ip, packet.src_port, packet.dst_ip, packet.dst_port)
		elif packet.is_ack():
			(self.src_ip, self.src_port, self.dst_ip, self.dst_port) = (packet.dst_ip, packet.dst_port, packet.src_ip, packet.src_port)
	def get(self):
		return ','.join(map(str, (self.label, self.src_ip, self.src_port, self.dst_ip, self.dst_port, self.start_time, self.end_time, self.start_seq, self.end_seq, self.packets)))
	def in_packet(self, packet):
		return packet.is_packet() and packet.i_seq >= self.start_seq and packet.i_seq < self.end_seq

class Burst(PacketGroup):
	def __init__(self, packet):
		self.set_stream(packet)
		self.start_seq = packet.i_seq
		self.end_seq = packet.i_seq + packet.i_len
		self.start_time = packet.f_time
		self.packets = 1
		self.label = 'B'
	def add_packet(self, packet):
		self.packets += 1
		self.end_seq = packet.i_seq + packet.i_len
		self.end_time = packet.f_time

class Trailing(PacketGroup):
	def __init__(self, packet):
		self.set_stream(packet)
		self.start_seq = packet.i_ack
		self.end_seq = packet.i_ack
		self.start_time = packet.f_time
		self.packets = 1
		self.label = 'T'
	def add_packet(self, packet):
		self.packets += 1
		self.end_seq = packet.i_ack
		self.end_time = packet.f_time

def parse(acksfiles, in_tempfile_path, in_tempfile_time_path, packetgroups_file_path):
	with open(in_tempfile_path, 'w') as in_tempfile, open(in_tempfile_time_path, 'w') as in_tempfile_time, open(packetgroups_file_path, 'w') as packetgroups:
		for acksfile_path in acksfiles:
			with open(acksfile_path, 'r') as acksfile:
				bursts = []
				trailings = []
				burst = None
				trailing = None
				for line in acksfile:
					p = Packet(line)

					if p.is_packet():
						wo_time = p.get_wo_time() + '\n'
						in_tempfile.write(wo_time)

					if p.is_packet():
						if burst is None:
							burst = Burst(p)
						else:
							burst.add_packet(p)

						if trailing is not None:
							if trailing.packets > 5 and trailing.end_seq - trailing.start_seq > 0:
								trailings.append(trailing)
								#print stream, (burst.end_time - burst.start_time)*1000
							trailing = None

					elif p.is_ack():
						if burst is not None:
							if burst.packets > 5 and burst.end_time - burst.start_time < 0.018:
								bursts.append(burst)
								#print stream, (burst.end_time - burst.start_time)*1000
							burst = None

						if trailing is None:
							trailing = Trailing(p)
						else:
							trailing.add_packet(p)

			for g in bursts+trailings:
				packetgroups.write(g.get() + '\n')

			with open(acksfile_path, 'r') as acksfile:
				for line in acksfile:
					p = Packet(line)

					if p.is_packet():
						line_towrite = p.time + ',' + p.get_wo_time()
						label = 'C'
						for trailing in trailings:
							if trailing.in_packet(p):
								label = 'T'
								break
						for burst in bursts:
							if burst.in_packet(p):
								label = 'B'
								break
						in_tempfile_time.write(line_towrite + ',' + label + '\n')

			# with open(acksfile_path, 'r') as acksfile, open('DEBUG_' + acksfile_path, 'w') as acksfile_debug:
			# 	for line in acksfile:
			# 		line = line.rstrip()
			# 		(t, stream, src_ip, src_port, dst_ip, dst_port, pkt_len, pkt_seq, pkt_ack) = line.split(',')
			# 		if src_port == '3000' and pkt_len != '0':
			# 			int_pkt_seq = int(pkt_seq)
			# 			for i, burst in enumerate(bursts):
			# 				if int_pkt_seq >= burst.start_seq and int_pkt_seq < burst.end_seq:
			# 					line += ',B'+str(i)
			# 			for i, trailing in enumerate(trailings):
			# 				if int_pkt_seq >= trailing.start_seq and int_pkt_seq < trailing.end_seq:
			# 					line += ',T'+str(i)
			# 		acksfile_debug.write(line+'\n')

if __name__ == "__main__":
	try:
		opts, args = getopt(sys.argv[1:], '', ('in_tempfile=', 'in_tempfile_time=', 'packetgroups='))
		acksfiles = [a.rstrip(os.sep) for a in args]
		if len(acksfiles) is 0:
			raise IndexError()
		for acksfile in acksfiles:
			if not os.path.exists(acksfile):
				raise IndexError()
	except (GetoptError, IndexError):
		print 'Usage: {} --in_tempfile= --in_tempfile_time= --packetgroups= <in_tempfile_acks.*...>\n\n(where the two in_tempfiles are actually an output)'.format(sys.argv[0])
		sys.exit(1)

	for opt, arg in opts:
		if opt in ("--in_tempfile"):
			in_tempfile_path = arg
		elif opt in ("--in_tempfile_time"):
			in_tempfile_time_path = arg
		elif opt in ("--packetgroups"):
			packetgroups_file_path = arg

	parse(acksfiles, in_tempfile_path, in_tempfile_time_path, packetgroups_file_path)
