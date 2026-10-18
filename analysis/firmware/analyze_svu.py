#!/usr/bin/env python3
"""Static SVU analysis; reads original and writes only supplied output directory."""
import argparse,collections,hashlib,json,math,re,struct,zlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('out',type=Path);a=p.parse_args();b=a.input.read_bytes();a.out.mkdir(parents=True,exist_ok=True)
def entropy(d):
 c=collections.Counter(d);return -sum(n/len(d)*math.log2(n/len(d)) for n in c.values()) if d else 0
assert len(b)>=12 and b[:4]==b'FORM' and b[8:12]==b'L6FF';declared=struct.unpack_from('>I',b,4)[0];assert declared+8==len(b)
r={'input':str(a.input),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'form_type':b[8:12].decode(),'form_size':declared,'chunks':[]};off=12
seen=set()
while off<len(b):
 assert off+8<=len(b)
 name=b[off:off+4].decode('ascii');assert re.fullmatch('[A-Za-z0-9_]{4}',name) and name not in seen;seen.add(name)
 n=struct.unpack_from('>I',b,off+4)[0];start=off+8;end=start+n;assert end<=len(b);d=b[start:end];entry={'name':name,'header_offset':off,'payload_offset':start,'size':n,'sha256':hashlib.sha256(d).hexdigest(),'entropy':entropy(d)};r['chunks'].append(entry);(a.out/(name+'.bin')).write_bytes(d);off=end+(n%2)
assert off==len(b)
head=(a.out/'HEAD.bin').read_bytes();compressed=(a.out/'data.bin').read_bytes();obj=zlib.decompressobj();raw=obj.decompress(compressed)+obj.flush();assert obj.eof and not obj.unused_data
(a.out/'data.decompressed.bin').write_bytes(raw)
r['decompression']={'format':'zlib/DEFLATE','compressed_bytes':len(compressed),'decompressed_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'entropy':entropy(raw),'md5':hashlib.md5(raw).hexdigest(),'header_md5':b[0x28:0x38].hex(),'md5_matches':hashlib.md5(raw).digest()==b[0x28:0x38],'adler32':f'{zlib.adler32(raw):08x}','trailer':compressed[-4:].hex(),'adler32_matches':struct.pack('>I',zlib.adler32(raw))==compressed[-4:],'head_length_at_0x24':struct.unpack_from('>I',b,0x24)[0],'dinf_length_at_0x5c':struct.unpack_from('>I',b,0x5c)[0]}
assert r['decompression']['md5_matches'], 'Payload MD5 mismatch'
assert r['decompression']['adler32_matches'], 'zlib Adler-32 mismatch'
assert len(raw)==r['decompression']['head_length_at_0x24']==r['decompression']['dinf_length_at_0x5c'], 'Payload length mismatch'
# Magic hits are candidates only, never proof of a format.
magics={'ELF':b'\x7fELF','PE_MZ':b'MZ','gzip':b'\x1f\x8b\x08','xz':b'\xfd7zXZ\x00','7z':b'7z\xbc\xaf\x27\x1c','zip':b'PK\x03\x04','bzip2':b'BZh','squashfs_le':b'hsqs','squashfs_be':b'sqsh','uImage':b'\x27\x05\x19\x56','FDT':b'\xd0\x0d\xfe\xed','PNG':b'\x89PNG\r\n\x1a\n','JPEG':b'\xff\xd8\xff','ARM_exidx_text':b'.ARM.exidx','PEM':b'-----BEGIN','DER_sequence':b'\x30\x82'}
r['magic_candidates']={name:[m.start() for m in re.finditer(re.escape(magic),raw)] for name,magic in magics.items()}
r['windows_4k']=[{'offset':i,'size':len(raw[i:i+4096]),'entropy':entropy(raw[i:i+4096])} for i in range(0,len(raw),4096)]
# Evaluate every legal zlib header, bound output to 4 MiB per candidate.
r['embedded_zlib_valid']=[];r['embedded_zlib_candidates']=0
for i in range(len(raw)-2):
 cmf,flg=raw[i:i+2]
 if cmf&15==8 and cmf>>4<=7 and (cmf*256+flg)%31==0:
  r['embedded_zlib_candidates']+=1
  try:
   o=zlib.decompressobj();dd=o.decompress(raw[i:],4*1024*1024)
   if o.eof:r['embedded_zlib_valid'].append({'offset':i,'output_bytes':len(dd)})
  except zlib.error:pass
(a.out/'analysis.json').write_text(json.dumps(r,indent=2)+'\n')
for f,d in [('original',b),('decompressed',raw)]:
 (a.out/(f+'.strings.txt')).write_text('\n'.join(f'{m.start():08x} {m.group().decode("ascii")}' for m in re.finditer(rb'[\x20-\x7e]{8,}',d))+'\n')
print(json.dumps({k:v for k,v in r.items() if k not in ('windows_4k','magic_candidates')},indent=2))
# Parse stored DEFLATE blocks in this sample; reject other types explicitly.
off=2;blocks=[]
while True:
 h=compressed[off];last=h&1;kind=(h>>1)&3
 if kind!=0:raise ValueError('Non-stored DEFLATE block; use general bitstream parser')
 n,inv=struct.unpack_from('<HH',compressed,off+1);assert n^inv==65535
 blocks.append({'compressed_offset':off,'svu_offset':off+104,'final':bool(last),'type':'stored','size':n});off+=5+n
 if last:break
assert off+4==len(compressed) and sum(x['size'] for x in blocks)==len(raw)
(a.out/'deflate_blocks.json').write_text(json.dumps(blocks,indent=2)+'\n')
