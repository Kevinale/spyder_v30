#!/usr/bin/env python3
"""Hash Remote reconstruction/extraction and inspect PE metadata without loading code."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,'/workspace/analysis/tools/python')
import pefile
root=Path('/workspace/analysis/remote')
files=sorted((root/'reconstructed').rglob('*'))+sorted((root/'extracted').rglob('*'))
rows=[]
for p in files:
 if not p.is_file(): continue
 data=p.read_bytes()
 r={'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 if data[:2]==b'MZ':
  pe=pefile.PE(data=data,fast_load=True)
  pe.parse_data_directories(directories=[1,0])
  r['pe']={'machine':hex(pe.FILE_HEADER.Machine),'image_base':hex(pe.OPTIONAL_HEADER.ImageBase),
   'entry_rva':hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),'timestamp_untrusted':pe.FILE_HEADER.TimeDateStamp,
   'clr_directory':{'rva':hex(pe.OPTIONAL_HEADER.DATA_DIRECTORY[14].VirtualAddress),'size':pe.OPTIONAL_HEADER.DATA_DIRECTORY[14].Size},
   'certificate_table':{'file_offset':hex(pe.OPTIONAL_HEADER.DATA_DIRECTORY[4].VirtualAddress),'size':pe.OPTIONAL_HEADER.DATA_DIRECTORY[4].Size,'trust_verified':False},
   'sections':[{'name':s.Name.rstrip(b'\0').decode(errors='replace'),'raw_offset':hex(s.PointerToRawData),'raw_size':s.SizeOfRawData,'rva':hex(s.VirtualAddress),'virtual_size':s.Misc_VirtualSize} for s in pe.sections],
   'imports':{},'exports':[]}
  for d in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[]):
   r['pe']['imports'][d.dll.decode(errors='replace')]=[x.name.decode(errors='replace') if x.name else '#'+str(x.ordinal) for x in d.imports]
  if hasattr(pe,'DIRECTORY_ENTRY_EXPORT'):
   r['pe']['exports']=[{'name':x.name.decode(errors='replace') if x.name else None,'rva':hex(x.address),'file_offset':hex(pe.get_offset_from_rva(x.address)) if not x.forwarder else None} for x in pe.DIRECTORY_ENTRY_EXPORT.symbols]
 rows.append(r)
(root/'artifact_inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({'files':len(rows),'pe_files':sum('pe' in r for r in rows),'reconstructed_exe':rows[0]},indent=2)[:1500])
