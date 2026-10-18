-- Spider -> Gateway: OFFLINE replay of captured controls, not live USB.
-- Requires REAPER only. Does not send MIDI, USB, or firmware commands.
local function fail(msg) reaper.MB(msg,"Spider -> Gateway",0) end
if reaper.CountSelectedTracks(0) ~= 1 then fail("Selecciona SOLO la pista que contiene Gateway."); return end
local track=reaper.GetSelectedTrack(0,0)
if reaper.GetPlayState() & 4 ~= 0 then fail("Deten la grabacion antes de ejecutar la demo."); return end
if reaper.GetMediaTrackInfo_Value(track,"I_RECARM") ~= 0 then fail("Desarma la grabacion de esta pista. Usaremos una guitarra YA GRABADA."); return end
if reaper.GetMediaTrackInfo_Value(track,"I_RECMON") ~= 0 then fail("Apaga la monitorizacion de entrada de esta pista."); return end
if reaper.GetMediaTrackInfo_Value(track,"I_AUTOMODE") >= 2 then fail("Pon la automatizacion de pista en Trim/Read o Read. No se escribira automatizacion."); return end
if reaper.GetGlobalAutomationOverride() >= 2 then fail("Quita el override global Touch/Write/Latch de automatizacion antes de la demo."); return end
local fx=nil
for i=0,reaper.TrackFX_GetCount(track)-1 do
 local ok,name=reaper.TrackFX_GetFXName(track,i,"")
 if ok and name:lower():find("gateway",1,true) then
  if fx then fail("Hay mas de un Gateway en esta pista. Deja solo uno para esta prueba."); return end
  fx=i
 end
end
if fx==nil then fail("No se encontro Gateway en la pista seleccionada."); return end
local guid=reaper.TrackFX_GetFXGUID(track,fx)
local function valid() return reaper.ValidatePtr2(0,track,"MediaTrack*") and reaper.TrackFX_GetFXGUID(track,fx)==guid end
local names,ids={},{}
local aliases={Drive={input=true,inputgain=true,inputlevel=true},Bass={bass=true},Mid={mid=true,middle=true},Treble={treble=true}}
local controls={"Drive","Bass","Mid","Treble"}
for p=0,reaper.TrackFX_GetNumParams(track,fx)-1 do
 local ok,name=reaper.TrackFX_GetParamName(track,fx,p,"")
 if ok then
  names[p]=name
  local clean=name:lower():gsub("[^a-z]","")
  for _,c in ipairs(controls) do if aliases[c][clean] then
   if ids[c]~=nil then ids[c]=-2 else ids[c]=p end
  end end
 end
