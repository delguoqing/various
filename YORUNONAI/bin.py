import sys
from util import get_getter

def parse(data):
	get = get_getter(data, ">")
	off = 0x0
	i = 0
	while off < len(data):
		str_len = get(off, "b")
		if str_len == -1:
			break
		str_text = data[off + 1: off + 1 + str_len]
		off += 1 + str_len
		print "%3d:" % i, str_text
		i += 1
		
if __name__ == '__main__':
	f = open(sys.argv[1], "rb")
	data = f.read()
	f.close()
	
	parse(data)