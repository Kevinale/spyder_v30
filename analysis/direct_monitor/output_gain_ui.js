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
