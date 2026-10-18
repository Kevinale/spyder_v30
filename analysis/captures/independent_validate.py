#!/usr/bin/env python3
"""Independent offline PCAPNG USBPcap validator; publishes target-only data."""
import struct,json,hashlib,collections,argparse
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--input',type=Path,default=Path('/workspace/attachments/61bdc038-8b34-48fc-8c44-f8520be47b2c/SpiderV_USB2perilla.pcapng .pcapng'))
ap.add_argument('--directory',type=Path,default=Path('/workspace/analysis/captures'))
args=ap.parse_args();src=args.input
b=src.read_bytes();cursor=0;frame=0;rows=[];blocks=collections.Counter();base=None;resolution=10**-6
while cursor<len(b):
 kind,size=struct.unpack_from('<II',b,cursor);assert size>=12 and size%4==0 and cursor+size<=len(b)
 assert struct.unpack_from('<I',b,cursor+size-4)[0]==size
 blocks[hex(kind)]+=1
 if kind==0xa0d0d0a:assert b[cursor+8:cursor+12]==b'\x4d\x3c\x2b\x1a'
 if kind==1:
  assert struct.unpack_from('<H',b,cursor+8)[0]==249
  z=cursor+16
  while z<cursor+size-4:
   code,n=struct.unpack_from('<HH',b,z);z+=4
   if not code:break
   if code==9:
    exponent=b[z];resolution=2**-(exponent&127) if exponent&128 else 10**-exponent
   z+=(n+3)//4*4
 if kind==6:
  frame+=1;iface,hi,lo,cap,wire=struct.unpack_from('<IIIII',b,cursor+8)
  assert iface==0 and cap==wire
  ts=((hi<<32)+lo)*resolution
  if base is None:base=ts
  p=cursor+28;h=struct.unpack_from('<H',b,p)[0]
  bus,dev=struct.unpack_from('<HH',b,p+17);ep=b[p+21];typ=b[p+22];length=struct.unpack_from('<I',b,p+23)[0]
  assert cap==h+length
  if (bus,dev)==(2,4):
   rows.append(dict(frame=frame,time=round(ts-base,6),offset=p+h,ep=ep,typ=typ,completion=bool(b[p+16]&1),data=b[p+h:p+cap],h=h,irp=struct.unpack_from('<Q',b,p+2)[0],status=struct.unpack_from('<I',b,p+10)[0],stage=b[p+27] if h==28 else None))
 cursor+=size
assert cursor==len(b)
# Build streams directly from all CINs. Independent F0/F7 assembly, not completion-CIN state.
streams={};messages=[];counts=collections.Counter();padding=[]
lengths={2:2,3:3,4:3,5:1,6:2,7:3,8:3,9:3,10:3,11:3,12:2,13:2,14:3,15:1}
for r in rows:
 if r['typ']!=3 or not r['data']:continue
 assert r['completion']==bool(r['ep']&128)
 data=r['data'];assert len(data)%4==0
 for n in range(0,len(data),4):
  header=data[n];cin=header&15;cable=header>>4;counts[(r['ep'],cable,cin)]+=1
  assert cin in lengths
  key=(r['ep'],cable);payload=data[n+1:n+1+lengths[cin]]
  assert cin in (4,5,6,7)
  if any(data[n+1+lengths[cin]:n+4]):padding.append({'frame':r['frame'],'event_offset':r['offset']+n,'cin':cin,'ignored_bytes':data[n+1+lengths[cin]:n+4].hex()})
  for v in payload:
   if v==240:
    assert key not in streams;streams[key]={'first_frame':r['frame'],'first_time':r['time'],'hex':bytearray()}
   assert key in streams
   streams[key]['hex'].append(v)
   if v==247:
    x=streams.pop(key);x['hex']=x['hex'].hex();x.update(last_frame=r['frame'],last_time=r['time'],direction='IN' if r['ep']&128 else 'OUT');messages.append(x)
assert not streams
root=json.load(open(args.directory/'sysex_messages.json'))
assert len(root)==len(messages)
for x,y in zip(messages,root):
 for k in x:assert x[k]==y[k],(k,x,y)
# Descriptor chain from target configuration completion only.
config=next(r for r in rows if r['typ']==2 and r['completion'] and r['data'][:2]==b'\x09\x02')['data']
assert len(config)==int.from_bytes(config[2:4],'little')
descriptors=[];i=0;interface=None;alt=None
while i<len(config):
 n,t=config[i:i+2];assert n>=2 and i+n<=len(config);d=config[i:i+n]
 entry={'configuration_offset':i,'length':n,'type':t,'hex':d.hex()}
 if t==4:interface=d[2];alt=d[3];entry.update(interface=interface,alternate=alt,endpoints=d[4],class_=d[5],subclass=d[6],protocol=d[7])
 if t==5:entry.update(interface=interface,alternate=alt,endpoint=hex(d[2]),attributes=hex(d[3]),max_packet=int.from_bytes(d[4:6],'little'),interval=d[6])
 if t==36 and interface in (3,4) and len(d)>=8 and d[2]==2:entry['rates_hz']=[int.from_bytes(d[j:j+3],'little') for j in range(8,len(d),3)]
 descriptors.append(entry);i+=n
pending={};unmatched=[];paired=0
for r in rows:
 if r['typ']!=3:continue
 if not r['completion']:
  assert r['irp'] not in pending;pending[r['irp']]=r
 else:
  prior=pending.pop(r['irp'],None)
  if prior is None:unmatched.append({'frame':r['frame'],'endpoint':hex(r['ep'])})
  else:
   assert prior['ep']==r['ep'];paired+=1
report={'all_target_status_zero':all(r['status']==0 for r in rows),'bulk_urb_matched_pairs':paired,'bulk_completion_without_submission':unmatched,'bulk_pending_at_end':[{'frame':r['frame'],'endpoint':hex(r['ep'])} for r in pending.values()],'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'blocks':dict(blocks),'frames':frame,'target_frames':len(rows),'target_only':True,'independent_matches_root_sysex_exactly':True,'messages':len(messages),'nonzero_ignored_padding_events':len(padding),'first_bulk_time':next(r['time'] for r in rows if r['typ']==3),'cin_counts':[{'endpoint':hex(ep),'cable':ca,'cin':ci,'count':co} for (ep,ca,ci),co in sorted(counts.items())],'configuration_descriptors':descriptors}
(args.directory/'independent_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('configuration_descriptors','cin_counts')},indent=2))
