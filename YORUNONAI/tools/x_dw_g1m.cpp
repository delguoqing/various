#include "xentax.h"
#include "x_file.h"
#include "x_findfile.h"
#include "x_stream.h"
#include "x_dds.h"
#include "x_amc.h"
#include "x_dw_g1m.h"
using namespace std;

#pragma region DEBUGGING

static bool debug = true;
static bool debug_skeleton = true;

bool DWGetDebugModelMode(void)
{
 return ::debug;
}

bool DWSetDebugModelMode(bool state)
{
 bool prev = ::debug;
 ::debug = state;
 return prev;
}

bool DWGetDebugSkeletonMode(void)
{
 return ::debug_skeleton;
}

bool DWSetDebugSkeletonMode(bool state)
{
 bool prev = ::debug_skeleton;
 ::debug_skeleton = state;
 return prev;
}

#pragma endregion

#pragma region REGION_G1MG_STRUCTURES

struct G1MGSECTION {
 uint32 type;
 uint32 size;
 boost::shared_array<char> data;
 G1MGSECTION() : type(0), size(0) {}
};

#pragma endregion

#pragma region REGION_G1MG_00010002

struct G1MG0102TEXTURE {
 uint16 p01; // texture identifier
 uint32 p02; // texture type
 uint16 p03; // ????
 uint16 p04; // 0x0004
 uint16 p05; // 0x0004
};

struct G1MG0102ITEM {
 uint32 p01; // ????
 uint32 p02; // number of textures
 uint32 p03; // ????
 uint32 p04; // ????
 boost::shared_array<G1MG0102TEXTURE> p05;
};

struct G1MG0102DATA {
 uint32 elem;
 boost::shared_array<G1MG0102ITEM> data;
};

#pragma endregion

#pragma region REGION_G1MG_00010003

struct G1MG0103ATTR {
 uint32 p01;
 uint32 p02;
 uint32 p03;
 uint16 p04;
 uint16 p05;
 char p06[1024];
};

struct G1MG0103ITEM {
 uint32 p01;
 boost::shared_array<G1MG0103ATTR> p02;
};

struct G1MG0103DATA {
 uint32 elem;
 boost::shared_array<G1MG0103ITEM> data;
};

#pragma endregion

#pragma region REGION_G1MG_00010004

struct G1MG0104ITEM {
 uint32 p01;
 uint32 p02;
 uint32 p03;
 uint32 p04;
 boost::shared_array<char> p05;
};

struct G1MG0104DATA {
 uint32 elem;
 boost::shared_array<G1MG0104ITEM> data;
};

#pragma endregion

#pragma region REGION_G1MG_00010005

struct G1MG0105SEMANTIC {
 uint16 p01;
 uint16 p02;
 uint16 p03;
 uint16 p04;
};

struct G1MG0105ITEM {
 uint32 n_refs;
 boost::shared_array<uint32> refs;
 uint32 n_semantics;
 boost::shared_array<G1MG0105SEMANTIC> semantics;
};

struct G1MG0105DATA {
 uint32 elem;
 boost::shared_array<G1MG0105ITEM> data;
};

#pragma endregion

#pragma region REGION_G1MG_00010006

struct G1MG0106ITEMENTRY {
 uint32 p01;
 uint16 p02;
 uint16 p03;
 uint16 p04;
 uint16 p05;
};

struct G1MG0106ITEM {
 uint32 elem;
 boost::shared_array<G1MG0106ITEMENTRY> data;
};

struct G1MG0106DATA {
 uint32 elem;
 boost::shared_array<G1MG0106ITEM> data;
};

#pragma endregion

#pragma region REGION_G1MG_00010007

struct G1MG0107ITEM {
 uint32 elem;
 uint32 type;
 uint32 unknown;
 boost::shared_array<char> data;
};

struct G1MG0107DATA {
 uint32 elem;
 boost::shared_array<G1MG0107ITEM> data;
};

#pragma endregion

#pragma region REGION_G1MG_00010008

struct G1MG0108DATA {
 uint32 elem;
 boost::shared_array<boost::shared_array<uint32>> data;
};

#pragma endregion

#pragma region REGION_NUNO_STRUCTURES

// struct NUNOCLOTHINFO1 {
//  real32 v[4];
// };
// 
// struct NUNOCLOTHINFO2 {
//  uint32 unk01;
//  uint32 unk02;
//  uint32 unk03;
//  uint32 unk04;
//  real32 unk05;
//  real32 unk06;
// };
// 
// struct NUNOCLOTHINFO3 {
//  real32 unk01;
//  real32 unk02;
//  real32 unk03;
//  real32 unk04;
//  real32 unk05;
//  uint32 unk06;
//  uint32 unk07;
//  uint32 unk08;
//  uint32 unk09;
//  uint32 unk10;
//  uint32 unk11;
//  uint32 unk12;
// };
// 
// struct NUNO0301ITEM {
//  uint16 unk01;
//  uint16 unk02;
//  uint32 unk03;
//  uint32 unk04;
//  uint32 unk05;
//  uint32 unk06;
//  uint32 unk07;
//  real32 unk08;
//  real32 unk09;
//  uint32 unk10;
//  real32 unk11;
//  real32 unk12;
//  real32 unk13;
//  real32 unk14;
//  real32 unk15;
//  real32 unk16;
//  real32 unk17;
//  real32 unk18;
//  real32 unk19;
//  uint32 unk20;
//  real32 unk21;
//  real32 unk22;
//  real32 unk23;
//  real32 unk24;
//  real32 unk25;
//  real32 unk26;
//  boost::shared_array<NUNOCLOTHINFO1> data1;
//  boost::shared_array<NUNOCLOTHINFO2> data2;
//  boost::shared_array<NUNOCLOTHINFO3> data3;
// };
// 
// struct NUNO0301 {
//  uint32 n_items;
//  boost::shared_array<NUNO0301ITEM> data;
// };


struct NUNOSUBCHUNK0301ENTRY_DATATYPE1 {
 uint32 p01;
 uint32 p02;
 uint32 p03;
 uint32 p04;
 real32 p05;
 real32 p06;
};

struct NUNOSUBCHUNK0301ENTRY_DATATYPE2 {
 real32 p01[4];
 real32 p02[4];
 uint32 p03;
 uint32 p04;
 uint32 p05;
 uint32 p06;
};

struct NUNOSUBCHUNK0301ENTRY {
 uint32 h01;
 uint32 h02;
 uint32 h03;
 uint32 h04;
 uint32 h05;
 uint32 h06;
 real32 h07;
 real32 h08;
 uint32 h09;
 real32 h10[4];
 real32 h11[4];
 real32 h12;
 uint32 h13;
 real32 h14[3]; // unsure
 real32 h15[3]; // unsure
 boost::shared_array<std::array<real32,4>> p01;
 boost::shared_array<NUNOSUBCHUNK0301ENTRY_DATATYPE1> p02;
 boost::shared_array<NUNOSUBCHUNK0301ENTRY_DATATYPE2> p03;
 boost::shared_array<uint32> p04;
 boost::shared_array<uint32> p05;
 boost::shared_array<uint32> p06;
};

struct NUNOSUBCHUNK0302ENTRY {
};

struct NUNODATA {
 std::deque<NUNOSUBCHUNK0301ENTRY> _0301;
 std::deque<NUNOSUBCHUNK0302ENTRY> _0302;
};

//
// NUNV
//

struct NUNV0501SUBENTRY1 {
 real32 p01;
 real32 p02;
 real32 p03;
 real32 p04;
};

struct NUNV0501SUBENTRY2 {
 uint32 p01; // index
 uint32 p02; // index
 uint32 p03; // index
 uint32 p04; // index
 real32 p05; // ???
 real32 p06; // ???
};

struct NUNV0501SUBENTRY3 {
 real32 p01[4];
 real32 p02[4];
 uint32 p03;
 uint32 p04;
 uint32 p05;
 uint32 p06;
};

struct NUNV0501ENTRY {
 uint32 h01;    // 00 00 00 09
 uint32 h02;    // 00 00 00 10
 uint32 h03;    // 00 00 00 04
 uint32 h04;    // 00 00 00 03
 uint32 h05;    // 00 00 00 04
 real32 h06;    // 40 00 00 00
 real32 h07[3]; // 3F 00 00 00 3D CC CC CD 3F 33 33 33
 real32 h08[3]; // 3F 00 00 00 3F 80 00 00 3D CC CC CD
 real32 h09[3]; // BF C9 0F DB 3F 32 B8 C2 3F 80 00 00
 real32 h10[3]; // BF 32 B8 C2 3F 32 B8 C2 3F 00 00 00
 real32 h11[3]; // 3F 80 00 00 42 70 00 00 3F 80 00 00
 real32 h12[3]; // 3C 88 89 3B 00 00 00 00 3F 80 00 00
 uint32 h13;    // 00 01 01 00
 boost::shared_array<NUNV0501SUBENTRY1> p01; // h02 * 0x10 bytes
 boost::shared_array<NUNV0501SUBENTRY2> p02; // h02 * 0x18 bytes
 boost::shared_array<NUNV0501SUBENTRY3> p03; // h03 * 0x30 bytes
 boost::shared_array<uint32> p04; // h04 * 0x04 bytes
};

struct NUNV0502ENTRY {
};

struct NUNVDATA {
 std::deque<NUNV0501ENTRY> _0501;
 std::deque<NUNV0502ENTRY> _0502;
};

#pragma endregion

//
// MODELS
//

struct MODELDATA {
 public :
  STDSTRING filename;
  STDSTRING pathname;
  STDSTRING shrtname;
  std::ifstream ifile;
  std::ofstream dfile;
 public :
  std::deque<binary_stream> G1MF_list;
  std::deque<binary_stream> G1MS_list;
  std::deque<binary_stream> G1MM_list;
  std::deque<binary_stream> G1MG_list;
  std::deque<binary_stream> NUNO_list;
  std::deque<binary_stream> NUNV_list;
 public :
  NUNODATA nuno;
  NUNVDATA nunv;
 public :
  G1MGSECTION section01;
  G1MGSECTION section02;
  G1MGSECTION section03;
  G1MGSECTION section04;
  G1MGSECTION section05;
  G1MGSECTION section06;
  G1MGSECTION section07;
  G1MGSECTION section08;
  G1MGSECTION section09;
 public :
  G1MG0102DATA data0102;
  G1MG0103DATA data0103;
  G1MG0104DATA data0104;
  G1MG0105DATA data0105;
  G1MG0106DATA data0106;
  G1MG0107DATA data0107;
  G1MG0108DATA data0108;
};

bool process0101(MODELDATA& md)
{
 // UNKNOWN SECTION
 // 00010001 00000090 00000002
 // 00000100
 // #1 3F800000 3F800000 3F800000 3F800000 3F333333 3F333333 3F333333 00001111
 //    3F333333 3F333333 3F333333 41F00000 00000000 00000000 00000000 FFFF0000
 // #2 3F800000 3F800000 3F800000 3F800000 3F800000 3F800000 3F800000 00001011
 //    00000000 00000000 00000000 00000000 00000000 00000000 00000000 FFFF0000

 return true;
}

bool process0102(MODELDATA& md)
{
 // nothing to do
 if(!md.section02.data) return true;
 if(!md.section02.size) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "-------------------" << endl;
    md.dfile << " MATERIALS SECTION " << endl;
    md.dfile << " 0x00010002        " << endl;
    md.dfile << "-------------------" << endl;
    md.dfile << endl;
   }

 // read number of index buffers
 binary_stream bs(md.section02.data, md.section02.size);
 md.data0102.elem = bs.BE_read_uint32();
 if(!md.data0102.elem) return true;

 // read entries
 md.data0102.data.reset(new G1MG0102ITEM[md.data0102.elem]);
 for(size_t i = 0; i < md.data0102.elem; i++)
    {
     // read material properties
     md.data0102.data[i].p01 = bs.BE_read_uint32(); // 0x00000000
     md.data0102.data[i].p02 = bs.BE_read_uint32(); // number of textures
     md.data0102.data[i].p03 = bs.BE_read_uint32(); // 0x00000000, 0x00000001, 0xFFFFFFFF
     md.data0102.data[i].p04 = bs.BE_read_uint32(); // 0x00000000, 0x00000001, 0xFFFFFFFF

     // create texture property data
     if(md.data0102.data[i].p02)
        md.data0102.data[i].p05.reset(new G1MG0102TEXTURE[md.data0102.data[i].p02]);

     // read texture properties
     for(uint32 j = 0; j < md.data0102.data[i].p02; j++) {
        md.data0102.data[i].p05[j].p01 = bs.BE_read_uint16(); // texture identifier
        md.data0102.data[i].p05[j].p02 = bs.BE_read_uint32(); // texture type
        md.data0102.data[i].p05[j].p03 = bs.BE_read_uint16(); // ??????
        md.data0102.data[i].p05[j].p04 = bs.BE_read_uint16(); // 0x0004
        md.data0102.data[i].p05[j].p05 = bs.BE_read_uint16(); // 0x0004
       }
    }

 // debug
 if(DWGetDebugModelMode())
   {
    // number of materials
    md.dfile << setfill('0');
    md.dfile << "number of materials = 0x" << hex << md.data0102.elem << dec << endl;
    md.dfile << endl;
    for(size_t i = 0; i < md.data0102.elem; i++) {
        md.dfile << " MATERIAL 0x" << hex << setw(2) << i << dec << endl;
        md.dfile << "  p01 = 0x" << hex << setw(8) << md.data0102.data[i].p01 << dec << " (???)" << endl;
        md.dfile << "  p02 = 0x" << hex << setw(8) << md.data0102.data[i].p02 << dec << " (number of textures)" << endl;
        md.dfile << "  p03 = 0x" << hex << setw(8) << md.data0102.data[i].p03 << dec << " (???)" << endl;
        md.dfile << "  p04 = 0x" << hex << setw(8) << md.data0102.data[i].p04 << dec << " (???)" << endl;
        for(uint32 j = 0; j < md.data0102.data[i].p02; j++) {
            md.dfile << "  TEXTURE INFO 0x" << hex << setw(2) << j << dec << endl;
            md.dfile << "   p01 = 0x" << hex << setw(4) << md.data0102.data[i].p05[j].p01 << dec << " (texture ID)" << endl;
            md.dfile << "   p02 = 0x" << hex << setw(8) << md.data0102.data[i].p05[j].p02 << dec << " (texture type)" << endl;
            md.dfile << "   p03 = 0x" << hex << setw(4) << md.data0102.data[i].p05[j].p03 << dec << " (???)" << endl;
            md.dfile << "   p04 = 0x" << hex << setw(4) << md.data0102.data[i].p05[j].p04 << dec << " (???)" << endl;
            md.dfile << "   p05 = 0x" << hex << setw(4) << md.data0102.data[i].p05[j].p05 << dec << " (???)" << endl;
           }
       }
    md.dfile << endl;
   }

 // success
 return true;
}

