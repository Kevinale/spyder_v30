'use strict';
const assert=require('node:assert/strict'),fs=require('fs');
const{SpiderBypassTrial}=require('./bypass_trial.js');const{LE}=require('./reader.js');
function make({noamp=false,ignoreZero=false,rejectZero=false,failRestore=false}={}){
 const logs=[],r=new SpiderBypassTrial(s=>logs.push(s));r.ready=true;r.ids={Amp:42,Bypass:239,GuitarProc:884,AmpEnable:835,Drive:38,Bass:33,Mid:35,Treble:36};
 let value=1;const writes=[];r.getModel=async()=>noamp?239:124;r.read=async()=>value;
 r.write=async v=>{writes.push(v);if(v===0&&rejectZero)throw Error('rejected');if(v===1&&failRestore)throw Error('lost transport');if(!(v===0&&ignoreZero))value=v;};
 return{r,writes,logs,value:()=>value};
}
(async()=>{
 const results=[];let x=make();await assert.rejects(()=>x.r.start(false),/explicita/);assert.deepEqual(x.writes,[]);results.push('No active test without explicit action.');
 x=make({noamp:true});await assert.rejects(()=>x.r.start(true),/No Amp/);assert.deepEqual(x.writes,[]);results.push('No Amp model refused before any write.');
 x=make();await x.r.start(true);assert.equal(x.value(),0);assert.equal(x.r.stage,'active');
 for(const p of[38,33,35,36])x.r.observe(4,[...LE(42),...LE(p),...LE(4),...LE(0)]);
 assert.deepEqual(x.r.counts,{Drive:1,Bass:1,Mid:1,Treble:1});await x.r.finish();assert.equal(x.value(),1);assert.deepEqual(x.writes,[0,1]);results.push('Snapshot1 -> set0/readback -> same model -> four physical IDs -> restore1/readback.');
 x=make();await x.r.start(true);await x.r.close();assert.deepEqual(x.writes,[0,1]);results.push('Normal close restores before releasing ports.');
 x=make({ignoreZero:true});await assert.rejects(()=>x.r.start(true),/distinta/);assert.deepEqual(x.writes,[0,1]);results.push('Ignored zero is detected and restoration attempted.');
 x=make({rejectZero:true});await assert.rejects(()=>x.r.start(true),/rejected/);assert.deepEqual(x.writes,[0,1]);results.push('Rejected or uncertain write still triggers restore attempt.');
 x=make({failRestore:true});await x.r.start(true);await assert.rejects(()=>x.r.finish(),/lost transport/);assert.equal(x.r.stage,'restore_failed');assert.equal(x.r.attempted,true);results.push('Restore failure is retained/reported, never labelled restored.');
 // Exercise actual outbound gate before a transport can be touched.
 const r=new SpiderBypassTrial();r.ready=true;r.ids={Amp:42,GuitarProc:884,AmpEnable:835};r.original=1;r.output={send(){throw Error('must not send');}};
 assert.throws(()=>r.experimental(10,[...LE(884),...LE(835),...LE(3),...LE(0)]),/bloqueada/);
 r.stage='applying';assert.throws(()=>r.experimental(10,[...LE(884),...LE(33),...LE(3),...LE(0)]),/bloqueada/);
 r.stage='restoring';assert.throws(()=>r.experimental(10,[...LE(884),...LE(835),...LE(3),...LE(0)]),/bloqueada/);
 results.push('Transport gate rejects idle writes, other parameters and zero during restoration.');
 fs.writeFileSync(__dirname+'/trial_validation.json',JSON.stringify({passed:results,actual_device_writes:'NONE in cloud; user authorized the manual Windows trial, device execution pending',timeout_restore_browser_limits:'Browser suspension/tab close/USB loss can prevent a timed restore. Keep page visible and use explicit Restore before closing.'},null,2)+'\n');for(const s of results)console.log('PASS:',s);
})().catch(e=>{console.error(e);process.exitCode=1;});
