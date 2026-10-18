#!/usr/bin/env python3
"""Package reports and reproducible evidence, omitting tools/runtimes/projects."""
from pathlib import Path
import hashlib, json, zipfile
root=Path('/workspace/analysis')
destination=Path('/workspace/SpiderV_NAM_ANALYSIS_v5.zip')
selected=[]
for p in root.rglob('*'):
    if not p.is_file(): continue
    rel=p.relative_to(root)
    if p.suffix.lower() in ('.pcapng','.pcap') or (rel.parts[0]=='captures_noamp' and 'input' in rel.parts): continue
    if rel.parts[0]=='tools': continue
    if rel.parts[0]=='remote':
        if any(x in rel.parts for x in ('volumes','reconstructed','projects','ghidra','config','cache','.cache')): continue
        if 'extracted' in rel.parts and p.suffix.lower() not in ('.json','.models','.bin','.plist'): continue
        if p.suffix in ('.gpr','.lock','.ulock') or any(x.endswith('.rep') for x in rel.parts): continue
    if rel.parts[0]=='usb' and not (len(rel.parts)==2 and p.suffix in ('.txt','.h')): continue
    if '__pycache__' in rel.parts or p.name=='EVIDENCE_SHA256.json': continue
    selected.append(p)
selected.sort()
manifest={str(p.relative_to(root)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in selected}
manifest_path=root/'EVIDENCE_SHA256.json'
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in selected+[manifest_path]: z.write(p,Path('SpiderV_NAM_ANALYSIS')/p.relative_to(root))
with zipfile.ZipFile(destination) as z:
    assert z.testzip() is None
    for name,meta in manifest.items():
        assert hashlib.sha256(z.read('SpiderV_NAM_ANALYSIS/'+name)).hexdigest()==meta['sha256']
digest=hashlib.sha256(destination.read_bytes()).hexdigest()
destination.with_suffix('.zip.sha256').write_text(f'{digest}  {destination.name}\n')
print(json.dumps({'archive':str(destination),'bytes':destination.stat().st_size,'files':len(selected)+1,'sha256':digest},indent=2))