bool process0103(MODELDATA& md)
{
 // nothing to do
 if(!md.section03.data) return true;
 if(!md.section03.size) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "--------------------" << endl;
    md.dfile << " ATTRIBUTES SECTION " << endl;
    md.dfile << " 0x00010003         " << endl;
    md.dfile << "--------------------" << endl;
    md.dfile << endl;
   }

 // read number of index buffers
 binary_stream bs(md.section03.data, md.section03.size);
 md.data0103.elem = bs.BE_read_uint32();
 if(!md.data0103.elem) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << setfill('0');
    md.dfile << "number of entries = 0x" << hex << md.data0103.elem << dec << endl;
    md.dfile << endl;
   }

 // read entries
 md.data0103.data.reset(new G1MG0103ITEM[md.data0103.elem]);
 for(size_t i = 0; i < md.data0103.elem; i++)
    {
     // read number of attributes
     md.data0103.data[i].p01 = bs.BE_read_uint32();
     if(bs.fail()) return error("Stream read failure.");

     // create attributes
     if(md.data0103.data[i].p01)
        md.data0103.data[i].p02.reset(new G1MG0103ATTR[md.data0103.data[i].p01]);

     // read attributes
     for(size_t j = 0; j < md.data0103.data[i].p01; j++) {
         md.data0103.data[i].p02[j].p01 = bs.BE_read_uint32(); // length
         md.data0103.data[i].p02[j].p02 = bs.BE_read_uint32(); // string length
         md.data0103.data[i].p02[j].p03 = bs.BE_read_uint32(); // ????
         md.data0103.data[i].p02[j].p04 = bs.BE_read_uint16(); // ????
         md.data0103.data[i].p02[j].p05 = bs.BE_read_uint16(); // ????
         if(md.data0103.data[i].p02[j].p02) bs.BE_read_array(&md.data0103.data[i].p02[j].p06[0], md.data0103.data[i].p02[j].p02);
         uint32 remaining = md.data0103.data[i].p02[j].p01 - md.data0103.data[i].p02[j].p02 - 0x10;
         bs.move(remaining);
         if(bs.fail()) return error("Stream seek failure.");
        }

     // debug
     if(DWGetDebugModelMode()) {
        md.dfile << setfill('0');
        md.dfile << "ENTRY 0x" << hex << setw(2) << i << dec << endl;
        md.dfile << " number of attributes = 0x" << hex << setw(8) << md.data0103.data[i].p01 << dec << endl;
        for(size_t j = 0; j < md.data0103.data[i].p01; j++) {
            md.dfile << " ATTRIBUTE 0x" << hex << setw(4) << j << dec << endl;
            md.dfile << "  p01 = 0x" << hex << setw(4) << md.data0103.data[i].p02[j].p01 << dec << " (length)" << endl;
            md.dfile << "  p02 = 0x" << hex << setw(4) << md.data0103.data[i].p02[j].p02 << dec << " (string length)" << endl;
            md.dfile << "  p03 = 0x" << hex << setw(4) << md.data0103.data[i].p02[j].p03 << dec << " (???)" << endl;
            md.dfile << "  p04 = 0x" << hex << setw(4) << md.data0103.data[i].p02[j].p04 << dec << " (???)" << endl;
            md.dfile << "  p05 = 0x" << hex << setw(4) << md.data0103.data[i].p02[j].p05 << dec << " (???)" << endl;
            md.dfile << "  p06 = " << md.data0103.data[i].p02[j].p06 << " (name)" << endl;
           }
        md.dfile << endl;
       }
    }

 // success
 return true;
}

bool process0104(MODELDATA& md)
{
 // nothing to do
 if(!md.section04.data) return true;
 if(!md.section04.size) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "----------------" << endl;
    md.dfile << " VERTEX BUFFERS " << endl;
    md.dfile << " 0x00010004     " << endl;
    md.dfile << "----------------" << endl;
    md.dfile << endl;
   }

 // read number of index buffers
 binary_stream bs(md.section04.data, md.section04.size);
 md.data0104.elem = bs.BE_read_uint32();
 if(!md.data0104.elem) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "number of buffers = 0x" << hex << md.data0104.elem << dec << endl;
    md.dfile << endl;
   }

 // read entries
 md.data0104.data.reset(new G1MG0104ITEM[md.data0104.elem]);
 for(size_t i = 0; i < md.data0104.elem; i++)
    {
     // read properties
     md.data0104.data[i].p01 = bs.BE_read_uint32(); // ????
     md.data0104.data[i].p02 = bs.BE_read_uint32(); // vertsize
     md.data0104.data[i].p03 = bs.BE_read_uint32(); // vertices
     md.data0104.data[i].p04 = bs.BE_read_uint32(); // ????
     if(bs.fail()) return error("Stream read failure.");

     // read vertex buffer
     uint32 size = md.data0104.data[i].p02 * md.data0104.data[i].p03;
     md.data0104.data[i].p05.reset(new char[size]);
     bs.BE_read_array(md.data0104.data[i].p05.get(), size);
     if(bs.fail()) return error("Stream read failure.");

     // debug
     if(DWGetDebugModelMode()) {
        md.dfile << setfill('0');
        md.dfile << "VERTEX BUFFER 0x" << hex << i << dec << endl;
        md.dfile << " unknown1 = 0x" << hex << md.data0104.data[i].p01 << dec << endl;
        md.dfile << " vertsize = 0x" << hex << md.data0104.data[i].p02 << dec << endl;
        md.dfile << " vertices = 0x" << hex << md.data0104.data[i].p03 << dec << endl;
        md.dfile << " unknown2 = 0x" << hex << md.data0104.data[i].p04 << dec << endl;
        binary_stream cs(md.data0104.data[i].p05, size);
        for(size_t j = 0; j < md.data0104.data[i].p03; j++) {
            md.dfile << " " << hex << setfill('0') << setw(4) << (uint32)j << dec << ": ";
            for(uint32 k = 0; k < md.data0104.data[i].p02; k++)
                md.dfile << hex << setfill('0') << setw(2) << (uint32)cs.BE_read_uint08() << dec;
            md.dfile << endl;
           }
        md.dfile << endl;
       }
    }

 // success
 return true;
}

bool process0105(MODELDATA& md)
{
 // nothing to do
 if(!md.section05.data) return true;
 if(!md.section05.size) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "-------------------" << endl;
    md.dfile << " INPUT LAYOUT DATA " << endl;
    md.dfile << " 0x00010005        " << endl;
    md.dfile << "-------------------" << endl;
    md.dfile << endl;
   }

 // read number of index buffers
 binary_stream bs(md.section05.data, md.section05.size);
 md.data0105.elem = bs.BE_read_uint32();
 if(!md.data0105.elem) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "number of entries = 0x" << hex << md.data0105.elem << dec << endl;
    md.dfile << endl;
   }

 // create entries
 md.data0105.data.reset(new G1MG0105ITEM[md.data0105.elem]);

 // read entries
 for(size_t i = 0; i < md.data0105.elem; i++)
    {
     // read number of vertex buffer references
     md.data0105.data[i].n_refs = bs.BE_read_uint32(); // usually 0x01 or 0x02
     if(bs.fail()) return error("Stream read failure.");

     // validate number of indices
     if(md.data0105.data[i].n_refs < 1) return error("Invalid number of vertex buffer references.");
     if(md.data0105.data[i].n_refs > 4) return error("Invalid number of vertex buffer references.");

     // read indices
     md.data0105.data[i].refs.reset(new uint32[md.data0105.data[i].n_refs]);
     bs.BE_read_array(md.data0105.data[i].refs.get(), md.data0105.data[i].n_refs);
     if(bs.fail()) return error("Stream read failure.");

     // read number of semantics
     md.data0105.data[i].n_semantics = bs.BE_read_uint32();
     if(!md.data0105.data[i].n_semantics) return error("Must have at least one vertex semantic defined.");

     // read semantics
     md.data0105.data[i].semantics.reset(new G1MG0105SEMANTIC[md.data0105.data[i].n_semantics]);
     for(uint32 j = 0; j < md.data0105.data[i].n_semantics; j++) {
         md.data0105.data[i].semantics[j].p01 = bs.BE_read_uint16(); // buffer index
         md.data0105.data[i].semantics[j].p02 = bs.BE_read_uint16(); // offset
         md.data0105.data[i].semantics[j].p03 = bs.BE_read_uint16(); // data type
         md.data0105.data[i].semantics[j].p04 = bs.BE_read_uint16(); // semantic
        }

     // debug
     if(DWGetDebugModelMode()) {
        md.dfile << setfill('0');
        md.dfile << "ENTRY 0x" << hex << i << dec << endl;
        md.dfile << " number of vertex buffers: 0x" << hex << md.data0105.data[i].n_refs << dec << endl;
        md.dfile << " number of semantics: 0x" << hex << md.data0105.data[i].n_semantics << dec << endl;
        // print references
        for(uint32 j = 0; j < md.data0105.data[i].n_refs; j++)
            md.dfile << " REFERENCE 0x" << hex << j << dec << ": 0x" << hex << setw(4) << md.data0105.data[i].refs[j] << dec << endl;
        // print semantics
        for(uint32 j = 0; j < md.data0105.data[i].n_semantics; j++) {
            md.dfile << " SEMANTIC 0x" << hex << j << dec << endl;
            md.dfile << "  p01: 0x" << hex << setw(4) << md.data0105.data[i].semantics[j].p01 << dec << " (buffer index)" << endl;
            md.dfile << "  p02: 0x" << hex << setw(4) << md.data0105.data[i].semantics[j].p02 << dec << " (offset)" << endl;
            md.dfile << "  p03: 0x" << hex << setw(4) << md.data0105.data[i].semantics[j].p03 << dec << " (data type)" << endl;
            md.dfile << "  p04: 0x" << hex << setw(4) << md.data0105.data[i].semantics[j].p04 << dec << " (semantic)" << endl;
           }
        md.dfile << endl;
       }
    }

 // success
 return true;
}

bool process0106(MODELDATA& md)
{
 // nothing to do
 if(!md.section06.data) return true;
 if(!md.section06.size) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "----------------" << endl;
    md.dfile << " JOINT MAP DATA " << endl;
    md.dfile << " 0x00010006     " << endl;
    md.dfile << "----------------" << endl;
    md.dfile << endl;
   }

 // read number of index buffers
 binary_stream bs(md.section06.data, md.section06.size);
 md.data0106.elem = bs.BE_read_uint32();
 if(!md.data0106.elem) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "number of entries = 0x" << hex << md.data0106.elem << dec << endl;
    md.dfile << endl;
   }

 // create entries
 md.data0106.data.reset(new G1MG0106ITEM[md.data0106.elem]);

 // read entries
 for(size_t i = 0; i < md.data0106.elem; i++)
    {
     // read number of items
     md.data0106.data[i].elem = bs.BE_read_uint32();
     if(bs.fail()) return error("Stream read failure.");

     // allocate items
     if(md.data0106.data[i].elem)
        md.data0106.data[i].data.reset(new G1MG0106ITEMENTRY[md.data0106.data[i].elem]);

     // read items
     for(size_t j = 0; j < md.data0106.data[i].elem; j++) {
         md.data0106.data[i].data[j].p01 = bs.BE_read_uint32(); // reference to G1MM matrix
         md.data0106.data[i].data[j].p02 = bs.BE_read_uint16(); // ???
         md.data0106.data[i].data[j].p03 = bs.BE_read_uint16(); // if not 0x0000, this part needs to be moved
         md.data0106.data[i].data[j].p04 = bs.BE_read_uint16(); // ???
         md.data0106.data[i].data[j].p05 = bs.BE_read_uint16(); // joint[j] maps to this joint
        }
    }

 // debug entries
 if(DWGetDebugModelMode()) {
    for(size_t i = 0; i < md.data0106.elem; i++) {
        md.dfile << "ENTRY[0x" << hex << i << dec << "]" << endl;
        md.dfile << " number of items = 0x" << hex << md.data0106.data[i].elem << dec << endl;
        for(size_t j = 0; j < md.data0106.data[i].elem; j++) {
            md.dfile << " ITEM[0x" << setfill('0') << setw(2) << hex << j << dec << "]: ";
            md.dfile << setfill('0') << setw(8) << hex << md.data0106.data[i].data[j].p01 << dec << " ";
            md.dfile << setfill('0') << setw(8) << hex << md.data0106.data[i].data[j].p02 << dec << " ";
            md.dfile << setfill('0') << setw(4) << hex << md.data0106.data[i].data[j].p03 << dec << " ";
            md.dfile << setfill('0') << setw(4) << hex << md.data0106.data[i].data[j].p04 << dec << " ";
            md.dfile << setfill('0') << setw(4) << hex << md.data0106.data[i].data[j].p05 << dec << " ";
            md.dfile << endl;
           }
       }
    md.dfile << endl;
   }

 // success
 return true;
}

bool process0107(MODELDATA& md)
{
 // nothing to do
 if(!md.section07.data) return true;
 if(!md.section07.size) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "-------------------" << endl;
    md.dfile << " INDEX BUFFER LIST " << endl;
    md.dfile << " 0x00010007        " << endl;
    md.dfile << "-------------------" << endl;
    md.dfile << endl;
   }

 // read number of index buffers
 binary_stream bs(md.section07.data, md.section07.size);
 md.data0107.elem = bs.BE_read_uint32();
 if(!md.data0107.elem) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "number of index buffers = 0x" << hex << md.data0107.elem << dec << endl;
    md.dfile << endl;
   }

 // create entries
 md.data0107.data.reset(new G1MG0107ITEM[md.data0107.elem]);
 for(uint32 i = 0; i < md.data0107.elem; i++) {
     md.data0107.data[i].elem = 0;
     md.data0107.data[i].type = 0;
     md.data0107.data[i].unknown = 0;
    }

 // for each mesh
 for(size_t i = 0; i < md.data0107.elem; i++)
    {
     // read index buffer header
     md.data0107.data[i].elem = bs.BE_read_uint32();    // number of indices
     md.data0107.data[i].type = bs.BE_read_uint32();    // 0x08/0x10/0x20
     md.data0107.data[i].unknown = bs.BE_read_uint32(); // 0x00

     // determine index buffer format
     uint32 indexsize = 0;
     if(md.data0107.data[i].type == 0x08) indexsize = sizeof(uint08);
     else if(md.data0107.data[i].type == 0x10) indexsize = sizeof(uint16);
     else if(md.data0107.data[i].type == 0x20) indexsize = sizeof(uint32);
     else return error("Unknown index buffer data type.");

     // read index buffer
     uint32 total_bytes = md.data0107.data[i].elem * indexsize;
     if(total_bytes) {
        md.data0107.data[i].data.reset(new char[total_bytes]);
        switch(md.data0107.data[i].type) {
          case(0x08) : bs.BE_read_array(reinterpret_cast<uint08*>(md.data0107.data[i].data.get()), md.data0107.data[i].elem); break;
          case(0x10) : bs.BE_read_array(reinterpret_cast<uint16*>(md.data0107.data[i].data.get()), md.data0107.data[i].elem); break;
          case(0x20) : bs.BE_read_array(reinterpret_cast<uint32*>(md.data0107.data[i].data.get()), md.data0107.data[i].elem); break;
         }
       }

     // debug
     if(DWGetDebugModelMode()) {
        md.dfile << setfill('0');
        md.dfile << "INDEX BUFFER[0x" << setw(2) << hex << i << dec << "]" << endl; 
        md.dfile << " elem = 0x" << hex << setw(8) << md.data0107.data[i].elem << dec << endl;
        md.dfile << " type = 0x" << hex << setw(8) << md.data0107.data[i].type << dec << endl;
        md.dfile << " unknown = 0x" << hex << setw(8) << md.data0107.data[i].unknown << dec << endl;
        md.dfile << endl;
       }

     // BEGIN TESTING
     // [PS3] Dragon Quest Heroes\LINKDATA\0139\000\000_MDLK\016.g1m
     auto position = bs.tell();
     if((position % 4) && (md.data0107.elem > 1)) {
        if(DWGetDebugModelMode()) cout << " NOTE: The next index buffer position is not divisible by 4!" << endl;
        position = ((position + 0x03) & (~0x03));
        bs.seek(position);
       }
     // END TESTING
    }

 // success
 return true;
}

