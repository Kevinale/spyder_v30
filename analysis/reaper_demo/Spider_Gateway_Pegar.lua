-- Demo OFFLINE con muestras reducidas de las capturas. No escucha USB.
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
local datos={
 {0.848305,0.680952,0.507829,0.207748,0.494447,0.821783,0.960784,0.658823,0.243137,0.117647},
 {0.466193,0.261906,0.003937,0.157480,0.440945,0.681102,0.921260,0.767717,0.401575,0.000000},
 {0.480122,0.089166,0.255906,0.476378,0.724409,0.983966,0.791339,0.539370,0.279528,0.000000},
 {0.434103,0.039370,0.244094,0.503937,0.748031,0.968504,0.811024,0.559055,0.271654,0.000000}
}
local labels={"Drive -> Input","Bass","Mid -> Middle","Treble"}
local cerrado=false
local function restaurar()
 if valido() then for p,v in pairs(old) do reaper.TrackFX_SetParamNormalized(tr,fx,p,v) end end
end
local function cerrar()
 if cerrado then return end
 cerrado=true;restaurar();gfx.quit()
end
reaper.atexit(cerrar)
gfx.init("Spider / Gateway: DEMO OFFLINE",580,150)
local inicio=reaper.time_precise()+3;local anterior=0
local function ciclo()
 local tecla=gfx.getchar()
 if tecla<0 or tecla==27 or not valido() then cerrar();return end
 if ocupado() then cerrar();return end
 local t=reaper.time_precise()-inicio
 if t>=35 then cerrar();return end
 local texto="Inicio en "..string.format("%.1f",math.max(0,-t)).." segundos"
 if t>=0 then
  local fase=math.floor(t/9)+1;local tiempo=t%9
  if fase~=anterior then restaurar();anterior=fase end
  texto=labels[fase]
  if tiempo<8 then
   local x=tiempo/8*9;local j=math.floor(x)+1;local f=x-math.floor(x)
   local valores=datos[fase];local v=valores[j]+(valores[math.min(j+1,10)]-valores[j])*f
   if fase==1 then
    if drive_ok then
     local u=v*256;local k=math.floor(u);local f2=u-k
     local n=lut[k+1]+(lut[math.min(k+2,257)]-lut[k+1])*f2
     reaper.TrackFX_SetParamNormalized(tr,fx,1,n)
    else texto=texto.." OMITIDO: formato de ganancia no disponible" end
   else reaper.TrackFX_SetParamNormalized(tr,fx,ids[fase],v) end
  else restaurar();texto="Pausa: valores restaurados" end
 end
 gfx.set(.08,.09,.11,1);gfx.rect(0,0,gfx.w,gfx.h,1)
 gfx.set(.95,.95,.95,1);gfx.setfont(1,"Arial",17)
 gfx.x=15;gfx.y=15;gfx.drawstr(texto)
 gfx.setfont(1,"Arial",13);gfx.x=15;gfx.y=52
 gfx.drawstr("Reproduce la guitarra grabada. No es control USB en vivo.")
 gfx.x=15;gfx.y=79;gfx.drawstr("Input acotado a -12 / +6 dB; EQ de Gateway debe estar activo.")
 gfx.x=15;gfx.y=106;gfx.drawstr("Esc o cerrar: detener y restaurar los cuatro parametros.")
 gfx.update();reaper.defer(ciclo)
end
ciclo()
