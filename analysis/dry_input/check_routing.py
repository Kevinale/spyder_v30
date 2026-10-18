#!/usr/bin/env python3
"""Read-only audit of existing USB captures and extracted Remote resources."""
from pathlib import Path
import json,struct,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dry_input'
inputs=[]
def read(rel):
 p=ROOT/rel;b=p.read_bytes();inputs.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});return b
rows=[]
for folder in ['captures','captures_tone','captures_noamp']:
 frames=json.loads(read(folder+'/target_frames.json'))
 descriptors=[];interfaces=[];formats=[];endpoints=[];selectors=[];context=None;offset=0
 for f in frames:
  raw=bytes.fromhex(f.get('payload_hex',''))
  if f['transfer_type']==2 and f['completion'] and len(raw)>=9 and raw[1]==2 and len(raw)==int.from_bytes(raw[2:4],'little'):
   descriptors.append({'frame':f['frame'],'payload_offset':f['payload_offset'],'hex':raw.hex()})
 if not descriptors:raise ValueError('No configuration descriptor in '+folder)
 raw=bytes.fromhex(descriptors[0]['hex'])
 while offset<len(raw):
  n,typ=raw[offset:offset+2];assert n>=2 and offset+n<=len(raw)
  a=raw[offset:offset+n]
  if typ==4:
   context={'interface':a[2],'alternate':a[3],'endpoints':a[4],'class':a[5],'subclass':a[6]}
   interfaces.append(dict(context,configuration_offset=offset))
  elif typ==36 and context and context['class']==1:
   if context['subclass']==1 and a[2]==5:selectors.append({'configuration_offset':offset,'hex':a.hex()})
   if context['subclass']==2 and a[2]==2:
    assert a[3]==1
    rates=[int.from_bytes(a[i:i+3],'little')for i in range(8,8+3*a[7],3)]
    formats.append(dict(context,configuration_offset=offset,channels=a[4],subframe_bytes=a[5],resolution_bits=a[6],rates_hz=rates))
  elif typ==5 and context:
   endpoints.append(dict(context,configuration_offset=offset,address=hex(a[2]),attributes=hex(a[3]),transfer=['control','isochronous','bulk','interrupt'][a[3]&3],usage=(a[3]>>4)&3,max_packet=int.from_bytes(a[4:6],'little')))
  offset+=n
 assert len(formats)==2 and all(f['channels']==2 and f['resolution_bits']==16 and f['rates_hz']==[48000,44100]for f in formats)
 assert not selectors
 assert [x['address']for x in endpoints if x['transfer']=='isochronous' and x['usage'] in (0,2)]==['0x83','0x4']
 assert [x['address']for x in endpoints if x['transfer']=='isochronous' and x['usage']==1]==['0x84']
 rows.append({'capture':folder,'config_descriptor_instances':len(descriptors),'descriptor':descriptors[0],'interfaces':interfaces,'formats':formats,'endpoints':endpoints,'standard_selector_units':selectors})
assert len({r['descriptor']['hex']for r in rows})==1
fixed=json.loads(read('remote/resources/fixed.models.json'))
assets=json.loads(read('remote/resources/assets.json'))
models=json.loads(read('remote/resources/amps.models.json'))
noamp=[m for m in models if m['symbolicID']=='Bypass'];assert len(noamp)==1
assert [p['symbolicID']for p in noamp[0]['params']]==['@volume']
amp_assets=[a for a in assets if '/ampCategory' in a.get('category_path','')]
amp_enabled=[a.get('engineID')for a in amp_assets if any(p.get('engineID')=='@enabled'for p in a.get('assetParameters',[]))]
assert not amp_enabled
symbols=json.loads(read('captures/device_symbols.json'))
hits=[s for s in symbols if re.search('USB|Guit.*Gain|Bypass|Dry|dry|Record|record|Routing|routing',s['text'])]
il=read('remote/managed/Spider_V_Remote.il.txt').decode()
il_hits=[{'line':i+1,'text':s.strip()}for i,s in enumerate(il.splitlines())if 'ldstr ' in s and re.search(r'usb|dry|unprocessed|reamp|recording|monitor',s,re.I)]
# This records negative search results, not a proof that binary functionality is absent.
native=read('remote/native/audio_bypass_targets.txt').decode()
assert 'BypassGlobalEQ' in native and 'FUN_10084100' in native
result={'usb':rows,'same_configuration_all_captures':True,'no_amp':noamp[0],'amp_asset_count':len(amp_assets),'amp_assets_with_enabled_param':amp_enabled,'symbol_candidates':hits,'managed_routing_literal_hits':il_hits,'inputs':inputs,'limitations':['No hardware access or vendor requests executed.','Absent descriptors or strings do not exclude undocumented firmware routing.','USBInLevel/USBOutLevel/Guit*Gain names alone do not establish tap points or writable semantics.','Reported live tests are owner observations, not local instrumented measurements.']}
(OUT/'routing_evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: same USB config in 3 captures; one stereo capture and playback stream; feedback endpoint distinguished; no standard selector; No Amp Volume-only; '+str(len(amp_assets))+' amp assets without declared @enabled; managed routing literal hits='+str(len(il_hits)))
for r in rows:print(r['capture'],r['descriptor']['frame'],r['descriptor']['payload_offset'])