end
local missing=false
for _,c in ipairs(controls) do if not ids[c] or ids[c]<0 then missing=true end end
if missing then
 reaper.ShowConsoleMsg("\nGateway: indices de parametros (base 0)\n")
 for p=0,reaper.TrackFX_GetNumParams(track,fx)-1 do reaper.ShowConsoleMsg(p.." = "..(names[p] or "?").."\n") end
 local defaults={}
 for _,c in ipairs(controls) do defaults[#defaults+1]=tostring(ids[c] and ids[c]>=0 and ids[c] or -1) end
 local ok,text=reaper.GetUserInputs("IDs Gateway: consulta la consola; -1 omite",4,"Drive/Input ID,Bass ID,Mid/Middle ID,Treble ID",table.concat(defaults,","))
 if not ok then return end
 local fields={} for s in (text..","):gmatch("(.-),") do fields[#fields+1]=s end
 if #fields~=4 then fail("Se necesitan cuatro indices separados por comas."); return end
 for i,c in ipairs(controls) do
  local n=tonumber(fields[i])
  if not n or n%1~=0 or n < -1 or n >= reaper.TrackFX_GetNumParams(track,fx) then fail("Indice no valido: "..c); return end
  ids[c]=n>=0 and n or nil
 end
end
local used={}
for _,c in ipairs(controls) do
 local p=ids[c]
 if p then if used[p] then fail("No asignes dos controles al mismo parametro."); return end; used[p]=true end
end
-- Input gain: derive a bounded [-12,+6] dB mapping from the plugin formatter.
-- Never map an unknown input gain across its entire normalized range.
local function db_at(p,n)
 local ok,s=reaper.TrackFX_FormatParamValueNormalized(track,fx,p,n,"")
 if not ok or not s:lower():find("db",1,true) then return nil end
 return tonumber((s:gsub(",",".")):match("([%+%-]?%d+%.?%d*)"))
end
local function db_to_norm(p,target)
 local lo,hi=0,1; local low,high=db_at(p,lo),db_at(p,hi)
 if not low or not high or low>=high or target<low or target>high then return nil end
 for _=1,28 do
  local mid=(lo+hi)/2;local db=db_at(p,mid)
  if not db then return nil end
  if db<target then lo=mid else hi=mid end
 end
 return (lo+hi)/2
end
local drive_lut=nil;local drive_note=""
if ids.Drive then
 local lut={};local good=true
 for i=0,256 do
  lut[i+1]=db_to_norm(ids.Drive,-12+18*i/256)
  if not lut[i+1] then good=false;break end
 end
 if good then drive_lut=lut else ids.Drive=nil;drive_note="Drive omitido: Gateway no expone un formato dB verificable." end
end
local enabled=0 for _,c in ipairs(controls) do if ids[c] then enabled=enabled+1 end end
if enabled==0 then fail("No hay parametros mapeados. Revisa los nombres/IDs de Gateway.");return end
local _,script_path=reaper.get_action_context()
local directory=script_path:match("^(.*[\\/])") or ""
local f=io.open(directory.."controls_demo.csv","r")
if not f then fail("Falta controls_demo.csv junto al script Lua. Extrae TODOS los archivos del ZIP.");return end
local events={};f:read("*l")
for line in f:lines() do
 local t,c,v=line:match("^([%d%.]+),([^,]+),([%d%.eE%+%-]+),")
 t,v=tonumber(t),tonumber(v)
 if not t or not v or not aliases[c] or v~=v or v<0 or v>1 then f:close();fail("CSV no valido.");return end
 events[#events+1]={t=t,c=c,v=v}
end
f:close()
if #events==0 then fail("CSV vacio.");return end
for i=2,#events do if events[i].t<events[i-1].t then fail("CSV fuera de orden.");return end end
local original={}
for _,c in ipairs(controls) do local p=ids[c];if p then original[p]=reaper.TrackFX_GetParamNormalized(track,fx,p) end end
local closed=false
local function restore()
 if valid() then for p,v in pairs(original) do reaper.TrackFX_SetParamNormalized(track,fx,p,v) end end
end
local function cleanup()
 if closed then return end;closed=true;restore();gfx.quit()
end
reaper.atexit(cleanup)
gfx.init("Spider -> Gateway | DEMO OFFLINE",620,185)
local start=reaper.time_precise()+3;local next_event=1;local phase=nil;local shown="Cuenta atras: 3 segundos";local shown_value=""
local function set(c,v)
 local p=ids[c];if not p then return end
 local n=v
 if c=="Drive" then
  local x=v*256;local i=math.floor(x);local f=x-i
  n=drive_lut[i+1]+((drive_lut[math.min(i+2,257)] or drive_lut[i+1])-drive_lut[i+1])*f
 end
 reaper.TrackFX_SetParamNormalized(track,fx,p,n)
end
local function loop()
 if closed then return end
 local char=gfx.getchar()
 if char<0 or char==27 or not valid() then cleanup();return end
 if reaper.GetPlayState() & 4 ~= 0 or reaper.GetMediaTrackInfo_Value(track,"I_AUTOMODE")>=2 or reaper.GetGlobalAutomationOverride()>=2 or reaper.GetMediaTrackInfo_Value(track,"I_RECARM")~=0 or reaper.GetMediaTrackInfo_Value(track,"I_RECMON")~=0 then cleanup();return end
 local elapsed=reaper.time_precise()-start
 if elapsed>=0 then
  while next_event<=#events and events[next_event].t<=elapsed do
   local e=events[next_event]
   if e.c~=phase then restore();phase=e.c end
   set(e.c,e.v);shown=e.c.." -> "..(ids[e.c] and names[ids[e.c]] or "omitido")
   shown_value=string.format("Captura: %.3f | demo %.1f s / 35 s",e.v,elapsed)
   next_event=next_event+1
  end
  if next_event>#events and elapsed>events[#events].t+.75 then cleanup();return end
 else shown=string.format("Inicio en %.1f segundos",-elapsed) end
 gfx.set(0.08,0.09,0.11,1);gfx.rect(0,0,gfx.w,gfx.h,1)
 gfx.set(0.93,0.94,0.96,1);gfx.setfont(1,"Arial",18);gfx.x=16;gfx.y=16;gfx.drawstr(shown)
 gfx.setfont(1,"Arial",13);gfx.x=16;gfx.y=52;gfx.drawstr(shown_value)
 gfx.x=16;gfx.y=83;gfx.drawstr("Reproduce la guitarra ya grabada; no es escucha USB en vivo.")
 gfx.x=16;gfx.y=108;gfx.drawstr("Drive: Input -12 a +6 dB. EQ: habilitar manualmente en Gateway.")
 gfx.x=16;gfx.y=132;gfx.drawstr(drive_note~="" and drive_note or "Cerrar/Esc detiene y restaura los parametros originales.")
 gfx.update();reaper.defer(loop)
end
loop()
