#!/usr/bin/env python3
"""Offline negative controls for the sample-specific SVU parser; originals are read only."""
from pathlib import Path
import hashlib, json, subprocess, sys, tempfile
root=Path('/workspace/analysis')
original=Path('/workspace/attachments/1cef6881-5b69-4396-8afa-a13ba64b248f/SpiderV_30_60_2.05.0.svu')
data=original.read_bytes()
before=hashlib.sha256(data).hexdigest()
cases={'original':data,'truncated':data[:-1]}
for name,offset in [('bad_md5',0x28),('bad_declared_payload_size',0x24),('bad_adler',len(data)-1)]:
    modified=bytearray(data); modified[offset]^=1; cases[name]=bytes(modified)
results=[]
with tempfile.TemporaryDirectory(prefix='spiderv-validation-',dir='/tmp') as tmp:
    base=Path(tmp)
    for name,blob in cases.items():
        inp=base/(name+'.svu'); inp.write_bytes(blob)
        run=subprocess.run([sys.executable,str(root/'firmware/analyze_svu.py'),str(inp),str(base/name)],capture_output=True,text=True)
        expected=(name=='original')
        passed=(run.returncode==0)==expected
        results.append({'case':name,'expected_accept':expected,'exit_code':run.returncode,'passed':passed,
                        'diagnostic':run.stderr.strip().splitlines()[-1] if run.stderr.strip() else 'accepted'})
after=hashlib.sha256(original.read_bytes()).hexdigest()
report={'original_sha256_before':before,'original_sha256_after':after,'original_unchanged':before==after,'cases':results}
(root/'logs/parser_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
sys.exit(0 if before==after and all(x['passed'] for x in results) else 1)
