from pathlib import Path
import json,hashlib
p=Path('/workspace/attachments/ef63fc06-4cf7-49ac-8747-fdb26ccbee3d/Deity Crunch.svl6p');original=p.read_bytes();obj=json.loads(original);out=Path(__file__).resolve().parent
(out/'preset.pretty.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
refs={}
for name in ['amps','stomps','cabs']:
 data=json.loads((Path('/workspace/analysis/remote/resources')/(name+'.models.json')).read_text())
 def walk(x):
  if isinstance(x,dict):
   if isinstance(x.get('symbolicID'),str) and 'params' in x:refs[x['symbolicID']]={'catalog':name+'.models.json','name':x.get('name'),'id':x.get('id')}
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(data)
blocks=[]
for group,data in obj['data']['tone'].items():
 if isinstance(data,dict) and '@model' in data:blocks.append({'group':group,'model':data['@model'],'enabled_field':data.get('@enabled'),'existing_remote_catalog_match':refs.get(data['@model'])})
result={'source':str(p),'bytes':len(original),'sha256':hashlib.sha256(original).hexdigest(),'format':'UTF-8 JSON','schema':obj.get('schema'),'schema_version':obj.get('version'),'device_id':hex(obj['data']['device']),'device_version_raw':hex(obj['data']['device_version']),'blocks':blocks,'limits':['Device ID 0x220004 differs from live V30 0x220000; compatibility not tested by importing.','This exact JSON has parameter and metadata values, no executable payload, neural weights, model graph or audio sample array.','Does not prove every possible SVL6P variant has identical capabilities.','SharcPodFixedComp is a model symbol, not evidence of a SHARC processor.','Absent @enabled fields are not interpreted as confirmed current device state.']}
(out/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');assert hashlib.sha256(p.read_bytes()).hexdigest()==result['sha256'];print('Preset parsed and three model references cross-checked; original unchanged.')
