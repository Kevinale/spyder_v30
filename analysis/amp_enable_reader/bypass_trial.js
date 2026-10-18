'use strict';
// Separate experimental component. NEVER loaded by the read-only page.
// A start(true) user action is required; connecting/reading never sets a value.
const Base=typeof module!=='undefined'?require('./reader.js').SpiderReadOnly:SpiderReadOnly;
const U=typeof module!=='undefined'?require('./reader.js').U32:U32;
const L=typeof module!=='undefined'?require('./reader.js').LE:LE;
const F=typeof module!=='undefined'?require('./reader.js').frame:frame;
class SpiderBypassTrial extends Base {
 constructor(log){super(log);this.stage='idle';this.attempted=false;this.original=null;this.model=null;this.timer=null;this.restoring=null;this.counts={Drive:0,Bass:0,Mid:0,Treble:0};this.onmessage=(kind,body)=>this.observe(kind,body);}
 experimental(op,body){
  const modelRead=op===7&&this.ready&&this.ids&&body.length===4&&U(body)===this.ids.Amp;
  const value=body.length===16?U(body,12):-1;
  const write=op===10&&this.ready&&this.ids&&body.length===16&&U(body)===this.ids.GuitarProc&&U(body,4)===this.ids.AmpEnable&&U(body,8)===3&&((this.stage==='applying'&&value===0)||(this.stage==='restoring'&&this.original===1&&value===1));
  if(!modelRead&&!write)throw Error('Operacion experimental bloqueada');
  if(this.pending)throw Error('Consulta pendiente');
  if(!this.output)throw Error('Puerto cerrado');
  return new Promise((resolve,reject)=>{const timer=setTimeout(()=>{this.pending=null;reject(Error('Tiempo de respuesta agotado'));},10000);this.pending={resolve,reject,timer};try{this.output.send(F([...L(op),...L(body.length),...body],this.q));this.q=(this.q+1)&127;}catch(e){this.abort(e.message);}});
 }
 async getModel(){const b=await this.experimental(7,L(this.ids.Amp));if(b.length!==8||(U(b)|0)!==0)throw Error('No se pudo verificar modelo Amp');return U(b,4);}
 async write(value){const b=await this.experimental(10,[...L(this.ids.GuitarProc),...L(this.ids.AmpEnable),...L(3),...L(value)]);if(b.length!==4||(U(b)|0)!==0)throw Error('El equipo no confirmo el cambio de AmpEnable');}
 observe(kind,b){if(this.stage!=='active'||kind!==4||b.length!==16||U(b)!==this.ids.Amp||U(b,8)!==4)return;const names=['Drive','Bass','Mid','Treble'];const name=names.find(n=>this.ids[n]===U(b,4));if(name){this.counts[name]++;this.log('Perilla '+name+': '+this.counts[name]+' eventos identificados');}}
 async start(consent){
  if(consent!==true)throw Error('Falta accion explicita para iniciar prueba activa');
  if(this.stage!=='idle'||!this.ready)throw Error('Conecta y termina cualquier prueba anterior');
  for(const n of ['Amp','Bypass','GuitarProc','AmpEnable','Drive','Bass','Mid','Treble'])if(!Object.hasOwn(this.ids,n))throw Error('Falta simbolo '+n);
  this.stage='checking';
  try{
   this.model=await this.getModel();if(this.model===this.ids.Bypass)throw Error('Selecciona un Amp activo, no No Amp');
   this.original=await this.read();if(this.original!==1)throw Error('La prueba exige AmpEnable inicial1; no se cambio');
   this.counts={Drive:0,Bass:0,Mid:0,Treble:0};this.stage='applying';this.attempted=true;
   await this.write(0);
   const value=await this.read();if(value!==0)throw Error('Lectura posterior distinta de0');
   if(await this.getModel()!==this.model)throw Error('El modelo cambio; prueba detenida');
   this.stage='active';this.log('AmpEnable=0 verificado; mismo modelo. Prueba20 segundos: toca y mueve las cuatro perillas.');
   this.timer=setTimeout(()=>{this.finish().catch(e=>this.log('RESTAURACION NO CONFIRMADA: '+e.message));},20000);
  }catch(e){if(this.attempted){try{await this.finish();}catch(r){throw Error(e.message+'; RESTAURACION NO CONFIRMADA: '+r.message);}}else this.stage='idle';throw e;}
 }
 async finish(){
  if(this.restoring)return this.restoring;
  clearTimeout(this.timer);this.timer=null;
  if(!this.attempted){this.stage='idle';return;}
  this.restoring=(async()=>{
   this.stage='restoring';
   try{this.beforeRestore=await this.read();this.log('Antes de restaurar: AmpEnable='+this.beforeRestore+(this.beforeRestore===0?' (seguia desactivado).':' (se reactivo o cambio durante la prueba).'));}catch(e){this.log('No se pudo leer estado al final; se intenta restaurar igualmente: '+e.message);}
   try{await this.write(this.original);const value=await this.read();if(value!==this.original)throw Error('Lectura final no coincide con valor inicial');this.attempted=false;this.stage='idle';this.log('Restauracion confirmada: AmpEnable='+value+'. Eventos: '+JSON.stringify(this.counts));}
   catch(e){this.stage='restore_failed';this.log('No se confirmo la restauracion. Conserva la pagina abierta y reintenta Restaurar.');throw e;}
  })();
  try{return await this.restoring;}finally{this.restoring=null;}
 }
 async close(){if(this.attempted)await this.finish();return super.close();}
}
if(typeof module!=='undefined')module.exports={SpiderBypassTrial};
