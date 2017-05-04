import mmap
import os
import pylzma
import struct
import sys

UNCOMP_BLOCK_SIZE = 0x10000

def decompress_block(params, block, out, size):
	block = params + block
	out.write(pylzma.decompress(block, size, maxlength=size))

def decompress_tlzc(buf, out):
	assert(buf[0:4] == "TLZC")
	comp_size, uncomp_size = struct.unpack("<II", buf[8:16])
	num_blocks = (uncomp_size + 0xFFFF) / UNCOMP_BLOCK_SIZE

	lzma_params = buf[24:29]

	block_header_off = 29
	data_off = block_header_off + 2 * num_blocks
	remaining = uncomp_size
	for i in xrange(num_blocks):
		off = block_header_off + 2 * i
		comp_block_size = struct.unpack("<H", buf[off:off+2])[0]

		block = buf[data_off:data_off+comp_block_size]
		data_off += comp_block_size

		if remaining < UNCOMP_BLOCK_SIZE:
			decompress_block(lzma_params, block, out, remaining)
		else:
			decompress_block(lzma_params, block, out, UNCOMP_BLOCK_SIZE)
		remaining -= UNCOMP_BLOCK_SIZE
		
if __name__ == "__main__":
	buf = open(sys.argv[1], "rb").read()
	decompress_tlzc(buf, open(sys.argv[2], "wb"))