bool process0108(MODELDATA& md)
{
 // nothing to do
 if(!md.section08.data) return true;
 if(!md.section08.size) return true;

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "---------------------" << endl;
    md.dfile << " SURFACE INFORMATION " << endl;
    md.dfile << " 0x00010008          " << endl;
    md.dfile << "---------------------" << endl;
    md.dfile << endl;
   }

 // read number of entries
 binary_stream bs(md.section08.data, md.section08.size);
 md.data0108.elem = bs.BE_read_uint32();
 if(!md.data0108.elem) return true; // nothing to do

 // create entries
 md.data0108.data.reset(new boost::shared_array<uint32>[md.data0108.elem]);
 for(uint32 i = 0; i < md.data0108.elem; i++) md.data0108.data[i].reset(new uint32[14]);

 // read entries
 for(size_t i = 0; i < md.data0108.elem; i++)
    {
     // read entry
     md.data0108.data[i][0x00] = bs.BE_read_uint32(); // C00000D0
     md.data0108.data[i][0x01] = bs.BE_read_uint32(); // vertex buffer reference
     md.data0108.data[i][0x02] = bs.BE_read_uint32(); // index into joint map
     md.data0108.data[i][0x03] = bs.BE_read_uint32(); // ???
     md.data0108.data[i][0x04] = bs.BE_read_uint32(); // ???
     md.data0108.data[i][0x05] = bs.BE_read_uint32(); // ???
     md.data0108.data[i][0x06] = bs.BE_read_uint32(); // material reference
     md.data0108.data[i][0x07] = bs.BE_read_uint32(); // index buffer reference
     md.data0108.data[i][0x08] = bs.BE_read_uint32(); // ???
     md.data0108.data[i][0x09] = bs.BE_read_uint32(); // ??? index buffer format ???
     md.data0108.data[i][0x0A] = bs.BE_read_uint32(); // vertex buffer start
     md.data0108.data[i][0x0B] = bs.BE_read_uint32(); // number of vertices
     md.data0108.data[i][0x0C] = bs.BE_read_uint32(); // index buffer start
     md.data0108.data[i][0x0D] = bs.BE_read_uint32(); // number of indices
    }

 // debug
 if(DWGetDebugModelMode()) {
    md.dfile << "number of entries = 0x" << hex << md.data0108.elem << dec << endl;
    md.dfile << endl;
    md.dfile << "SURFACE DATA" << endl;
    for(size_t i = 0; i < md.data0108.elem; i++) {
        md.dfile << setfill('0');
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x00] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x01] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x02] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x03] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x04] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x05] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x06] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x07] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x08] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x09] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x0A] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x0B] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x0C] << dec;
        md.dfile << " 0x" << hex << setw(8) << md.data0108.data[i][0x0D] << dec;
        md.dfile << endl;
       }
    md.dfile << endl;
   }

 // success
 return true;
}

bool process0109(MODELDATA& md)
{
 return true;
}

bool buildPhase1(MODELDATA& md, ADVANCEDMODELCONTAINER& amc)
{
 // nothing to do
 G1MG0102DATA& matdata = md.data0102;
 if(!matdata.elem) return true;

 // filemap type maps a texture ID to a file index
 std::map<uint16, uint16> filemap;
 uint16 texture_index = AMC_INVALID_TEXTURE;

 // for each material
 for(size_t i = 0; i < matdata.elem; i++)
    {
     // create surface name
     stringstream ss;
     ss << "material_0x" << setfill('0') << setw(2) << hex << i << dec;

     // initialize material
     AMC_SURFMAT mat;
     mat.name = ss.str();
     mat.twoside = 0;
     mat.unused1 = 0;
     mat.unused2 = 0;
     mat.unused3 = 0;
     mat.basemap = AMC_INVALID_TEXTURE;
     mat.specmap = AMC_INVALID_TEXTURE;
     mat.tranmap = AMC_INVALID_TEXTURE;
     mat.bumpmap = AMC_INVALID_TEXTURE;
     mat.normmap = AMC_INVALID_TEXTURE;
     mat.lgthmap = AMC_INVALID_TEXTURE;
     mat.envimap = AMC_INVALID_TEXTURE;
     mat.glssmap = AMC_INVALID_TEXTURE;
     mat.resmap1 = AMC_INVALID_TEXTURE;
     mat.resmap2 = AMC_INVALID_TEXTURE;
     mat.resmap3 = AMC_INVALID_TEXTURE;
     mat.resmap4 = AMC_INVALID_TEXTURE;
     mat.resmap5 = AMC_INVALID_TEXTURE;
     mat.resmap6 = AMC_INVALID_TEXTURE;
     mat.resmap7 = AMC_INVALID_TEXTURE;
     mat.resmap8 = AMC_INVALID_TEXTURE;
     mat.basemapchan = 0;
     mat.specmapchan = 0;
     mat.tranmapchan = 0;
     mat.bumpmapchan = 0;
     mat.normmapchan = 0;
     mat.lghtmapchan = 0;
     mat.envimapchan = 0;
     mat.glssmapchan = 0;
     mat.resmapchan1 = 0;
     mat.resmapchan2 = 0;
     mat.resmapchan3 = 0;
     mat.resmapchan4 = 0;
     mat.resmapchan5 = 0;
     mat.resmapchan6 = 0;
     mat.resmapchan7 = 0;
     mat.resmapchan8 = 0;

     // for each texture
     for(uint32 j = 0; j < matdata.data[i].p02; j++)
        {
         // texture properties
         uint16 texture_iden = matdata.data[i].p05[j].p01;
         uint32 texture_type = matdata.data[i].p05[j].p02;
         uint16 unk01 = matdata.data[i].p05[j].p03; // ??? texture channel ???
         uint16 unk02 = matdata.data[i].p05[j].p04; // 0x0004
         uint16 unk03 = matdata.data[i].p05[j].p05; // 0x0004

         // insert texture into filelist
         auto iter = filemap.find(texture_iden);
         if(iter == filemap.end()) {
            filemap.insert(map<uint16, uint16>::value_type(texture_iden, filemap.size()));
            stringstream ss;
            ss << setfill('0') << setw(3) << texture_iden << ".dds";
            AMC_IMAGEFILE aif = { ss.str() };
            amc.iflist.push_back(aif);
            texture_index = amc.iflist.size() - 1;
           }
         else
            texture_index = iter->second;

         // set texture type
         texture_type &= 0xFFFF;
         switch(texture_type) {
           case(0x00000000) : mat.specmap = texture_index; break;
           case(0x00000001) : mat.basemap = texture_index; break;
           case(0x00000002) : break;
           case(0x00000003) : mat.normmap = texture_index; break;
           case(0x00000005) : break; // BLJM61225 DW8: Empires
           case(0x00000006) : break; // Wii-U Hyrule Warriors
           case(0x00000011) : break;
           case(0x00000013) : break;
           case(0x00000015) : break;
           case(0x0000001D) : break; // BLJM61225 DW8: Empires
           case(0x00000080) : break;
           case(0x00000081) : break;
           case(0x00000082) : break;
           case(0x00000083) : break;
           case(0x00000084) : break;
           case(0x00000085) : break;
           case(0x00000086) : break;
           case(0x00010003) : break; // this might be normal map (two 16-bit values)
           case(0x00010080) : break; // this might be 0x0080 (two 16-bit values with first value as channel?)
           case(0x00010081) : break; // this might be 0x0081 (two 16-bit values with first value as channel?)
           case(0x00010011) : break; // this might be 0x0011 (two 16-bit values with first value as channel?)
           case(0x00020011) : break; // this might be 0x0011 (two 16-bit values with first value as channel?)
           default : {
                stringstream ss;
                ss << "Warning! Unknown texture type 0x" << hex << texture_type << dec << ".";
                message(ss.str().c_str()); // make it just a warning now
                // return error(ss);
               }
          }
        }

     // insert material
     amc.surfmats.push_back(mat);
    }

 return true;
}

bool buildPhase2(MODELDATA& md, ADVANCEDMODELCONTAINER& amc)
{
 // nothing to do
 G1MG0106DATA& data = md.data0106;
 if(!data.elem) return true;

 // for each entry
 for(size_t i = 0; i < data.elem; i++)
    {
     // construct joint map
     G1MG0106ITEM& item = data.data[i];
     deque<uint32> jntmap;
     for(size_t j = 0; j < item.elem; j++) jntmap.push_back(item.data[j].p05);

     // insert joint map
     AMC_JOINTMAP jmap;
     jmap.jntmap = jntmap;
     amc.jmaplist.push_back(jmap);
    }

 return true;
}

