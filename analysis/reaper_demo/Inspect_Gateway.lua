-- Diagnostico de solo lectura: no mueve parametros ni accede al Spider.
if reaper.CountSelectedTracks(0) ~= 1 then
  reaper.MB("Selecciona solo la pista que contiene Gateway.", "Gateway", 0)
  return
end
local track = reaper.GetSelectedTrack(0, 0)
local found = false
for fx = 0, reaper.TrackFX_GetCount(track) - 1 do
  local ok, name = reaper.TrackFX_GetFXName(track, fx, "")
  if ok and name:lower():find("gateway", 1, true) then
    found = true
    reaper.ShowConsoleMsg("\n--- " .. name .. " | FX " .. fx .. " ---\n")
    for p = 0, reaper.TrackFX_GetNumParams(track, fx) - 1 do
      local _, label = reaper.TrackFX_GetParamName(track, fx, p, "")
      local valid, value = reaper.TrackFX_GetFormattedParamValue(track, fx, p, "")
      reaper.ShowConsoleMsg(p .. " | " .. label .. " | " .. (valid and value or "") .. "\n")
    end
  end
end
if not found then
  reaper.MB("No encontre Gateway en la pista seleccionada.", "Gateway", 0)
end
