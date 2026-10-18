'use strict';
// Consulta acotada: identidad, version, tabla, handshake y GetDspModelParam.
// No setters, carga de modelos, presets, actualizacion ni acceso a memoria.
const U32=(b,o=0)=>(b[o]|b[o+1]<<8|b[o+2]<<16|b[o+3]<<24)>>>0;
const LE=n=>[n&255,n>>>8&255,n>>>16&255,n>>>24&255];
const CRC=b=>{let c=0xffffffff;for(const v of b){c^=v;for(let i=0;i<8;i++)c=c&1?(c>>>1)^0xedb88320:c>>>1;}return(c^0xffffffff)>>>0;};
function unpack(b){const a=[];for(let i=0;i<b.length;i+=8)for(let j=1;j<8&&i+j<b.length;j++)a.push(b[i+j]|((b[i]>>(7-j)&1)<<7));return a;}
function frame(raw,q){const a=[240,0,1,12,34,0,77,0,q,0,(raw.length-1)>>4,(raw.length-1)&15];for(let i=0;i<raw.length;i+=7){let mask=0,g=[];for(let j=0;j<7;j++){const v=raw[i+j]||0;mask|=(v>>7)<<(6-j);g.push(v&127);}a.push(mask,...g);}return[...a,247];}
class SpiderReadOnly {
 constructor(log=()=>{}){this.log=log;this.q=0;this.stream=[];this.rx=[];this.seq=-1;this.end=-1;this.pending=null;this.ready=false;this.seen=false;this.ids=null;}
 abort(reason){if(this.pending){clearTimeout(this.pending.timer);this.pending.reject(Error(reason));this.pending=null;}}
 feed(bytes){for(const v of bytes){if(v>=248)continue;if(v===240)this.rx=[v];else if(this.rx.length){this.rx.push(v);if(this.rx.length>200000){this.rx=[];this.abort('SysEx demasiado largo');}else if(v===247){const s=this.rx;this.rx=[];try{this.packet(s);}catch(e){this.abort(e.message);}}}}}
 packet(s){
  if(s.length===17&&s[0]===240&&s[1]===126&&s[3]===6&&s[4]===2&&s.slice(5,12).join(',')==='0,1,12,34,0,0,0')this.seen=true;
  if(s.length<14||s.slice(0,8).join(',')!=='240,0,1,12,34,0,77,0'||s.at(-1)!==247)return;
  if(s.slice(1,-1).some(v=>v>127))throw Error('SysEx no valido');
  const q=s[8],end=(s[9]<<8)|(s[10]<<4)|s[11];
  if(s[10]>15||s[11]>15)throw Error('Cabecera de fragmento no valida');
  if(q!==this.seq){this.stream=[];this.end=-1;this.seq=q;}
  const n=end-this.end,raw=unpack(s.slice(12,-1));
  if(n<=0||n>raw.length)throw Error('Fragmento incompleto o fuera de orden');
  this.end=end;this.stream.push(...raw.slice(0,n));
  while(this.stream.length>=8){
   const size=U32(this.stream,4);if(size>131072)throw Error('Respuesta fuera de limites');
   if(this.stream.length<8+size)break;
   const kind=U32(this.stream),body=this.stream.slice(8,8+size);this.stream.splice(0,8+size);
   if(this.onmessage)this.onmessage(kind,body);
   if(kind===1&&this.pending){const p=this.pending;this.pending=null;clearTimeout(p.timer);p.resolve(body);}
  }
 }
 request(op,body=[]){
  const allowed=(op===1||op===2||op===3)?body.length===0:op===4?body.length===4&&this.table&&U32(body)===CRC(this.table):op===9?this.ready&&this.ids&&body.length===8&&U32(body)===this.ids.GuitarProc&&U32(body,4)===this.ids.AmpEnable:false;
  if(!allowed)throw Error('Operacion bloqueada por lista de solo lectura');
  if(this.pending)throw Error('Ya hay una consulta pendiente');
  if(!this.output)throw Error('Puerto MIDI cerrado');
  return new Promise((resolve,reject)=>{const timer=setTimeout(()=>{this.pending=null;reject(Error('Sin respuesta; cierra Remote y libera el MIDI del Spider en REAPER.'));},10000);this.pending={resolve,reject,timer};try{this.output.send(frame([...LE(op),...LE(body.length),...body],this.q));this.q=(this.q+1)&127;}catch(e){this.abort(e.message);}});
 }
 parseSymbols(table){
  if(table.length<8||U32(table,4)!==table.length)throw Error('Tamano de tabla incorrecto');
  const n=U32(table),pool=8+12*n;if(n>4096||pool>table.length)throw Error('Tabla fuera de limites');
  const ids={};const decoder=new TextDecoder('utf-8',{fatal:true});
  for(let i=0;i<n;i++){const o=8+12*i,p=pool+U32(table,o),len=U32(table,o+8);if(p<pool||p+len>=table.length||table[p+len]!==0)throw Error('Cadena fuera de tabla');const bytes=table.slice(p,p+len);if(CRC(bytes)!==U32(table,o+4))throw Error('CRC de simbolo incorrecto');const name=decoder.decode(Uint8Array.from(bytes));if(Object.hasOwn(ids,name))throw Error('Simbolo duplicado');ids[name]=i;}
  for(const k of ['GuitarProc','AmpEnable','AmpEnableState'])if(!Object.hasOwn(ids,k))throw Error('Falta simbolo '+k);
  return ids;
 }
 async connect(){
  if(this.input||this.output)throw Error('Desconecta primero');
  if(!navigator.requestMIDIAccess)throw Error('Abre esta pagina en Edge o Chrome con Web MIDI.');
  const access=await navigator.requestMIDIAccess({sysex:true});
  const ins=[...access.inputs.values()].filter(p=>/spider\s*v/i.test(p.name||''));
  const outs=[...access.outputs.values()].filter(p=>/spider\s*v/i.test(p.name||''));
  if(ins.length!==1||outs.length!==1)throw Error('Necesito exactamente una entrada y salida MIDI Spider V. Cierra Remote y deshabilita su MIDI en REAPER.');
  this.input=ins[0];this.output=outs[0];await this.input.open();await this.output.open();
  this.input.onmidimessage=e=>this.feed(e.data);this.seen=false;
  this.output.send([240,126,127,6,1,247]);
  for(let i=0;i<60&&!this.seen;i++)await new Promise(r=>setTimeout(r,50));
  if(!this.seen)throw Error('No se verifico identidad Spider V30; no se consultan parametros.');
  const version=await this.request(1);if(version.length!==4||U32(version)!==0x02050030)throw Error('Version distinta de la captura 2.05.0; consulta detenida.');
  this.log('Identidad y version coinciden con tu Spider V30 / 2.05.0.');
  const size=await this.request(2);if(size.length!==4||U32(size)>131072)throw Error('Tamano de simbolos incorrecto');
  this.table=await this.request(3);if(this.table.length!==U32(size))throw Error('Tabla incompleta');
  this.ids=this.parseSymbols(this.table);this.log('Tabla recibida; CRC de todos los simbolos valido.');
  const status=await this.request(4,LE(CRC(this.table)));if(status.length!==4||U32(status)!==0)throw Error('Sesion rechazada; no se cambian parametros.');
  this.ready=true;this.log('Sesion de consulta abierta.');return this.read();
 }
 async read(){
  if(!this.ready)throw Error('Conecta primero');
  const b=await this.request(9,[...LE(this.ids.GuitarProc),...LE(this.ids.AmpEnable)]);
  if(b.length!==12)throw Error('Respuesta de parametro inesperada');
  const status=U32(b)|0;if(status!==0)throw Error('AmpEnable no pudo leerse: estado '+status);
  const type=U32(b,4),value=U32(b,8);if(type!==3||value>1)throw Error('AmpEnable respondio con tipo/valor inesperado: '+type+'/'+value);
  this.log('AmpEnable = '+value+' (booleano).');return value;
 }
 async close(){this.ready=false;this.abort('Consulta cancelada');const input=this.input,output=this.output;this.input=null;this.output=null;if(input){input.onmidimessage=null;await input.close();}if(output)await output.close();}
}
if(typeof module!=='undefined')module.exports={SpiderReadOnly,U32,LE,CRC,frame};
