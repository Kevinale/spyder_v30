#!/usr/bin/env python3
"""Read-only PE extraction of Parker special name triples from APIV3EngineDLL."""
import sys,pathlib,struct,json
sys.path.insert(0,'/workspace/analysis/tools/python')
import pefile
p=pathlib.Path('/workspace/analysis/remote/extracted/Spider V Remote/APIV3EngineDLL.dll');b=p.read_bytes();pe=pefile.PE(data=b);base=pe.OPTIONAL_HEADER.ImageBase

def off(va):return pe.get_offset_from_rva(va-base)
def string(va):o=off(va);return b[o:b.index(b'\0',o)].decode('ascii')
rows=[]
for i in range(25):
 va=0x1018e8a8+i*12;ptrs=struct.unpack_from('<III',b,off(va));rows.append({'index':i,'VA':hex(va),'RVA':hex(va-base),'offset':hex(off(va)),'pointers':[hex(v) for v in ptrs],'firmware_name':string(ptrs[0]),'application_group':string(ptrs[1]),'application_parameter':string(ptrs[2])})
pathlib.Path('/workspace/analysis/captures_noamp/parker_special_mapping.json').write_text(json.dumps(rows,indent=2))
funcs=[]
for va in [0x10084570,0x100987c0,0x100ac720,0x100998e0,0x100999a0,0x10098ef0,0x1001d100]:funcs.append({'VA':hex(va),'RVA':hex(va-base),'offset':hex(off(va))})
pathlib.Path('/workspace/analysis/captures_noamp/native_reserved_offsets.json').write_text(json.dumps(funcs,indent=2))
print(json.dumps(rows[24],indent=2))
