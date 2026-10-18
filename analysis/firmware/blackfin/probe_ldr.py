"""Bounded static probe of a public Blackfin 16-byte LDR hypothesis, not a decoder."""
from pathlib import Path
import struct,json,hashlib,importlib.util,functools,operator
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('own_image_probe',R/'firmware/revisit/probe_image.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
FILL=0x100;FIRST=0x4000;FINAL=0x8000

def header(b,o):
 if o<0 or o+16>len(b) or b[o+3]!=0xad:return None
 h=b[o:o+16]
 if functools.reduce(operator.xor,h,0):return None
 code,target,n,arg=struct.unpack('<IIII',h)
 if not code&FILL and n>len(b)-o-16:return None
 if target+n>0x100000000:return None
 return {'offset':o,'code':hex(code),'target':hex(target),'bytes':n,'argument':hex(arg),'fill':bool(code&FILL),'first':bool(code&FIRST),'final':bool(code&FINAL)}
def chain(b,start):
 blocks=[];o=start
 for _ in range(4096):
  h=header(b,o)
  if not h:return None
  blocks.append(h);o+=16+(0 if h['fill'] else h['bytes'])
  if h['final']:return {'start':start,'end':o,'count':len(blocks),'blocks':blocks,'whole_buffer':start==0 and o==len(b)}
 return None

def mk(code,target,n,arg=0,data=b''):
 h=bytearray(struct.pack('<IIII',0xad000000|code,target,n,arg));h[2]=functools.reduce(operator.xor,h,0);return bytes(h)+data

def selftest():
 stream=mk(FIRST,0,0)+mk(FINAL,0x80000000,4,data=b'abcd')
 c=chain(stream,0);assert c and c['count']==2 and c['whole_buffer']
 wrong=bytearray(stream);wrong[2]^=1;assert not chain(wrong,0)
 assert not chain(stream[:-1],0)
 assert not chain(mk(FIRST,0,0),0)
 fill=mk(FIRST|FILL,0x80000000,4096)+mk(FINAL,0x80001000,0)
 assert chain(fill,0)['whole_buffer']
 assert not header(mk(FINAL,0xfffffffe,4,data=b'abcd'),0)
 return ['two-block complete stream accepted','checksum corruption rejected','truncated data rejected','missing final rejected','fill consumes no payload','target overflow rejected']

def main():
 tests=selftest();p=R/'firmware/data.decompressed.bin';b=p.read_bytes();rows=[]
 for name,data in mod.variants(b):
  hs=[];cs=[]
  for o in range(len(data)-15):
   if data[o+3]!=0xad:continue
   h=header(data,o)
   if h:
    hs.append(h);c=chain(data,o)
    if c:cs.append(c)
  rows.append({'transform':name,'candidate_headers':hs,'complete_candidates':cs,'strong_multi_block_candidates':[c for c in cs if c['count']>=2],'uboot_signature_at_start':data[3]==0xad and struct.unpack_from('<I',data,8)[0]==0})
 result={'input':str(p),'sha256':hashlib.sha256(b).hexdigest(),'selftests':tests,'hypothesis':'16-byte little-endian header, AD signature, XOR checksum, count, fill/final flags based on reviewed public sources','results':rows,'limits':['Not an exhaustive BF707 boot-format specification','Does not exclude headerless code, other wrappers, transforms, encoding or encryption','No target RAM map inferred from random header candidates','No code execution and no device IO']}
 (O/'ldr_probe.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS selftests:',len(tests))
 for x in rows:print(x['transform'],'headers',len(x['candidate_headers']),'complete',len(x['complete_candidates']),'multi-block',len(x['strong_multi_block_candidates']))
if __name__=='__main__':main()
