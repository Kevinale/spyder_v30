#!/usr/bin/env python3
"""Offline SVU comparison. Never executes firmware or accesses a device."""
import argparse, hashlib, json, struct, zlib
from pathlib import Path

def load(path):
    b = path.read_bytes()
    if len(b)<12 or b[:4]!=b'FORM' or b[8:12]!=b'L6FF' or struct.unpack_from('>I',b,4)[0]+8!=len(b):
        raise ValueError('Invalid FORM/L6FF length or magic')
    chunks={}; pos=12
    while pos<len(b):
        if pos+8>len(b): raise ValueError('Truncated chunk header')
        name=b[pos:pos+4].decode('ascii'); n=struct.unpack_from('>I',b,pos+4)[0]
        end=pos+8+n
        if end>len(b) or name in chunks: raise ValueError('Invalid or duplicate chunk')
        chunks[name]=(pos,b[pos+8:end]); pos=end+(n&1)
    if pos!=len(b): raise ValueError('Missing padding')
    head=chunks['HEAD'][1]
    if len(head)<52: raise ValueError('Short HEAD')
    dec=zlib.decompressobj(); raw=dec.decompress(chunks['data'][1])+dec.flush()
    if not dec.eof or dec.unused_data: raise ValueError('Invalid zlib extent')
    if len(raw)!=struct.unpack_from('>I',head,16)[0] or hashlib.md5(raw).digest()!=head[20:36]:
        raise ValueError('HEAD payload size/MD5 mismatch')
    return {'path':str(path),'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),
            'head_words':list(struct.unpack('>13I',head[:52])),
            'chunks':{k:{'offset':v[0],'size':len(v[1]),'sha256':hashlib.sha256(v[1]).hexdigest()} for k,v in chunks.items()},
            'payload_size':len(raw),'payload_sha256':hashlib.sha256(raw).hexdigest()},raw

def compare(a,b):
    limit=min(len(a),len(b)); prefix=0; suffix=0
    while prefix<limit and a[prefix]==b[prefix]: prefix+=1
    while suffix<limit-prefix and a[-suffix-1]==b[-suffix-1]: suffix+=1
    blocks=[]
    for off in range(0,limit,4096):
        x,y=a[off:off+4096],b[off:off+4096]
        blocks.append({'offset':off,'same_length':len(x)==len(y),'equal_bytes':sum(i==j for i,j in zip(x,y)),'compared_bytes':min(len(x),len(y))})
    return {'identical':a==b,'common_prefix_bytes':prefix,'common_suffix_bytes':suffix,
            'same_offset_equal_bytes':sum(x==y for x,y in zip(a,b)),
            'aligned_4096_byte_windows':blocks,
            'limits':'Differences do not establish encryption, executable boundaries, relocation or instruction set.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('first',type=Path);p.add_argument('second',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    if args.output.resolve() in (args.first.resolve(),args.second.resolve()): p.error('Output must not overwrite an input')
    x,a=load(args.first); y,b=load(args.second)
    args.output.write_text(json.dumps({'first':x,'second':y,'comparison':compare(a,b)},indent=2)+'\n')
    print('Comparison saved:',args.output)
