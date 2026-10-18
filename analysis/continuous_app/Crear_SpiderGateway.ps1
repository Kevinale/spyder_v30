$ErrorActionPreference = 'Stop'
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
// SPIDER_CONTINUOUS_V1: explicit Start/Stop replaces the proven20s timer.
const continuousClient=(crypto.randomUUID?crypto.randomUUID():String(Date.now())+'-'+Math.random());
const appLog=s=>{s=String(s).replace(/Prueba20 segundos: toca y mueve las cuatro perillas\./g,'Mueve las cuatro perillas para controlar Gateway.').replace(/PRUEBA20 SEGUNDOS: toca y mueve Drive\/Bass\/Mid\/Treble\./g,'Mueve las cuatro perillas para controlar Gateway.');const el=document.getElementById('log');el.textContent=(el.textContent+s+'\n').slice(-18000);};
trialLog=appLog;
const oldPublisher=publishLink;
publishLink=async function(forceOff=false){
 if(!trial?.ready&&!forceOff)return false;
 return oldPublisher(forceOff);
};
const continuousStart=SpiderBypassTrial.prototype.start;
SpiderBypassTrial.prototype.start=async function(consent){
 await continuousStart.call(this,consent);
 if(this.stage==='active'){
  clearTimeout(this.timer);this.timer=null;
  this.log('NAM CONTINUO ACTIVO. Manten esta pagina visible. Detener restaura el Amp.');
  document.getElementById('status').textContent='NAM activo';
 }
};
const continuousFinish=SpiderBypassTrial.prototype.finish;
SpiderBypassTrial.prototype.finish=async function(){
 const answer=await continuousFinish.call(this);
 if(!this.attempted){
  document.getElementById('status').textContent='Detenido: Amp restaurado';
  document.getElementById('trial').disabled=!this.ready;
 }
 return answer;
};
// Counter and diagnostic code from the prototype can generate many messages.
// Retain incoming values for REAPER but suppress per-event text in normal use.
const continuousObserve=SpiderBypassTrial.prototype.observe;
SpiderBypassTrial.prototype.observe=function(kind,b){
 const keep=this.log;
 this.log=()=>{};
 try{return continuousObserve.call(this,kind,b);}finally{this.log=keep;}
};
document.title='SpiderGateway';
document.querySelector('h1').textContent='SpiderGateway';
for(const p of document.querySelectorAll('p'))p.remove();
const info=document.createElement('p');
info.textContent='Gateway en REAPER, pista armada y script Continuo abierto. Spider Remote cerrado. Mantén esta pagina abierta y visible; al ocultarla se detiene y restaura. Usa Detener antes de cerrar.';
document.querySelector('h1').after(info);
const status=document.createElement('p');status.id='status';status.textContent='Preparado';info.after(status);
button('connect').textContent='Conectar';
button('trial').textContent='Iniciar NAM continuo';
button('restore').textContent='Detener y restaurar Amp';
button('disconnect').textContent='Restaurar y desconectar';
button('trial').onclick=async()=>{
 button('trial').disabled=true;button('restore').disabled=false;
 try{await trial.start(true);}catch(e){appLog('ERROR: '+e.message);if(!trial?.attempted)button('trial').disabled=!trial?.ready;}
};
button('restore').onclick=async()=>{try{await trial.finish();}catch(e){appLog('RESTAURACION NO CONFIRMADA: '+e.message);}};
const recovery=document.createElement('button');recovery.textContent='Recuperar Amp a1';
recovery.onclick=async()=>{
 if(!trial?.ready){appLog('Conecta primero.');return;}
 if(trial.attempted){await trial.finish().catch(e=>appLog(e.message));return;}
 if(!confirm('Recuperar el Amp: cambiar AmpEnable a1 y verificarlo?'))return;
 try{
  const value=await trial.read();
  if(value===1){appLog('AmpEnable ya esta en1.');return;}
  trial.original=1;trial.attempted=true;
  await trial.finish();
 }catch(e){appLog('Recuperacion no confirmada: '+e.message);}
};
button('disconnect').after(recovery);
const quit=document.createElement('button');quit.textContent='Restaurar y cerrar aplicacion';
quit.onclick=async()=>{
 try{
  if(trial){
   if(trial.ready&&!trial.attempted&&await trial.read()!==1){trial.original=1;trial.attempted=true;}
   await trial.close();
  }
  trial=null;link.pause=true;
  const response=await fetch('/shutdown',{method:'POST',headers:{'X-Spider-Token':localToken,'X-Spider-Client':continuousClient}});
  if(!response.ok)throw Error('No se pudo cerrar el servidor local');
  document.body.textContent='SpiderGateway cerrado. Puedes cerrar esta pestaña. La monitorizacion de REAPER queda apagada.';
 }catch(e){appLog('No cierres todavia: '+e.message);}
};recovery.after(quit);
button('disconnect').onclick=async()=>{
 try{
  if(trial){if(trial.ready&&!trial.attempted&&await trial.read()!==1){trial.original=1;trial.attempted=true;}await trial.close();}trial=null;link.pause=true;
  await fetch('/release',{method:'POST',headers:{'X-Spider-Token':localToken,'X-Spider-Client':continuousClient}});
  button('connect').disabled=false;button('trial').disabled=true;button('restore').disabled=true;
  status.textContent='Desconectado';appLog('Puertos MIDI cerrados.');
 }catch(e){appLog('No se confirmo desconexion/restauracion: '+e.message);}
};
document.getElementById('log').textContent='Preparado. Conectar solo lee. Iniciar activa el bypass hasta pulsar Detener.\n';

