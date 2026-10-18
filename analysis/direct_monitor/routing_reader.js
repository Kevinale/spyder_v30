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
