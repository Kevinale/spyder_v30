#!/usr/bin/env python3
"""Bounded structural probes, not an ISA detector or encryption classifier."""
from pathlib import Path
import hashlib,json,math,struct,collections,random,zlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
IMAGE=ROOT/'firmware/data.decompressed.bin'

def entropy(b):
 c=collections.Counter(b);n=len(b);return -sum((v/n)*math.log2(v/n)for v in c.values()) if n else 0

def probes(b):
 hits={'elf':[],'pe':[],'cortex_m_vector_candidates':[],'a32_vector_candidates':[]}
 # Strong structural checks; simple magic occurrences are NOT executables.
 start=0
 while (o:=b.find(b'\x7fELF',start))>=0:
  start=o+1
  if o+64>len(b)or b[o+4]not in(1,2)or b[o+5]not in(1,2)or b[o+6]!=1:continue
  endian='<'if b[o+5]==1 else'>';cl=b[o+4]
  machine=struct.unpack_from(endian+'H',b,o+18)[0]
  phoff=struct.unpack_from(endian+('I'if cl==1 else'Q'),b,o+(28 if cl==1 else 32))[0]
  ehsize,phsize,phnum=struct.unpack_from(endian+'HHH',b,o+(40 if cl==1 else 52))
  if ehsize==(52 if cl==1 else 64)and phsize==(32 if cl==1 else 56)and 0<phnum<=128 and phoff+phsize*phnum<=len(b)-o:
   hits['elf'].append({'offset':o,'class':cl,'machine':machine})
 start=0
 while(o:=b.find(b'MZ',start))>=0:
  start=o+1
  if o+64>len(b):continue
  pe=struct.unpack_from('<I',b,o+60)[0]+o
  if pe+24>len(b)or b[pe:pe+4]!=b'PE\0\0':continue
  machine,sections=struct.unpack_from('<HH',b,pe+4)
  if machine in(0x14c,0x8664,0x1c0,0x1c4,0xaa64)and 0<sections<=96:hits['pe'].append({'offset':o,'pe_offset':pe,'machine':machine})
 # Explicit ARM hypotheses only: cannot rule out other CPUs or headerless code.
 for o in range(0,len(b)-64,4):
  sp,reset=struct.unpack_from('<II',b,o)
  if 0x20000000<=sp<0x40000000 and sp%8==0 and reset&1:
   words=struct.unpack_from('<16I',b,o)
   base=reset&0xffe00000
   active=[v for v in words[1:]if v not in(0,0xffffffff)]
   good=[v for v in active if v&1 and base<=(v&~1)<base+0x200000]
   if len(active)>=8 and len(good)>=max(8,math.ceil(.8*len(active))):
    hits['cortex_m_vector_candidates'].append({'offset':o,'stack':hex(sp),'reset':hex(reset),'consistent':len(good),'active':len(active)})
  first=struct.unpack_from('<I',b,o)[0]
  def arm_vector(w):return(w&0xff000000)==0xea000000 or(w&0xfffff000)in(0xe59ff000,0xe51ff000)
  if arm_vector(first):
   words=struct.unpack_from('<8I',b,o)
   if sum(map(arm_vector,words))>=7:hits['a32_vector_candidates'].append({'offset':o,'words':[hex(w)for w in words]})
 return hits

def variants(b):
 yield 'identity',b
 yield 'xor_ff',bytes(v^255 for v in b)
 table=bytes(int(f'{v:08b}'[::-1],2)for v in range(256))
 yield 'reverse_bits_in_each_byte',b.translate(table)
 for size in [2,4,6,8]:
  q=len(b)//size*size;out=bytearray(b)
  for o in range(0,q,size):out[o:o+size]=b[o:o+size][::-1]
  yield f'reverse_bytes_in_{size}_byte_words',bytes(out)
 # Byte rotation cannot establish a CPU; check only fixed documented transforms.
 for shift in [1,2,3,4]:
  yield f'rotate_each_byte_left_{shift}',bytes(((v<<shift)|(v>>(8-shift)))&255 for v in b)

def selftest():
 b=bytearray(512);v=[0x20010000]+[0x08000081+4*i for i in range(15)]
 struct.pack_into('<16I',b,0,*v)
 assert len(probes(b)['cortex_m_vector_candidates'])==1
 b=bytearray(512);struct.pack_into('<8I',b,0,*([0xea000000]*8))
 assert probes(b)['a32_vector_candidates']
 b=bytearray(512);b[:4]=b'\x7fELF';b[4:7]=bytes([1,1,1]);struct.pack_into('<H',b,18,40);struct.pack_into('<I',b,28,52);struct.pack_into('<HHH',b,40,52,32,1)
 assert probes(b)['elf']
 b=bytearray(512);b[:2]=b'MZ';struct.pack_into('<I',b,60,128);b[128:132]=b'PE\0\0';struct.pack_into('<HH',b,132,0x14c,1)
 assert probes(b)['pe']
 assert not any(probes(b'random MZ and \x7fELF'+bytes(200)).values())
 print('PASS: structural probe positive controls (Cortex-M/A32/ELF/PE) and malformed headers.')

def main():
 selftest();b=IMAGE.read_bytes();before=hashlib.sha256(b).hexdigest();rows=[]
 for name,data in variants(b):
  hits=probes(data);rows.append({'transform':name,'sha256':hashlib.sha256(data).hexdigest(),'hits':hits})
 # Collision counts are descriptive, never an encryption verdict.
 blocks=[]
 for size in [4,6,8,16,32]:
  a=[b[o:o+size]for o in range(0,len(b)-size+1,size)];counts=collections.Counter(a)
  blocks.append({'size':size,'full_blocks':len(a),'distinct':len(counts),'extra_duplicates':sum(v-1 for v in counts.values()),'remainder':len(b)%size})
 lanes=[{'lane':i,'stride':4,'entropy':entropy(b[i::4]),'zero_fraction':b[i::4].count(0)/len(b[i::4])}for i in range(4)]
 result={'input':str(IMAGE),'bytes':len(b),'sha256':before,'entropy':entropy(b),'moduli':{str(k):len(b)%k for k in[2,3,4,6,8,16,32,256]},'aligned_block_collisions':blocks,'byte_lanes':lanes,'probes':rows,'limits':['Negative probes cannot exclude headerless code, another ISA, other byte transforms, compression or encryption.','Entropy and block alignment do not identify cipher or CPU.','No extracted payload is executed; no architecture is selected in Ghidra without evidence.']}
 assert hashlib.sha256(IMAGE.read_bytes()).hexdigest()==before
 (OUT/'image_probes.json').write_text(json.dumps(result,indent=2)+'\n')
 for r in rows:print(r['transform'],{k:len(v)for k,v in r['hits'].items()})
 print('Original hash unchanged:',before)
if __name__=='__main__':main()
