"""Find exact strings/CRC constants in extracted files without executing them."""
from pathlib import Path
import json,struct,sys
sys.path.insert(0,'/workspace/analysis/tools/python')
import pefile
R=Path('/workspace/analysis');names=['GuitProcOutputGain','USBOutLevel','USBInLevel','GuitProcInputGain','GuitInputGain','GuitarProcEnable']
symbols={x['text']:x for x in json.loads((R/'captures/device_symbols.json').read_text()) if x['text'] in names}
rows=[]
for folder in ['remote/extracted/Spider V Remote','driver/extracted']:
 for p in (R/folder).rglob('*'):
  if not p.is_file() or p.suffix.lower() not in ['.dll','.exe','.sys','.cpl','.plist']:continue
  b=p.read_bytes()
  try:pe=pefile.PE(data=b,fast_load=True)
  except Exception:pe=None
  for name,s in symbols.items():
   for kind,needle in [('ascii',name.encode()+b'\0'),('utf16',name.encode('utf-16le')+b'\0\0'),('crc32le',struct.pack('<I',int(s['crc32'],16)))]:
    pos=0
    while (pos:=b.find(needle,pos))>=0:
     rec={'file':str(p.relative_to(R)),'symbol':name,'kind':kind,'file_offset':hex(pos)}
     if pe:
      try:
       rva=pe.get_rva_from_offset(pos);sec=pe.get_section_by_rva(rva)
       rec.update(va=hex(pe.OPTIONAL_HEADER.ImageBase+rva),section=sec.Name.rstrip(b'\0').decode() if sec else None)
      except Exception:pass
     rows.append(rec);pos+=1
(R/'direct_monitor/parameter_occurrences.json').write_text(json.dumps({'device_symbols':symbols,'occurrences':rows},indent=2)+'\n')
for x in rows:print(x)
