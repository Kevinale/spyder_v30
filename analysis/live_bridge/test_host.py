import sys,struct,json
from pathlib import Path
sys.path.insert(0,'/workspace/analysis/tools/python')
from lupa.lua54 import LuaRuntime
root=Path('/workspace/analysis')
import ast
module=ast.parse((root/'reaper_demo/test_paste.py').read_text())
mock=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MOCK' for t in n.targets))
source=(root/'live_bridge/Spider_Live.lua').read_text()
def packet(f):
 h=f['header_len'];p=bytearray(h);struct.pack_into('<H',p,0,h);struct.pack_into('<I',p,10,int(f['status'],16));p[16]=int(f['completion']);struct.pack_into('<HH',p,17,f['bus'],f['device']);p[21]=int(f['endpoint'],16);p[22]=f['transfer_type'];struct.pack_into('<I',p,23,f['data_length']);return bytes(p)+bytes.fromhex(f.get('payload_hex',''))
path=Path('/tmp/SpiderGateway-live.pcap')
frames=json.loads((root/'captures_tone/target_frames.json').read_text())
# Lua source uses backslash Windows path; map to Linux test fixture.
source='\n'.join('local path="/tmp/SpiderGateway-live.pcap"' if line.startswith('local path=') else line for line in source.splitlines())
global_header=struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,128,249)
def record(f):
 p=packet(f);return struct.pack('<IIII',0,0,len(p),len(p))+p
path.write_bytes(global_header+b''.join(map(record,frames)))
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(mock);lua.execute(source);g=lua.globals()
for i in range(5):
 fun=g.queued;g.queued=None;fun()
assert len(g.calls)==0,'Historical events were applied'
# Append same verified event stream as NEW bytes: capture starts mid-record, exercises partial read.
new=b''.join(map(record,frames))
with path.open('ab')as out:out.write(new[:9])
fun=g.queued;g.queued=None;fun();assert len(g.calls)==0
with path.open('ab')as out:out.write(new[9:])
for i in range(5):
 fun=g.queued;g.queued=None;fun()
assert len(g.calls)==1006,len(g.calls)
assert set(g.calls[i]['p']for i in range(1,1007))=={3,4,5}
g.key=27;g.queued();assert g.closed
for i in [1,3,4,5]:assert abs(g['values'][i]-g.initial[i])<1e-12
# Refuse armed tracks before opening files.
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(mock);lua.execute('record_arm=1');lua.execute(source);assert len(lua.globals().calls)==0 and len(lua.globals().messages)==1
print('PASS: history skipped; partial records wait; 1006 live updates; Escape restores; armed track refused. Windows launcher untested here.')
