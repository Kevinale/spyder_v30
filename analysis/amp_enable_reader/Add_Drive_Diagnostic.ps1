$ErrorActionPreference = 'Stop'
if (!$html -or !$html.Contains('class SpiderBypassTrial')) {
 throw 'Usa la ventana PowerShell de la prueba8767 y pulsa Ctrl+C antes de pegar este bloque.'
}
if (!$html.Contains('SPIDER_DRIVE_DIAGNOSTIC_V1')) {
 $diagnostic = @'
// SPIDER_DRIVE_DIAGNOSTIC_V1
const diagName=(r,id)=>Object.keys(r.ids||{}).find(k=>r.ids[k]===id)||('ID_'+id);
const diagGetModel=SpiderBypassTrial.prototype.getModel;
SpiderBypassTrial.prototype.getModel=async function(){
 const id=await diagGetModel.call(this);
 this.log('Modelo Amp: '+diagName(this,id)+' (ID '+id+')');
 return id;
};
const diagObserve=SpiderBypassTrial.prototype.observe;
SpiderBypassTrial.prototype.observe=function(kind,b){
 diagObserve.call(this,kind,b);
 if(this.stage!=='active'||kind!==4||b.length!==16)return;
 if(this.diagLastCounts!==this.counts){this.diagLastCounts=this.counts;this.diagCount=0;}
 this.diagCount++;
 if(this.diagCount<=80){
  const group=U32(b),param=U32(b,4),type=U32(b,8);
  const value=type===4?new DataView(Uint8Array.from(b).buffer).getFloat32(12,true):U32(b,12);
  this.log('DATO '+diagName(this,group)+'.'+diagName(this,param)+' | IDs '+group+'/'+param+' | tipo '+type+' | valor '+value);
 }else if(this.diagCount===81)this.log('Mas de80 notificaciones; detalle adicional omitido.');
};
document.getElementById('log').textContent='DIAGNOSTICO DRIVE: conecta, inicia la prueba y mueve SOLO Drive. No cambies el modelo.\n';

'@
 $html = $html.Replace('</html>', '<script>' + $diagnostic + '</script></html>')
}
$listener = [Net.HttpListener]::new()
$listener.Prefixes.Add('http://localhost:8767/')
try {
 $listener.Start()
 Write-Host 'Abre http://localhost:8767/ en Edge o Chrome. Cierra esta ventana al terminar.'
 Start-Process 'http://localhost:8767/'
 while ($listener.IsListening) {
  $context = $listener.GetContext()
  $response = $context.Response
  if ($context.Request.RawUrl -eq '/') {
   $bytes = [Text.Encoding]::UTF8.GetBytes($html)
   $response.ContentType = 'text/html; charset=utf-8'
   $response.Headers.Add('Cache-Control','no-store')
   $response.Headers.Add('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'none'; frame-ancestors 'none'")
   $response.ContentLength64 = $bytes.Length
   $response.OutputStream.Write($bytes,0,$bytes.Length)
  } else { $response.StatusCode = 404 }
  $response.Close()
 }
} finally { $listener.Close() }
