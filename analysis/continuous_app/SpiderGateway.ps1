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
