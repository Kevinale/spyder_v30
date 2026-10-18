import dnfile,json,pathlib
root=pathlib.Path('/workspace/analysis/remote')
for fn in ['Spider V Remote.exe','EngineCLIWrapper.dll']:
 p=dnfile.dnPE(str(root/'extracted/Spider V Remote'/fn)); types=[]
 for t in p.net.mdtables.TypeDef.rows:
  types.append({'type':str(t.TypeNamespace)+'.'+str(t.TypeName),'methods':[{'token':hex(0x06000000|x.row_index),'name':str(x.row.Name),'signature_hex':x.row.Signature.value.hex(),'parameters':[{'sequence':a.row.Sequence,'name':str(a.row.Name)} for a in x.row.ParamList]} for x in t.MethodList],'fields':[str(x.row.Name) for x in t.FieldList]})
 (root/'managed'/(fn.replace(' ','_')+'.metadata.json')).write_text(json.dumps(types,indent=2))