bool buildPhase3(MODELDATA& md, ADVANCEDMODELCONTAINER& amc)
{
 // nothing to do
 G1MG0104DATA& vb_data = md.data0104;
 if(!vb_data.elem) return true;

 // nothing to do
 G1MG0105DATA& il_data = md.data0105;
 if(!il_data.elem) return true;

 // for each input layout
 for(uint32 i = 0; i < il_data.elem; i++)
    {
     // validate input layout item
     G1MG0105ITEM& il_item = il_data.data[i];
     if(il_item.n_refs == 0) return error("An input layout must contain at least one vertex buffer reference.");

     // validate vertex buffer references
     for(uint32 j = 0; j < il_item.n_refs; j++)
         if(!(il_item.refs[j] < vb_data.elem))
            return error("Input layout vertex buffer reference out of range.");

     // validate number of vertices
     for(uint32 j = 1; j < il_item.n_refs; j++) {
         uint32 index1 = il_item.refs[0];
         uint32 index2 = il_item.refs[j];
         G1MG0104ITEM& item1 = vb_data.data[index1];
         G1MG0104ITEM& item2 = vb_data.data[index2];
         if(item1.p03 != item2.p03)
            return error("Input layouts that reference multiple vertex buffers must have buffers with matching number of vertices.");
        }

     // get number of vertices
     uint32 n_vertices = vb_data.data[il_item.refs[0]].p03;
     if(!n_vertices) return error("Vertex buffer has no vertices.");

     // prepare vertex buffer
     AMC_VTXBUFFER vb;
     vb.name = "default";
     vb.elem = n_vertices;
     vb.data.reset(new AMC_VERTEX[vb.elem]);
     vb.flags = AMC_VERTEX_POSITION;
     vb.uvchan = 0;
     vb.uvtype[0] = AMC_INVALID_MAP;
     vb.uvtype[1] = AMC_INVALID_MAP;
     vb.uvtype[2] = AMC_INVALID_MAP;
     vb.uvtype[3] = AMC_INVALID_MAP;
     vb.uvtype[4] = AMC_INVALID_MAP;
     vb.uvtype[5] = AMC_INVALID_MAP;
     vb.uvtype[6] = AMC_INVALID_MAP;
     vb.uvtype[7] = AMC_INVALID_MAP;
     vb.colors = 0;

     // booleans to keep track of mesh type
     bool has_blendweights = false;
     bool has_blendindices = false;
     bool has_cloth = false;

     // prepare vertex buffer flags
     for(uint32 j = 0; j < il_item.n_semantics; j++)
        {
         G1MG0105SEMANTIC& semantic = il_item.semantics[j];
         switch(semantic.p04) {
           case(0x0100) : {
                has_blendweights = true;
                vb.flags |= AMC_VERTEX_WEIGHTS;
                break;
               }
           case(0x0200) : {
                has_blendindices = true;
                vb.flags |= AMC_VERTEX_WEIGHTS;
                break;
               }
           case(0x0300) : {
                vb.flags |= AMC_VERTEX_NORMAL;
                break;
               }
           // PSIZE[n] (float)
           case(0x0400) : {
                break;
               }
           case(0x0500) : {
                vb.uvchan++;
                vb.uvtype[0] = AMC_DIFFUSE_MAP;
                break;
               }
           case(0x0501) : {
                vb.uvchan++;
                vb.uvtype[1] = AMC_DIFFUSE_MAP;
                break;
               }
           case(0x0502) : {
                vb.uvchan++;
                vb.uvtype[2] = AMC_DIFFUSE_MAP;
                break;
               }
           case(0x0700) : {
                has_cloth = true;
                break;
               }
           // FOG (float)
           case(0x0B00) : {
                break;
               }
          }
        }
     if(vb.uvchan) vb.flags |= AMC_VERTEX_UV;

     // process vertex semantics
     for(uint32 j = 0; j < il_item.n_semantics; j++)
        {
         // semantic properties
         G1MG0105SEMANTIC& item = il_item.semantics[j];
         uint16 p01 = item.p01; // buffer reference
         uint16 p02 = item.p02; // offset
         uint16 p03 = item.p03; // datatype
         uint16 p04 = item.p04; // semantic

         // binary stream from buffer
         auto stride = vb_data.data[il_item.refs[p01]].p02; // stride
         auto n_vert = vb_data.data[il_item.refs[p01]].p03; // number of vertices
         auto buffer = vb_data.data[il_item.refs[p01]].p05; // vertex buffer

         // binary stream from buffer
         binary_stream bs(buffer, n_vert * stride);
         uint32 offset = p02;

         // POSITION
         if(p04 == 0x0000)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                // 0x0200 STATIC MODELS
                if(p03 == 0x0200) {
                   vb.data[k].vx = bs.BE_read_real32();
                   vb.data[k].vy = bs.BE_read_real32();
                   vb.data[k].vz = bs.BE_read_real32();
                   vb.data[k].vw = 1.0f;
                  }
                // 0x0300 CHARACTER MODELS
                else if(p03 == 0x0300) {
                   vb.data[k].vx = bs.BE_read_real32();
                   vb.data[k].vy = bs.BE_read_real32();
                   vb.data[k].vz = bs.BE_read_real32();
                   vb.data[k].vw = bs.BE_read_real32();
                  }
                // 0x0B00 CHARACTER MODELS
                else if(p03 == 0x0B00) {
                   vb.data[k].vx = bs.BE_read_real16();
                   vb.data[k].vy = bs.BE_read_real16();
                   vb.data[k].vz = bs.BE_read_real16();
                   vb.data[k].vw = bs.BE_read_real16();
                  }
                else
                   return error("Unknown vertex stream 0x0000 type.");

                // move to next item
                offset += stride;
               }
           }
         // BLEND WEIGHTS
         else if(p04 == 0x0100)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                if(p03 == 0x0000) {
                   real32 w1 = bs.BE_read_real32();
                   real32 w2 = 1.0f - w1;
                   if(w2 < 0.0001f) w2 = 0.0f;
                   vb.data[k].wv[0] = w1;
                   vb.data[k].wv[1] = w2;
                   vb.data[k].wv[2] = 0.0f;
                   vb.data[k].wv[3] = 0.0f;
                   vb.data[k].wv[4] = 0.0f;
                   vb.data[k].wv[5] = 0.0f;
                   vb.data[k].wv[6] = 0.0f;
                   vb.data[k].wv[7] = 0.0f;
                  }
                else if(p03 == 0x0100) {
                   real32 w1 = bs.BE_read_real32();
                   real32 w2 = bs.BE_read_real32();
                   real32 w3 = 1.0f - w1 - w2;
                   if(w3 < 0.0001f) w3 = 0.0f;
                   vb.data[k].wv[0] = w1;
                   vb.data[k].wv[1] = w2;
                   vb.data[k].wv[2] = w3;
                   vb.data[k].wv[3] = 0.0f;
                   vb.data[k].wv[4] = 0.0f;
                   vb.data[k].wv[5] = 0.0f;
                   vb.data[k].wv[6] = 0.0f;
                   vb.data[k].wv[7] = 0.0f;
                   vb.data[k].wv[8] = 0.0f;
                  }
                else if(p03 == 0x0200) {
                   real32 w1 = bs.BE_read_real32();
                   real32 w2 = bs.BE_read_real32();
                   real32 w3 = bs.BE_read_real32();
                   real32 w4 = 1.0f - w1 - w2 - w3;
                   if(w4 < 0.0001f) w4 = 0.0f;
                   vb.data[k].wv[0] = w1;
                   vb.data[k].wv[1] = w2;
                   vb.data[k].wv[2] = w3;
                   vb.data[k].wv[3] = w4;
                   vb.data[k].wv[4] = 0.0f;
                   vb.data[k].wv[5] = 0.0f;
                   vb.data[k].wv[6] = 0.0f;
                   vb.data[k].wv[7] = 0.0f;
                   vb.data[k].wv[8] = 0.0f;
                  }
                else if(p03 == 0x0300) {
                   vb.data[k].wv[0] = bs.BE_read_real32();
                   vb.data[k].wv[1] = bs.BE_read_real32();
                   vb.data[k].wv[2] = bs.BE_read_real32();
                   vb.data[k].wv[3] = bs.BE_read_real32();
                  }
                else if(p03 == 0x0A00) {
                   real32 w1 = bs.BE_read_real16();
                   real32 w2 = bs.BE_read_real16();
                   real32 w3 = 1.0f - w1 - w2;
                   if(w3 < 0.0001f) w3 = 0.0f;
                   vb.data[k].wv[0] = w1;
                   vb.data[k].wv[1] = w2;
                   vb.data[k].wv[2] = w3;
                   vb.data[k].wv[3] = 0.0f;
                   vb.data[k].wv[4] = 0.0f;
                   vb.data[k].wv[5] = 0.0f;
                   vb.data[k].wv[6] = 0.0f;
                   vb.data[k].wv[7] = 0.0f;
                   vb.data[k].wv[8] = 0.0f;
                  }
                else if(p03 == 0x0B00) {
                   vb.data[k].wv[0] = bs.BE_read_real16();
                   vb.data[k].wv[1] = bs.BE_read_real16();
                   vb.data[k].wv[2] = bs.BE_read_real16();
                   vb.data[k].wv[3] = bs.BE_read_real16();
                   vb.data[k].wv[4] = 0.0f;
                   vb.data[k].wv[5] = 0.0f;
                   vb.data[k].wv[6] = 0.0f;
                   vb.data[k].wv[7] = 0.0f;
                   vb.data[k].wv[8] = 0.0f;
                  }
                else if(p03 == 0x0D00) {
                   vb.data[k].wv[0] = (real32)(bs.BE_read_uint08()/255.0f);
                   vb.data[k].wv[1] = (real32)(bs.BE_read_uint08()/255.0f);
                   vb.data[k].wv[2] = (real32)(bs.BE_read_uint08()/255.0f);
                   vb.data[k].wv[3] = (real32)(bs.BE_read_uint08()/255.0f);
                   vb.data[k].wv[4] = 0.0f;
                   vb.data[k].wv[5] = 0.0f;
                   vb.data[k].wv[6] = 0.0f;
                   vb.data[k].wv[7] = 0.0f;
                   vb.data[k].wv[8] = 0.0f;
                  }
                else
                   return error("Unknown vertex stream 0x0100 type.");

                // move to next item
                offset += stride;
               }
           }
         // BLEND INDICES
         else if(p04 == 0x0200)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                if(p03 == 0x0500)
                  {
                   // read indices
                   uint16 b1 = bs.BE_read_uint08();
                   uint16 b2 = bs.BE_read_uint08();
                   uint16 b3 = bs.BE_read_uint08();
                   uint16 b4 = bs.BE_read_uint08();

                   // cloth does not have blend weights
                   if(has_cloth)
                     {
                      vb.data[k].wi[0] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[1] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[2] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[3] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[4] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[5] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[6] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[7] = AMC_INVALID_VERTEX_WMAP_INDEX;
                     }
                   // normal divide-by-three blend indices
                   else if(has_blendweights) {
                      vb.data[k].wi[0] = (b1 / 3);
                      vb.data[k].wi[1] = (b2 / 3);
                      vb.data[k].wi[2] = (b3 / 3);
                      vb.data[k].wi[3] = (b4 / 3);
                      vb.data[k].wi[4] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[5] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[6] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[7] = AMC_INVALID_VERTEX_WMAP_INDEX;
                     }
                   // normal divide-by-three blend indices (no weights specified though)
                   // WARNING!
                   // Eyeballs have weight indices, but do not have any weight values. Since
                   // eyeball are cylindrical, assume that the first weight value is 1.0f.
                   // There should only be one weight index for this.
                   else {
                      // set blendweights
                      vb.data[k].wv[0] = 1.0f;
                      vb.data[k].wv[1] = 0.0f;
                      vb.data[k].wv[2] = 0.0f;
                      vb.data[k].wv[3] = 0.0f;
                      vb.data[k].wv[4] = 0.0f;
                      vb.data[k].wv[5] = 0.0f;
                      vb.data[k].wv[6] = 0.0f;
                      vb.data[k].wv[7] = 0.0f;
                      // set blendindices
                      vb.data[k].wi[0] = b1 / 3;
                      vb.data[k].wi[1] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[2] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[3] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[4] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[5] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[6] = AMC_INVALID_VERTEX_WMAP_INDEX;
                      vb.data[k].wi[7] = AMC_INVALID_VERTEX_WMAP_INDEX;
                     }
                  }
                else
                   return error("Unknown vertex stream 0x0200 type.");

                // move to next item
                offset += stride;
               }
           }
         // NORMAL
         else if(p04 == 0x0300)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                // 0x0200 STATIC MODELS
                if(p03 == 0x0200) {
                   vb.data[k].nx = bs.BE_read_real32();
                   vb.data[k].ny = bs.BE_read_real32();
                   vb.data[k].nz = bs.BE_read_real32();
                   vb.data[k].nw = 1.0f;
                  }
                // 0x0300 CHARACTER MODELS
                else if(p03 == 0x0300) {
                   vb.data[k].nx = bs.BE_read_real32();
                   vb.data[k].ny = bs.BE_read_real32();
                   vb.data[k].nz = bs.BE_read_real32();
                   vb.data[k].nw = bs.BE_read_real32();
                  }
                // 0x0B00 CHARACTER MODELS
                else if(p03 == 0x0B00) {
                   vb.data[k].nx = bs.BE_read_real16();
                   vb.data[k].ny = bs.BE_read_real16();
                   vb.data[k].nz = bs.BE_read_real16();
                   vb.data[k].nw = bs.BE_read_real16();
                  }
                else
                   return error("Unknown vertex stream 0x0300 type.");

                // move to next item
                offset += stride;
               }
           }
         // UNKNOWN INDICES
         else if(p04 == 0x0400)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                // move to next item
                offset += stride;
               }
           }
         // TEXCOORD1
         else if(p04 == 0x0500)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                if(p03 == 0x0100) {
                   vb.data[k].uv[0][0] = bs.BE_read_real32();
                   vb.data[k].uv[0][1] = bs.BE_read_real32();
                  }
                else if(p03 == 0x0A00) {
                   vb.data[k].uv[0][0] = bs.BE_read_real16();
                   vb.data[k].uv[0][1] = bs.BE_read_real16();
                  }
                else
                   return error("Unknown vertex stream 0x0500 type.");

                // move to next item
                offset += stride;
               }
           }
         // TEXCOORD2
         else if(p04 == 0x0501)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                if(p03 == 0x0100) {
                   vb.data[k].uv[1][0] = bs.BE_read_real32();
                   vb.data[k].uv[1][1] = bs.BE_read_real32();
                  }
                else if(p03 == 0x0A00) {
                   vb.data[k].uv[1][0] = bs.BE_read_real16();
                   vb.data[k].uv[1][1] = bs.BE_read_real16();
                  }
                else
                   return error("Unknown vertex stream 0x0501 type.");

                // move to next item
                offset += stride;
               }
           }
         // TEXCOORD3
         else if(p04 == 0x0502)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                if(p03 == 0x0100) {
                   vb.data[k].uv[2][0] = bs.BE_read_real32();
                   vb.data[k].uv[2][1] = bs.BE_read_real32();
                  }
                else if(p03 == 0x0A00) {
                   vb.data[k].uv[2][0] = bs.BE_read_real16();
                   vb.data[k].uv[2][1] = bs.BE_read_real16();
                  }
                else
                   return error("Unknown vertex stream 0x0502 type.");

                // move to next item
                offset += stride;
               }
           }
         // UNKNOWN
         else if(p04 == 0x0504)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                // move to next item
                offset += stride;
               }
           }
         // UNKNOWN
         else if(p04 == 0x0505)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                // move to next item
                offset += stride;
               }
           }
         // UNKNOWN
         else if(p04 == 0x0600)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                // move to next item
                offset += stride;
               }
           }
         // UNKNOWN
         else if(p04 == 0x0700)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                // move to next item
                offset += stride;
               }
           }
         // UNKNOWN
         else if(p04 == 0x0A00)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                // move to next item
                offset += stride;
               }
           }
         // UNKNOWN
         else if(p04 == 0x0A01)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                // move to next item
                offset += stride;
               }
           }
         // UNKNOWN
         else if(p04 == 0x0B00)
           {
            for(uint32 k = 0; k < n_vertices; k++)
               {
                // move to offset
                bs.seek(offset);
                if(bs.fail()) return error("Stream seek failure.");

                // move to next item
                offset += stride;
               }
           }
        }

     // insert vertex buffer
     amc.vblist.push_back(vb);
    }

 // success
 return true;

/*
             // 0x0400 UNKNOWN CLOTH INDICES
             else if(vxtype == 0x0400)
               {
                if(format == 0x0500) {
                   uint16 i1 = cs.BE_read_uint08();
                   uint16 i2 = cs.BE_read_uint08();
                   uint16 i3 = cs.BE_read_uint08();
                   uint16 i4 = cs.BE_read_uint08();
                   if(max_cloth_index < i1) max_cloth_index = i1;
                   if(max_cloth_index < i2) max_cloth_index = i2;
                   if(max_cloth_index < i3) max_cloth_index = i3;
                   if(max_cloth_index < i4) max_cloth_index = i4;
                  }
                else
                   return error("Unknown vertex stream 0x0400 type.");
               }
             // 0x0504 UNKNOWN (NOT TEXTURE COORDINATES)
             else if(vxtype == 0x0504)
               {
                if(format == 0x0100) {
                   vb.data[j].uv[4][0] = cs.BE_read_real32();
                   vb.data[j].uv[4][1] = cs.BE_read_real32();
                  }
                else if(format == 0x0A00) {
                   vb.data[j].uv[4][0] = cs.BE_read_real16();
                   vb.data[j].uv[4][1] = cs.BE_read_real16();
                  }
                else {
                   stringstream ss;
                   ss << "0x0504 vertex semantic uses unknown type ";
                   ss << "0x" << hex << format << dec << ".";
                   return error(ss);
                  }
               }
             // 0x0505 UNKNOWN INDICES
             else if(vxtype == 0x0505)
               {
                if(format == 0x0300) {
                   real32 v1 = cs.BE_read_real32(); // NEW! DW8 static geometry!
                   real32 v2 = cs.BE_read_real32();
                   real32 v3 = cs.BE_read_real32();
                   real32 v4 = cs.BE_read_real32();
                  }
                else if(format == 0x0500) {
                   uint16 i1 = cs.BE_read_uint08();
                   uint16 i2 = cs.BE_read_uint08();
                   uint16 i3 = cs.BE_read_uint08();
                   uint16 i4 = cs.BE_read_uint08();
                   if(max_cloth_index < i1) max_cloth_index = i1;
                   if(max_cloth_index < i2) max_cloth_index = i2;
                   if(max_cloth_index < i3) max_cloth_index = i3;
                   if(max_cloth_index < i4) max_cloth_index = i4;
                  }
                else {
                   stringstream ss;
                   ss << "0x0505 vertex semantic uses unknown type ";
                   ss << "0x" << hex << format << dec << ".";
                   return error(ss);
                  }
               }
             // 0x0600 UNKNOWN VECTOR
             else if(vxtype == 0x0600)
               {
                if(format == 0x0300) {
                   real32 ux = cs.BE_read_real32();
                   real32 uy = cs.BE_read_real32();
                   real32 uz = cs.BE_read_real32();
                   real32 uw = cs.BE_read_real32();
                  }
                else if(format == 0x0B00) {
                   real32 ux = cs.BE_read_real16();
                   real32 uy = cs.BE_read_real16();
                   real32 uz = cs.BE_read_real16();
                   real32 uw = cs.BE_read_real16();
                  }
                else
                   return error("Unknown vertex stream 0x0600 type.");
               }
             // 0x0700 UNKNOWN CLOTH VECTOR
             // these values sum to 1.0 and can be negative
             // if all of these values are 0, then this vertex is an anchor point
             // with normal weights and the blend indices, which come after, are
             // divided by 3 like normal blend indices for non-cloth items.
             else if(vxtype == 0x0700)
               {
                if(format == 0x0300) {
                   real32 ux = cs.BE_read_real32();
                   real32 uy = cs.BE_read_real32();
                   real32 uz = cs.BE_read_real32();
                   real32 uw = cs.BE_read_real32();
                   real32 sum = ux + uy + uz + uw;
                   if(ux == 0 && uy == 0 && uz == 0 && uw == 0) {
                      is_anchor_point = true;
                      n_anchors++;
                     }
                  }
                else if(format == 0x0b00) {
                   real32 ux = cs.BE_read_real16();
                   real32 uy = cs.BE_read_real16();
                   real32 uz = cs.BE_read_real16();
                   real32 uw = cs.BE_read_real16();
                   real32 sum = ux + uy + uz + uw;
                   if(ux == 0 && uy == 0 && uz == 0 && uw == 0) {
                      is_anchor_point = true;
                      n_anchors++;
                     }
                  }
                else
                   return error("Unknown vertex stream 0x0700 type.");
               }
             // read 0xFFFFFFFF
             else if(vxtype == 0x0a00)
               {
                if(format == 0x0D00) {
                  }
               }
             // 0x0A01 UNKNOWN VECTOR
             else if(vxtype == 0x0A01)
               {
                if(format == 0x0300) {
                   real32 ux = cs.BE_read_real32();
                   real32 uy = cs.BE_read_real32();
                   real32 uz = cs.BE_read_real32();
                   real32 uw = cs.BE_read_real32();
                  }
                else if(format == 0x0B00) {
                   real32 ux = cs.BE_read_real16();
                   real32 uy = cs.BE_read_real16();
                   real32 uz = cs.BE_read_real16();
                   real32 uw = cs.BE_read_real16();
                  }
                else if(format == 0x0D00) { // SHIN GUNDAM MUSOU
                  }
                else
                   return error("Unknown vertex stream 0x0A01 type.");
               }
             // 0x0B00 UNKNOWN CLOTH INDICES
             else if(vxtype == 0x0B00)
               {
                if(format == 0x0500) {
                   uint16 i1 = cs.BE_read_uint08();
                   uint16 i2 = cs.BE_read_uint08();
                   uint16 i3 = cs.BE_read_uint08();
                   uint16 i4 = cs.BE_read_uint08();
                   if(max_cloth_index < i1) max_cloth_index = i1;
                   if(max_cloth_index < i2) max_cloth_index = i2;
                   if(max_cloth_index < i3) max_cloth_index = i3;
                   if(max_cloth_index < i4) max_cloth_index = i4;
                  }
                else if(format == 0x0D00) { // SHIN GUNDAM MUSOU
                  }
                else
                   return error("Unknown vertex stream 0x0B00 type.");
               }
             else return error("Unknown vertex type in vertex format descriptor.");
            }
        } // end vertex loop
*/
}

