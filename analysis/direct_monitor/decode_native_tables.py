from pathlib import Path
import json,sys,struct
sys.path.insert(0,'/workspace/analysis/tools/python');import pefile
R=Path('/workspace/analysis');p=pefile.PE(str(R/'remote/extracted/Spider V Remote/APIV3EngineDLL.dll'));base=p.OPTIONAL_HEADER.ImageBase

def word(a):return struct.unpack('<I',p.get_data(a-base,4))[0]
def text(a):
 if not(base<=a<base+p.OPTIONAL_HEADER.SizeOfImage):return None
 return p.get_data(a-base,200).split(b'\0')[0].decode('ascii',errors='replace')
rows={}
for label,va in [('Parker',0x1018e490),('AEON',0x1018e580),('fallback',0x1018e7e0)]:
 table=[]
 for i in range(64):
  a=va+12*i;x,y,z=word(a),word(a+4),word(a+8)
  if not x:break
  table.append({'entry_va':hex(a),'wire_group':text(x),'preset_group':text(y),'flag':z})
 rows[label]=table
(R/'direct_monitor/native_group_maps.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows['Parker'],indent=2))
