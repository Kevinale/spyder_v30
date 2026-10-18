from pathlib import Path
R=Path(__file__).resolve().parent
runtime=(R/'Leer_Rutas.ps1').read_text().replace('lectura.html','prueba.html').replace('8771','8772').replace('LECTURA SOLAMENTE:','PRUEBA TEMPORAL:')
setup=r'''& {
$ErrorActionPreference='Stop'
try {
 $desktop=[Environment]::GetFolderPath('Desktop')
 $folder=Get-ChildItem -LiteralPath $desktop -Directory -Filter 'SpiderLectura-*' | Sort-Object Name -Descending | Select-Object -First 1
 if (!$folder) {throw 'No encuentro la carpeta SpiderLectura de la prueba anterior.'}
 $old=[IO.File]::ReadAllText((Join-Path $folder.FullName 'lectura.html'))
 if (!$old.Contains('class SpiderRoutingReader') -or $old.Contains('class SpiderOutputGainTrial')) {throw 'La pagina de lectura no coincide. No se modifico.'}
 $extra=@'
__ADDON__
'@
 $runtime=@'
__RUNTIME__
'@
 $page=$old.Replace('</html>','<script>'+$extra+'</script></html>')
 $dest=Join-Path $desktop ('SpiderSalida-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss-fff'))
 [void][IO.Directory]::CreateDirectory($dest)
 $utf8=[Text.UTF8Encoding]::new($true)
 [IO.File]::WriteAllText((Join-Path $dest 'prueba.html'),$page,$utf8)
 $file=Join-Path $dest 'Probar_Salida.ps1'
 [IO.File]::WriteAllText($file,$runtime,$utf8)
 Write-Host ('Creado: '+$dest) -ForegroundColor Green
 Start-Process -FilePath "$PSHOME\powershell.exe" -Verb RunAs -ArgumentList @('-NoProfile','-ExecutionPolicy','RemoteSigned','-File',('"'+$file+'"'))
} catch {Write-Host ('ERROR: '+$_.Exception.Message) -ForegroundColor Red}
}
'''
addon=(R/'output_gain_trial.js').read_text()+'\n'+(R/'output_gain_ui.js').read_text()
(R/'Preparar_Prueba_Salida.ps1').write_text(setup.replace('__ADDON__',addon).replace('__RUNTIME__',runtime))
print('Generated:',(R/'Preparar_Prueba_Salida.ps1').stat().st_size)
