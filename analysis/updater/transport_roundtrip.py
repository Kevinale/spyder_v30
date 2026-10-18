"""Offline validation of the observed 7-bit transport encoding. No USB/MIDI IO."""
from pathlib import Path
import json,hashlib,functools,operator
R=Path(__file__).resolve().parent

def encode(raw):
 out=bytearray()
 for i in range(0,len(raw),7):
  group=raw[i:i+7];out.append(sum(((v>>7)&1)<<(6-j)for j,v in enumerate(group)))
  out.extend(v&127 for v in group)
 return bytes(out)
def xor(data):return functools.reduce(operator.xor,data,0)
def decode(packed,checksum):
 if any(x>127 for x in packed) or xor(packed)!=checksum:raise ValueError('invalid7bit/checksum')
 out=bytearray()
 for i in range(0,len(packed),8):
  group=packed[i:i+8]
  if len(group)<2:raise ValueError('orphan mask')
  for j,v in enumerate(group[1:]):out.append(v|(((group[0]>>(6-j))&1)<<7))
 return bytes(out)

def main():
 # All byte values, boundaries and corruption: verification, not execution of updater.
 for n in [1,6,7,8,27,28,29,255,256]:
  data=bytes(i%256 for i in range(n));packed=encode(data);assert decode(packed,xor(packed))==data
 bad=bytearray(encode(b'\xff\x80\x01'));check=xor(bad);bad[-1]^=1
 try:decode(bad,check);raise AssertionError('corruption accepted')
 except ValueError:pass
 p=R.parent/'firmware/data.decompressed.bin';data=p.read_bytes();back=bytearray();n=0;maxlen=0
 for i in range(0,len(data),28):
  packed=encode(data[i:i+28]);assert len(packed)<=32;maxlen=max(maxlen,len(packed));back.extend(decode(packed,xor(packed)));n+=1
 assert bytes(back)==data
 result={'input':str(p),'bytes':len(data),'input_sha256':hashlib.sha256(data).hexdigest(),'decoded_sha256':hashlib.sha256(back).hexdigest(),'modeled_encoded_capacity':32,'raw_bytes_per_full_packet':28,'modeled_packets':n,'max_encoded_bytes':maxlen,'exact_roundtrip':True,'bad_checksum_rejected':True,'limits':'Offline model based on static code, not device capture or complete updater reimplementation. No ready-to-send messages generated; no device IO.'}
 (R/'transport_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
