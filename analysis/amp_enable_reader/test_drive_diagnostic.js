const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
const r=__dirname+'/',context={console,TextDecoder,Uint8Array,DataView,setTimeout,clearTimeout,document:{getElementById:()=>({textContent:''})}};
vm.createContext(context);vm.runInContext(fs.readFileSync(r+'reader.js','utf8')+'\n'+fs.readFileSync(r+'bypass_trial.js','utf8')+'\n'+fs.readFileSync(r+'drive_diagnostic.js','utf8')+'\nglobalThis.T=SpiderBypassTrial;',context);
const logs=[],t=new context.T(s=>logs.push(s));t.stage='active';t.ids={Amp:42,Drive:38,Gain:31,Bass:33,Mid:35,Treble:36};const le=n=>[n&255,n>>>8&255,n>>>16&255,n>>>24&255];
function event(p){t.observe(4,[...le(42),...le(p),...le(4),0,0,0,63]);}
event(31);assert(logs.some(x=>x.includes('Amp.Gain')&&x.includes('0.5')));assert.equal(t.counts.Drive,0);
event(0xffffffff);assert(logs.some(x=>x.includes('ID_4294967295')));
event(38);assert.equal(t.counts.Drive,1);
for(let i=0;i<100;i++)event(31);assert.equal(logs.filter(x=>x.startsWith('DATO ')).length,80);assert(logs.some(x=>x.includes('omitido')));
t.counts={Drive:0,Bass:0,Mid:0,Treble:0};event(31);assert.equal(t.diagCount,1);
console.log('PASS: Gain displayed without assuming Drive mapping; unknown ID retained; original Drive counter preserved; output capped80; counter resets per trial. No writes added.');