bool buildPhase4(MODELDATA& md, ADVANCEDMODELCONTAINER& amc)
{
 // get index buffer data
 G1MG0107DATA& data = md.data0107;
 if(!data.elem) return true;

 // get surface information
 G1MG0108DATA& data08 = md.data0108;
 if(!data08.elem) return true;

 // for each surface, we need to know what the format of the index buffer is
 map<uint32, uint32> format_map;
 for(size_t i = 0; i < data08.elem; i++) {
     auto item = data08.data[i];
     auto ib_ref = item[0x07];
     auto ib_fmt = item[0x09];
     if(ib_fmt == 0x03) ; // triangle list
     else if(ib_fmt == 0x04) ; // triangle strip
     else return error("Unknown index buffer format.", __LINE__);
     typedef map<uint32, uint32>::value_type value_type;
     format_map.insert(value_type(ib_ref, ib_fmt));
    }

 // for each index buffer
 for(size_t i = 0; i < data.elem; i++)
    {
     // create mesh name
     G1MG0107ITEM& item = data.data[i];
     stringstream ss;
     ss << "ibuffer_" << setfill('0') << setw(4) << hex << i << dec;

     // get index buffer format
     auto fmtmap_iter = format_map.find(i);
     if(fmtmap_iter == format_map.end()) return error("Index buffer reference lookup failed.", __LINE__);

     // save index buffer
     AMC_IDXBUFFER ib;
     if(fmtmap_iter->second == 0x3) ib.type = AMC_TRIANGLES;
     else if(fmtmap_iter->second == 0x4) ib.type = AMC_TRISTRIP;
     else return error("Unknown index buffer format.", __LINE__);
     ib.name = ss.str();
     ib.wind = AMC_CW;
     ib.elem = item.elem;
     ib.data = item.data;

     // save index buffer data type
     if(item.type == 0x08) ib.format = AMC_UINT08;
     else if(item.type == 0x10) ib.format = AMC_UINT16;
     else if(item.type == 0x20) ib.format = AMC_UINT32;
     else return error("Unknown index buffer data type.");

     // insert index buffer
     amc.iblist.push_back(ib);
    }

 return true;
}

bool buildPhase5(MODELDATA& md, ADVANCEDMODELCONTAINER& amc)
{
 // nothing to do
 G1MG0108DATA& data = md.data0108;
 if(!data.elem) return true;

 for(uint32 i = 0; i < data.elem; i++)
    {
     // validate input layout index
     boost::shared_array<uint32> item = data.data[i];
     uint32 il_index = item[0x01];
     if(!(il_index < md.data0105.elem)) return error("Input layout reference out of range."); 

     // validate vertex buffer index
     uint32 vb_index = md.data0105.data[il_index].refs[0];
     if(!(vb_index < md.data0104.elem)) return error("Vertex buffer reference out of range.");

     // validate number of vertices
     uint32 n_vertex = md.data0104.data[vb_index].p03;
     uint32 min_vertex_index = item[0x0A];
     uint32 max_vertex_index = item[0x0A] + item[0x0B];
     if(max_vertex_index > n_vertex) {
        stringstream ss;
        ss << "Vertex reference out of range. ";
        ss << "0x" << hex << item[0x0A] << dec << " + ";
        ss << "0x" << hex << item[0x0B] << " is greater than ";
        ss << "0x" << hex << n_vertex << dec << " where vertex buffer index = ";
        ss << "0x" << hex << vb_index << dec << ".";
        return error(ss);
       }

     // create surface name
     stringstream ss;
     ss << "surface_" << setfill('0') << setw(3) << i;

     // create surface
     AMC_SURFACE surface;
     surface.name = ss.str();
     surface.surfmat = static_cast<uint16>(item[0x06]);
     AMC_REFERENCE ref;
     ref.vb_index = il_index;   // vbuffer index (use input layout since non-interleaved buffers possible)
     ref.vb_start = 0;          // use full vertex buffer
     ref.vb_width = n_vertex;   // use full vertex buffer
     ref.ib_index = item[0x07]; // ibuffer index
     ref.ib_start = item[0x0C]; // ibuffer start index
     ref.ib_width = item[0x0D]; // number of indices
     ref.jm_index = item[0x02]; // joint map index
     surface.refs.push_back(ref);
     
     // save surface
     amc.surfaces.push_back(surface);
    }

 return true;
}

bool buildModel(MODELDATA& md)
{
 // construct model
 ADVANCEDMODELCONTAINER amc;
 if(!buildPhase1(md, amc)) return false; // materials and textures
 if(!buildPhase2(md, amc)) return false; // joint mapping
 if(!buildPhase3(md, amc)) return false; // vtx buffers
 if(!buildPhase4(md, amc)) return false; // idx buffers
 if(!buildPhase5(md, amc)) return false; // surfaces

 // transform and save AMC file
 ADVANCEDMODELCONTAINER transformed = TransformAMC(amc);
 SaveAMC(md.pathname.c_str(), md.shrtname.c_str(), transformed);
 SaveOBJ(md.pathname.c_str(), md.shrtname.c_str(), transformed);

 // success
 return true;
}

bool processG1MS(MODELDATA& md)
{
 // debug information
 if(DWGetDebugSkeletonMode()) {
    md.dfile << "-----------" << endl;
    md.dfile << " SKELETONS " << endl;
    md.dfile << "-----------" << endl;
    md.dfile << endl;
    md.dfile << "number of skeletons = 0x" << hex << md.G1MS_list.size() << dec << endl;
    md.dfile << endl;
   }

 for(size_t i = 0; i < md.G1MS_list.size(); i++)
    {
     // read chunk properties
     binary_stream bs = md.G1MS_list[i];
     uint32 chunkname = bs.BE_read_uint32();
     uint32 chunkvers = bs.BE_read_uint32();
     uint32 chunksize = bs.BE_read_uint32();
     if(DWGetDebugSkeletonMode()) {
        md.dfile << "SKELETON[0x" << setfill('0') << setw(2) << i << "]" << endl;
        md.dfile << " HEADER" << endl;
        md.dfile << "  chunkname = 0x" << setfill('0') << setw(8) << hex << chunkname << dec << endl;
        md.dfile << "  chunkvers = 0x" << setfill('0') << setw(8) << hex << chunkvers << dec << endl;
        md.dfile << "  chunksize = 0x" << setfill('0') << setw(8) << hex << chunksize << dec << endl;
       }

     // read skeleton parameters
     uint32 p01 = bs.BE_read_uint32(); // offset to joint data
     uint32 p02 = bs.BE_read_uint32(); // ????
     uint16 p03 = bs.BE_read_uint16(); // number of joints in this file
     uint16 p04 = bs.BE_read_uint16(); // number of joints indices
     uint16 p05 = bs.BE_read_uint16(); // number of 0x8000 parents
     uint16 p06 = bs.BE_read_uint16(); // 0x0000
     if(DWGetDebugSkeletonMode()) {
        md.dfile << " PARAMETERS" << endl;
        md.dfile << "  p01 = 0x" << setfill('0') << setw(8) << hex << p01 << dec << " (offset to joint data)" << endl;
        md.dfile << "  p02 = 0x" << setfill('0') << setw(8) << hex << p02 << dec << " (????)" << endl;
        md.dfile << "  p03 = 0x" << setfill('0') << setw(4) << hex << p03 << dec << " (number of joints)" << endl;
        md.dfile << "  p04 = 0x" << setfill('0') << setw(4) << hex << p04 << dec << " (number of joint indices)" << endl;
        md.dfile << "  p05 = 0x" << setfill('0') << setw(4) << hex << p05 << dec << " (number of joints under roots?)" << endl;
        md.dfile << "  p06 = 0x" << setfill('0') << setw(4) << hex << p06 << dec << " (0x00)" << endl;
       }

     // read identifiers
     boost::shared_array<uint16> idlist(new uint16[p04]);
     bs.BE_read_array(idlist.get(), p04);
     if(bs.fail()) return error("Stream read failure.");
     if(DWGetDebugSkeletonMode()) {
        md.dfile << " JOINT IDENTIFIERS" << endl;
        for(uint32 j = 0; j < p04; j++) {
            md.dfile << "  id[0x" << hex << setfill('0') << setw(4) << j << dec << "] = ";
            md.dfile << "0x" << hex << setfill('0') << setw(4) << idlist[j] << endl;
           }
       }

     // if there are joints and this is a regular skeleton chunk
     // EDIT: in some models, p03 can be less than p04 and there
     // can still be a valid skeleton
     if(p03 && p04)
       {
        // seek joints
        bs.seek(p01);
        if(bs.fail()) return error("Stream seek failure.");

        // create skeleton name
        stringstream ss;
        ss << "skeleton_";
        ss << setfill('0') << setw(2) << hex << i << dec << endl;

        // initialize skeleton
        AMC_SKELETON2 skel;
        skel.format = AMC_JOINT_FORMAT_RELATIVE | AMC_JOINT_FORMAT_MATRIX | AMC_JOINT_FORMAT_X_BONEAXIS;
        skel.name = ss.str();

        // read joints
        struct DWJOINTITEM {
          uint32 id;
          real32 scale[3];
          uint32 parent;
          real32 rotation[4];
          real32 position[4];
        };
        deque<DWJOINTITEM> jointlist;
        for(uint32 j = 0; j < p04; j++) {
            if(idlist[j] == 0xFFFF) continue;
            DWJOINTITEM item;
            item.id = idlist[j];
            item.scale[0] = bs.BE_read_real32();
            item.scale[1] = bs.BE_read_real32();
            item.scale[2] = bs.BE_read_real32();
            item.parent = bs.BE_read_uint32();
            item.rotation[0] = bs.BE_read_real32();
            item.rotation[1] = bs.BE_read_real32();
            item.rotation[2] = bs.BE_read_real32();
            item.rotation[3] = bs.BE_read_real32();
            item.position[0] = bs.BE_read_real32();
            item.position[1] = bs.BE_read_real32();
            item.position[2] = bs.BE_read_real32();
            item.position[3] = bs.BE_read_real32();
            jointlist.push_back(item);
           }

        // debug
        if(DWGetDebugSkeletonMode()) {
           md.dfile << " JOINT DATA" << endl;
           for(uint32 j = 0; j < jointlist.size(); j++) {
               uint32 sx = *reinterpret_cast<uint32*>(&jointlist[j].scale[0]);
               uint32 sy = *reinterpret_cast<uint32*>(&jointlist[j].scale[1]);
               uint32 sz = *reinterpret_cast<uint32*>(&jointlist[j].scale[2]);
               uint32 qx = *reinterpret_cast<uint32*>(&jointlist[j].rotation[0]);
               uint32 qy = *reinterpret_cast<uint32*>(&jointlist[j].rotation[1]);
               uint32 qz = *reinterpret_cast<uint32*>(&jointlist[j].rotation[2]);
               uint32 qw = *reinterpret_cast<uint32*>(&jointlist[j].rotation[3]);
               uint32 px = *reinterpret_cast<uint32*>(&jointlist[j].position[0]);
               uint32 py = *reinterpret_cast<uint32*>(&jointlist[j].position[1]);
               uint32 pz = *reinterpret_cast<uint32*>(&jointlist[j].position[2]);
               uint32 pw = *reinterpret_cast<uint32*>(&jointlist[j].position[3]);
               md.dfile << hex << setfill('0');
               md.dfile << "  joint 0x" << setw(4) << jointlist[j].id << ":";
               md.dfile << " <" << setw(8) << sx << " " << setw(8) << sy << " " << setw(8) << sz << ">";
               md.dfile << " <" << setfill('0') << setw(8) << jointlist[j].parent << ">";
               md.dfile << " <" << setw(8) << qx << " " << setw(8) << qy << " " << setw(8) << qz << " " << setw(8) << qw << ">";
               md.dfile << " <" << setw(8) << px << " " << setw(8) << py << " " << setw(8) << pz << " " << setw(8) << pw << ">";
               md.dfile << dec << endl;
              }
           md.dfile << endl;
          }

        // test for attachment system
        bool attachments = false;
        for(uint32 j = 0; j < jointlist.size(); j++) {
            uint32 parent = jointlist[j].parent;
            uint32 hi = (parent & 0xFFFF0000ul) >> 16;
            uint32 lo = (parent & 0x0000FFFFul);
            if(hi == 0xFFFF) continue;
            if(hi == 0x0000) continue;
            attachments = true;
            break;
           }

        if(p03 != p04) message(" p03 != p04");
        if(attachments) message(" attachments");

        if(attachments)
          {
          }
        else
          {
           // process joints
           for(uint32 j = 0; j < jointlist.size(); j++)
              {
               // parent
               uint32 parent = jointlist[j].parent;
               if(parent == 0xFFFFFFFF) parent = AMC_INVALID_JOINT;
           
               // local rotation
               real32 qx = jointlist[j].rotation[0];
               real32 qy = jointlist[j].rotation[1];
               real32 qz = jointlist[j].rotation[2];
               real32 qw = jointlist[j].rotation[3];
           
               // local position
               real32 px = jointlist[j].position[0];
               real32 py = jointlist[j].position[1];
               real32 pz = jointlist[j].position[2];
               real32 pw = jointlist[j].position[3];
           
               // rotation matrix
               cs::math::quaternion<real32> Q(qw, qx, qy, qz);
               cs::math::matrix4x4<real32> R;
               cs::math::quaternion_to_matrix4x4(&Q.v[0], R.get());
           
               // create joint name
               stringstream ss;
               ss << "jnt_" << setfill('0') << setw(3) << jointlist[j].id;
           
               // create joint
               AMC_JOINT joint;
               joint.name = ss.str();
               joint.id = jointlist[j].id;
               joint.parent = parent;
               joint.m_rel[0x0] = R[0x0];
               joint.m_rel[0x1] = R[0x1];
               joint.m_rel[0x2] = R[0x2];
               joint.m_rel[0x3] = R[0x3];
               joint.m_rel[0x4] = R[0x4];
               joint.m_rel[0x5] = R[0x5];
               joint.m_rel[0x6] = R[0x6];
               joint.m_rel[0x7] = R[0x7];
               joint.m_rel[0x8] = R[0x8];
               joint.m_rel[0x9] = R[0x9];
               joint.m_rel[0xA] = R[0xA];
               joint.m_rel[0xB] = R[0xB];
               joint.m_rel[0xC] = R[0xC];
               joint.m_rel[0xD] = R[0xD];
               joint.m_rel[0xE] = R[0xE];
               joint.m_rel[0xF] = R[0xF];
               joint.p_rel[0] = px;
               joint.p_rel[1] = py;
               joint.p_rel[2] = pz;
               joint.p_rel[3] = 1.0f;
               skel.joints.push_back(joint);
              }
           
           // insert skeleton into model container
           ADVANCEDMODELCONTAINER amc;
           amc.skllist2.push_back(skel);
           
           // save AMC file
           STDSTRINGSTREAM fnss;
           fnss << md.shrtname << TEXT("_skel_") << setfill(TCHAR('0')) << setw(2) << i;
           SaveAMC(md.pathname.c_str(), fnss.str().c_str(), amc);
          }
       }
    }

 return true;
}

