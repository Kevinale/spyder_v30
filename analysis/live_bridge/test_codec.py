import sys,json,struct
from pathlib import Path
sys.path.insert(0,'/workspace/analysis/tools/python')
from lupa.lua54 import LuaRuntime
root=Path('/workspace/analysis')
source=(root/'live_bridge/codec.lua').read_text()
results=[]
for folder in ['captures','captures_tone','captures_noamp']:
 lua=LuaRuntime(encoding=None,unpack_returned_tuples=True)
 emitted=[]
 make=lua.execute(source+'\nreturn decoder')
 d=make(lambda n,v:emitted.append((n.decode(),v)))
 frames=json.loads((root/folder/'target_frames.json').read_text())
 for f in frames:
  payload=bytes.fromhex(f.get('payload_hex',''))
  h=f['header_len'];p=bytearray(h)
  struct.pack_into('<H',p,0,h)
  struct.pack_into('<I',p,10,int(f['status'],16))
  p[16]=int(f['completion']);struct.pack_into('<HH',p,17,f['bus'],f['device'])
  p[21]=int(f['endpoint'],16);p[22]=f['transfer_type']
  struct.pack_into('<I',p,23,f['data_length'])
  d[b'feed'](bytes(p)+payload,True)
 counts={k:sum(n==k for n,v in emitted)for k in ['Drive','Bass','Middle','Treble']}
 assert all(0<=v<=1 for n,v in emitted)
 if folder=='captures_tone':assert counts=={'Drive':0,'Bass':293,'Middle':356,'Treble':357},counts
 if folder=='captures_noamp':assert not emitted and d[b'unknown']==650,(counts,d[b'unknown'])
 if folder=='captures':assert counts['Drive']==140,counts
 results.append(dict(capture=folder,identified=bool(d[b'verified']),counts=counts,unknown=d[b'unknown']))
# Gate without descriptors, and do not emit historical notifications.
lua=LuaRuntime(encoding=None,unpack_returned_tuples=True);make=lua.execute(source+'\nreturn decoder')
e=[];d=make(lambda *args:e.append(args))
for f in frames:
 if f['transfer_type']!=3:continue
 h=f['header_len'];p=bytearray(h);struct.pack_into('<H',p,0,h);p[16]=int(f['completion']);struct.pack_into('<HH',p,17,f['bus'],f['device']);p[21]=int(f['endpoint'],16);p[22]=3;struct.pack_into('<I',p,23,f['data_length']);d[b'feed'](bytes(p)+bytes.fromhex(f.get('payload_hex','')),True)
assert not e and not d[b'verified']
print(json.dumps(results,indent=2))
(root/'live_bridge/codec_validation.json').write_text(json.dumps(results,indent=2)+'\n')
