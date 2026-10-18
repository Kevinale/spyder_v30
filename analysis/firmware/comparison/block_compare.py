from pathlib import Path
import hashlib,json,collections,struct
root=Path('/workspace/analysis/firmware');a=(root/'v2.02/data.decompressed.bin').read_bytes();b=(root/'data.decompressed.bin').read_bytes()
r={'method':'Nonoverlapping blocks indexed in 2.02, searched at every byte offset in 2.05; exact byte verification after hash lookup.','matches':{}}
for size in (16,64,256,1024,4096):
 index=collections.defaultdict(list)
 for i in range(0,len(a)-size+1,size):index[a[i:i+size]].append(i)
 matches=[]
 for j in range(len(b)-size+1):
  key=b[j:j+size]
  if key in index:
   for i in index[key]:matches.append({'offset_2_02':i,'offset_2_05':j,'bytes':size})
 r['matches'][str(size)]={'count':len(matches),'first_100':matches[:100]}
# XOR distribution is descriptive and does not establish encryption or its absence.
x=bytes(i^j for i,j in zip(a,b));r['same_offset_xor']={'compared_bytes':len(x),'most_common':collections.Counter(x).most_common(12),'first_64_hex':x[:64].hex()}
r['input_sha256']=[hashlib.sha256(a).hexdigest(),hashlib.sha256(b).hexdigest()]
(root/'comparison/block_comparison.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
