import sys,json,pathlib
import dnfile
from dncil.cil.body.reader import read_method_body_from_bytes
from dncil.clr.token import Token
root=pathlib.Path('/workspace/analysis/remote')
for fn in ['Spider V Remote.exe','EngineCLIWrapper.dll']:
 p=dnfile.dnPE(str(root/'extracted/Spider V Remote'/fn)); names={}; methods=[]
 for tid,t in enumerate(p.net.mdtables.TypeDef.rows,1):
  typ=f'{t.TypeNamespace}.{t.TypeName}'
  names[0x02000000|tid]=typ
  for x in t.MethodList:names[0x06000000|x.row_index]=typ+'::'+str(x.row.Name)
  for x in t.FieldList:names[0x04000000|x.row_index]=typ+'::'+str(x.row.Name)
 for i,r in enumerate(p.net.mdtables.MemberRef.rows,1):
  cl=r.Class.row; names[0x0a000000|i]=str(getattr(cl,'TypeNamespace',''))+'.'+str(getattr(cl,'TypeName',getattr(cl,'Name','')))+'::'+str(r.Name)
 def resolve(v):
  if not isinstance(v,Token):return str(v)
  if v.table==0x70:
   try:return repr(p.net.user_strings.get(v.rid).value)
   except:return str(v)
  return f'{v} '+names.get(v.value,'')
 for i,r in enumerate(p.net.mdtables.MethodDef.rows,1):
  tok=0x06000000|i; d={'token':hex(tok),'name':names.get(tok),'rva':hex(r.Rva),'impl':str(r.ImplFlags),'il':[]}
  if r.Rva:
   d['offset']=hex(p.get_offset_from_rva(r.Rva)); d['va']=hex(p.OPTIONAL_HEADER.ImageBase+r.Rva)
   if r.ImplFlags.miIL:
    try:
     b=read_method_body_from_bytes(p.get_data(r.Rva,100000));d['il']=[f'{i.offset:04x} {i.opcode.name} {resolve(i.operand)}' for i in b.instructions]
    except Exception as e:d['error']=str(e)
  methods.append(d)
 out=root/'managed'/fn.replace(' ','_')
 out.with_suffix('.json').write_text(json.dumps(methods,indent=2))
 with out.with_suffix('.il.txt').open('w') as f:
  for d in methods:f.write('\n'+json.dumps({k:v for k,v in d.items() if k!='il'})+'\n'+'\n'.join(d['il'])+'\n')
 if p.net.mdtables.ImplMap:
  with out.with_suffix('.pinvoke.txt').open('w') as f:
   for r in p.net.mdtables.ImplMap.rows:f.write(str(r.ImportScope.row.Name)+' '+str(r.ImportName)+' '+str(r.MemberForwarded.row.Name)+'\n')
