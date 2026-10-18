from pathlib import Path
R=Path(__file__).resolve().parent
runtime=r'''$ErrorActionPreference='Stop'
$server=$null
try {
 $html=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'lectura.html'))
 $server=[Net.HttpListener]::new()
 $server.Prefixes.Add('http://localhost:8771/')
 $server.Start()
 Write-Host 'LECTURA SOLAMENTE: http://localhost:8771/ . Deja esta consola abierta.'
 Start-Process 'http://localhost:8771/'
 $task=$server.GetContextAsync()
 while ($server.IsListening) {
  if (!$task.Wait(100)) {continue}
  $c=$task.Result
  try {
   if ($c.Request.HttpMethod -eq 'GET' -and $c.Request.Url.AbsolutePath -eq '/') {
    $bytes=[Text.Encoding]::UTF8.GetBytes($html)
    $c.Response.ContentType='text/html; charset=utf-8'
    $c.Response.Headers.Add('Cache-Control','no-store')
    $c.Response.Headers.Add('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'none'; frame-ancestors 'none'")
    $c.Response.ContentLength64=$bytes.Length
    $c.Response.OutputStream.Write($bytes,0,$bytes.Length)
   } else {$c.Response.StatusCode=404}
  } finally {$c.Response.Close()}
  $task=$server.GetContextAsync()
 }
} catch {Write-Host ('ERROR: '+$_.Exception.Message) -ForegroundColor Red;Read-Host 'Pulsa Enter para cerrar'}
finally {if ($server) {$server.Close()}}
'''
(R/'Leer_Rutas.ps1').write_text(runtime)
setup=r'''& {
$ErrorActionPreference='Stop'
try {
 $source=Join-Path ([Environment]::GetFolderPath('Desktop')) 'SpiderGateway\app.html'
 if (!(Test-Path -LiteralPath $source)) {
  Add-Type -AssemblyName System.Windows.Forms
  $dialog=[Windows.Forms.OpenFileDialog]::new()
  $dialog.Title='Selecciona app.html dentro de tu carpeta SpiderGateway'
  $dialog.Filter='Pagina HTML (*.html)|*.html'
  try {
   if ($dialog.ShowDialog() -ne [Windows.Forms.DialogResult]::OK) {throw 'Cancelado.'}
   $source=$dialog.FileName
  } finally {$dialog.Dispose()}
 }
 $old=[IO.File]::ReadAllText($source)
 $scripts=[regex]::Matches($old,'(?is)<script[^>]*>(.*?)</script>')
 $reader=$null
 foreach ($s in $scripts) {
  $m=[regex]::Match($s.Groups[1].Value,'(?ms)\A(.*?class\s+SpiderReadOnly\b.*?^\})')
  if ($m.Success) {$reader=$m.Groups[1].Value;break}
 }
 if (!$reader -or !$reader.Contains('const U32=') -or !$reader.Contains('function frame(') -or $reader.Contains('class SpiderBypassTrial')) {
  throw 'No pude extraer de forma segura el lector original. No se modifico la aplicacion.'
 }
 $extra=@'
__JS__
'@
 $runtime=@'
__RUNTIME__
'@
 $page='<!doctype html><html lang="es"><meta charset="utf-8"><title>Spider: leer rutas</title><style>body{font:18px system-ui;padding:20px}button{font:inherit;padding:10px}pre{white-space:pre-wrap}</style><h1>Spider: diagnostico de lectura</h1><p>Solo consulta seis combinaciones de parametros; no cambia niveles ni activa bypass. Remote y otros clientes MIDI deben estar desconectados.</p><button id="connect">Conectar y leer</button><button id="read" hidden></button><button id="disconnect" hidden></button><pre id="log">Preparado.</pre><script>'+$reader+"`n"+$extra+'</script></html>'
 $dest=Join-Path ([Environment]::GetFolderPath('Desktop')) ('SpiderLectura-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss-fff'))
 [void][IO.Directory]::CreateDirectory($dest)
 $encoding=[Text.UTF8Encoding]::new($true)
 [IO.File]::WriteAllText((Join-Path $dest 'lectura.html'),$page,$encoding)
 $file=Join-Path $dest 'Leer_Rutas.ps1'
 [IO.File]::WriteAllText($file,$runtime,$encoding)
 Write-Host ('Creado en: '+$dest) -ForegroundColor Green
 Start-Process -FilePath "$PSHOME\powershell.exe" -Verb RunAs -ArgumentList @('-NoProfile','-ExecutionPolicy','RemoteSigned','-File',('"'+$file+'"'))
} catch {Write-Host ('ERROR: '+$_.Exception.Message) -ForegroundColor Red}
}
'''
setup=setup.replace('__JS__',(R/'routing_reader.js').read_text()).replace('__RUNTIME__',runtime)
(R/'Preparar_Lectura.ps1').write_text(setup)
print(len(setup))
