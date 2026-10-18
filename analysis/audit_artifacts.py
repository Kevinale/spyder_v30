#!/usr/bin/env python3
"""Read-only inventory of supplied artifacts and statically extracted driver files."""
from pathlib import Path
import hashlib, json, sys, re
sys.path.insert(0, '/workspace/analysis/tools/python')
import pefile
from cryptography.hazmat.primitives.serialization import pkcs7, Encoding

ROOT = Path('/workspace/analysis')
originals = sorted(Path('/workspace/attachments').rglob('*'))
files = [p for p in originals if p.is_file()] + sorted((ROOT/'driver/extracted').rglob('*'))
records = []
strings_out = ROOT/'driver/strings'
strings_out.mkdir(exist_ok=True)
for p in files:
    if not p.is_file(): continue
    data=p.read_bytes()
    r={'path':str(p), 'size':len(data), 'sha256':hashlib.sha256(data).hexdigest(), 'md5':hashlib.md5(data).hexdigest()}
    if data[:2] == b'MZ':
        pe=pefile.PE(data=data)
        r['pe']={'machine':hex(pe.FILE_HEADER.Machine), 'image_base':hex(pe.OPTIONAL_HEADER.ImageBase),
                 'entry_rva':hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
                 'header_checksum':hex(pe.OPTIONAL_HEADER.CheckSum), 'calculated_checksum':hex(pe.generate_checksum()),
                 'timestamp_untrusted':pe.FILE_HEADER.TimeDateStamp,
                 'sections':[{'name':s.Name.rstrip(b'\x00').decode(errors='replace'), 'raw_offset':hex(s.PointerToRawData),
                             'raw_size':s.SizeOfRawData,'rva':hex(s.VirtualAddress),'virtual_size':s.Misc_VirtualSize,'entropy':s.get_entropy()} for s in pe.sections],
                 'imports':{},'exports':[]}
        for imp in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[]):
            r['pe']['imports'][imp.dll.decode(errors='replace')]=[{'name':x.name.decode(errors='replace') if x.name else None,'ordinal':x.ordinal,'iat_va':hex(x.address)} for x in imp.imports]
        if hasattr(pe,'DIRECTORY_ENTRY_EXPORT'):
            r['pe']['exports']=[{'name':s.name.decode(errors='replace') if s.name else None,'ordinal':s.ordinal,'rva':hex(s.address)} for s in pe.DIRECTORY_ENTRY_EXPORT.symbols]
        sec=pe.OPTIONAL_HEADER.DATA_DIRECTORY[4]
        r['pe']['certificate_table']={'file_offset':hex(sec.VirtualAddress),'size':sec.Size,'trust_verified':False,'certificates':[]}
        if sec.Size>=8 and sec.VirtualAddress+sec.Size<=len(data):
            try:
                certdata=data[sec.VirtualAddress+8:sec.VirtualAddress+sec.Size]
                for cert in pkcs7.load_der_pkcs7_certificates(certdata):
                    der=cert.public_bytes(Encoding.DER)
                    r['pe']['certificate_table']['certificates'].append({'subject':cert.subject.rfc4514_string(), 'issuer':cert.issuer.rfc4514_string(),'sha256':hashlib.sha256(der).hexdigest()})
            except Exception as e: r['pe']['certificate_parse_error']=str(e)
        strings=[]
        for m in re.finditer(rb'[\x20-\x7e]{5,}',data): strings.append((m.start(),'ascii',m.group().decode()))
        for m in re.finditer(rb'(?:[\x20-\x7e]\x00){5,}',data): strings.append((m.start(),'utf16le',m.group().decode('utf-16le')))
        outname=r['sha256'][:12]+'_'+p.name+'.txt'
        (strings_out/outname).write_text('\n'.join(f'0x{o:08x}\t{enc}\t{s}' for o,enc,s in sorted(strings)),encoding='utf-8')
        r['strings_file']=str(strings_out/outname)
    records.append(r)
(ROOT/'artifact_inventory.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
(ROOT/'originals.sha256').write_text(''.join(f"{r['sha256']}  {r['path']}\n" for r in records if '/attachments/' in r['path']))
print(f'Inventoried {len(records)} files; originals: {sum("/attachments/" in r["path"] for r in records)}')
