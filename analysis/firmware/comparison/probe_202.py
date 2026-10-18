import importlib.util,json,hashlib
from pathlib import Path
root=Path('/workspace/analysis/firmware');spec=importlib.util.spec_from_file_location('ldr',root/'blackfin/probe_ldr.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=(root/'v2.02/data.decompressed.bin').read_bytes();rows=[]
for name,data in m.mod.variants(b):
 candidates=[];strong=[]
 for pos in range(len(data)-15):
  if data[pos+3]!=0xad:continue
  h=m.header(data,pos)
  if h:
   candidates.append(h);chain=m.chain(data,pos)
   if chain and chain['count']>=2:strong.append(chain)
 rows.append({'transform':name,'header_candidates':len(candidates),'multi_block_candidates':strong})
print(json.dumps(rows,indent=2));(root/'comparison/2.02_ldr_probe.json').write_text(json.dumps({'sha256':hashlib.sha256(b).hexdigest(),'hypothesis':'Same bounded generic Blackfin header hypothesis used for 2.05; not exhaustive BF707 validation.','results':rows},indent=2)+'\n')
