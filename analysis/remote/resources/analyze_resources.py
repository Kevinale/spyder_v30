#!/usr/bin/env python3
"""Static resource inventory; never loads target executables. Offsets are zero based."""
import argparse,collections,hashlib,json,plistlib,struct,zlib
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('/workspace/analysis/remote/extracted/Spider V Remote'));ap.add_argument('--out',type=Path,default=Path('/workspace/analysis/remote/resources'));a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
def save(name,obj): (a.out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
inventory=[];summaries=[];hits=[]
for f in sorted((a.root/'res').glob('*')):
 b=f.read_bytes();inventory.append({'path':str(f),'size':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 if f.suffix=='.bin':
  n,size=struct.unpack_from('<II',b);base=8+n*12;records=[];errors=[]
  for i in range(n):
   ro=8+12*i;off,word,length=struct.unpack_from('<III',b,ro);start=base+off;s=b[start:start+length]
   if start+length>=len(b) or b[start+length]!=0:errors.append(i)
   text=s.decode('utf8');r={'index':i,'record_offset':ro,'string_offset':start,'pool_offset':off,'word':f'0x{word:08x}','length':length,'text':text};records.append(r)
   if any(k in text.lower() for k in ['spider','firebird','usb','firm','knob','midi','speaker','crossover','sharc','pedal','tweak']):hits.append({'file':f.name,**r})
  summary={'file':f.name,'count':n,'size_field':size,'actual_size':len(b),'string_pool_offset':base,'invalid_string_records':errors,'last_string_end':records[-1]['string_offset']+records[-1]['length']+1,'crc32_matches':sum(int(r['word'],16)==zlib.crc32(r['text'].encode()) for r in records)};summaries.append(summary);save(f.name+'.json',records)
 elif f.suffix=='.models':
  d=json.loads(b);save(f.name+'.json',d);summaries.append({'file':f.name,'type':type(d).__name__,'count':len(d),'parameters':sum(len(m.get('params',[])) for m in d)})
 elif f.suffix=='.json':
  d=json.loads(b);save(f.name,d);summaries.append({'file':f.name,'schema':d.get('schema'),'version':d.get('version'),'device':d.get('data',{}).get('device'),'device_version':d.get('data',{}).get('device_version'),'tone_blocks':list(d.get('data',{}).get('tone',{}))})
p=a.root/'AssetDefs.plist';b=p.read_bytes();d=plistlib.loads(b);assets=[]
def walk(c,path):
 path=path+'/'+c.get('categoryID','?')
 for asset in c.get('assets',[]):assets.append({'category_path':path,**asset})
 for child in c.get('childCategories',[]):walk(child,path)
for c in d['Categories']:walk(c,'')
save('assets.json',assets);save('inventory.json',inventory+[{'path':str(p),'size':len(b),'sha256':hashlib.sha256(b).hexdigest()}]);save('summary.json',summaries);save('symbol_keyword_hits.json',hits)
counts=collections.Counter()
for asset in assets:
 for param in asset.get('assetParameters',[]):counts[str(param.get('canBeExternallyBound'))]+=1
save('asset_summary.json',{'assets':len(assets),'parameters':sum(len(x.get('assetParameters',[])) for x in assets),'canBeExternallyBound_counts':counts,'engineIDs':[x.get('engineID') for x in assets]})
print(json.dumps({'summary':summaries,'assets':len(assets),'binding':counts},indent=2))