'@
 $runtime = @'
# SpiderGateway local. Does not modify firmware or save presets.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
$appRoot = $PSScriptRoot
$principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if (!$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
 try { Start-Process -FilePath "$PSHOME\powershell.exe" -Verb RunAs -ArgumentList @('-NoProfile','-ExecutionPolicy','RemoteSigned','-File',('"' + $PSCommandPath + '"')) }
 catch { [Windows.Forms.MessageBox]::Show('No se inicio SpiderGateway: ' + $_.Exception.Message) | Out-Null }
 exit
}
$mutex = [Threading.Mutex]::new($false,'Local\SpiderGateway-Continuous-v1')
$owned = $false
$listener = $null
$statePath = Join-Path $env:TEMP 'SpiderGateway-continuous.txt'
$serverSeq = 0
$token = [Guid]::NewGuid().ToString('N')
$clientOwner = $null
$clientSeen = [DateTime]::UtcNow
$stopRequested = $false
function Write-State([string]$active,[string[]]$values) {
 $script:serverSeq++
 $line = $script:token + ',' + $script:serverSeq + ',' + $active + ',' + ($values -join ',') + "`n"
 $data = [Text.Encoding]::ASCII.GetBytes($line)
 $stream = [IO.FileStream]::new($script:statePath,[IO.FileMode]::Create,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite)
 try { $stream.Write($data,0,$data.Length);$stream.Flush() } finally { $stream.Dispose() }
}
try {
 try { $owned = $mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $owned = $true }
 if (!$owned) { [Windows.Forms.MessageBox]::Show('SpiderGateway ya esta abierto. Usa su pagina actual.') | Out-Null;exit }
 $html = [IO.File]::ReadAllText((Join-Path $appRoot 'app.html'),[Text.Encoding]::UTF8)
 if (!$html.Contains('__SPIDER_CONT_TOKEN__')) { throw 'No se encontro la plantilla de la aplicacion.' }
 $html = $html.Replace('__SPIDER_CONT_TOKEN__',$token)
 Write-State '0' @('-1','-1','-1','-1')
 $listener = [Net.HttpListener]::new()
 $listener.Prefixes.Add('http://localhost:8770/')
 $listener.Start()
 Write-Host 'SpiderGateway: http://localhost:8770/ . Mantén esta consola abierta.'
 Start-Process 'http://localhost:8770/'
 $accept = $listener.GetContextAsync()
 while ($listener.IsListening -and !$stopRequested) {
  if (!$accept.Wait(100)) { continue }
  $context = $accept.Result
  $response = $context.Response
  try {
   $route = $context.Request.Url.AbsolutePath
   $method = $context.Request.HttpMethod
   if ($method -eq 'GET' -and $route -eq '/') {
    $bytes = [Text.Encoding]::UTF8.GetBytes($html)
    $response.ContentType = 'text/html; charset=utf-8'
    $response.Headers.Add('Cache-Control','no-store')
    $response.Headers.Add('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'")
    $response.ContentLength64 = $bytes.Length
    $response.OutputStream.Write($bytes,0,$bytes.Length)
   } elseif ($method -eq 'POST' -and $context.Request.Headers['X-Spider-Token'] -eq $token) {
    $client = $context.Request.Headers['X-Spider-Client']
    if (!$client -or $client.Length -gt 80) { $response.StatusCode=403 }
    elseif ($clientOwner -and $clientOwner -ne $client -and ([DateTime]::UtcNow-$clientSeen).TotalSeconds -lt 3) { $response.StatusCode=409 }
    elseif ($route -eq '/state' -and $context.Request.ContentLength64 -ge 1 -and $context.Request.ContentLength64 -le 256) {
     $reader=[IO.StreamReader]::new($context.Request.InputStream)
     try { $body=$reader.ReadToEnd() } finally { $reader.Dispose() }
     $parts=$body.Split(',')
     $valid=$parts.Length -eq 6 -and $parts[0] -match '^\d{1,12}$' -and $parts[1] -match '^[01]$'
     if ($valid) {
      for ($i=2;$i -lt 6;$i++) {
       $number=0.0
       $ok=[double]::TryParse($parts[$i],[Globalization.NumberStyles]::Float,[Globalization.CultureInfo]::InvariantCulture,[ref]$number)
       if (!$ok -or [double]::IsNaN($number) -or [double]::IsInfinity($number) -or ($number -ne -1 -and ($number -lt 0 -or $number -gt 1))) {$valid=$false}
      }
     }
     if ($valid) { $clientOwner=$client;$clientSeen=[DateTime]::UtcNow;Write-State $parts[1] $parts[2..5];$response.StatusCode=204 }
     else {$response.StatusCode=400}
    } elseif ($route -eq '/release' -or $route -eq '/shutdown') {
     Write-State '0' @('-1','-1','-1','-1')
     $clientOwner=$null
     $response.StatusCode=204
     if ($route -eq '/shutdown') {$stopRequested=$true}
    } else {$response.StatusCode=400}
   } else {$response.StatusCode=403}
  } finally { $response.Close() }
  if (!$stopRequested) {$accept=$listener.GetContextAsync()}
 }
} catch {
 [Windows.Forms.MessageBox]::Show('SpiderGateway: ' + $_.Exception.Message + "`nSi no se confirmo restauracion del Amp, usa Recuperar Amp a1 al reconectar.") | Out-Null
} finally {
 if ($owned) { try { Write-State '0' @('-1','-1','-1','-1') } catch {} }
 if ($listener) {$listener.Close()}
 if ($owned) {$mutex.ReleaseMutex()}
 $mutex.Dispose()
}

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
