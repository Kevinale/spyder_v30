#!/usr/bin/env python3
"""Reassemble captured Parker byte streams and export Drive telemetry. Offline only."""
from pathlib import Path
import collections,csv,hashlib,json,math,struct
R=Path('/workspace/analysis/captures')
raw=json.loads((R/'native_decoded_packets.json').read_text());byid={x['index']:x for x in raw}
streams={};messages=[]
for r in raw:
 key=(r['direction'],r['channel']);s=streams.setdefault(key,{'data':bytearray(),'origins':[],'total':0})
 chunk=bytes.fromhex(r['raw_hex']);s['data'].extend(chunk);s['origins'].extend((r['index'],i) for i in range(len(chunk)));s['total']+=len(chunk)
 while len(s['data'])>=8:
  op,n=struct.unpack_from('<II',s['data']);assert n<=1024*1024,'Implausible logical payload length'
  size=8+n
  if len(s['data'])<size:break
  packet=bytes(s['data'][:size]);origins=s['origins'][:size];parts=[]
  for j,(idx,o) in enumerate(origins):
   if parts and parts[-1]['sysex_index']==idx and parts[-1]['raw_byte_offset']+parts[-1]['length']==o:parts[-1]['length']+=1
   else:parts.append({'logical_offset':j,'sysex_index':idx,'raw_byte_offset':o,'length':1})
  first=byid[origins[0][0]];last=byid[origins[-1][0]]
  messages.append({'logical_index':len(messages)+1,'direction':key[0],'channel':key[1],'opcode':op,'payload_length':n,
    'first_frame':first['first_frame'],'last_frame':last['last_frame'],'first_time':first['first_time'],'last_time':last['last_time'],
    'raw_hex':packet.hex(),'payload_hex':packet[8:].hex(),'parts':parts})
  del s['data'][:size];del s['origins'][:size]
assert all(not s['data'] for s in streams.values()),'Unfinished logical streams'
(R/'logical_messages.json').write_text(json.dumps(messages,indent=2)+'\n')
# The received symbol table is an independent on-device mapping, not an assumption
# that the editor's shipped index ordering matches this firmware.
tables=[]
for m in messages:
 if m['direction']!='IN' or m['opcode']!=1 or m['payload_length']<10000:continue
 data=bytes.fromhex(m['payload_hex']);count,size=struct.unpack_from('<II',data)
 if size!=len(data) or 8+12*count>=len(data):continue
 import zlib
 pool=8+12*count;symbols=[]
 for i in range(count):
  o,c,l=struct.unpack_from('<III',data,8+i*12);p=pool+o;text=data[p:p+l]
  assert p+l<len(data) and data[p+l]==0 and zlib.crc32(text)==c
  symbols.append({'index':i,'text':text.decode('utf8'),'crc32':f'{c:08x}','string_offset':p,'record_offset':8+i*12})
 tables.append((m,data,symbols))
assert len(tables)==1
table_message,data,symbols=tables[0];(R/'device_symbol_reply.bin').write_bytes(data)
(R/'device_symbols.json').write_text(json.dumps(symbols,indent=2)+'\n')
group=next(x['index'] for x in symbols if x['text']=='Amp');param=next(x['index'] for x in symbols if x['text']=='Drive')
events=[]
for m in messages:
 if m['channel']!=0 or m['payload_length']!=16:continue
 if (m['direction'],m['opcode']) not in [('OUT',10),('IN',4)]:continue
 g,p,field4=struct.unpack_from('<III',bytes.fromhex(m['payload_hex']))
 if (g,p)!=(group,param):continue
 payload=bytes.fromhex(m['payload_hex']);value=struct.unpack_from('<f',payload,12)[0];assert math.isfinite(value)
 events.append({'logical_index':m['logical_index'],'direction':m['direction'],'first_frame':m['first_frame'],'last_frame':m['last_frame'],
  'time_seconds':m['first_time'],'group_index':g,'group':'Amp','parameter_index':p,'parameter':'Drive','raw_type_field':field4,
  'value_float32':value,'value_bytes_le':payload[12:16].hex(),'opcode':m['opcode'],
  'sysex_indices':[x['sysex_index'] for x in m['parts']]})
(R/'drive_events.json').write_text(json.dumps(events,indent=2)+'\n')
with (R/'drive_events.csv').open('w',newline='') as f:
 cols=['logical_index','direction','first_frame','last_frame','time_seconds','group','parameter','raw_type_field','value_float32','value_bytes_le']
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
 for e in events:w.writerow({k:e[k] for k in cols})
# Generic telemetry replay for an external controller. It writes no MIDI/USB and
# does not assume a trained NAM model exposes an internal Drive parameter.
with (R/'nam_control_events.jsonl').open('w') as f:
 for e in events:
  if e['direction']=='IN':f.write(json.dumps({'source':'captured_spider_v30','time_seconds':e['time_seconds'],'control':'Amp.Drive','value':e['value_float32'],'source_frame':e['first_frame']})+'\n')
old=json.loads(Path('/workspace/analysis/remote/resources/defaultSymbolTable_Parker.bin.json').read_text())
summary={'logical_messages':len(messages),'streams':[{'direction':k[0],'channel':k[1],'bytes':s['total'],'unconsumed':len(s['data'])} for k,s in streams.items()],
 'received_symbol_table':{'logical_index':table_message['logical_index'],'first_frame':table_message['first_frame'],'last_frame':table_message['last_frame'],'count':len(symbols),
 'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'all_crcs_match':True,'editor_prefix_matches':all(symbols[x['index']]['text']==x['text'] for x in old)},
 'drive_group':group,'drive_parameter':param,'directions':{}}
for direction in ['OUT','IN']:
 es=[e for e in events if e['direction']==direction];assert es
 summary['directions'][direction]={'count':len(es),'first_time':es[0]['time_seconds'],'last_time':es[-1]['time_seconds'],
 'first_frame':es[0]['first_frame'],'last_frame':es[-1]['last_frame'],'min':min(e['value_float32'] for e in es),'max':max(e['value_float32'] for e in es),
 'first_event':es[0],'last_event':es[-1]}
(R/'drive_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