bool processG1MM(MODELDATA& md)
{
 // skip
 if(md.G1MM_list.size() == 0) return true;

 // DEBUG BEGIN
 if(DWGetDebugSkeletonMode()) {
    md.dfile << "------" << endl;
    md.dfile << " G1MM " << endl;
    md.dfile << "------" << endl;
    md.dfile << endl;
    md.dfile << "number of G1MM chunks = 0x" << hex << md.G1MM_list.size() << dec << endl;
    md.dfile << endl;
   }
 // DEBUG END

 // read matrix sets
 for(size_t i = 0; i < md.G1MM_list.size(); i++)
    {
     // read chunk properties
     binary_stream bs = md.G1MM_list[i];
     uint32 chunkname = bs.BE_read_uint32();
     uint32 chunkvers = bs.BE_read_uint32();
     uint32 chunksize = bs.BE_read_uint32();
     if(bs.fail()) return error("Stream read failure.", __LINE__);

     if(DWGetDebugSkeletonMode()) {
        md.dfile << "MATRIX[0x" << setfill('0') << setw(2) << i << "]" << endl;
        md.dfile << " HEADER" << endl;
        md.dfile << "  chunkname = 0x" << setfill('0') << setw(8) << hex << chunkname << dec << endl;
        md.dfile << "  chunkvers = 0x" << setfill('0') << setw(8) << hex << chunkvers << dec << endl;
        md.dfile << "  chunksize = 0x" << setfill('0') << setw(8) << hex << chunksize << dec << endl;
       }

     // read number of entries
     uint32 n_entries = bs.BE_read_uint32();
     if(bs.fail()) return error("Stream read failure.", __LINE__);

     // nothing to do
     if(!n_entries) continue;

     // read matrices
     boost::shared_array<boost::shared_array<real32>> data(new boost::shared_array<real32>[n_entries]);
     for(uint32 j = 0; j < n_entries; j++) {
         boost::shared_array<real32> item(new real32[16]);
         bs.BE_read_array(item.get(), 16);
         if(bs.fail()) return error("Stream read failure.", __LINE__);
         data[j] = item;
        }

     // debug
     if(DWGetDebugSkeletonMode()) {
        for(uint32 j = 0; j < n_entries; j++) {
            md.dfile << hex << setfill('0') << "  ";
            md.dfile << "matrix[0x" << setw(2) << j << "] =";
            md.dfile << " <" << data[j][0x0] << ", " << data[j][0x1] << ", " << data[j][0x2] << ", " << data[j][0x3] << ">";
            md.dfile << " <" << data[j][0x4] << ", " << data[j][0x5] << ", " << data[j][0x6] << ", " << data[j][0x7] << ">";
            md.dfile << " <" << data[j][0x8] << ", " << data[j][0x9] << ", " << data[j][0xA] << ", " << data[j][0xB] << ">";
            md.dfile << " <" << data[j][0xC] << ", " << data[j][0xD] << ", " << data[j][0xE] << ", " << data[j][0xF] << ">";
            md.dfile << dec << endl;
           }
        md.dfile << endl;
       }
    }

 return true;
}

bool processNUNO(MODELDATA& md)
{
 // skip
 if(md.NUNO_list.size() == 0) return true;

 // DEBUG BEGIN
 if(DWGetDebugModelMode()) {
    md.dfile << "------" << endl;
    md.dfile << " NUNO " << endl;
    md.dfile << "------" << endl;
    md.dfile << endl;
    md.dfile << "number of NUNO chunks = 0x" << hex << md.NUNO_list.size() << dec << endl;
    md.dfile << endl;
   }
 // DEBUG END

 // number of NUNO chunks must be 0 or 1
 uint32 n_NUNO = md.NUNO_list.size();
 if(n_NUNO != 0 && n_NUNO != 1) return error("Number of NUNOs must be 0 or 1.");

 // read header
 binary_stream& bs = md.NUNO_list[0];
 uint32 h01 = bs.BE_read_uint32(); // 0x4E554E4F (NUNO)
 uint32 h02 = bs.BE_read_uint32(); // 0x30303234 (0024)
 uint32 h03 = bs.BE_read_uint32(); // chunksize
 uint32 h04 = bs.BE_read_uint32(); // number of subchunks
 if(DWGetDebugModelMode()) {
    md.dfile << "HEADER" << endl;
    md.dfile << hex << setfill('0');
    md.dfile << " chunkname = 0x" << setw(8) << h01 << endl;
    md.dfile << " chunkvers = 0x" << setw(8) << h02 << endl;
    md.dfile << " chunksize = 0x" << setw(8) << h03 << endl;
    md.dfile << " subchunks = 0x" << setw(8) << h04 << endl;
    md.dfile << dec;
   }

 // validate header
 if(h01 != 0x4E554E4F) return error("Not a NUNO chunk.");
 switch(h02) {
   case(0x30303234) : break;
   default : return error("Unsupported NUNO version.");
  }
 if(h03 == 0) return error("Invalid NUNO chunksize.");
 if(h04 == 0) return error("Invalid number of NUNO subchunks.");

 // save offsets to subchunks
 binary_stream::size_type s00030001_offset = 0x00;
 binary_stream::size_type s00030002_offset = 0x00;

 // scan subchunks
 if(DWGetDebugModelMode()) md.dfile << "SUBCHUNK LIST" << endl;
 for(uint32 i = 0; i < h04; i++)
    {
     // read subchunk properties
     uint32 subchunk_type = bs.BE_read_uint32();
     uint32 subchunk_size = bs.BE_read_uint32();
     if(bs.fail()) return error("NUNO stream read failure.");
     if(DWGetDebugModelMode()) {
        md.dfile << hex << setfill('0');
        md.dfile << " SUBCHUNK[0x" << i << "]" << endl;
        md.dfile << "  type = 0x" << setw(8) << subchunk_type << endl;
        md.dfile << "  size = 0x" << setw(8) << subchunk_size << endl;
        md.dfile << dec;
       }

     // save offset
     switch(subchunk_type) {
       case(0x00030001) : s00030001_offset = bs.tell(); break;
       case(0x00030002) : s00030002_offset = bs.tell(); break;
       default : return error("Unsupported NUNO subchunk type.");
      }

     // move to next subchunk
     bs.move(subchunk_size - 0x08);
     if(bs.fail()) return error("NUNO stream seek failure.");
    }

 // if there is an 0x00030001 subchunk
 if(s00030001_offset)
   {
    // move to 0x00030001 subchunk
    bs.seek(s00030001_offset);
    if(bs.fail()) return error("NUNO stream seek failure.");
   
    // read number of 0x00030001 entries
    uint32 n_entries = bs.BE_read_uint32();
    if(bs.fail()) return error("NUNO stream read failure.");

    // debug
    if(DWGetDebugModelMode()) {
       md.dfile << "SUBCHUNK DATA 0x00030001" << endl;
       md.dfile << hex << setfill('0');
       md.dfile << " number of entries = 0x" << setw(8) << n_entries << endl;
       md.dfile << dec;
      }

    // for each 0x00030001 entry
    for(uint32 i = 0; i < n_entries; i++)
       {
        // read entry header
        NUNOSUBCHUNK0301ENTRY item;
        item.h01 = bs.BE_read_uint32();
        item.h02 = bs.BE_read_uint32();
        item.h03 = bs.BE_read_uint32();
        item.h04 = bs.BE_read_uint32();
        item.h05 = bs.BE_read_uint32();
        item.h06 = bs.BE_read_uint32();
        item.h07 = bs.BE_read_real32();
        item.h08 = bs.BE_read_real32();
        item.h09 = bs.BE_read_uint32();
        bs.BE_read_array(&item.h10[0], 4);
        bs.BE_read_array(&item.h11[0], 4);
        item.h12 = bs.BE_read_real32();
        item.h13 = bs.BE_read_uint32();
        bs.BE_read_array(&item.h14[0], 3);
        bs.BE_read_array(&item.h15[0], 3);
        if(bs.fail()) return error("NUNO stream read failure.");
   
        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << setfill('0');
           md.dfile << " ENTRY[0x" << hex << i << dec << "]" << endl;
           md.dfile << "  h01 = 0x" << hex << setw(8) << item.h01 << dec << " ()" << endl;
           md.dfile << "  h02 = 0x" << hex << setw(8) << item.h02 << dec << " (number of control points)" << endl;
           md.dfile << "  h03 = 0x" << hex << setw(8) << item.h03 << dec << " ()" << endl;
           md.dfile << "  h04 = 0x" << hex << setw(8) << item.h04 << dec << " ()" << endl;
           md.dfile << "  h05 = 0x" << hex << setw(8) << item.h05 << dec << " ()" << endl;
           md.dfile << "  h06 = 0x" << hex << setw(8) << item.h06 << dec << " ()" << endl;
           md.dfile << "  h07 = " << item.h07 << " ()" << endl;
           md.dfile << "  h08 = " << item.h08 << " ()" << endl;
           md.dfile << "  h09 = 0x" << hex << setw(8) << item.h09 << dec << " ()" << endl;
           md.dfile << "  h10 = <" << item.h10[0] << ", " << item.h10[1] << ", " << item.h10[2] << ", " << item.h10[3] << ">" << " ()" << endl;
           md.dfile << "  h11 = <" << item.h11[0] << ", " << item.h11[1] << ", " << item.h11[2] << ", " << item.h11[3] << ">" << " ()" << endl;
           md.dfile << "  h12 = " << item.h12 << " ()" << endl;
           md.dfile << "  h13 = 0x" << hex << item.h13 << dec << " ()" << endl;
           md.dfile << "  h14 = <" << item.h14[0] << ", " << item.h14[1] << ", " << item.h14[2] << ">" << " ()" << endl;
           md.dfile << "  h15 = <" << item.h15[0] << ", " << item.h15[1] << ", " << item.h15[2] << ">" << " ()" << endl;
          }

        // the number of control points must be valid
        if(!item.h02) return error("The number of NUNO control points cannot be zero.");
   
        // read control points
        item.p01.reset(new array<real32,4>[item.h02]);
        for(uint32 j = 0; j < item.h02; j++) {
            bs.BE_read_array(&item.p01[j][0], 4);
            if(bs.fail()) return error("NUNO stream read failure.");
           }
        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << "  CONTROL POINTS" << endl;
           for(uint32 j = 0; j < item.h02; j++) {
               md.dfile << "   point[0x" << hex << j << dec << "] = ";
               md.dfile << "<" << item.p01[j][0] << ", " << item.p01[j][1] << ", " << item.p01[j][2] << ", " << item.p01[j][3] << ">" << endl;
              }
          }

        // read influence data
        item.p02.reset(new NUNOSUBCHUNK0301ENTRY_DATATYPE1[item.h02]);
        for(uint32 j = 0; j < item.h02; j++) {
            item.p02[j].p01 = bs.BE_read_uint32(); // index to another point
            item.p02[j].p02 = bs.BE_read_uint32(); // index to another point
            item.p02[j].p03 = bs.BE_read_uint32(); // index to another point
            item.p02[j].p04 = bs.BE_read_uint32(); // index to another point
            item.p02[j].p05 = bs.BE_read_real32(); // ???
            item.p02[j].p06 = bs.BE_read_real32(); // ???
            if(bs.fail()) return error("NUNO stream read failure.");
           }
        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << "  INFLUENCE DATA" << endl;
           for(uint32 j = 0; j < item.h02; j++) {
               md.dfile << "   influence[0x" << hex << j << dec << "] = ";
               md.dfile << setfill('0');
               md.dfile << "<" << setw(8) << hex << item.p02[j].p01 << dec << ", " <<
                                  setw(8) << hex << item.p02[j].p02 << dec << ", " <<
                                  setw(8) << hex << item.p02[j].p03 << dec << ", " <<
                                  setw(8) << hex << item.p02[j].p04 << dec << "> - ";
               md.dfile << "<" << item.p02[j].p05 << ", " << item.p02[j].p06 << ">";
               md.dfile << endl;
              }
          }

        // read ??? data
        item.p03.reset(new NUNOSUBCHUNK0301ENTRY_DATATYPE2[item.h03]);
        for(uint32 j = 0; j < item.h03; j++) {
            bs.BE_read_array(&item.p03[j].p01[0], 4);
            bs.BE_read_array(&item.p03[j].p02[0], 4);
            item.p03[j].p03 = bs.BE_read_uint32();
            item.p03[j].p04 = bs.BE_read_uint32();
            item.p03[j].p05 = bs.BE_read_uint32();
            item.p03[j].p06 = bs.BE_read_uint32();
            if(bs.fail()) return error("NUNO stream read failure.");
           }
        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << "  UNKNOWN DATA" << endl;
           for(uint32 j = 0; j < item.h03; j++) {
               md.dfile << "   unknown[0x" << hex << j << dec << "] = ";
               md.dfile << setfill('0');
               md.dfile << setw(8) << hex << item.p03[j].p03 << dec << " ";
               md.dfile << setw(8) << hex << item.p03[j].p04 << dec << " ";
               md.dfile << setw(8) << hex << item.p03[j].p05 << dec << " ";
               md.dfile << setw(8) << hex << item.p03[j].p06 << dec << " ";
               md.dfile << "<" << item.p03[j].p01[0] << ", " <<
                                  item.p03[j].p01[1] << ", " <<
                                  item.p03[j].p01[2] << ", " <<
                                  item.p03[j].p01[3] << ">";
               md.dfile << " ";
               md.dfile << "<" << item.p03[j].p02[0] << ", " <<
                                  item.p03[j].p02[1] << ", " <<
                                  item.p03[j].p02[2] << ", " <<
                                  item.p03[j].p02[3] << ">";
               md.dfile << endl;
              }
          }

        // read 1st index set
        if(item.h04) {
           item.p04.reset(new uint32[item.h04]);
           bs.BE_read_array(&item.p04[0], item.h04);
           if(bs.fail()) return error("NUNO stream read failure.");
          }
        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << "  INDEX SET #1" << endl;
           for(uint32 j = 0; j < item.h04; j++) {
               md.dfile << "   index[0x" << hex << j << dec << "] = ";
               md.dfile << setfill('0') << setw(8) << hex << item.p04[j] << dec << endl;
              }
          }

        // read 2nd index set
        if(item.h05) {
           item.p05.reset(new uint32[item.h05]);
           bs.BE_read_array(&item.p05[0], item.h05);
           if(bs.fail()) return error("NUNO stream read failure.");
          }
        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << "  INDEX SET #2" << endl;
           for(uint32 j = 0; j < item.h05; j++) {
               md.dfile << "   index[0x" << hex << j << dec << "] = ";
               md.dfile << setfill('0') << setw(8) << hex << item.p05[j] << dec << endl;
              }
          }

        // read 3rd index set
        if(item.h06) {
           item.p06.reset(new uint32[item.h06]);
           bs.BE_read_array(&item.p06[0], item.h06);
           if(bs.fail()) return error("NUNO stream read failure.");
          }
        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << "  INDEX SET #3" << endl;
           for(uint32 j = 0; j < item.h06; j++) {
               md.dfile << "   index[0x" << hex << j << dec << "] = ";
               md.dfile << setfill('0') << setw(8) << hex << item.p06[j] << dec << endl;
              }
          }

        // insert item
        md.nuno._0301.push_back(item);
       }
   
    // TODO: DELETE ME
    // save obj file
   
    STDSTRINGSTREAM objname;
    objname << md.pathname << md.shrtname << TEXT("_NUNO.obj");
    ofstream objfile(objname.str().c_str());
    objfile << "o " << "object_" << md.shrtname.c_str() << endl;
   
    // save control points
    for(uint32 i = 0; i < md.nuno._0301.size(); i++) {
        objfile << "# NUNO ENTRY 0x" << hex << i << dec << endl;
        NUNOSUBCHUNK0301ENTRY& item = md.nuno._0301[i];
        for(uint32 j = 0; j < item.h02; j++)
            objfile << "v " << item.p01[j][0] << " " << item.p01[j][1] << " " << item.p01[j][2] << endl;
        objfile << endl;
       }
   
    // save control connectivities
    uint32 vertex_index = 1;
    for(uint32 i = 0; i < md.nuno._0301.size(); i++) {
        objfile << "# NUNO ENTRY 0x" << hex << i << dec << endl;
        objfile << "g group_" << i << endl;
        NUNOSUBCHUNK0301ENTRY& item = md.nuno._0301[i];
        for(uint32 j = 0; j < item.h02; j++) {
            uint32 a[4] = { item.p02[j].p01, item.p02[j].p02, item.p02[j].p03, item.p02[j].p04 };
            if(a[0] != 0xFFFFFFFF) objfile << "f " << (vertex_index + j) << " " << (vertex_index + a[0]) << endl;
            if(a[1] != 0xFFFFFFFF) objfile << "f " << (vertex_index + j) << " " << (vertex_index + a[1]) << endl;
            if(a[2] != 0xFFFFFFFF) objfile << "f " << (vertex_index + j) << " " << (vertex_index + a[2]) << endl;
            if(a[3] != 0xFFFFFFFF) objfile << "f " << (vertex_index + j) << " " << (vertex_index + a[3]) << endl;
           }
        objfile << endl;
        vertex_index += item.h02;
       }
   }

 // finished
 if(DWGetDebugModelMode()) md.dfile << endl;
 return true;
}

