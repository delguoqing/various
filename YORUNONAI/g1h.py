import struct
import os
import math
import sys
from util import get_getter, dump_data

def extract(data, path):
	g1m_data = []
	
	get = get_getter(data, ">")
	fourcc = get(0x0, "8s")
	assert fourcc == "G1H_0020", "invalid fourcc"
	file_size = get(0x8, "I")
	assert len(data) == file_size, "file size not match!"
	
	unk0, g1hp_chunk_count = get(0xc, "2H")
	assert unk0 == 0x10, "hey, guess wrong, this value has special meaning"
	
	g1hp_chunk_offset_list = get(0x10, "%dI" % g1hp_chunk_count)
	
	for i in xrange(g1hp_chunk_count):
		off = g1hp_chunk_offset_list[i]
		chunk_size = get(off + 0x8, "I")
		g1m_data = extract_g1hp(data[off: off + chunk_size])
		for j in xrange(len(g1m_data)):
			dump_data(path.replace(".g1h", "_%d_%d.g1m" % (i, j)), g1m_data[j])
			
def extract_g1hp(g1hp_data):
	print "extracting"
	get = get_getter(g1hp_data, ">")
	fourcc = get(0x0, "8s")
	assert fourcc == "G1HP0010", "invalid fourcc"
	chunk_size = get(0x8, "I")
	assert len(g1hp_data) - chunk_size < 0x10, "invalid chunk size! 0x%x vs 0x%x" % (len(g1hp_data),
																					 chunk_size)
	unk0 = get(0xc, "I")
	g1m_count, unk1 = get(0x10, "2H")
	g1m_offset_list = get(0x14, "%dI" % g1m_count)
	print "offset_list", g1m_offset_list
	g1m_data = []
	for i in xrange(g1m_count):
		off = g1m_offset_list[i]
		g1m_size = get(off + 0x8, "I")
		g1m_data.append(g1hp_data[off: off + g1m_size])
	return g1m_data
	
if __name__ == '__main__':
	f = open(sys.argv[1], "rb")
	data = f.read()
	f.close()
	
	extract(data, sys.argv[1])