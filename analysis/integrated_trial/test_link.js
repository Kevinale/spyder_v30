const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
const events=[],requests=[];
const context={console,DataView,Uint8Array,Number,document:{querySelector:()=>({textContent:''}),querySelectorAll:()=>[],getElementById:()=>({textContent:''})},setInterval:()=>0,setTimeout:f=>{queueMicrotask(f);return 0;},fetch:async(url,opts)=>{requests.push({url,...opts});events.push('post:'+opts.body.split(',')[1]);return{ok:true};}};
vm.createContext(context);
vm.runInContext(`
const U32=(b,o=0)=>(b[o]|b[o+1]<<8|b[o+2]<<16|b[o+3]<<24)>>>0;
const trialLog=()=>{};
class SpiderBypassTrial {
 constructor(){this.stage='idle';this.ids={Amp:42,Drive:38,Gain:37,Bass:33,Mid:35,Treble:36};this.attempted=false;}
 observe(){}
 async start(consent){if(!consent)throw Error('Consent');this.stage='active';this.attempted=true;}
 async finish(){this.stage='idle';this.attempted=false;globalThis.restored=true;}
 log(){}
}
let trial=new SpiderBypassTrial();
`,context);
vm.runInContext(fs.readFileSync(__dirname+'/link.js','utf8').replace('__LOCAL_TOKEN__','a'.repeat(32))+'\nglobalThis.api={trial,link,publishLink};',context);
const{api}=context;
(async()=>{
 await api.trial.start(true);assert.equal(requests[0].body.split(',')[1],'1');
 const le=n=>[n&255,n>>>8&255,n>>>16&255,n>>>24&255];
 for(const[p,v]of[[37,.75],[38,.25],[33,.2],[35,.3],[36,.4]]){
  const f=new Uint8Array(4);new DataView(f.buffer).setFloat32(0,v,true);
  api.trial.observe(4,[...le(42),...le(p),...le(4),...f]);
 }
 assert.equal(api.link.values[0],.25);assert(Math.abs(api.link.values[1]-.2)<1e-6);
 await api.publishLink();assert.equal(requests.at(-1).url,'/state');assert.equal(requests.at(-1).headers['X-Spider-Token'],'a'.repeat(32));
 await api.trial.finish();assert.equal(requests.at(-1).body.split(',')[1],'0');assert.equal(context.restored,true);
 const valid=api.link.values.slice();api.trial.stage='active';api.trial.observe(4,[...le(42),...le(0xffffffff),...le(4),0,0,0,63]);assert.deepEqual(api.link.values,valid);
 console.log('PASS: Gain37 and Drive38 map same input; local state authenticated; unknown ID ignored; OFF published before original restoration. No extra device commands implemented.');
})().catch(e=>{console.error(e);process.exitCode=1;});
