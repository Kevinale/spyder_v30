const log=s=>{document.getElementById('log').textContent+=s+'\n';};
let reader=null;
async function connect(){
 document.getElementById('connect').disabled=true;
 try{reader=new SpiderReadOnly(log);await reader.connect();document.getElementById('read').disabled=false;}
 catch(e){log('ERROR: '+e.message);if(reader)await reader.close().catch(()=>{});reader=null;document.getElementById('connect').disabled=false;}
}
async function read(){document.getElementById('read').disabled=true;try{await reader.read();}catch(e){log('ERROR: '+e.message);}finally{document.getElementById('read').disabled=!reader?.ready;}}
async function disconnect(){if(reader)await reader.close().catch(e=>log(e.message));reader=null;document.getElementById('read').disabled=true;document.getElementById('connect').disabled=false;log('Puertos MIDI cerrados.');}
document.getElementById('connect').onclick=connect;
document.getElementById('read').onclick=read;
document.getElementById('disconnect').onclick=disconnect;
window.addEventListener('pagehide',()=>reader?.close());
