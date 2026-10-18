const vm=require('vm'),fs=require('fs'),assert=require('node:assert/strict');
let timerId=0;const timers=new Map();const ctx={console,Uint8Array,DataView,TextDecoder,setTimeout:(f,t)=>{timers.set(++timerId,{f,t});return timerId;},clearTimeout:id=>timers.delete(id),document:{getElementById:()=>({textContent:'',hidden:false})}};vm.createContext(ctx);
vm.runInContext(['../amp_enable_reader/reader.js','routing_reader.js','output_gain_trial.js'].map(f=>fs.readFileSync(__dirname+'/'+f,'utf8')).join('\n')+'\nglobalThis.Trial=SpiderOutputGainTrial;globalThis.unpackFn=unpack;globalThis.U=U32;globalThis.L=LE;',ctx);
const L=ctx.L,U=ctx.U;
function device(options={}){
 const t=new ctx.Trial(()=>{});let gain=options.initial??0x3f800000;const sent=[];
 t.ready=true;t.ids={GuitarProc:884,AmpEnable:835,GuitProcOutputGain:899,USBOutLevel:900,USBInLevel:901};
 t.output={send(packet){const raw=ctx.unpackFn(packet.slice(12,-1)),op=U(raw),g=U(raw,8),p=U(raw,12);sent.push({op,g,p,raw});assert.equal(g,0xffffffff);assert.equal(p,899);let reply;
 if(op===10){assert.equal(U(raw,16),4);const v=U(raw,20);if(options.rejectRestore&&v===0x3f800000)reply=L(0xffffffff);else{if(!options.ignoreZero||v!==0)gain=v;reply=L(0);}}
 else {assert.equal(op,9);reply=[...L(0),...L(4),...L(gain)];}
 queueMicrotask(()=>{const pending=t.pending;t.pending=null;pending.resolve(reply);});
 }};return {t,sent,get gain(){return gain;}};
}
(async()=>{
 let d=device();await assert.rejects(()=>d.t.start(false));assert.equal(d.sent.length,0);
 d=device({initial:0x3f000000});await assert.rejects(()=>d.t.start(true));assert(d.sent.every(x=>x.op===9));
 d=device();await d.t.start(true);assert.equal(d.gain,0);assert.equal(d.t.stage,'active');assert([...timers.values()].some(x=>x.t===15000));await d.t.finish();assert.equal(d.gain,0x3f800000);assert.equal(d.t.attempted,false);
 d=device({ignoreZero:true});await assert.rejects(()=>d.t.start(true));assert.equal(d.gain,0x3f800000);assert.equal(d.t.attempted,false);
 d=device({rejectRestore:true});await d.t.start(true);await assert.rejects(()=>d.t.finish());assert.equal(d.t.attempted,true);assert.equal(d.t.stage,'restore_failed');
 d=device();await assert.rejects(()=>d.t.writeGainWord(0));d.t.stage='applying';await assert.rejects(()=>d.t.writeGainWord(0x40000000));
 console.log('PASS: no write without explicit consent; initial1 required; only global899 float0/1; readback;15s timer; restore on ignored0; failed restoration retained. Mock only.');
})().catch(e=>{console.error(e);process.exitCode=1;});
