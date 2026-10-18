& {
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
// Bounded parameter reads only. No setter, preset, model-load or memory opcode.
class SpiderRoutingReader extends SpiderReadOnly {
 request(op,body=[]){
  if(op!==9)return super.request(op,body);
  const names=['AmpEnable','GuitProcOutputGain','USBOutLevel','USBInLevel'];
  const valid=this.ready&&this.ids&&body.length===8&&
   (U32(body)===this.ids.GuitarProc||U32(body)===0xffffffff)&&
   names.some(n=>Object.hasOwn(this.ids,n)&&U32(body,4)===this.ids[n]);
  if(!valid)throw Error('Consulta fuera de la lista de lectura');
  if(this.pending||!this.output)throw Error('Consulta pendiente o puerto cerrado');
  return new Promise((resolve,reject)=>{
   const timer=setTimeout(()=>{this.pending=null;reject(Error('Sin respuesta: diagnostico detenido'));},5000);
   this.pending={resolve,reject,timer};
   try{this.output.send(frame([...LE(9),...LE(8),...body],this.q));this.q=(this.q+1)&127;}
   catch(e){this.abort(e.message);}
  });
 }
 async inspectRouting(){
  for(const name of ['GuitProcOutputGain','USBOutLevel','USBInLevel']){
   if(!Object.hasOwn(this.ids,name)){this.log(name+': simbolo ausente');continue;}
   // Two explicit hypotheses, not a scan of arbitrary groups or addresses.
   for(const group of [0xffffffff,this.ids.GuitarProc]){
    const label=group===0xffffffff?'global(-1)':'GuitarProc';
    const b=await this.request(9,[...LE(group),...LE(this.ids[name])]);
    if(b.length<4)throw Error('Respuesta incompleta');
    const status=U32(b)|0;
    if(status!==0){this.log(name+' | '+label+' | estado='+status);continue;}
    if(b.length!==12)throw Error('Respuesta exitosa con longitud inesperada');
    const type=U32(b,4),raw=U32(b,8);
    let value='sin interpretar';
    if(type===3&&raw<=1)value=String(raw)+' (booleano)';
    if(type===4){const f=new DataView(Uint8Array.from(b).buffer).getFloat32(8,true);value=Number.isFinite(f)?String(f)+' (float; unidades desconocidas)':'float no finito';}
    this.log(name+' | '+label+' | tipo='+type+' | valor='+value+' | raw=0x'+raw.toString(16).padStart(8,'0'));
   }
  }
  this.log('FIN. Solo consultas; no se cambio ningun nivel.');
 }
}
const routingLog=s=>{document.getElementById('log').textContent+=s+'\n';};
document.getElementById('connect').textContent='Conectar y leer rutas';
document.getElementById('connect').onclick=async()=>{
 const b=document.getElementById('connect');b.disabled=true;
 const reader=new SpiderRoutingReader(routingLog);
 document.getElementById('log').textContent='Diagnostico de lectura. Remote y otros clientes MIDI cerrados.\n';
 try{await reader.connect();await reader.inspectRouting();}
 catch(e){routingLog('ERROR: '+e.message);}
 finally{await reader.close().catch(e=>routingLog('Cierre: '+e.message));routingLog('Puertos cerrados. Copia este registro al chat.');b.disabled=false;}
};
for(const id of ['read','disconnect'])document.getElementById(id).hidden=true;

'@
 $runtime=@'
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
