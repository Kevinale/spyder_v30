#!/usr/bin/env python3
"""Offline generic typed parameter notifications from already decoded Parker streams."""
import argparse,collections,csv,hashlib,json,math,struct
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--directory',type=Path,required=True)
ap.add_argument('--symbols',type=Path,required=True,help='Explicit reference symbol table JSON; provenance retained')
a=ap.parse_args();R=a.directory
packets=json.loads((R/'native_decoded_packets.json').read_text());symbols=json.loads(a.symbols.read_text());names={x['index']:x['text'] for x in symbols}
source=json.loads((R/'summary.json').read_text());streams={};messages=[]
for r in packets:
 key=(r['direction'],r['channel']);s=streams.setdefault(key,{'buffer':bytearray(),'origins':[],'bytes':0})
 chunk=bytes.fromhex(r['raw_hex']);s['buffer'].extend(chunk);s['origins'].extend([r]*len(chunk));s['bytes']+=len(chunk)
 while len(s['buffer'])>=8:
  op,n=struct.unpack_from('<II',s['buffer']);assert n<=1024*1024
  if len(s['buffer'])<8+n:break
  packet=bytes(s['buffer'][:8+n]);first=s['origins'][0];last=s['origins'][7+n];ps=[]
  for x in s['origins'][:8+n]:
   if not ps or ps[-1]!=x['index']:ps.append(x['index'])
  messages.append({'logical_index':len(messages)+1,'direction':key[0],'channel':key[1],'opcode':op,'payload_length':n,
                   'first_frame':first['first_frame'],'last_frame':last['last_frame'],'first_time':first['first_time'],'last_time':last['last_time'],
                   'sysex_indices':ps,'raw_hex':packet.hex(),'payload_hex':packet[8:].hex()})
  del s['buffer'][:8+n];del s['origins'][:8+n]
assert all(not s['buffer'] for s in streams.values())
events=[]
for m in messages:
 if m['channel']!=0 or m['payload_length']!=16 or (m['direction'],m['opcode']) not in [('IN',4),('OUT',10)]:continue
 payload=bytes.fromhex(m['payload_hex']);g,p,t=struct.unpack_from('<III',payload)
 if t!=4:continue
 value=struct.unpack_from('<f',payload,12)[0];assert math.isfinite(value)
 events.append({'logical_index':m['logical_index'],'direction':m['direction'],'time_seconds':m['first_time'],'last_time_seconds':m['last_time'],
                'first_frame':m['first_frame'],'last_frame':m['last_frame'],'group_index':g,'group':names.get(g,f'unknown:{g}'),
                'parameter_index':p,'parameter':names.get(p,f'unknown:{p}'),'type':t,'value':value,'value_bytes_le':payload[12:].hex(),
                'raw_api_hex':m['raw_hex'],'sysex_indices':m['sysex_indices']})
controls=[]
for key in sorted(set((e['group_index'],e['parameter_index'],e['direction']) for e in events)):
 es=[e for e in events if (e['group_index'],e['parameter_index'],e['direction'])==key]
 controls.append({'group_index':key[0],'group':es[0]['group'],'parameter_index':key[1],'parameter':es[0]['parameter'],'direction':key[2],
                  'count':len(es),'first_time':es[0]['time_seconds'],'last_time':es[-1]['last_time_seconds'],
                  'first_frame':es[0]['first_frame'],'last_frame':es[-1]['last_frame'],
                  'min':min(e['value'] for e in es),'max':max(e['value'] for e in es),'unique_values':len(set(e['value'] for e in es))})
named_in=[e for e in events if e['direction']=='IN' and not e['group'].startswith('unknown:') and not e['parameter'].startswith('unknown:')]
unresolved_in=[e for e in events if e['direction']=='IN' and (e['group'].startswith('unknown:') or e['parameter'].startswith('unknown:'))]
summary={'input_sha256':source['sha256'],'input_bytes':source['bytes'],'frames':source['frames'],'duration_seconds':source['duration_seconds'],
         'raw_parker_packets':len(packets),'logical_messages':len(messages),'opcode_counts':dict(collections.Counter(str(m['opcode']) for m in messages)),
         'stream_unconsumed_bytes':sum(len(s['buffer']) for s in streams.values()),'symbol_reference':str(a.symbols),
         'symbol_reference_sha256':hashlib.sha256(a.symbols.read_bytes()).hexdigest(),
         'symbol_provenance_note':'Explicit reference table from prior capture; no new table assumed received in this file.',
         'controls':controls,'typed_control_events':len(events),'named_incoming_control_events':len(named_in),
         'unresolved_incoming_events':len(unresolved_in),'other_logical_messages':len(messages)-len(events)}
for n,x in [('logical_messages',messages),('control_events',events),('controls_summary',summary)]:
 (R/(n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
with (R/'control_events.csv').open('w',newline='') as f:
 cols=['direction','time_seconds','first_frame','last_frame','group_index','group','parameter_index','parameter','type','value','value_bytes_le']
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
 for e in events:w.writerow({k:e[k] for k in cols})
with (R/'nam_control_events.jsonl').open('w') as f:
 for e in named_in:
  f.write(json.dumps({'source':'captured_spider_v30','capture_sha256':source['sha256'],'time_seconds':e['time_seconds'],
   'control':e['group']+'.'+e['parameter'],'value':e['value'],'source_frame':e['first_frame']})+'\n')
with (R/'unresolved_events.jsonl').open('w') as f:
 for e in unresolved_in:f.write(json.dumps({'source':'captured_spider_v30','capture_sha256':source['sha256'],
  'time_seconds':e['time_seconds'],'group_index':e['group_index'],'parameter_index':e['parameter_index'],
  'type':e['type'],'value':e['value'],'source_frame':e['first_frame'],'mapping':'unresolved; do not route as a named NAM control'})+'\n')
print(json.dumps(summary,indent=2))
