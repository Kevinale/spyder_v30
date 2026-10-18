"""Test a zero-padding-based periodic XOR hypothesis; never establishes decoding alone."""
from pathlib import Path
import collections,json,hashlib,importlib.util,math
root=Path('/workspace/analysis/firmware');sp=importlib.util.spec_from_file_location('ldr',root/'blackfin/probe_ldr.py');ldr=importlib.util.module_from_spec(sp);sp.loader.exec_module(ldr)
def entropy(b):
 c=collections.Counter(b);return -sum(n/len(b)*math.log2(n/len(b)) for n in c.values())
a=(root/'v2.02/data.decompressed.bin').read_bytes();b=(root/'data.decompressed.bin').read_bytes();rows=[]
for period in (1,2,4,8,16,32,64,128,256,512,1024):
 # Infer each byte from modal value in 2.02, assuming zeros are common plaintext.
 key=bytes(collections.Counter(a[i::period]).most_common(1)[0][0] for i in range(period))
 row={'period':period,'hypothesis':'2.02 modal phase byte assumed zero plaintext; unverified','key_sha256':hashlib.sha256(key).hexdigest(),'results':[]}
 for name,data in [('2.02',a),('2.05',b)]:
  out=bytes(v^key[i%period] for i,v in enumerate(data));chains=[]
  for pos in range(len(out)-15):
   if out[pos+3]==0xad:
    c=ldr.chain(out,pos)
    if c and c['count']>=2:chains.append(c)
  row['results'].append({'version':name,'entropy':entropy(out),'zero_fraction':out.count(0)/len(out),'multi_block_ldr_candidates':chains,'ELF_magic_count':out.count(b'\x7fELF'),'known_name_hits':[x.decode() for x in (b'AmpEnable',b'GuitProcOutputGain',b'Blackfin',b'Line6') if x in out]})
 rows.append(row)
 print(period,[(r['version'],round(r['zero_fraction'],4),len(r['multi_block_ldr_candidates']),r['known_name_hits']) for r in row['results']],flush=True)
(root/'structure/periodic_xor.json').write_text(json.dumps({'limits':'Negative results apply only to these periods, modal-zero assumption and same phase; no encryption conclusion.','results':rows},indent=2)+'\n')
