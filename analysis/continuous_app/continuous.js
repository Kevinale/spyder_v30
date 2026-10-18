// SPIDER_CONTINUOUS_V1: explicit Start/Stop replaces the proven20s timer.
const continuousClient=(crypto.randomUUID?crypto.randomUUID():String(Date.now())+'-'+Math.random());
const appLog=s=>{s=String(s).replace(/Prueba20 segundos: toca y mueve las cuatro perillas\./g,'Mueve las cuatro perillas para controlar Gateway.').replace(/PRUEBA20 SEGUNDOS: toca y mueve Drive\/Bass\/Mid\/Treble\./g,'Mueve las cuatro perillas para controlar Gateway.');const el=document.getElementById('log');el.textContent=(el.textContent+s+'\n').slice(-18000);};
trialLog=appLog;
const oldPublisher=publishLink;
publishLink=async function(forceOff=false){
 if(!trial?.ready&&!forceOff)return false;
 return oldPublisher(forceOff);
};
const continuousStart=SpiderBypassTrial.prototype.start;
SpiderBypassTrial.prototype.start=async function(consent){
 await continuousStart.call(this,consent);
 if(this.stage==='active'){
  clearTimeout(this.timer);this.timer=null;
  this.log('NAM CONTINUO ACTIVO. Manten esta pagina visible. Detener restaura el Amp.');
  document.getElementById('status').textContent='NAM activo';
 }
};
const continuousFinish=SpiderBypassTrial.prototype.finish;
SpiderBypassTrial.prototype.finish=async function(){
 const answer=await continuousFinish.call(this);
 if(!this.attempted){
  document.getElementById('status').textContent='Detenido: Amp restaurado';
  document.getElementById('trial').disabled=!this.ready;
 }
 return answer;
};
// Counter and diagnostic code from the prototype can generate many messages.
// Retain incoming values for REAPER but suppress per-event text in normal use.
const continuousObserve=SpiderBypassTrial.prototype.observe;
SpiderBypassTrial.prototype.observe=function(kind,b){
 const keep=this.log;
 this.log=()=>{};
 try{return continuousObserve.call(this,kind,b);}finally{this.log=keep;}
};
document.title='SpiderGateway';
document.querySelector('h1').textContent='SpiderGateway';
for(const p of document.querySelectorAll('p'))p.remove();
const info=document.createElement('p');
info.textContent='Gateway en REAPER, pista armada y script Continuo abierto. Spider Remote cerrado. Mantén esta pagina abierta y visible; al ocultarla se detiene y restaura. Usa Detener antes de cerrar.';
document.querySelector('h1').after(info);
const status=document.createElement('p');status.id='status';status.textContent='Preparado';info.after(status);
button('connect').textContent='Conectar';
button('trial').textContent='Iniciar NAM continuo';
button('restore').textContent='Detener y restaurar Amp';
button('disconnect').textContent='Restaurar y desconectar';
button('trial').onclick=async()=>{
 button('trial').disabled=true;button('restore').disabled=false;
 try{await trial.start(true);}catch(e){appLog('ERROR: '+e.message);if(!trial?.attempted)button('trial').disabled=!trial?.ready;}
};
button('restore').onclick=async()=>{try{await trial.finish();}catch(e){appLog('RESTAURACION NO CONFIRMADA: '+e.message);}};
const recovery=document.createElement('button');recovery.textContent='Recuperar Amp a1';
recovery.onclick=async()=>{
 if(!trial?.ready){appLog('Conecta primero.');return;}
 if(trial.attempted){await trial.finish().catch(e=>appLog(e.message));return;}
 if(!confirm('Recuperar el Amp: cambiar AmpEnable a1 y verificarlo?'))return;
 try{
  const value=await trial.read();
  if(value===1){appLog('AmpEnable ya esta en1.');return;}
  trial.original=1;trial.attempted=true;
  await trial.finish();
 }catch(e){appLog('Recuperacion no confirmada: '+e.message);}
};
button('disconnect').after(recovery);
const quit=document.createElement('button');quit.textContent='Restaurar y cerrar aplicacion';
quit.onclick=async()=>{
 try{
  if(trial){
   if(trial.ready&&!trial.attempted&&await trial.read()!==1){trial.original=1;trial.attempted=true;}
   await trial.close();
  }
  trial=null;link.pause=true;
  const response=await fetch('/shutdown',{method:'POST',headers:{'X-Spider-Token':localToken,'X-Spider-Client':continuousClient}});
  if(!response.ok)throw Error('No se pudo cerrar el servidor local');
  document.body.textContent='SpiderGateway cerrado. Puedes cerrar esta pestaña. La monitorizacion de REAPER queda apagada.';
 }catch(e){appLog('No cierres todavia: '+e.message);}
};recovery.after(quit);
button('disconnect').onclick=async()=>{
 try{
  if(trial){if(trial.ready&&!trial.attempted&&await trial.read()!==1){trial.original=1;trial.attempted=true;}await trial.close();}trial=null;link.pause=true;
  await fetch('/release',{method:'POST',headers:{'X-Spider-Token':localToken,'X-Spider-Client':continuousClient}});
  button('connect').disabled=false;button('trial').disabled=true;button('restore').disabled=true;
  status.textContent='Desconectado';appLog('Puertos MIDI cerrados.');
 }catch(e){appLog('No se confirmo desconexion/restauracion: '+e.message);}
};
document.getElementById('log').textContent='Preparado. Conectar solo lee. Iniciar activa el bypass hasta pulsar Detener.\n';
