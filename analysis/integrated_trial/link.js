// SPIDER_INTEGRATED_LINK_V1: inherits only the already validated20s trial.
const localToken='__LOCAL_TOKEN__';
const link={seq:0,values:[-1,-1,-1,-1],pause:false,busy:false};
async function publishLink(forceOff=false){
 if(link.busy)return false;link.busy=true;
 const enabled=!forceOff&&!link.pause&&trial?.stage==='active'?1:0;
 const body=[++link.seq,enabled,...link.values].join(',');
 try{
  const response=await fetch('/state',{method:'POST',headers:{'Content-Type':'text/plain','X-Spider-Token':localToken},body});
  if(!response.ok)throw Error('Estado local rechazado');return true;
 }catch(e){if(enabled)trialLog('Puente local sin respuesta; REAPER apagara monitor por caducidad.');return false;}
 finally{link.busy=false;}
}
const linkObserve=SpiderBypassTrial.prototype.observe;
SpiderBypassTrial.prototype.observe=function(kind,b){
 linkObserve.call(this,kind,b);
 if(this.stage!=='active'||kind!==4||b.length!==16||U32(b)!==this.ids.Amp||U32(b,8)!==4)return;
 const id=U32(b,4),v=new DataView(Uint8Array.from(b).buffer).getFloat32(12,true);
 if(!Number.isFinite(v)||v<0||v>1)return;
 const slot=(id===this.ids.Drive||id===this.ids.Gain)?0:id===this.ids.Bass?1:id===this.ids.Mid?2:id===this.ids.Treble?3:-1;
 if(slot>=0){link.values[slot]=v;if(slot===0&&id===this.ids.Gain)this.log('Drive fisico recibido como Gain.');}
};
const linkStart=SpiderBypassTrial.prototype.start;
SpiderBypassTrial.prototype.start=async function(consent){
 link.values=[-1,-1,-1,-1];link.pause=false;
 await linkStart.call(this,consent);
 if(this.stage==='active')await publishLink();
};
const linkFinish=SpiderBypassTrial.prototype.finish;
SpiderBypassTrial.prototype.finish=async function(){
 link.pause=true;
 if(this.attempted){
  // Give the Lua consumer time to turn monitoring off before restoring Amp1.
  for(let i=0;i<5&&link.busy;i++)await new Promise(r=>setTimeout(r,100));
  await publishLink(true);await new Promise(r=>setTimeout(r,500));
 }
 return linkFinish.call(this);
};
setInterval(()=>publishLink(),100);
document.querySelector('h1').textContent='Spider + Gateway: ensayo integrado20 segundos';
for(const p of document.querySelectorAll('p'))p.textContent='Remote cerrado. REAPER abierto con Gateway activo, pista armada y el script Integrado ejecutandose. Manten esta pagina visible durante20 segundos. Al terminar se apaga monitorizacion y se restaura Amp1.';
document.getElementById('log').textContent='Integracion preparada. Inicia el script de REAPER antes de Probar bypass.\n';
