-- Parser pasivo: USBPcap -> USB MIDI -> Parker -> notificaciones.
local function decoder(emit)
 local d={verified=false,events=0,unknown=0};local midi="";local streams={};local seq={}
 local function sysex(s,live)
  if s:sub(1,7)~=string.char(240,0,1,12,34,0,77) or #s<14 then return end
  local ch,q=s:byte(8,9);local n=((s:byte(11)&15)*16+(s:byte(12)&15))+1
  local raw={};local i=13
  while i<#s do
   local mask=s:byte(i);i=i+1
   for bit=6,0,-1 do
    if i>=#s then break end
    raw[#raw+1]=string.char(s:byte(i)|(((mask>>bit)&1)<<7));i=i+1
   end
  end
  local r=table.concat(raw):sub(1,n);if #r~=n then return end
  if seq[ch] and q~=(seq[ch]+1)%128 then streams[ch]="" end
  seq[ch]=q;local b=(streams[ch] or "")..r
  while #b>=8 do
   local op,len=string.unpack("<I4I4",b)
   if len>1048576 then b="";break end
   if #b<8+len then break end
   if op==4 and len==16 then
    local group,param,kind,v=string.unpack("<I4I4I4f",b,9)
    if group==42 and kind==4 then
     local names={[37]="Drive",[38]="Drive",[33]="Bass",[35]="Middle",[36]="Treble"}
     if names[param] and v==v and v>=0 and v<=1 then
      d.events=d.events+1;if live then emit(names[param],v) end
     else d.unknown=d.unknown+1 end
    end
   end
   b=b:sub(9+len)
  end
  streams[ch]=b
 end
 function d.feed(p,live)
  if #p<27 then return end
  local h=string.unpack("<I2",p);if h<27 or h>#p then return end
  local status=string.unpack("<I4",p,11)
  local bus,dev=string.unpack("<I2I2",p,18)
  local ep,typ=p:byte(22,23);local complete=(p:byte(17)&1)~=0
  local len=string.unpack("<I4",p,24);local a=p:sub(h+1,h+len)
  if typ==2 and complete and status==0 and #a==18 and a:byte(1)==18 and a:byte(2)==1 then
   local vid,pid=string.unpack("<I2I2",a,9)
   if vid==0x0e41 and pid==0x5068 then d.bus=bus;d.dev=dev;d.verified=true
   elseif bus==d.bus and dev==d.dev then d.verified=false;midi="";streams={};seq={} end
  end
  if not d.verified or bus~=d.bus or dev~=d.dev or ep~=0x82 or typ~=3 or not complete or status~=0 or #a~=len then return end
  local sizes={[4]=3,[5]=1,[6]=2,[7]=3}
  for i=1,#a-3,4 do
   local tag=a:byte(i);local size=sizes[tag&15]
   if tag>>4==0 and size then
    for j=1,size do
     local v=a:byte(i+j)
     if v==240 then midi=string.char(v)
     elseif #midi>0 then
      midi=midi..string.char(v)
      if v==247 then sysex(midi,live);midi="" elseif #midi>1024 then midi="" end
     end
    end
   end
  end
 end
 return d
end
