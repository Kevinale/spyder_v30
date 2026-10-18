#!/usr/bin/env python3
"""Offline PCAPNG/USBPcap and USB-MIDI SysEx parser. No USB APIs or device access."""
import argparse,collections,csv,hashlib,json,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--out',type=Path,default=Path('/workspace/analysis/captures'));p.add_argument('--control-midi-only',action='store_true',help='Export only control/bulk metadata and payloads; omit audio ISO from target_frames.json');a=p.parse_args();a.out.mkdir(exist_ok=True,parents=True)
b=a.input.read_bytes(); off=0; interfaces=[];frames=[];base=None;blocks=collections.Counter();endian='<'
def options(data):
 o=0;result={}
 while o+4<=len(data):
  t,n=struct.unpack_from(endian+'HH',data,o);o+=4
  if t==0:break
  assert o+n<=len(data)
  result[t]=data[o:o+n];o+=(n+3)&~3
 return result
while off<len(b):
 assert off+12<=len(b)
 if b[off:off+4]==b'\x0a\x0d\x0d\x0a':
  endian='<' if b[off+8:off+12]==b'\x4d\x3c\x2b\x1a' else '>'
  assert b[off+8:off+12] in (b'\x4d\x3c\x2b\x1a',b'\x1a\x2b\x3c\x4d')
  interfaces=[]
 t,n=struct.unpack_from(endian+'II',b,off);assert n>=12 and n%4==0 and off+n<=len(b)
 assert struct.unpack_from(endian+'I',b,off+n-4)[0]==n;blocks[t]+=1;body=b[off+8:off+n-4]
 if t==1:
  link,_,snap=struct.unpack_from(endian+'HHI',body);opts=options(body[8:]);res=opts.get(9,b'\x06')[0]
  scale=(2**-(res&127)) if res&128 else 10**-res
  interfaces.append({'link_type':link,'snaplen':snap,'resolution':res,'scale':scale,'name':opts.get(2,b'').decode(errors='replace')})
 if t==6:
  i,hi,lo,cap,wire=struct.unpack_from(endian+'IIIII',body);assert i<len(interfaces) and 20+cap<=len(body)
  assert interfaces[i]['link_type']==249,'Expected USBPcap link type 249'
  raw=body[20:20+cap];assert len(raw)>=27
  h,irp,status,func,info,bus,dev,ep,typ,length=struct.unpack_from('<HQIHBHHBBI',raw)
  assert 27<=h<=len(raw)
  ts=((hi<<32)|lo)*interfaces[i]['scale']
  if base is None:base=ts
  payload=raw[h:]
  assert len(payload)==length, 'Truncation or unexpected USBPcap data length'
  row={'frame':len(frames)+1,'block_offset':off,'packet_offset':off+28,'captured_length':cap,'wire_length':wire,
       'time':round(ts-base,6),'timestamp':ts,'interface':i,'header_len':h,'irp_id':hex(irp),'status':hex(status),
       'function':hex(func),'completion':bool(info&1),'bus':bus,'device':dev,'endpoint':hex(ep),'transfer_type':typ,
       'data_length':length,'payload_offset':off+28+h,'payload_hex':payload.hex()}
  if typ==2 and h>=28:
   row['control_stage']=raw[27]
   if raw[27]==0 and len(payload)>=8:
    rt,rq,v,idx,ln=struct.unpack_from('<BBHHH',payload)
    row['setup']={'bmRequestType':hex(rt),'bRequest':hex(rq),'wValue':hex(v),'wIndex':hex(idx),'wLength':ln}
  frames.append(row)
 off+=n
assert off==len(b)
# Select only the target; do not publish other USB device payloads.
targets=set()
for r in frames:
 d=bytes.fromhex(r['payload_hex'])
 if r['completion'] and r['transfer_type']==2 and d[:2]==b'\x12\x01' and len(d)>=18:
  vid,pid=struct.unpack_from('<HH',d,8)
  if (vid,pid)==(0x0e41,0x5068):targets.add((r['bus'],r['device']))
assert targets,'Spider V 30 descriptor not found'
target=[r for r in frames if (r['bus'],r['device']) in targets]
messages=[];partial={};warnings=[];midi_events=0
cin_lengths={2:2,3:3,4:3,5:1,6:2,7:3,8:3,9:3,10:3,11:3,12:2,13:2,14:3,15:1}
for r in target:
 ep=int(r['endpoint'],16)
 if r['transfer_type']!=3 or not r['data_length']:continue
 # OUT data on request, IN data on completion: no double counting of URBs.
 if bool(ep&128)!=r['completion']:continue
 direction='IN' if ep&128 else 'OUT';data=bytes.fromhex(r['payload_hex']);assert len(data)%4==0
 for i in range(0,len(data),4):
  event=data[i:i+4];cin=event[0]&15;cable=event[0]>>4;midi_events+=1
  if cin not in cin_lengths:warnings.append({'frame':r['frame'],'invalid_cin':cin});continue
  midi=event[1:1+cin_lengths[cin]];key=(r['bus'],r['device'],ep,cable)
  if cin in (4,5,6,7):
   if midi[:1]==b'\xf0':
    if key in partial:warnings.append({'frame':r['frame'],'replaced_unfinished_sysex':True})
    partial[key]={'data':bytearray(),'first_frame':r['frame'],'first_time':r['time'],'event_offsets':[],'frames':[]}
   if key not in partial:
    warnings.append({'frame':r['frame'],'unmatched_sysex_fragment':midi.hex()});continue
   x=partial[key];x['data'].extend(midi);x['event_offsets'].append(r['payload_offset']+i)
   if not x['frames'] or x['frames'][-1]!=r['frame']:x['frames'].append(r['frame'])
   if cin in (5,6,7):
    msg=bytes(x['data']);assert msg[:1]==b'\xf0' and msg[-1:]==b'\xf7'
    messages.append({'index':len(messages)+1,'direction':direction,'endpoint':hex(ep),'cable':cable,
        'first_frame':x['first_frame'],'last_frame':r['frame'],'first_time':x['first_time'],'last_time':r['time'],
        'length':len(msg),'hex':msg.hex(),'frames':x['frames'],'event_offsets':x['event_offsets']})
    del partial[key]
  else:warnings.append({'frame':r['frame'],'non_sysex_midi':midi.hex(),'cin':cin})
export_target=[r for r in target if r['transfer_type'] in (2,3)] if a.control_midi_only else target
summary={'input':str(a.input),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'frames':len(frames),
         'duration_seconds':frames[-1]['time'],'interfaces':interfaces,'targets':sorted(targets),
         'target_frames':len(target),'exported_target_frames':len(export_target),'export_control_midi_only':a.control_midi_only,
         'target_transfer_counts':dict(collections.Counter(str(r['transfer_type']) for r in target)),
         'all_usb_status_zero':all(r['status']=='0x0' for r in frames),
         'target_payload_urbs':sum(r['data_length']>0 and r['transfer_type']==3 for r in target),
         'midi_events':midi_events,'sysex_messages':len(messages),'sysex_counts':dict(collections.Counter(m['direction'] for m in messages)),
         'unfinished_sysex':len(partial),'warnings':warnings}
for name,rows in [('target_frames',export_target),('sysex_messages',messages)]:
 (a.out/(name+'.json')).write_text(json.dumps(rows,indent=2)+'\n')
(a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
with (a.out/'sysex_messages.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['index','direction','first_frame','last_frame','first_time','last_time','length','hex']);w.writeheader()
 for m in messages:w.writerow({k:m[k] for k in w.fieldnames})
print(json.dumps(summary,indent=2))
