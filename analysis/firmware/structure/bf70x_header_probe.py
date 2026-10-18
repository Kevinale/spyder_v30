"""Source-guided relaxed-signature probe. Static input only, no address access."""
from pathlib import Path
import struct,json,functools,operator
root=Path('/workspace/analysis/firmware');rows=[]
def parse(b,o,sign=None):
 if o+16>len(b):return None
 h=b[o:o+16]
 if functools.reduce(operator.xor,h,0):return None
 code,addr,n,arg=struct.unpack('<4I',h)
 if sign is not None and h[3]!=sign:return None
 if addr%4 or n%4 or addr+n>0x100000000:return None
 fill=bool(code&0x100)
 end=o+16+(0 if fill else n)
 if end>len(b):return None
 return {'offset':o,'code':hex(code),'address':hex(addr),'count':n,'end':end,'first':bool(code&0x4000),'final':bool(code&0x8000),'signature':h[3]}
for name,p in [('2.02',root/'v2.02/data.decompressed.bin'),('2.05',root/'data.decompressed.bin')]:
 b=p.read_bytes();starts=[];strong=[];rolling=functools.reduce(operator.xor,b[:16],0)
 for o in range(len(b)-15):
  if o:rolling^=b[o-1]^b[o+15]
  if rolling:continue
  h=parse(b,o)
  if not h or not h['first']:continue
  starts.append(h);chain=[h]
  while not chain[-1]['final'] and len(chain)<4096:
   item=parse(b,chain[-1]['end'],h['signature'])
   if item is None:break
   chain.append(item)
  if len(chain)>=3 and chain[-1]['final']:strong.append(chain)
 rows.append({'version':name,'initial_header_xor':functools.reduce(operator.xor,b[:16],0),'first_header_at_offset_zero':parse(b,0),'candidate_first_headers':len(starts),'three_or_more_block_final_chains':strong})
(root/'structure/bf70x_relaxed_signature.json').write_text(json.dumps({'source':'majbthrd/ldrshrink, static format review; no authoritative silicon specification claimed','limits':'identity representation only; first flag, stable signature, XOR checksum, aligned target/count, bounded payload, final marker; at least three blocks required','results':rows},indent=2)+'\n');print(json.dumps(rows,indent=2))
