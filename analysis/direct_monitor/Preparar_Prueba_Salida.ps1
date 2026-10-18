& {
$ErrorActionPreference='Stop'
try {
 $desktop=[Environment]::GetFolderPath('Desktop')
 $folder=Get-ChildItem -LiteralPath $desktop -Directory -Filter 'SpiderLectura-*' | Sort-Object Name -Descending | Select-Object -First 1
 if (!$folder) {throw 'No encuentro la carpeta SpiderLectura de la prueba anterior.'}
 $old=[IO.File]::ReadAllText((Join-Path $folder.FullName 'lectura.html'))
 if (!$old.Contains('class SpiderRoutingReader') -or $old.Contains('class SpiderOutputGainTrial')) {throw 'La pagina de lectura no coincide. No se modifico.'}
 $extra=@'
// Separate proposed experiment. NOT part of the read-only diagnostic.
// Must not be started without explicit owner consent to this parameter test.
class SpiderOutputGainTrial extends SpiderRoutingReader {
 constructor(log){super(log);this.stage='idle';this.attempted=false;this.running=null;this.restoring=null;this.timer=null;this.stopRequested=false;}
 async readOutputGain(){
  const b=await this.request(9,[...LE(0xffffffff),...LE(this.ids.GuitProcOutputGain)]);
  if(b.length!==12||(U32(b)|0)!==0||U32(b,4)!==4)throw Error('No se pudo leer gain global float');
  const raw=U32(b,8);return {raw,value:new DataView(Uint8Array.from(b).buffer).getFloat32(8,true)};
 }
 async writeGainWord(word){
  const valid=this.ready&&this.ids&&this.ids.GuitProcOutputGain!==undefined&&
   ((this.stage==='applying'&&word===0)||(this.stage==='restoring'&&word===0x3f800000));
  if(!valid||this.pending||!this.output)throw Error('Escritura bloqueada');
  const body=[...LE(0xffffffff),...LE(this.ids.GuitProcOutputGain),...LE(4),...LE(word)];
  const reply=await new Promise((resolve,reject)=>{
   const timer=setTimeout(()=>{this.pending=null;reject(Error('Sin respuesta a gain'));},5000);
   this.pending={resolve,reject,timer};
   try{this.output.send(frame([...LE(10),...LE(16),...body],this.q));this.q=(this.q+1)&127;}
   catch(e){this.abort(e.message);}
  });
  if(reply.length!==4||(U32(reply)|0)!==0)throw Error('Cambio de gain no confirmado');
 }
 async start(consent){
  if(consent!==true||!this.ready||this.stage!=='idle'||this.running||this.attempted)throw Error('Conecta y autoriza esta prueba por separado');
  this.stopRequested=false;this.stage='checking';
  this.running=(async()=>{
   try{
    const snapshot=await this.readOutputGain();
    if(snapshot.raw!==0x3f800000)throw Error('Se exige valor inicial exactamente1; no se cambio');
    if(this.stopRequested){this.stage='idle';return;}
    this.stage='applying';this.attempted=true;
    await this.writeGainWord(0);
    const now=await this.readOutputGain();
    if(now.raw!==0)throw Error('Gain0 no verificado');
    this.stage='active';this.log('Gain global0 leido. Prueba15s: observar sonido directo y medidor de entrada; no guardar preset.');
    this.timer=setTimeout(()=>this.finish().catch(e=>this.log('RESTAURACION NO CONFIRMADA: '+e.message)),15000);
   }catch(e){
    if(this.attempted)await this.restoreGain();else this.stage='idle';
    throw e;
   }
  })();
  try{await this.running;}finally{this.running=null;}
  if(this.stopRequested&&this.attempted)await this.restoreGain();
 }
 async restoreGain(){
  clearTimeout(this.timer);this.timer=null;
  if(this.restoring)return this.restoring;
  if(!this.attempted){this.stage='idle';return;}
  this.stage='restoring';
  this.restoring=(async()=>{
   try{
    await this.writeGainWord(0x3f800000);
    const now=await this.readOutputGain();if(now.raw!==0x3f800000)throw Error('Gain1 no verificado');
    this.attempted=false;this.stage='idle';this.log('Restauracion confirmada: GuitProcOutputGain=1');
   }catch(e){this.stage='restore_failed';throw e;}
  })();
  try{await this.restoring;}finally{this.restoring=null;}
 }
 async finish(){this.stopRequested=true;if(this.running)await this.running.catch(()=>{});await this.restoreGain();}
 async close(){await this.finish();await super.close();}
}

const gainLog=s=>{document.getElementById('log').textContent+=s+'\n';};
let gainTest=null;
const gainButton=id=>document.getElementById(id);
document.title='Spider: prueba de salida15s';
document.querySelector('h1').textContent='Prueba temporal de salida15 segundos';
document.querySelector('p').textContent='Remote cerrado. REAPER: pista armada, Gateway apagado, monitorizacion apagada y reproduccion detenida. Volume del Amp restaurado a su valor habitual. Mira el medidor de entrada mientras tocas. No guardar presets. Manten esta pagina visible.';
gainButton('connect').textContent='Conectar y leer';
gainButton('read').hidden=true;
gainButton('disconnect').hidden=false;
gainButton('disconnect').textContent='Restaurar y desconectar';
for(const[id,label]of [['gainStart','Probar salida15s'],['gainRestore','Restaurar ahora']]){
 const b=document.createElement('button');b.id=id;b.textContent=label;b.disabled=true;
 gainButton('disconnect').before(b);
}
gainButton('connect').onclick=async()=>{
 gainButton('connect').disabled=true;
 try{
  gainTest=new SpiderOutputGainTrial(gainLog);const ampFlag=await gainTest.connect();
  if(ampFlag!==1)throw Error('Restaura AmpEnable1 en SpiderGateway antes de esta prueba.');
  const snap=await gainTest.readOutputGain();gainLog('GuitProcOutputGain='+snap.value+' (float).');
  if(snap.raw!==0x3f800000)throw Error('Se requiere gain inicial1. No se cambia.');
  gainButton('gainStart').disabled=false;
 }catch(e){gainLog('ERROR: '+e.message);if(gainTest)await gainTest.close().catch(r=>gainLog(r.message));gainTest=null;gainButton('connect').disabled=false;}
};
gainButton('gainStart').onclick=async()=>{
 if(!gainTest)return;
 gainButton('gainStart').disabled=true;gainButton('gainRestore').disabled=false;
 try{await gainTest.start(true);}catch(e){gainLog('ERROR: '+e.message);}
};
gainButton('gainRestore').onclick=async()=>{
 try{if(gainTest)await gainTest.finish();}
 catch(e){gainLog('RESTAURACION NO CONFIRMADA: '+e.message);}
};
gainButton('disconnect').onclick=async()=>{
 try{
  if(gainTest)await gainTest.close();gainTest=null;
  gainButton('connect').disabled=false;gainButton('gainStart').disabled=true;gainButton('gainRestore').disabled=true;
  gainLog('Puertos MIDI cerrados.');
 }catch(e){gainLog('No cierres todavia: '+e.message);}
};
window.addEventListener('beforeunload',e=>{if(gainTest?.attempted){e.preventDefault();e.returnValue='';}});
document.addEventListener('visibilitychange',()=>{
 if(document.hidden&&gainTest&&(gainTest.attempted||gainTest.running))gainTest.finish().catch(e=>gainLog('RESTAURACION NO CONFIRMADA: '+e.message));
});
document.getElementById('log').textContent='Preparado. Conectar solo lee. Probar salida cambia exclusivamente GuitProcOutputGain1 a0 durante15s y restaura1.\n';

'@
 $runtime=@'
$ErrorActionPreference='Stop'
$server=$null
try {
 $html=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'prueba.html'))
 $server=[Net.HttpListener]::new()
 $server.Prefixes.Add('http://localhost:8772/')
 $server.Start()
 Write-Host 'PRUEBA TEMPORAL: http://localhost:8772/ . Deja esta consola abierta.'
 Start-Process 'http://localhost:8772/'
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
