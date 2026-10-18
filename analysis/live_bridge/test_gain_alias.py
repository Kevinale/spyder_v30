"""Synthetic wire records from owner-reported Gain37, not a new capture."""
import sys,struct,json,ast
from pathlib import Path
sys.path.insert(0,'/workspace/analysis/tools/python')
from lupa.lua54 import LuaRuntime
ROOT=Path('/workspace/analysis');HERE=ROOT/'live_bridge'
syms=json.loads((ROOT/'captures/device_symbols.json').read_text());assert next(x for x in syms if x['text']=='Gain')['index']==37
frames=json.loads((ROOT/'captures/target_frames.json').read_text())
f=next(f for f in frames if f['transfer_type']==2 and f['completion']and f['payload_hex'].startswith('1201'))
def usb(payload,ep=0x82,typ=3,h=27):
 p=bytearray(h);struct.pack_into('<H',p,0,h);p[16]=1;struct.pack_into('<HH',p,17,2,4);p[21]=ep;p[22]=typ;struct.pack_into('<I',p,23,len(payload));return bytes(p)+payload
ident=usb(bytes.fromhex(f['payload_hex']),ep=0x80,typ=2,h=28)
def event(param,value,seq):
 raw=struct.pack('<IIIII f',4,16,42,param,4,value)
 s=bytearray([240,0,1,12,34,0,77,0,seq,0,1,7])
 for o in range(0,len(raw),7):
  g=raw[o:o+7].ljust(7,b'\0');s.append(sum(((v>>7)&1)<<(6-j)for j,v in enumerate(g)));s.extend(v&127 for v in g)
 s.append(247);midi=bytearray()
 for o in range(0,len(s),3):
  g=s[o:o+3];cin=4 if o+3<len(s)else {1:5,2:6,3:7}[len(g)];midi.append(cin);midi.extend(g.ljust(3,b'\0'))
 return usb(midi)
values=[.7648134231567383,0.,1.,.7283464670181274]
lua=LuaRuntime(encoding=None,unpack_returned_tuples=True);emitted=[];make=lua.execute((HERE/'codec.lua').read_text()+'\nreturn decoder');d=make(lambda n,v:emitted.append((n.decode(),v)));d[b'feed'](ident,False)
for i,v in enumerate(values):d[b'feed'](event(37,v,i),True)
assert emitted==[('Drive',v)for v in values]
d[b'feed'](event(0xffffffff,.5,4),True);assert len(emitted)==4
# Exercise the actual ReaScript host path and bounded Input mapping.
module=ast.parse((ROOT/'reaper_demo/test_paste.py').read_text());mock=next(ast.literal_eval(n.value)for n in module.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='MOCK'for t in n.targets))
path=Path('/tmp/SpiderGateway-gain.pcap')
def record(p):return struct.pack('<IIII',0,0,len(p),len(p))+p
path.write_bytes(struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,128,249)+record(ident))
source='\n'.join('local path="/tmp/SpiderGateway-gain.pcap"'if l.startswith('local path=')else l for l in(HERE/'Spider_Live.lua').read_text().splitlines())
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(mock);lua.execute(source);g=lua.globals();assert not len(g.calls)
for i,v in enumerate(values):
 with path.open('ab')as out:out.write(record(event(37,v,i)))
 fn=g.queued;g.queued=None;fn()
assert len(g.calls)==4
for i,v in enumerate(values,1):
 c=g.calls[i];assert c['p']==1
 db=-36+72*c['v'];assert abs(db-(-12+18*v))<.003,(db,v)
g.key=27;g.queued();assert abs(g['values'][1]-g.initial[1])<1e-12
result={'source':'synthetic USB/MIDI frames built from owner reported group42/param37/type4/float; not a device capture','samples':values,'checks':['Gain37 reaches logical Drive','unknown -1 remains ignored','actual ReaScript writes Gateway Input only','-12..+6 dB bounds and mapping validated','Escape restores Input'],'passed':True}
(HERE/'gain_alias_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: Gain37 -> Drive -> Gateway Input, four reported samples, bounded gain and restoration; unresolved -1 ignored.')
