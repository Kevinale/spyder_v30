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
