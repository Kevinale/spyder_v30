$ErrorActionPreference='Stop'
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