bool processNUNV(MODELDATA& md)
{
 // skip
 if(md.NUNV_list.size() == 0) return true;

 // DEBUG BEGIN
 if(DWGetDebugModelMode()) {
    md.dfile << "------" << endl;
    md.dfile << " NUNV " << endl;
    md.dfile << "------" << endl;
    md.dfile << endl;
    md.dfile << "number of NUNV chunks = 0x" << hex << md.NUNV_list.size() << dec << endl;
    md.dfile << endl;
   }
 // DEBUG END

 // number of NUNV chunks must be 0 or 1
 uint32 n_NUNV = md.NUNV_list.size();
 if(n_NUNV != 1) return error("Number of NUNVs must be 0 or 1.");

 // read header
 binary_stream& bs = md.NUNV_list[0];
 uint32 h01 = bs.BE_read_uint32(); // 0x4E554E56 (NUNV)
 uint32 h02 = bs.BE_read_uint32(); // 0x30303130 (0010)
 uint32 h03 = bs.BE_read_uint32(); // chunksize
 uint32 h04 = bs.BE_read_uint32(); // number of subchunks
 if(DWGetDebugModelMode()) {
    md.dfile << "HEADER" << endl;
    md.dfile << hex << setfill('0');
    md.dfile << " chunkname = 0x" << setw(8) << h01 << endl;
    md.dfile << " chunkvers = 0x" << setw(8) << h02 << endl;
    md.dfile << " chunksize = 0x" << setw(8) << h03 << endl;
    md.dfile << " subchunks = 0x" << setw(8) << h04 << endl;
    md.dfile << dec;
   }

 // validate header
 if(h01 != 0x4E554E56) return error("Not a NUNV chunk.");
 switch(h02) {
   case(0x30303130) : break;
   default : return error("Unsupported NUNV version.");
  }
 if(h03 == 0) return error("Invalid NUNV chunksize.");
 if(h04 == 0) return error("Invalid number of NUNV subchunks.");

 // save offsets to subchunks
 binary_stream::size_type s0501_offset = 0x00;
 binary_stream::size_type s0502_offset = 0x00;

 // scan subchunks
 if(DWGetDebugModelMode()) md.dfile << "SUBCHUNK LIST" << endl;
 for(uint32 i = 0; i < h04; i++)
    {
     // read subchunk properties
     uint32 subchunk_type = bs.BE_read_uint32();
     uint32 subchunk_size = bs.BE_read_uint32();
     if(bs.fail()) return error("NUNV stream read failure.");
     if(DWGetDebugModelMode()) {
        md.dfile << hex << setfill('0');
        md.dfile << " SUBCHUNK[0x" << i << "]" << endl;
        md.dfile << "  type = 0x" << setw(8) << subchunk_type << endl;
        md.dfile << "  size = 0x" << setw(8) << subchunk_size << endl;
        md.dfile << dec;
       }

     // save offset
     switch(subchunk_type) {
       case(0x00050001) : s0501_offset = bs.tell(); break;
       case(0x00050002) : s0502_offset = bs.tell(); break;
       default : return error("Unsupported NUNV subchunk type.");
      }

     // move to next subchunk
     bs.move(subchunk_size - 0x08);
     if(bs.fail()) return error("NUNV stream seek failure.");
    }

 // if there is an 0x00050001 subchunk
 if(s0501_offset)
   {
    // move to 0x00050001 subchunk
    bs.seek(s0501_offset);
    if(bs.fail()) return error("NUNV stream seek failure.");
   
    // read number of 0x00050001 entries
    uint32 n_entries = bs.BE_read_uint32();
    if(bs.fail()) return error("NUNV stream read failure.");

    // debug
    if(DWGetDebugModelMode()) {
       md.dfile << "SUBCHUNK DATA 0x00050001" << endl;
       md.dfile << hex << setfill('0');
       md.dfile << " number of entries = 0x" << setw(8) << n_entries << endl;
       md.dfile << dec;
      }

    // for each 0x00050001 entry
    for(uint32 i = 0; i < n_entries; i++)
       {
        // read entry header
        NUNV0501ENTRY item;
        item.h01 = bs.BE_read_uint32();
        item.h02 = bs.BE_read_uint32();
        item.h03 = bs.BE_read_uint32();
        item.h04 = bs.BE_read_uint32();
        item.h05 = bs.BE_read_uint32();
        item.h06 = bs.BE_read_real32();
        bs.BE_read_array(&item.h07[0], 3);
        bs.BE_read_array(&item.h08[0], 3);
        bs.BE_read_array(&item.h09[0], 3);
        bs.BE_read_array(&item.h10[0], 3);
        bs.BE_read_array(&item.h11[0], 3);
        bs.BE_read_array(&item.h12[0], 3);
        item.h13 = bs.BE_read_uint32(); // 0x00010100
        if(bs.fail()) return error("NUNV stream read failure.");

        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << setfill('0');
           md.dfile << " ENTRY[0x" << hex << i << dec << "]" << endl;
           md.dfile << "  h01 = 0x" << hex << setw(8) << item.h01 << dec << " ()" << endl;
           md.dfile << "  h02 = 0x" << hex << setw(8) << item.h02 << dec << " (number of control points)" << endl;
           md.dfile << "  h03 = 0x" << hex << setw(8) << item.h03 << dec << " ()" << endl;
           md.dfile << "  h04 = 0x" << hex << setw(8) << item.h04 << dec << " ()" << endl;
           md.dfile << "  h05 = 0x" << hex << setw(8) << item.h05 << dec << " ()" << endl;
           md.dfile << "  h06 = " << item.h06 << " ()" << endl;
           md.dfile << "  h07 = <" << item.h07[0] << ", " << item.h07[1] << ", " << item.h07[2] << ">" << " ()" << endl;
           md.dfile << "  h08 = <" << item.h08[0] << ", " << item.h08[1] << ", " << item.h08[2] << ">" << " ()" << endl;
           md.dfile << "  h09 = <" << item.h09[0] << ", " << item.h09[1] << ", " << item.h09[2] << ">" << " ()" << endl;
           md.dfile << "  h10 = <" << item.h10[0] << ", " << item.h10[1] << ", " << item.h10[2] << ">" << " ()" << endl;
           md.dfile << "  h11 = <" << item.h11[0] << ", " << item.h11[1] << ", " << item.h11[2] << ">" << " ()" << endl;
           md.dfile << "  h12 = <" << item.h12[0] << ", " << item.h12[1] << ", " << item.h12[2] << ">" << " ()" << endl;
           md.dfile << "  h13 = 0x" << hex << item.h13 << dec << " ()" << endl;
          }

        // the number of control points must be valid
        if(!item.h02) return error("The number of NUNV control points cannot be zero.");
        if(!item.h03) return error("NUNV h03 == 0.");
   
        // read control points
        item.p01.reset(new NUNV0501SUBENTRY1[item.h02]);
        for(uint32 j = 0; j < item.h02; j++) {
            item.p01[j].p01 = bs.BE_read_real32();
            item.p01[j].p02 = bs.BE_read_real32();
            item.p01[j].p03 = bs.BE_read_real32();
            item.p01[j].p04 = bs.BE_read_real32();
            if(bs.fail()) return error("NUNV stream read failure.");
           }
        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << "  CONTROL POINTS" << endl;
           for(uint32 j = 0; j < item.h02; j++) {
               md.dfile << "   point[0x" << hex << j << dec << "] = ";
               md.dfile << "<" << item.p01[j].p01 << ", " << item.p01[j].p02 << ", " << item.p01[j].p03 << ", " << item.p01[j].p04 << ">" << endl;
              }
          }

        // read influence data
        item.p02.reset(new NUNV0501SUBENTRY2[item.h02]);
        for(uint32 j = 0; j < item.h02; j++) {
            item.p02[j].p01 = bs.BE_read_uint32(); // index to another point
            item.p02[j].p02 = bs.BE_read_uint32(); // index to another point
            item.p02[j].p03 = bs.BE_read_uint32(); // index to another point
            item.p02[j].p04 = bs.BE_read_uint32(); // index to another point
            item.p02[j].p05 = bs.BE_read_real32(); // ???
            item.p02[j].p06 = bs.BE_read_real32(); // ???
            if(bs.fail()) return error("NUNV stream read failure.");
           }
        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << "  INFLUENCE DATA" << endl;
           for(uint32 j = 0; j < item.h02; j++) {
               md.dfile << "   influence[0x" << hex << j << dec << "] = ";
               md.dfile << setfill('0');
               md.dfile << "<" << setw(8) << hex << item.p02[j].p01 << dec << ", " <<
                                  setw(8) << hex << item.p02[j].p02 << dec << ", " <<
                                  setw(8) << hex << item.p02[j].p03 << dec << ", " <<
                                  setw(8) << hex << item.p02[j].p04 << dec << "> - ";
               md.dfile << "<" << item.p02[j].p05 << ", " << item.p02[j].p06 << ">";
               md.dfile << endl;
              }
          }

        // read ??? data
        item.p03.reset(new NUNV0501SUBENTRY3[item.h03]);
        for(uint32 j = 0; j < item.h03; j++) {
            bs.BE_read_array(&item.p03[j].p01[0], 4);
            bs.BE_read_array(&item.p03[j].p02[0], 4);
            item.p03[j].p03 = bs.BE_read_uint32();
            item.p03[j].p04 = bs.BE_read_uint32();
            item.p03[j].p05 = bs.BE_read_uint32();
            item.p03[j].p06 = bs.BE_read_uint32();
            if(bs.fail()) return error("NUNV stream read failure.");
           }
        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << "  UNKNOWN DATA" << endl;
           for(uint32 j = 0; j < item.h03; j++) {
               md.dfile << "   unknown[0x" << hex << j << dec << "] = ";
               md.dfile << setfill('0');
               md.dfile << setw(8) << hex << item.p03[j].p03 << dec << " ";
               md.dfile << setw(8) << hex << item.p03[j].p04 << dec << " ";
               md.dfile << setw(8) << hex << item.p03[j].p05 << dec << " ";
               md.dfile << setw(8) << hex << item.p03[j].p06 << dec << " ";
               md.dfile << "<" << item.p03[j].p01[0] << ", " <<
                                  item.p03[j].p01[1] << ", " <<
                                  item.p03[j].p01[2] << ", " <<
                                  item.p03[j].p01[3] << ">";
               md.dfile << " ";
               md.dfile << "<" << item.p03[j].p02[0] << ", " <<
                                  item.p03[j].p02[1] << ", " <<
                                  item.p03[j].p02[2] << ", " <<
                                  item.p03[j].p02[3] << ">";
               md.dfile << endl;
              }
          }

        // read 1st index set
        if(item.h04) {
           item.p04.reset(new uint32[item.h04]);
           bs.BE_read_array(&item.p04[0], item.h04);
           if(bs.fail()) return error("NUNV stream read failure.");
          }
        // debug
        if(DWGetDebugModelMode()) {
           md.dfile << "  INDEX SET #1" << endl;
           for(uint32 j = 0; j < item.h04; j++) {
               md.dfile << "   index[0x" << hex << j << dec << "] = ";
               md.dfile << setfill('0') << setw(8) << hex << item.p04[j] << dec << endl;
              }
          }
   
        // insert into NUNV data
        md.nunv._0501.push_back(item);
       }
   
    // TODO: DELETE ME
    // save obj file
   
    STDSTRINGSTREAM objname;
    objname << md.pathname << md.shrtname << TEXT("_NUNV.obj");
    ofstream objfile(objname.str().c_str());
    objfile << "o " << "object_" << md.shrtname.c_str() << endl;
   
    // save control points
    for(uint32 i = 0; i < md.nunv._0501.size(); i++) {
        objfile << "# NUNV ENTRY 0x" << hex << i << dec << endl;
        NUNV0501ENTRY& item = md.nunv._0501[i];
        for(uint32 j = 0; j < item.h02; j++)
            objfile << "v " << item.p01[j].p01 << " " << item.p01[j].p02 << " " << item.p01[j].p03 << endl;
        objfile << endl;
       }
   
    // save control connectivities
    uint32 vertex_index = 1;
    for(uint32 i = 0; i < md.nunv._0501.size(); i++) {
        objfile << "# NUNV ENTRY 0x" << hex << i << dec << endl;
        objfile << "g group_" << i << endl;
        NUNV0501ENTRY& item = md.nunv._0501[i];
        for(uint32 j = 0; j < item.h02; j++) {
            uint32 a[4] = { item.p02[j].p01, item.p02[j].p02, item.p02[j].p03, item.p02[j].p04 };
            if(a[0] != 0xFFFFFFFF) objfile << "f " << (vertex_index + j) << " " << (vertex_index + a[0]) << endl;
            if(a[1] != 0xFFFFFFFF) objfile << "f " << (vertex_index + j) << " " << (vertex_index + a[1]) << endl;
            if(a[2] != 0xFFFFFFFF) objfile << "f " << (vertex_index + j) << " " << (vertex_index + a[2]) << endl;
            if(a[3] != 0xFFFFFFFF) objfile << "f " << (vertex_index + j) << " " << (vertex_index + a[3]) << endl;
           }
        objfile << endl;
        vertex_index += item.h02;
       }
   }

 // finished
 if(DWGetDebugModelMode()) md.dfile << endl;
 return true;
}

