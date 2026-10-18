-- Ensayo integrado20s. Solo controla Gateway y monitorizacion de esta pista.
local function aviso(s) reaper.MB(s,"Spider / Gateway",0) end
if reaper.CountSelectedTracks(0)~=1 then aviso("Selecciona solo la pista con Gateway.");return end
local tr=reaper.GetSelectedTrack(0,0)
local function ocupado()
 return (reaper.GetPlayState() & 4)~=0
  or reaper.GetMediaTrackInfo_Value(tr,"I_AUTOMODE")>=2
  or reaper.GetGlobalAutomationOverride()>=2
end
if ocupado() then aviso("Deten la grabacion y usa automatizacion Trim/Read o Read.");return end
if reaper.GetMediaTrackInfo_Value(tr,"I_RECARM")~=1 then aviso("Arma solo esta pista con el boton rojo; no pulses Grabar.");return end
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
if not reaper.TrackFX_GetEnabled(tr,fx) then aviso("Activa Gateway en FX antes de iniciar.");return end
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
local path=(os.getenv("TEMP") or "").."\\SpiderGateway-integrated.txt"
local closed=false;local active=false;local session=nil
local lastseq=nil;local changed=0;local minimum=nil
local lastvalues={};local laststatus="Esperando la pagina de prueba"
local function trackvalid()return reaper.ValidatePtr2(0,tr,"MediaTrack*")end
local function stopaudio()
 if trackvalid() then reaper.SetMediaTrackInfo_Value(tr,"I_RECMON",0) end
 if active and valido() then
  for p,v in pairs(old) do reaper.TrackFX_SetParamNormalized(tr,fx,p,v) end
 end
 active=false;lastvalues={}
end
local function close()
 if closed then return end;closed=true;stopaudio();gfx.quit()
end
reaper.atexit(close)
local function state()
 local f=io.open(path,"rb");if not f then return nil end
 local s=f:read(256);f:close()
 if not s or #s>=256 then return nil end
 local t={};for v in s:gmatch("[^,\r\n]+")do t[#t+1]=v end
 if #t~=7 or #t[1]~=32 or t[1]:find("[^0-9a-f]") then return nil end
 for i=2,7 do t[i]=tonumber(t[i]);if not t[i] or t[i]~=t[i]then return nil end end
 if t[2]%1~=0 or t[2]<0 or (t[3]~=0 and t[3]~=1)then return nil end
 for i=4,7 do if t[i]~=-1 and (t[i]<0 or t[i]>1)then return nil end end
 return t
end
-- Existing file is history; require a new heartbeat before enabling monitoring.
local initial=state();if initial then session=initial[1];minimum=initial[2] end
reaper.SetMediaTrackInfo_Value(tr,"I_RECMON",0)
gfx.init("Spider + Gateway: ensayo integrado",560,135)
local function step()
 local key=gfx.getchar()
 if key<0 or key==27 or not valido() or ocupado() then close();return end
 if reaper.GetMediaTrackInfo_Value(tr,"I_RECARM")~=1 or not reaper.TrackFX_GetEnabled(tr,fx)then close();return end
 local now=reaper.time_precise();local s=state()
 local allowed=false
 if s then
  if session and session~=s[1]then close();aviso("Cambio la sesion de la pagina. Inicia de nuevo este script.");return end
  if not session then session=s[1];minimum=s[2] end
  if lastseq and s[2]<lastseq then close();aviso("La secuencia retrocedio. Inicia de nuevo el script.");return end
  if lastseq~=s[2]then lastseq=s[2];changed=now end
  allowed=s[3]==1 and now-changed<1.5 and (not minimum or s[2]>minimum)
 end
 if allowed then
  if not active then active=true;lastvalues={};laststatus="BYPASS confirmado: Gateway en vivo" end
  for i=1,4 do
   local v=s[i+3];local p=ids[i]
   if v>=0 and lastvalues[i]~=v then
    if i==1 then
     if drive_ok then
      local x=v*256;local k=math.floor(x);local f=x-k
      reaper.TrackFX_SetParamNormalized(tr,fx,p,lut[k+1]+(lut[math.min(k+2,257)]-lut[k+1])*f)
     end
    else reaper.TrackFX_SetParamNormalized(tr,fx,p,v)end
    lastvalues[i]=v
   end
  end
  reaper.SetMediaTrackInfo_Value(tr,"I_RECMON",1)
 else
  stopaudio();laststatus="Monitor apagado: esperando bypass / fin de ensayo"
 end
 gfx.set(.08,.09,.11,1);gfx.rect(0,0,gfx.w,gfx.h,1);gfx.set(1,1,1,1)
 gfx.x=12;gfx.y=12;gfx.drawstr(laststatus)
 gfx.x=12;gfx.y=42;gfx.drawstr("Deja visible la pagina y mueve Drive/Bass/Mid/Treble.")
 gfx.x=12;gfx.y=72;gfx.drawstr("Drive/Gain -> Input; los demas -> EQ de Gateway.")
 gfx.x=12;gfx.y=102;gfx.drawstr("Esc/cerrar: monitor apagado y controles restaurados.")
 gfx.update();reaper.defer(step)
end
step()
