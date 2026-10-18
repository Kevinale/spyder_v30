import sys,json,pathlib
sys.path.insert(0,'/workspace/analysis/tools/python');import pefile
pe=pefile.PE('/workspace/analysis/remote/extracted/Spider V Remote/APIV3EngineDLL.dll')
rows=[]
for va in [0x10001000,0x100012a0,0x100012c0,0x10002b10,0x10050660,0x100507c0,0x1005bf70,0x1005c080,0x1005c260,0x1005cf70,0x1005d140,0x10055150,0x10052fb0,0x10052f90,0x10078e90]:
 rva=va-pe.OPTIONAL_HEADER.ImageBase;rows.append({'va':hex(va),'rva':hex(rva),'file_offset':hex(pe.get_offset_from_rva(rva))})
pathlib.Path('/workspace/analysis/remote/native/function_offsets.json').write_text(json.dumps(rows,indent=2))
for r in rows:print(r)