bool processG1MG(MODELDATA& md)
{
 // skip
 if(md.G1MG_list.size() == 0) return true;

 // DEBUG BEGIN
 if(DWGetDebugModelMode()) {
    md.dfile << "------" << endl;
    md.dfile << " G1MG " << endl;
    md.dfile << "------" << endl;
    md.dfile << endl;
    md.dfile << "number of G1MG chunks = 0x" << hex << md.G1MG_list.size() << dec << endl;
    md.dfile << endl;
   }
 // DEBUG END

 // number of NUNV chunks must be 0 or 1
 if(md.G1MG_list.size() != 1) return error("Number of G1MGs must be 0 or 1.");

 // read header
 binary_stream& bs = md.G1MG_list[0];
 uint32 chunkname = bs.BE_read_uint32();
 uint32 chunkvers = bs.BE_read_uint32();
 uint32 chunksize = bs.BE_read_uint32();

 // validate version
 switch(chunkvers) {
   case(0x30303434) : break;
   default: message("Unknown G1MG version! Models may or may not extract.");
  }

 // read header
 uint32 head01 = bs.BE_read_uint32(); // platform
 uint32 head02 = bs.BE_read_uint32(); // 0x00
 real32 head03 = bs.BE_read_real32(); // min_x
 real32 head04 = bs.BE_read_real32(); // min_y
 real32 head05 = bs.BE_read_real32(); // min_z
 real32 head06 = bs.BE_read_real32(); // max_x
 real32 head07 = bs.BE_read_real32(); // max_y
 real32 head08 = bs.BE_read_real32(); // max_z
 uint32 head09 = bs.BE_read_uint32(); // sections

 // validate header
 switch(head01) {
   case(0x50533300) : break; // PS3
   case(0x58333630) : break; // X360
   case(0x57696955) : break; // WiiU
   default: return error("Only PS3, XBox360, and WiiU versions of this game are supported.");
  }
 if(head09 == 0) return error("Invalid number of G1MG sections.");

 // read sections
 for(uint32 i = 0; i < head09; i++)
    {
     // section information
     uint32 section_type = bs.BE_read_uint32();
     uint32 section_size = bs.BE_read_uint32();
     section_size -= 0x8;

     // read section
     boost::shared_array<char> section_data(new char[section_size]);
     bs.BE_read_array(section_data.get(), section_size);
     if(md.ifile.fail()) return error("Read failure.");

     if(section_type == 0x00010001) {
        md.section01.type = section_type;
        md.section01.data = section_data;
        md.section01.size = section_size;
       }
     else if(section_type == 0x00010002) {
        md.section02.type = section_type;
        md.section02.data = section_data;
        md.section02.size = section_size;
       }
     else if(section_type == 0x00010003) {
        md.section03.type = section_type;
        md.section03.data = section_data;
        md.section03.size = section_size;
       }
     else if(section_type == 0x00010004) {
        md.section04.type = section_type;
        md.section04.data = section_data;
        md.section04.size = section_size;
       }
     else if(section_type == 0x00010005) {
        md.section05.type = section_type;
        md.section05.data = section_data;
        md.section05.size = section_size;
       }
     else if(section_type == 0x00010006) {
        md.section06.type = section_type;
        md.section06.data = section_data;
        md.section06.size = section_size;
       }
     else if(section_type == 0x00010007) {
        md.section07.type = section_type;
        md.section07.data = section_data;
        md.section07.size = section_size;
       }
     else if(section_type == 0x00010008) {
        md.section08.type = section_type;
        md.section08.data = section_data;
        md.section08.size = section_size;
       }
     else if(section_type == 0x00010009) {
        md.section09.type = section_type;
        md.section09.data = section_data;
        md.section09.size = section_size;
       }
     else {
        stringstream ss;
        ss << "Unknown G1MG section 0x" << hex << section_type << dec << ".";
        return error(ss);
       }
    }

 // process sections
 if(!process0101(md)) return false;
 if(!process0102(md)) return false;
 if(!process0103(md)) return false;
 if(!process0104(md)) return false;
 if(!process0105(md)) return false;
 if(!process0106(md)) return false;
 if(!process0107(md)) return false;
 if(!process0108(md)) return false;
 if(!process0109(md)) return false;

 // construct model
 return buildModel(md);
}

bool processG1M(LPCTSTR filename)
{
 // model data
 MODELDATA md;
 md.filename = filename;
 md.pathname = GetPathnameFromFilename(md.filename.c_str()).get();
 md.shrtname = GetShortFilenameWithoutExtension(md.filename.c_str()).get();

 // open file
 md.ifile.open(md.filename.c_str(), ios::binary);
 if(!md.ifile) return error("Could not open file.");

 // debug
 if(DWGetDebugModelMode() || DWGetDebugSkeletonMode()) {
    md.dfile.close();
    STDSTRINGSTREAM ss;
    ss << md.pathname << md.shrtname << TEXT(".txt");
    md.dfile.open(ss.str().c_str());
   }

 // read header
 uint32 head01 = BE_read_uint32(md.ifile); // magic
 uint32 head02 = BE_read_uint32(md.ifile); // version
 uint32 head03 = BE_read_uint32(md.ifile); // filesize
 uint32 head04 = BE_read_uint32(md.ifile); // offset to 1st chunk
 uint32 head05 = BE_read_uint32(md.ifile); // 0x00
 uint32 head06 = BE_read_uint32(md.ifile); // number of chunks to read
 if(md.ifile.fail()) return error("Read failure.");

 // little endian PC format not supported
 if(head01 != 0x47314D5F) return message("Little Endian PC format not supported.");

 // validate header
 if(head01 != 0x47314D5F) return error("Expecting G1M_ section.");
 if(head03 == 0) return error("Invalid G1M_.");
 if(head04 == 0) return error("Invalid G1M_.");
 if(head06 == 0) return error("Invalid G1M_.");

 // validate version
 switch(head02) {
   case(0x30303334) : break; // OK, OPKM 1
   case(0x30303335) : break; // OK, OPKM 2
   case(0x30303336) : break; // OK, Shin Gundam Musou
   default : return error("Invalid G1M_ version.");
  }

 // move to start
 md.ifile.seekg(head04);
 if(md.ifile.fail()) return error("Seek failure.");

 // read chunks
 for(uint32 i = 0; i < head06; i++)
    {
     // read first chunk
     uint32 cposition = (uint32)md.ifile.tellg(); // save position
     uint32 chunkname = BE_read_uint32(md.ifile); // chunk name
     uint32 chunkvers = BE_read_uint32(md.ifile); // chunk version
     uint32 chunksize = BE_read_uint32(md.ifile); // chunk size

     // G1MF
     if(chunkname == 0x47314D46)
       {
        // seek data
        md.ifile.seekg(cposition);
        if(md.ifile.fail()) return error("Seek failure.");

        // read data
        boost::shared_array<char> data(new char[chunksize]);
        BE_read_array(md.ifile, data.get(), chunksize);
        if(md.ifile.fail()) return error("Read failure.");
        
        // save data
        md.G1MF_list.push_back(binary_stream(data, chunksize));
       }
     // G1MS
     else if(chunkname == 0x47314D53)
       {
        // seek data
        md.ifile.seekg(cposition);
        if(md.ifile.fail()) return error("Seek failure.");

        // read data
        boost::shared_array<char> data(new char[chunksize]);
        BE_read_array(md.ifile, data.get(), chunksize);
        if(md.ifile.fail()) return error("Read failure.");
        
        // save data
        md.G1MS_list.push_back(binary_stream(data, chunksize));
       }
     // G1MM
     else if(chunkname == 0x47314D4D)
       {
        // seek data
        md.ifile.seekg(cposition);
        if(md.ifile.fail()) return error("Seek failure.");

        // read data
        boost::shared_array<char> data(new char[chunksize]);
        BE_read_array(md.ifile, data.get(), chunksize);
        if(md.ifile.fail()) return error("Read failure.");
        
        // save data
        md.G1MM_list.push_back(binary_stream(data, chunksize));
       }
     // G1MG
     else if(chunkname == 0x47314D47)
       {
        // seek data
        md.ifile.seekg(cposition);
        if(md.ifile.fail()) return error("Seek failure.");

        // read data
        boost::shared_array<char> data(new char[chunksize]);
        BE_read_array(md.ifile, data.get(), chunksize);
        if(md.ifile.fail()) return error("Read failure.");
        
        // save data
        md.G1MG_list.push_back(binary_stream(data, chunksize));
       }
     // COLL
     else if(chunkname == 0x434F4C4C)
       {
        // skip data
        md.ifile.seekg(chunksize - 0x0C, ios::cur);
        if(md.ifile.fail()) return error("Seek failure.");
       }
     // NUNO
     else if(chunkname == 0x4E554E4F)
       {
        // seek data
        md.ifile.seekg(cposition);
        if(md.ifile.fail()) return error("Seek failure.");

        // read data
        boost::shared_array<char> data(new char[chunksize]);
        BE_read_array(md.ifile, data.get(), chunksize);
        if(md.ifile.fail()) return error("Read failure.");

        // save data
        md.NUNO_list.push_back(binary_stream(data, chunksize));
       }
     // NUNV
     else if(chunkname == 0x4E554E56)
       {
        // seek data
        md.ifile.seekg(cposition);
        if(md.ifile.fail()) return error("Seek failure.");

        // read data
        boost::shared_array<char> data(new char[chunksize]);
        BE_read_array(md.ifile, data.get(), chunksize);
        if(md.ifile.fail()) return error("Read failure.");

        // save data
        md.NUNV_list.push_back(binary_stream(data, chunksize));
       }
     // EXTR
     else if(chunkname == 0x45585452)
       {
        // skip data
        md.ifile.seekg(chunksize - 0x0C, ios::cur);
        if(md.ifile.fail()) return error("Seek failure.");
       }
     // UNKN
     else {
        stringstream ss;
        ss << "Unknown chunk 0x" << hex << chunkname << dec << " at offset 0x" << hex << cposition << dec << ".";
        return error(ss);
       }
    }

 // validate chunks
 if(md.G1MF_list.size() != 1) return error("Unexpected number of G1MF chunks.");
 if(md.G1MM_list.size() != 1) return error("Unexpected number of G1MM chunks.");
 if(md.G1MG_list.size() != 1) return error("Unexpected number of G1MG chunks.");

 //
 // PROCESS G1MS and G1MM
 //

 if(!processG1MM(md)) return false;
 if(!processG1MS(md)) return false;

 //
 // PROCESS NUNO and NUNV
 //

 if(!processNUNO(md)) return false;
 if(!processNUNV(md)) return false;

 //
 // PROCESS G1MG (MODEL DATA)
 //

 if(!processG1MG(md)) return false;

 // finished
 return true;
}

bool DWConvertModel(LPCTSTR pathname)
{
 return processG1M(pathname);
}