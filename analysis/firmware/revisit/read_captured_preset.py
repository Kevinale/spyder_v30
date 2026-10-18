#!/usr/bin/env python3
"""Strict read-only parser of an already captured edit-buffer reply."""
from pathlib import Path
import json,struct,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
syms=json.loads((ROOT/'captures/device_symbols.json').read_text());names={x['index']:x['text']for x in syms}
messages=json.loads((ROOT/'captures/logical_messages.json').read_text())
m=next(x for x in messages if x['logical_index']==18)
b=bytes.fromhex(m['payload_hex']);assert struct.unpack_from('<i',b)[0]==0
p=4;entries=[];stack=[];section=None
while p<len(b):
 start=p;assert p+6<=len(b)
 key,typ=struct.unpack_from('<IH',b,p);p+=6
 if typ==0:value=None
 elif typ in(1,2,7):assert p+4<=len(b);value=struct.unpack_from('<i',b,p)[0];p+=4
 elif typ==3:assert p+4<=len(b);value=struct.unpack_from('<f',b,p)[0];p+=4
 elif typ==4:
  assert p+4<=len(b);n=struct.unpack_from('<I',b,p)[0];p+=4
  assert 0<n<=len(b)-p and b[p+n-1]==0;value=b[p:p+n-1].decode('utf-8');p+=n
 else:raise ValueError((start,typ))
 if key==0x80000001:section=struct.pack('>I',value).decode()
 if key==0x80000003:stack.append(names.get(value,str(value)))
 e={'payload_offset':start,'key':hex(key),'type':typ,'value':value,'section':section,'block_path':list(stack)}
 if key<0x80000000:e['symbol']=names.get(key) if section=='GTRT' else None
 entries.append(e)
 if key==0x80000004:assert stack;stack.pop()
 if key==0x80000002:assert not stack
assert p==len(b) and not stack
hits=[e for e in entries if e.get('symbol')in ['AmpEnableState','AmpEnable','FX1EnableState','CabEnableState','GuitarProcEnableState']]
result={'message_index':18,'channel':m['channel'],'frames':[m['first_frame'],m['last_frame']],'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'fully_consumed':True,'entry_count':len(entries),'key_hits':hits,'entries':entries,'limit':'Stored preset state does not prove runtime writable support or preservation of physical knob telemetry after disabling Amp.'}
(OUT/'captured_edit_buffer.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'captured_edit_buffer.bin').write_bytes(b)
print('PASS: parsed',len(entries),'entries and consumed all',len(b),'bytes; root matches:')
print(json.dumps(hits,indent=2))
