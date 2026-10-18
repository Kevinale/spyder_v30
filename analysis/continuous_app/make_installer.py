"""Build a plain-text, one-time Windows setup from the owner's running local page."""
from pathlib import Path
R=Path(__file__).resolve().parent
setup=r'''$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
try {
 $baseHtml = (Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:8768/' -TimeoutSec 5).Content
 if (!$baseHtml.Contains('class SpiderBypassTrial') -or !$baseHtml.Contains('const link=')) { throw 'No encuentro la pagina integrada esperada en8768.' }
 if ($baseHtml.Contains('SPIDER_CONTINUOUS_V1')) { throw 'La pagina ya es continua; usa la integrada8768 como origen.' }
 if ([regex]::Matches($baseHtml,"const\s+localToken\s*=\s*'[a-f0-9]{32}'").Count -ne 1) { throw 'No se encontro un token de sesion unico en la pagina integrada.' }
 $baseHtml = [regex]::Replace($baseHtml,"const\s+localToken\s*=\s*'[a-f0-9]{32}'", "const localToken='__SPIDER_CONT_TOKEN__'")
 $baseHtml = [regex]::Replace($baseHtml,'\bconst\s+trialLog\s*=','let trialLog=')
 $headerPattern="'X-Spider-Token'\s*:\s*localToken"
 if ([regex]::Matches($baseHtml,$headerPattern).Count -ne 1) { throw 'Formato inesperado del puente local.' }
 $baseHtml = [regex]::Replace($baseHtml,$headerPattern,"'X-Spider-Token':localToken,'X-Spider-Client':continuousClient")
 $luaSource = $null
 $scripts = Join-Path $env:APPDATA 'REAPER\Scripts'
 if (Test-Path -LiteralPath $scripts) {
  $found = Get-ChildItem -LiteralPath $scripts -Filter 'Spider_Gateway_Integrado.lua' -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { $luaSource = $found.FullName }
 }
 if (!$luaSource) {
  $dialog = [Windows.Forms.OpenFileDialog]::new()
  $dialog.Title = 'Selecciona Spider_Gateway_Integrado.lua, el script que acabamos de probar'
  $dialog.Filter = 'Script Lua (*.lua)|*.lua'
  $dialog.FileName = 'Spider_Gateway_Integrado.lua'
  if (Test-Path -LiteralPath $scripts) { $dialog.InitialDirectory=$scripts }
  try {
   if ($dialog.ShowDialog() -ne [Windows.Forms.DialogResult]::OK) { throw 'Cancelado: no se creo la aplicacion.' }
   $luaSource = $dialog.FileName
  } finally { $dialog.Dispose() }
 }
 $lua = [IO.File]::ReadAllText($luaSource)
 if (!$lua.Contains('SpiderGateway-integrated.txt') -or !$lua.Contains('I_RECMON') -or !$lua.Contains('TrackFX_SetParamNormalized')) { throw 'El archivo elegido no parece ser nuestro script integrado. No se modifico.' }
 $lua = $lua.Replace('SpiderGateway-integrated.txt','SpiderGateway-continuous.txt').Replace('ensayo integrado','modo continuo').Replace('fin de ensayo','sesion detenida')
 $addon = @'
__ADDON__
'@
 $runtime = @'
__RUNTIME__
'@
 $readme = @'
SPIDERGATEWAY - modo continuo

1. En Spider Remote: modelo Amp activo (por ejemplo Line6BigBottom), No Cabinet y efectos apagados. Cierra Remote.
2. Abre INICIAR SpiderGateway. Acepta el aviso de administrador de Windows.
3. En REAPER: ASIO Spider, Gateway activo con modelo NAM cargado y EQ activo. Selecciona una sola pista y armala con su boton rojo. No pulses Grabar.
4. Carga una sola vez Spider_Gateway_Continuo.lua desde esta carpeta mediante Actions > New action > Load ReaScript. Ejecutalo cada vez que inicies la aplicacion. No ejecutes tambien los scripts anteriores.
5. En la pagina local: Conectar > Iniciar NAM continuo. Manten la pagina abierta y visible. Puedes colocarla junto a Gateway.
6. Detener y restaurar Amp apaga la monitorizacion y verifica AmpEnable1. Restaurar y cerrar aplicacion tambien cierra el servidor.

No requiere USBPcap ni las consolas/paginas antiguas despues de crear esta carpeta.
No hay limite20s en modo activo. Ocultar la pagina provoca restauracion, por ahora no funciona como aplicacion minimizada.
NAM corre en el PC. El programa no modifica firmware ni guarda presets. Los giros cambian parametros del modelo en el estado de edicion.
Si se pierde USB, se fuerza cierre del navegador o falla restauracion, no se garantiza Amp1. Reconecta y utiliza Recuperar Amp a1 y comprueba la confirmacion. No asumas que apagar el equipo restaura ese flag.
El script apaga monitorizacion si deja de recibir datos y al terminar. La mezcla de sonido directo del Spider no se ha aislado ni medido.
El lanzador pide elevacion para HttpListener local y usa RemoteSigned solo en su proceso; no cambia la politica de ejecucion global. Politicas de empresa pueden impedir iniciarlo.
Si tu navegador predeterminado no soporta MIDI/SysEx, abre http://localhost:8770/ en Edge o Chrome actual.
Esta nueva version continua necesita validacion real en tu Windows; el ensayo20s si se probo con audio y cuatro perillas.
'@
 $desktop=[Environment]::GetFolderPath('Desktop')
 $appFolder=Join-Path $desktop 'SpiderGateway'
 if (Test-Path -LiteralPath $appFolder) { $appFolder=Join-Path $desktop ('SpiderGateway-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss')) }
 if (Test-Path -LiteralPath $appFolder) { throw 'Ya existe la carpeta de destino; no se sobrescribio.' }
 [void][IO.Directory]::CreateDirectory($appFolder)
 $utf8=[Text.UTF8Encoding]::new($true)
 $html=$baseHtml.Replace('</html>','<script>'+$addon+'</script></html>')
 [IO.File]::WriteAllText((Join-Path $appFolder 'app.html'),$html,$utf8)
 [IO.File]::WriteAllText((Join-Path $appFolder 'SpiderGateway.ps1'),$runtime,$utf8)
 [IO.File]::WriteAllText((Join-Path $appFolder 'Spider_Gateway_Continuo.lua'),$lua,$utf8)
 [IO.File]::WriteAllText((Join-Path $appFolder 'LEEME.txt'),$readme,$utf8)
 $shortcut=Join-Path $desktop 'INICIAR SpiderGateway.lnk'
 if (Test-Path -LiteralPath $shortcut) { $shortcut=Join-Path $desktop ('INICIAR SpiderGateway-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss')+'.lnk') }
 $shell=New-Object -ComObject WScript.Shell
 $link=$shell.CreateShortcut($shortcut)
 $link.TargetPath=Join-Path $PSHOME 'powershell.exe'
 $link.Arguments='-NoProfile -ExecutionPolicy RemoteSigned -File "'+(Join-Path $appFolder 'SpiderGateway.ps1')+'"'
 $link.WorkingDirectory=$appFolder
 $link.Description='SpiderGateway local: NAM en REAPER y perillas del Spider'
 $link.Save()
 Write-Host ('Creado: '+$appFolder)
 Write-Host 'Tus archivos anteriores no se reemplazaron. No cierres una prueba activa sin restaurar.'
 Start-Process explorer.exe -ArgumentList ('"'+$appFolder+'"')
 [Windows.Forms.MessageBox]::Show('Aplicacion creada. Antes de iniciarla, restaura y desconecta la pagina anterior. El script nuevo esta en la carpeta abierta.') | Out-Null
} catch {
 [Windows.Forms.MessageBox]::Show('No se completo la preparacion: '+$_.Exception.Message) | Out-Null
 throw
}
'''
setup=setup.replace('__ADDON__',(R/'continuous.js').read_text()).replace('__RUNTIME__',(R/'SpiderGateway.ps1').read_text())
(R/'Crear_SpiderGateway.ps1').write_text(setup)
print('Generated plain-text setup:',len(setup),'characters')
if __name__=='__main__':pass
