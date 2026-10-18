#!/usr/bin/env python3
"""Offline-only: reproduce APIV3 FUN_10057aa0 MSB decoding; never send packets."""
import json,pathlib,collections,struct,argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--directory',type=pathlib.Path,default=pathlib.Path('/workspace/analysis/captures'))
ROOT=parser.parse_args().directory
def unpack(payload):
 assert len(payload)%8==0
 out=bytearray()
 for i in range(0,len(payload),8):
  mask=payload[i]
  for j in range(7):out.append((payload[i+1+j]&127)|((mask<<(j+1))&128))
 return bytes(out)
def pack(raw):
 out=bytearray()
 for i in range(0,len(raw),7):
  group=raw[i:i+7].ljust(7,b'\0'); mask=sum(((b>>7)&1)<<(6-j) for j,b in enumerate(group));out.append(mask);out.extend(b&127 for b in group)
 return bytes(out)
rows=[]
for m in json.loads((ROOT/'sysex_messages.json').read_text()):
 b=bytes.fromhex(m['hex'])
 if b[:5]!=bytes.fromhex('f000010c22') or len(b)<13 or b[6]!=0x4d:continue
 n=((b[10]&15)<<4|(b[11]&15))+1
 rawp=unpack(b[12:-1]);raw=rawp[:n]
 assert n<=len(rawp) and pack(raw)==b[12:-1]
 r={k:m[k] for k in ['index','direction','first_frame','last_frame','first_time','last_time']}
 r.update(channel=b[7],sequence=b[8],fragment=b[9],raw_length=n,raw_hex=raw.hex(),words_le=[f'0x{x[0]:08x}' for x in struct.iter_unpack('<I',raw[:len(raw)//4*4])])
 rows.append(r)
(ROOT/'native_decoded_packets.json').write_text(json.dumps(rows,indent=2))
print('Decoded and canonical roundtrip verified:',len(rows))
print(collections.Counter((r['direction'],r['raw_length']) for r in rows).most_common(20))
for r in rows[-6:]:print(r)
