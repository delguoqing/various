import struct
import os
import math
import sys
from util import get_getter
from util import count
from util import log, set_log_level
import game_util

def parse(data, bone_names=()):
	get = get_getter(data, ">")
	fourcc = get(0x0, "8s")
	assert fourcc == "G1A_0042", "invalid fourcc"
	file_size = get(0x8, "I")
	assert len(data) == file_size * 0x10, "file size not match!"
	unk0 = get(0xc, "H")
	assert unk0 in (0x1c, 0x410, 0x14), "not header size, unknown"
	# 0x14 is used in Field model
	unk1, unk2 = get(0xe, "2B")
	assert 0 <= unk1 <= 2
	assert unk2 == 1
	unk_f = get(0x10, "f")
	# count(locals(), "unk_f")
	
	unk3 = get(0x14, "I")	# unk * 0x10 points to some offset of a specific data block below
							# specific block, i.e. keyframe block
	
	# 0x18 ~ 0x30
	# may be reserved fields
	unk0x18 = get(0x18, "I")
	assert unk0x18 == 0
	unk0x1c = get(0x1c, "I")
	assert unk0x1c == 0
	unk0x20 = get(0x20, "I")
	assert unk0x20 == 1
	unk0x24 = get(0x24, "I")
	assert unk0x24 == 0
	unk0x28 = get(0x28, "I")
	assert unk0x28 == 0
	unk0x2c = get(0x2c, "I")
	assert unk0x2c == 0	
	
	# 0x30 ~
	unk0x30, unk0x32 = get(0x30, "2H")
	# unk0x30: mapping count
	# unk0x32: max index
	assert unk0x30 == unk0x32 + 1 or unk0x30 == unk0x32
	values1 = []
	off = 0x34
	bone_indices = []
	block_info_offsets = []
	for i in xrange(unk0x30):
		values1.append(get(off , "2I"))	# (bone_index, )
		off += 0x8
		# log("%d, %d" % values1[-1], lv=0)
		block_info_offsets.append(values1[-1][1] * 0x10 + 0x30)
		# Example: MOB02A
		# bone count = 77
		# unk0x30 = 76, unk0x32 = 76
		# bone 50: Bip001_R_Calf, this bone maps to nothing
		assert values1[-1][0] <= unk0x32	# passed
	
	values2 = []
	# padding to 0x10 here
	rem = off % 0x10
	if rem != 0:
		off += 0x10 - rem
	
	block_info = []
	for i in xrange(unk0x30):
		assert off == block_info_offsets[i], "0x%x vs 0x%x" % (off, block_info_offsets[i])
		if unk0 == 0x410:	# morph animation
			size, _off = get(off + 0x4, "2I")
			block_info.append((off + _off * 0x10, size))
			off += 0x10
		else:	# bone animation
			# print "bone %d:" % i
			cnt = get(off, "I")
			assert cnt == 6	# 6 tracks in order of sx, sy, sz, rx, ry, rz, rw, x, y, z
			for j in xrange(10):
				size, _off = get(off + 0x4 + j * 0x8, "2I") # size ?
				block_info.append((off + _off * 0x10, size))
			# some reserved fields
			assert not any(get(off + 0x4 + 10 * 0x8, "3I")), get(off + 0x4 + 10 * 0x8, "3I")
			off += 0x60
		
	# ignore other types a.t.m
	if unk0 != 0x1c:
		return
	
	track_names = (
		"scaleX", "scaleY", "scaleZ", "QuatX", "QuatY", "QuatZ", "QuatW", "PosX", "PosY", "PosZ"
	)
	# offset@unk3 * 0x10
	assert off == unk3 * 0x10
	# chunk size may vary
	inv_file = False
	assert off == block_info[0][0], "0x%x vs 0x%x" % (off, block_info[0][0])

	for j, (blk_off, blk_size) in enumerate(block_info):
		assert blk_off == off
		
		bone_index = j / 10
		
		if 3 <= j % 10 < 7:
			qidx = j % 10 - 3
		else:
			qidx = -1
			
		try:
			bone_name = bone_names[bone_index]
		except IndexError:
			bone_name = "----"
		
		if j % 10 == 0:
			log("\n\nBone: %s" % bone_name, lv=0)
			qkeys = ([], [], [], [])	# x, y, z, w
			qtimes = []
			
		if j % 10 == 9:
			check_quaternion(qkeys, qtimes)
			
		log("========== %5s ========== @offset=0x%x" % (track_names[j % 10], blk_off), lv=0)
		times = get(off + blk_size * 0x10, "%df" % blk_size, force_tuple=True)
		if qidx >= 0:
			qtimes.append(times)
		assert times[-1] == unk_f	# keyframe block is always ends with that unknown float
		# this may be keyframe time, so it's in ascending order
		for i in xrange(blk_size - 1):
			assert times[i] <= times[i + 1]		
		times_ = (0.0, ) + times
		last_sum = None
		for i in xrange(blk_size):
			k = get(off + i * 0x10, "4f")
			now_sum = sum(k)
			if i == 0:
				eps_txt = ""
			else:
				eps = math.fabs(k[-1] - last_sum)
				eps_txt = "%f" % eps
				# if eps >= 1e-3:
				# 	count(locals(), "eps", fmt="%f")
			log("t=%f\t" % times_[i], k, "eps:", eps_txt, lv=0)
			if qidx >= 0:
				qkeys[qidx].append(k)
			last_sum = now_sum
		log("t=%f\t" % times[-1], lv=0)
			
		_real_size = blk_size * 0x14
		if _real_size % 0x10 != 0:
			_real_size += 0x10 - (_real_size % 0x10)
			
		off += _real_size
	
def print_eps(items):
	for eps, count in items:
		print str(eps), ":", count
		
def check_quaternion(qkeys, qtimes):
	# all time values
	all_qtimes = set([0.0])
	for qtime in qtimes:
		all_qtimes.update(qtime)
	all_qtimes = sorted(list(all_qtimes))
	
	all_qvalues = ([], [], [], [])		
	t_idx = 0
	
	for i in xrange(4):
		for t in all_qtimes:
			spline_idx = len(qtimes[i]) - 1
			for j, tend in enumerate(qtimes[i]):
				if t < tend:
					spline_idx = j
					break
			a, b, c, d = qkeys[i][spline_idx]
			tend = qtimes[i][spline_idx]
			if spline_idx == 0:
				tbeg = 0.0
			else:
				tbeg = qtimes[i][spline_idx - 1]
			t_perc = (t - tbeg) / (tend - tbeg)
			v = a * (t_perc ** 3) + b * (t_perc ** 2) + c * t_perc + d
			all_qvalues[i].append(v)
	
	for i in xrange(len(all_qtimes)):
		x, y, z, w = all_qvalues[0][i], all_qvalues[1][i], all_qvalues[2][i], all_qvalues[3][i]
		sqrsum = x**2 + y**2 + z**2 + w**2
		# log("t = %f, q: (%f, %f, %f, %f), sqrsum=%f" % (all_qtimes[i], x, y, z, w, sqrsum), lv=0)
		assert math.fabs(sqrsum - 1.0) < 1e-2, str(math.fabs(sqrsum - 1.0))
	
if __name__ == '__main__':
	f = open(sys.argv[1], "rb")
	data = f.read()
	f.close()
	
	set_log_level(0)
	bone_names = game_util.parse_bone_names_using_g1a_path(sys.argv[1])
	log("Total %d bone names parsed" % len(bone_names), lv=0)
		
	parse(data, bone_names)