#!/usr/bin/env python3
"""Verify AmpEnable evidence; construct a query DESCRIPTION, never send it."""
from pathlib import Path
import json,struct,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
symbols=json.loads((ROOT/'captures/device_symbols.json').read_text());by_name={x['text']:x for x in symbols}
keys={k:by_name[k]for k in ['AmpEnable','AmpEnableState','GuitarProc','Amp']}
assert keys['AmpEnable']['index']==835 and keys['AmpEnableState']['index']==821 and keys['GuitarProc']['index']==884
preset=json.loads((OUT/'captured_edit_buffer.json').read_text())
flag=next(x for x in preset['entries']if x.get('symbol')=='AmpEnableState')
assert flag['block_path']==['GuitarProc'] and flag['type']==1 and flag['value']==1
raw=(OUT/'captured_edit_buffer.bin').read_bytes();assert raw[367:377]==struct.pack('<IHI',821,1,1)
model=next(x for x in preset['entries']if x['block_path']==['GuitarProc','Amp']and x['key']=='0x80000005')
result={'symbols':keys,'stored_flag':flag,'separate_amp_model':dict(model,model_name=next(x['text']for x in symbols if x['index']==model['value'])),'reply_provenance':{'logical_index':18,'channel':1,'frames':[1281,1351],'flag_sysex_index':110,'flag_sysex_frames':[1295,1307],'flag_key_offset_in_reply_payload':367,'flag_value_offset_in_reply_payload':373},'next_read_only_query_description':{'status':'NOT SENT; requires appropriate session/transport and hardware','api_header_opcode':9,'api_payload_bytes':8,'object_symbol':'GuitarProc','object_id':884,'parameter_symbol':'AmpEnable','parameter_id':835,'api_message_hex':struct.pack('<IIII',9,8,884,835).hex(),'native_evidence':'captures/native_setters.txt FUN_10099810 VA0x10099810: opcode9 and two IDs; opcode10 setter is a separate function','read_question':'Does this parameter read succeed, and what is its value with an active model versus No Amp?','does_not_test':['Whether setting zero is accepted','Whether audio is bypassed','Whether four physical knob IDs remain distinct','Whether state is saved']},'correction':'The missing amp/@enabled mapping in Remote does not imply missing AmpEnable in the device. Both AmpEnable and stored AmpEnableState are in the device-supplied table; an actual preset includes the stored flag.'}
(OUT/'amp_enable_evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: AmpEnable835 / AmpEnableState821 / GuitarProc884; captured boolean state1; separate Line6SuperSparkle model. Query description generated, NOT sent.')
