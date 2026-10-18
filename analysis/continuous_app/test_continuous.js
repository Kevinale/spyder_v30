const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const elements=new Map(),requests=[],events=[],timers=new Map();let timerId=0;
const element=id=>{if(!elements.has(id))elements.set(id,{textContent:'',disabled:false,after(){},remove(){}});return elements.get(id);};
const ctx={console,crypto:{randomUUID:()=> 'client-test'},document:{getElementById:element,querySelector:element,querySelectorAll:()=>[],createElement:()=>element('created'+elements.size)},confirm:()=>true,setInterval:()=>0,setTimeout:(f,t)=>{if(t===20000){timers.set(++timerId,f);return timerId;}queueMicrotask(f);return 0;},clearTimeout:id=>timers.delete(id),fetch:async(url,opts)=>{requests.push({url,...opts});events.push(url);return {ok:true};},Uint8Array,DataView};vm.createContext(ctx);
vm.runInContext(`
let trialLog=()=>{};const button=id=>document.getElementById(id);
const U32=(b,o=0)=>(b[o]|b[o+1]<<8|b[o+2]<<16|b[o+3]<<24)>>>0;
class SpiderBypassTrial{
 constructor(){this.ready=true;this.stage='idle';this.attempted=false;this.log=s=>trialLog(s);this.ids={Amp:42,Gain:37,Drive:38,Bass:33,Mid:35,Treble:36};}
 observe(){}
 async start(consent){if(!consent)throw Error('Consent');this.stage='active';this.attempted=true;this.timer=setTimeout(()=>this.finish(),20000);}
 async finish(){this.stage='idle';this.attempted=false;globalThis.wasRestored=true;}
 async read(){return this.attempted?0:1;}
 async close(){if(this.attempted)await this.finish();this.ready=false;}
}
let trial=new SpiderBypassTrial();`,ctx);
const link=fs.readFileSync(__dirname+'/../integrated_trial/link.js','utf8').replace("'X-Spider-Token':localToken","'X-Spider-Token':localToken,'X-Spider-Client':continuousClient");
vm.runInContext(link+'\n'+fs.readFileSync(__dirname+'/continuous.js','utf8')+'\nglobalThis.api={trial,link,publishLink};',ctx);
(async()=>{
 await ctx.api.trial.start(true);assert.equal(timers.size,0,'20s timeout removed');assert.equal(ctx.api.trial.stage,'active');assert.equal(requests.at(-1).headers['X-Spider-Client'],'client-test');
 const le=n=>[n&255,n>>>8&255,n>>>16&255,n>>>24&255];
 for(const[p,v]of [[37,.8],[33,.2],[35,.3],[36,.4]]){const f=new Uint8Array(4);new DataView(f.buffer).setFloat32(0,v,true);ctx.api.trial.observe(4,[...le(42),...le(p),...le(4),...f]);}
 assert(ctx.api.link.values.every(v=>v>=0));await ctx.api.trial.finish();assert.equal(requests.at(-1).body.split(',')[1],'0');assert.equal(ctx.wasRestored,true);assert.equal(ctx.api.trial.stage,'idle');
 await ctx.api.trial.start(true);assert.equal(timers.size,0);await element('disconnect').onclick();assert.equal(requests.at(-1).url,'/release');assert.equal(ctx.api.trial.ready,false);
 console.log('PASS: continuous timer removed, four knob mapping retained, per-page lease header, OFF then restore, restart and disconnect. Mock device only.');
})().catch(e=>{console.error(e);process.exitCode=1;});
