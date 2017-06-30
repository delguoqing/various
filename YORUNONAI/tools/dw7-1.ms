if (heapSize < 20000000) then
	heapSize = 200000000 -- allow ~ 40 MB instead of just 7.5 MB. Prevents "Runtime Error: Out of scripter memory"

fname = getOpenFileName \ 
caption:"Open DW7 Model File" \
types:"DW7 Model File(*.g1m)|*.g1m" \
historyCategory:"DW7 Object Presets"
f = fopen fname "rb"


fn floatSwap2 f = 
(
	i = bit.floatAsInt f
	h = bit.intashex i
	while h.count < 8 do h = "0" + h
	s = (substring h 7 2) + (substring h 5 2) + (substring h 3 2) + (substring h 1 2)
	bit.intAsFloat (bit.hexasint s)
)	
fn ReadBEfloat fstream = (
return floatSwap2(readfloat fstream)
)
fn PrintOffset Var =
(
	local Var = Var
print ("This is the offset 0x" + (bit.intAsHex Var) as string)
	Var
)
fn PrintCount Var =
(
	local Var = Var
print ("This is the Count 0x" + (bit.intAsHex Var) as string)
	Var
)

fn ReadBEword fstream = (
return (bit.swapBytes (readshort fstream #unsigned) 1 2)
)

  	fn convertTo32 input16 = (
 		inputAsInt = input16
 		sign = bit.get inputAsInt 16
 		exponent = (bit.shift (bit.and inputAsInt (bit.hexasint "7C00")) -10) as integer - 16
 		fraction = bit.and inputAsInt (bit.hexasint "03FF")
 		if sign==true then sign = 1 else sign = 0
 		exponentF = exponent + 127
 		--Ouput 32 bit integer representing a 32 bit float
 		outputAsFloat = bit.or (bit.or (bit.shift fraction 13) (bit.shift exponentF 23)) (bit.shift sign 31)
 		--Output Check	
 		return bit.intasfloat outputasfloat
 	)

fn ReadBEHalfFloat fstream = (
return convertTo32(ReadBEword fstream)
)
 

fn ReadBElong fstream = (
long = readlong fstream
long = bit.swapBytes long 1 4
long = bit.swapBytes long 2 3
return long
)


fn ReadFixedString bstream fixedLen =
(
	local str = ""
	for i = 1 to fixedLen do
	(
		str += bit.intAsChar (ReadByte bstream #unsigned)
	)
	str
)

struct Vert_Offset_Struct
(
	Vert_Offset,VertSize,VertCount
)
struct Face_Offset_Struct
(
	ID,Face_Offset
)

struct Mesh_Info_Struct
(
	TexID,FaceID,VertStart,VertCount,FaceStart,FaceCount
)
G1M_ = ReadFixedString f 4
G1M_Version = ReadFixedString f 4
G1M_Size = ReadBElong f
G1M_Start = ReadBElong f
G1M_Null = ReadBElong f
G1M_Count = ReadBElong f	--G1M block count actually
fseek f G1M_Start#seek_set
G1MF = #()
G1MS = #()
G1MM = #()
G1MG = #()
COLL = #()
NUNO = #()
EXTR = #()
for a = 1 to G1M_Count Do (
start = (ftell f)
G1Mx = ReadFixedString f 4
G1MxVersion = ReadFixedString f 4
G1MxSize = ReadBElong f
print (G1Mx + G1MxVersion)
fseek f (start + G1MxSize) #seek_set
case of

(

(G1Mx == "G1MF"): append G1MF start

(G1Mx == "G1MS"): append G1MS start

(G1Mx == "G1MM"): append G1MM start
	
(G1Mx == "G1MG"): append G1MG start
	
(G1Mx == "COLL"): append COLL start

(G1Mx == "NUNO"): append NUNO start
	
(G1Mx == "EXTR"): append EXTR start

default: print G1Mx 

)

)

--
--finished adding different G1M blocks into specific array
--

-- seems like that only G1MG is parsed here
-- it is possible to have multiple G1MG block in one file?
-- only 1 G1MG block in one g1m file, at least this is true in YoruNoNaiKuni

for a = 1 to G1MG.count Do (
OffArry = #()						-- offset for what?(Schunk)
fseek f G1MG[a]#seek_set			-- seek to G1MG block start
G1MG0044 = ReadFixedString f 8
G1MGSize = ReadBElong f
Platform = ReadFixedString f 4
Null = ReadBElong f
fseek f 0x18#seek_cur --BBox
SchunkCount = ReadBElong f
for b = 1 to SchunkCount Do (
CStart = (ftell f)
Ctype = ReadBElong f
CSize = ReadBElong f
fseek f (CStart + CSize)#seek_set
append OffArry (CStart + 8)
)
VertOff = #()
VertOffC = #()
VSizeA = #()
FaceOff = #()
ElemArr = #()
fseek f OffArry[1]#seek_set
fseek f OffArry[2]#seek_set
fseek f OffArry[3]#seek_set
fseek f OffArry[4]#seek_set			-- most probably 0x10004
MeshSecs = ReadBElong f				-- mesh segment count
for b = 1 to MeshSecs Do (
Mstart = (ftell f)
Munk01 = ReadBElong f
Vsize = ReadBElong f
Vcount = ReadBElong f
Munk02 = ReadBElong f
fseek f (Vsize * Vcount)#seek_cur
if (Vsize != 12) Do (
append VertOff (Mstart + 16)
append VSizeA Vsize
printoffset Vsize
)
if (Vsize == 12) Do (
append VertOffC (Mstart + 16)
)
)
fseek f OffArry[5]#seek_set
fseek f OffArry[6]#seek_set
fseek f OffArry[7]#seek_set
FaceSecs = ReadBElong f
for b = 1 to FaceSecs Do (
fstart = (ftell f)
fcount = ReadBElong f
funk01 = ReadBElong f
funk02 = ReadBElong f
fseek f (fcount * 2)#seek_cur
append FaceOff (fstart + 12)
)
fseek f OffArry[8]#seek_set
NumElements = ReadBElong f
for b = 1 to NumElements Do (
UnkE01 = ReadBElong f
UnkE02 = ReadBElong f
UnkE03 = ReadBElong f
UnkE04 = ReadBElong f
UnkE05 = ReadBElong f
UnkE06 = ReadBElong f
TexID = ReadBElong f
FaceID = (ReadBElong f + 1)
UnkE09 = ReadBElong f
UnkE10 = ReadBElong f
VertStart = ReadBElong f
VertCount = ReadBElong f
FaceStart = ReadBElong f
FaceCount = ReadBElong f
append ElemArr (Mesh_Info_Struct TexID:TexID FaceID:FaceID VertStart:VertStart VertCount:VertCount FaceStart:FaceStart FaceCount:FaceCount)
)
fseek f OffArry[9]#seek_set
for b = 1 to NumElements Do (
Vert_array = #()
Normal_array = #()
UV_array = #()
Face_array = #()
Weight_array = #()
if VertOffC.count >= 1 Do (
fseek f (VertOffC[(ElemArr[b].FaceID)] + (0xC * ElemArr[b].VertStart))#seek_set
for c = 1 to ElemArr[b].VertCount Do (
color1 = ReadBEfloat f
tu = ReadBEfloat f
tv = ReadBEfloat f
append UV_array [tu,tv,0]
)
)
fseek f (VertOff[(ElemArr[b].FaceID)] + (VSizeA[(ElemArr[b].FaceID)] * ElemArr[b].VertStart))#seek_set
for c = 1 to ElemArr[b].VertCount Do (
if VSizeA[(ElemArr[b].FaceID)] == 0x20 Do (
vx = ReadBEfloat f
vy = ReadBEfloat f
vz = ReadBEfloat f
tu = 0
tv = 0
fseek f (VSizeA[(ElemArr[b].FaceID)] - 12)#seek_cur
)
if VSizeA[(ElemArr[b].FaceID)] == 0x24 Do (
vx = ReadBEfloat f
vy = ReadBEfloat f
vz = ReadBEfloat f
tu = 0
tv = 0
fseek f (VSizeA[(ElemArr[b].FaceID)] - 12)#seek_cur
)
if VSizeA[(ElemArr[b].FaceID)] == 0x28 Do (
vx = ReadBEfloat f
vy = ReadBEfloat f
vz = ReadBEfloat f
tu = 0
tv = 0
fseek f (VSizeA[(ElemArr[b].FaceID)] - 12)#seek_cur
)
if VSizeA[(ElemArr[b].FaceID)] == 0x2C Do (
vx = ReadBEfloat f
vy = ReadBEfloat f
vz = ReadBEfloat f
tu = 0
tv = 0
fseek f (VSizeA[(ElemArr[b].FaceID)] - 12)#seek_cur
)
if VSizeA[(ElemArr[b].FaceID)] == 0x30 Do (
vx = ReadBEfloat f
vy = ReadBEfloat f
vz = ReadBEfloat f

unk01 = ReadBEfloat f
unk02 = ReadBEfloat f
unk03 = ReadBEfloat f
unk04 = ReadBEfloat f
unk05 = ReadBEfloat f
unk06 = ReadBEfloat f
unk07 = ReadBEfloat f
tu = ReadBEHalfFloat f
tv = ReadBEHalfFloat f
unk08 = ReadBEfloat f
)
if VSizeA[(ElemArr[b].FaceID)] == 0x34 Do (
vx = ReadBEfloat f
vy = ReadBEfloat f
vz = ReadBEfloat f
tu = 0
tv = 0
fseek f (VSizeA[(ElemArr[b].FaceID)] - 12)#seek_cur
)
if VSizeA[(ElemArr[b].FaceID)] == 0x38 Do (
vx = ReadBEfloat f
vy = ReadBEfloat f
vz = ReadBEfloat f
tu = 0
tv = 0
fseek f (VSizeA[(ElemArr[b].FaceID)] - 12)#seek_cur
)
if VSizeA[(ElemArr[b].FaceID)] == 0x70 Do (
vx = ReadBEfloat f
vy = ReadBEfloat f
vz = ReadBEfloat f
tu = 0
tv = 0
fseek f (VSizeA[(ElemArr[b].FaceID)] - 12)#seek_cur
)
append Vert_array [vx,vy,vz]
if VertOffC.count <= 0 Do (
append UV_array [tu,tv,0]
)
)
fseek f (FaceOff[(ElemArr[b].FaceID)] + (2 * ElemArr[b].FaceStart))#seek_set
FaceEnd = ((ftell f) + (2 * ElemArr[b].facecount))
StartDirection = -1
f1 = ((ReadBEword f + 1) - ElemArr[b].VertStart)
f2 = ((ReadBEword f + 1) - ElemArr[b].VertStart)
FaceDirection = StartDirection
do (
f3 = ReadBEword f
if (f3==0xFFFF) then (
f1 = ((ReadBEword f + 1) - ElemArr[b].VertStart)
f2 = ((ReadBEword f + 1) - ElemArr[b].VertStart)
FaceDirection = StartDirection   
) else (
f3 += (1 - ElemArr[b].VertStart)
FaceDirection *= -1
if (f1!=f2)AND(f2!=f3)AND(f3!=f1) then (
if FaceDirection > 0 then append Face_array [(f1),(f2),(f3)]
else append Face_array [(f1),(f3),(f2)]
)
f1 = f2
f2 = f3
)
)while (ftell f) < (FaceEnd)
	


msh = mesh vertices:Vert_array faces:Face_array
msh.numTVerts = UV_array.count
buildTVFaces msh
--msh.name = Mesh_Name_array[a]
--msh.material = meditMaterials[1].materialList[(MatSlotTexID[a])]
for j = 1 to UV_array.count do setTVert msh j UV_array[j]
for j = 1 to Face_array.count do setTVFace msh j Face_array[j]
for j = 1 to Normal_array.count do setNormal msh j Normal_array[j]
	
)
)
print ElemArr
fclose f