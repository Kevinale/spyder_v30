"""Candidatos estáticos: no implica identificación definitiva de vtable/clase."""
import struct
import pefile
path='/workspace/analysis/driver/extracted/Tools/Driver2 Archive/SpiderV/l6SpiderV.sys'
p=pefile.PE(path); base=p.OPTIONAL_HEADER.ImageBase
for s in p.sections:
    if not s.Name.startswith(b'.rdata'): continue
    data=s.get_data(); start=None
    for i in range(0,len(data)-7,8):
        value=struct.unpack_from('<Q',data,i)[0]
        valid=0x1000 <= value-base < 0x3a000
        if valid and start is None: start=i
        if not valid and start is not None:
            if i-start >= 0x2a8:
                print(f'candidate={base+s.VirtualAddress+start:#x} count={(i-start)//8} slot_2a0={struct.unpack_from("<Q",data,start+0x2a0)[0]:#x}')
            start=None
