document.title='Spider: prueba temporal';
document.querySelector('h1').textContent='Spider: prueba de bypass20 segundos';
for(const p of document.querySelectorAll('p'))p.remove();
const instructions=document.createElement('p');instructions.textContent='Amp distorsionado, No Cabinet y efectos apagados; Remote y REAPER cerrados. Conectar solo lee. La prueba cambia AmpEnable temporalmente. Manten esta pagina visible y restaura antes de cerrar.';document.querySelector('h1').after(instructions);
document.getElementById('read').hidden=true;
for(const [id,text]of [['trial','Probar bypass20 segundos'],['restore','Restaurar ahora']]){const b=document.createElement('button');b.id=id;b.textContent=text;b.disabled=true;document.getElementById('disconnect').before(b);}
document.getElementById('log').textContent='Prueba preparada. Conectar solo lee; Probar bypass requiere confirmacion.\n';
const trialLog=s=>{document.getElementById('log').textContent+=s+'\n';};
let trial=null;
const button=id=>document.getElementById(id);
button('connect').onclick=async()=>{button('connect').disabled=true;try{trial=new SpiderBypassTrial(trialLog);await trial.connect();button('trial').disabled=false;}catch(e){trialLog('ERROR: '+e.message);if(trial)await trial.close().catch(()=>{});trial=null;button('connect').disabled=false;}};
button('trial').onclick=async()=>{
 if(!confirm('Prueba activa: cambiar AmpEnable de1 a0 durante20 segundos y restaurar1. No cambia modelo ni guarda preset. Mantene esta pagina visible y usa Restaurar antes de cerrarla. Continuar?'))return;
 button('trial').disabled=true;button('restore').disabled=false;
 try{await trial.start(true);}catch(e){trialLog('ERROR: '+e.message);}
};
button('restore').onclick=async()=>{try{await trial.finish();button('trial').disabled=false;}catch(e){trialLog('RESTAURACION NO CONFIRMADA: '+e.message);}};
button('disconnect').onclick=async()=>{try{if(trial)await trial.close();trial=null;button('trial').disabled=true;button('restore').disabled=true;button('connect').disabled=false;trialLog('Puertos cerrados.');}catch(e){trialLog('No cierres todavia: '+e.message);}};
window.addEventListener('beforeunload',e=>{if(trial?.attempted){e.preventDefault();e.returnValue='';}});
// Timers can be throttled in background. Restore as soon as the tab is hidden,
// but never claim this guarantees restoration on browser/USB/process failure.
document.addEventListener('visibilitychange',()=>{if(document.hidden&&trial?.attempted)trial.finish().catch(e=>trialLog('RESTAURACION NO CONFIRMADA: '+e.message));});
