# Ejecutar en Windows PowerShell como administrador; no ejecuta instaladores.
$ErrorActionPreference = 'Stop'
$candidates = @(
 "$env:ProgramFiles\USBPcap\USBPcapCMD.exe",
 "$env:ProgramFiles\Wireshark\extcap\USBPcapCMD.exe",
 "${env:ProgramFiles(x86)}\USBPcap\USBPcapCMD.exe"
)
$exe = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (!$exe) { throw 'No encuentro USBPcapCMD.exe. Indica donde esta instalado USBPcap.' }
$path = Join-Path $env:TEMP 'SpiderGateway-live.pcap'
$stream = $null; $process = $null
try {
 $stream = [IO.FileStream]::new($path,[IO.FileMode]::Create,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 $info = [Diagnostics.ProcessStartInfo]::new()
 $info.FileName = $exe
 $info.Arguments = '-d \\.\USBPcap2 --devices 4 --inject-descriptors -s 128 -b 4096 -o -'
 $info.UseShellExecute = $false
 $info.RedirectStandardOutput = $true
 $process = [Diagnostics.Process]::new()
 $process.StartInfo = $info
 [void]$process.Start()
 Write-Host 'Receptor activo por 120 segundos. Ahora ejecuta Spider_Live.lua en REAPER.'
 $buffer = New-Object byte[] 65536
 $watch = [Diagnostics.Stopwatch]::StartNew()
 while (!$process.HasExited -and $watch.Elapsed.TotalSeconds -lt 120 -and $stream.Length -lt 134217728) {
  $task = $process.StandardOutput.BaseStream.ReadAsync($buffer,0,$buffer.Length)
  while (!$task.Wait(200)) {
   if ($watch.Elapsed.TotalSeconds -ge 120) { break }
  }
  if (!$task.IsCompleted) { break }
  $n = $task.Result
  if ($n -eq 0) { break }
  $stream.Write($buffer,0,$n); $stream.Flush()
 }
} finally {
 if ($process) {
  if (!$process.HasExited) { $process.Kill(); $process.WaitForExit() }
  $process.Dispose()
 }
 if ($stream) { $stream.Dispose() }
 Write-Host 'Receptor detenido. El archivo temporal no se envia a ningun sitio.'
}
