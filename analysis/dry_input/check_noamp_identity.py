#!/usr/bin/env python3
"""Check whether No Amp notification bodies retain separate knob identities."""
from pathlib import Path
from collections import Counter
import json,struct
root=Path(__file__).resolve().parents[1]
messages=json.loads((root/'captures_noamp/logical_messages.json').read_text())
rows=[];patterns=Counter()
for m in messages:
 if m['direction']=='IN' and m['opcode']==4 and m['payload_length']==16:
  raw=bytes.fromhex(m['payload_hex']);g,p,t=struct.unpack('<III',raw[:12]);v=struct.unpack('<f',raw[12:])[0]
  patterns[(g,p,t)]+=1
  rows.append({'first_frame':m['first_frame'],'last_frame':m['last_frame'],'time':m['first_time'],'group':g,'parameter':hex(p),'type':t,'value':v})
assert len(rows)==650 and patterns==Counter({(42,0xffffffff,4):650})
result={'notifications':len(rows),'metadata_patterns':[{'group':g,'parameter':hex(p),'type':t,'count':n}for (g,p,t),n in patterns.items()],'only_variable_payload_bytes':'12..15: float32; bytes 0..11 are identical in all 650 notification payloads','conclusion':'The observed notification body does not carry four distinct parameter IDs. Transport sequence/time cannot be assumed to identify a physical knob. This does not exclude other firmware telemetry channels.','first_examples':rows[:3]}
(root/'dry_input/noamp_identity.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 650 device->host notifications; one (42,0xffffffff,4) metadata pattern; only float value varies inside payload.')
