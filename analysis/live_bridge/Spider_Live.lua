-- Puente pasivo USB; no envia comandos al Spider.
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
local function aviso(s) reaper.MB(s,"Spider / Gateway",0) end
if reaper.CountSelectedTracks(0)~=1 then aviso("Selecciona solo la pista con Gateway.");return end
local tr=reaper.GetSelectedTrack(0,0)
local function ocupado()
 return (reaper.GetPlayState() & 4)~=0
  or reaper.GetMediaTrackInfo_Value(tr,"I_RECARM")~=0
  or reaper.GetMediaTrackInfo_Value(tr,"I_RECMON")~=0
  or reaper.GetMediaTrackInfo_Value(tr,"I_AUTOMODE")>=2
  or reaper.GetGlobalAutomationOverride()>=2
end
if ocupado() then aviso("Desarma grabacion, apaga monitorizacion y usa automatizacion Trim/Read o Read.");return end
local fx
for i=0,reaper.TrackFX_GetCount(tr)-1 do
 local _,n=reaper.TrackFX_GetFXName(tr,i,"")
 if n:lower():find("gateway",1,true) then
  if fx then aviso("Deja solo un Gateway en esta pista.");return end
  fx=i
 end
end
if fx==nil then aviso("No encuentro Gateway.");return end
local ids={1,3,4,5};local names={"Input","Bass","Middle","Treble"}
for i,p in ipairs(ids) do
 local ok,n=reaper.TrackFX_GetParamName(tr,fx,p,"")
 if not ok or n:lower()~=names[i]:lower() then aviso("Los indices de Gateway no coinciden. No se cambio nada.");return end
end
local guid=reaper.TrackFX_GetFXGUID(tr,fx)
local function valido()
 return reaper.ValidatePtr2(0,tr,"MediaTrack*") and reaper.TrackFX_GetFXGUID(tr,fx)==guid
end
local old={}
for _,p in ipairs(ids) do old[p]=reaper.TrackFX_GetParamNormalized(tr,fx,p) end
-- Input muestra dB en esta version de Gateway, aunque el texto omite la unidad.
local function db(n)
 local ok,s=reaper.TrackFX_FormatParamValueNormalized(tr,fx,1,n,"")
 if not ok then return nil end
 return tonumber((s:gsub(",",".")):match("([%+%-]?%d+%.?%d*)"))
end
local function normalizado(target)
 local a,b=0,1;local x,y=db(a),db(b)
 if not x or not y or x>=y or target<x or target>y then return nil end
 for _=1,24 do
  local m=(a+b)/2;local v=db(m)
  if not v then return nil end
  if v<target then a=m else b=m end
 end
 return (a+b)/2
end
local lut={};local drive_ok=true
for i=0,256 do
 lut[i+1]=normalizado(-12+18*i/256)
 if not lut[i+1] then drive_ok=false;break end
end
if not drive_ok then old[1]=nil end
local path=(os.getenv("TEMP") or "").."\\SpiderGateway-live.pcap"
local file=io.open(path,"rb")
if not file then aviso("Primero inicia el receptor PowerShell. No encuentro "..path);return end
local header=file:read(24)
if not header or #header~=24 or header:sub(1,4)~=string.char(212,195,178,161)
 or string.unpack("<I4",header,21)~=249 then file:close();aviso("No es PCAP USBPcap valido. Espera dos segundos e intenta de nuevo.");return end
local initial=file:seek("end");file:seek("set",24)
local count=0;local last="Esperando perillas";local closed=false
local d=decoder(function(name,v)
 local p=({Drive=1,Bass=3,Middle=4,Treble=5})[name]
 if p==1 then
  if not drive_ok then return end
  local x=v*256;local k=math.floor(x);local f=x-k
  v=lut[k+1]+(lut[math.min(k+2,257)]-lut[k+1])*f
 end
 reaper.TrackFX_SetParamNormalized(tr,fx,p,v)
 count=count+1;last=name
end)
local function close()
 if closed then return end;closed=true;file:close()
 if valido() then for p,v in pairs(old) do reaper.TrackFX_SetParamNormalized(tr,fx,p,v) end end
 gfx.quit()
end
reaper.atexit(close)
gfx.init("Spider -> Gateway EN VIVO",540,130)
local start=reaper.time_precise()
local function step()
 local key=gfx.getchar()
 if key<0 or key==27 or not valido() or ocupado() or reaper.time_precise()-start>115 then close();return end
 local ok,err=pcall(function()
  for _=1,2000 do
   local pos=file:seek();local h=file:read(16)
   if not h or #h<16 then file:seek("set",pos);break end
   local n=string.unpack("<I4",h,9)
   if n>1048576 then error("Registro PCAP fuera de limites") end
   local p=file:read(n)
   if not p or #p<n then file:seek("set",pos);break end
   d.feed(p,pos+16+n>initial)
  end
 end)
 if not ok then close();aviso(tostring(err));return end
 gfx.set(.08,.09,.11,1);gfx.rect(0,0,gfx.w,gfx.h,1);gfx.set(1,1,1,1)
 gfx.x=12;gfx.y=12;gfx.drawstr(d.verified and "Spider V30 identificado" or "Sin identificar Spider: comprueba USBPcap2")
 gfx.x=12;gfx.y=40;gfx.drawstr("Cambios en vivo: "..count.." | "..last)
 gfx.x=12;gfx.y=68;gfx.drawstr("No Amp ignorados: "..d.unknown.." | Cerrar restaura Gateway")
 gfx.x=12;gfx.y=96;gfx.drawstr("Drive -> Input (-12 a +6 dB); Bass / Middle / Treble")
 gfx.update();reaper.defer(step)
end
step()
