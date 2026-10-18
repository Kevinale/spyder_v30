from pathlib import Path
import hashlib,json,sys,re,zlib
sys.path.insert(0,'/workspace/analysis/tools/python');import pefile
R=Path(__file__).resolve().parent;p=R/'reconstructed/Line 6 Updater v1.28 Installer.exe';b=p.read_bytes();(R/'reconstruction.json').write_text(json.dumps({'file':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'crc32':f'{zlib.crc32(b):08X}','executed':False},indent=2)+'\n')
files=[]
for f in (R/'extracted').rglob('*'):
 if f.is_file():files.append({'file':str(f.relative_to(R/'extracted')),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(R/'inventory.json').write_text(json.dumps(files,indent=2)+'\n')
p=R/'extracted/Line 6 Updater/Line 6 Updater.exe';b=p.read_bytes();pe=pefile.PE(data=b);rows=[]
pat=re.compile(rb'(?i)parker|blackfin|bf707|decrypt|encrypt|aes|blowfish|L6FF|L6IA|\.svu|spider|md5|firmware|imagearchive|sharc|crypto|secure')
for m in re.finditer(rb'[ -~]{5,}',b):
 if pat.search(m[0]):
  o=m.start();rv=pe.get_rva_from_offset(o);rows.append({'offset':hex(o),'va':hex(pe.OPTIONAL_HEADER.ImageBase+rv),'text':m[0].decode()})
(R/'native/string_candidates.json').write_text(json.dumps(rows,indent=2)+'\n')
(R/'native/strings.txt').write_text('\n'.join(hex(m.start())+' '+m[0].decode()for m in re.finditer(rb'[ -~]{5,}',b))+'\n')
imports=[{'dll':d.dll.decode(),'names':[x.name.decode() if x.name else '#'+str(x.ordinal)for x in d.imports]}for d in pe.DIRECTORY_ENTRY_IMPORT]
(R/'native/pe_summary.json').write_text(json.dumps({'file':str(p),'machine':hex(pe.FILE_HEADER.Machine),'imagebase':hex(pe.OPTIONAL_HEADER.ImageBase),'imports':imports,'sections':[{'name':s.Name.rstrip(b'\0').decode(),'rva':hex(s.VirtualAddress),'bytes':s.SizeOfRawData}for s in pe.sections]},indent=2)+'\n')
print('Installer',len(files),'extracted files; mainexe imagebase',hex(pe.OPTIONAL_HEADER.ImageBase))
for x in rows:print(x['va'],x['text'])
