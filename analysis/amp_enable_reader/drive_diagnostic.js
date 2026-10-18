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
