from util import swap_fourCC

# fvf
SEMATIC_NAME_MAP = {
	0x0: "POSITION",
	0x1: "BLENDWEIGHTS",	# last weight can be computed by 1.0 - sum(BLENDWEIGHTS)
	0x2: "BLENDINDICES",
	0x3: "NORMAL",
	0x5: "TEXCOORD0",
	0x105: "TEXCOORD1",
	0x205: "TEXCOORD2",
	0x305: "TEXCOORD3",
	0x405: "TEXCOORD4",
	0x6: "PACKED(TANGENT+BINORMAL)",	# (float3+sign)
	0xa: "COLOR0",
}

DATA_TYPE_MAP = {
	0x0: "float",
	0x1: "float2",
	0x2: "float3",
	0x3: "float4",
	0x5: "int4",
	0xd: "RGBA"
}

G1M_0036 = swap_fourCC("G1M_0036")
G1MS0032 = swap_fourCC("G1MS0032")
G1MM0020 = swap_fourCC("G1MM0020")
G1TG0060 = swap_fourCC("G1TG0060")
G1MG = swap_fourCC("G1MG")
G1MS = swap_fourCC("G1MS")
G1MM = swap_fourCC("G1MM")