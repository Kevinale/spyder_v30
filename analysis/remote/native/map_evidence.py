import pathlib,re,sys,json
sys.path.insert(0,'/workspace/analysis/tools/python')
import pefile
root=pathlib.Path('/workspace/analysis/remote/extracted/Spider V Remote')
rows=[]
for name in ['APIV3EngineDLL.dll','Interposer.dll','EngineCLIWrapper.dll']:
 p=root/name; b=p.read_bytes(); pe=pefile.PE(data=b)
 rows.append({'file':name,'imagebase':hex(pe.OPTIONAL_HEADER.ImageBase),'machine':hex(pe.FILE_HEADER.Machine),'size':len(b)})
 for m in re.finditer(rb'[ -~]{5,}',b):
  if re.search(rb'(?i)firmware|preset|sysex|firebird|L6FF|dinf|processor|MD5|UsbControl|knob|libusb_control|modelid',m.group()):
   rva=pe.get_rva_from_offset(m.start());rows.append({'file':name,'offset':hex(m.start()),'rva':hex(rva),'va':hex(pe.OPTIONAL_HEADER.ImageBase+rva),'string':m.group().decode()})
pathlib.Path('/workspace/analysis/remote/native/string_offsets.json').write_text(json.dumps(rows,indent=2))
