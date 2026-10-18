const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const sent=[],nodes={};let tid=0;
const context={console,Uint8Array,DataView,TextDecoder,setTimeout:()=>++tid,clearTimeout:()=>{},document:{getElementById:id=>nodes[id]??=( {textContent:'',disabled:false,hidden:false})}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(__dirname+'/../amp_enable_reader/reader.js','utf8')+'\n'+fs.readFileSync(__dirname+'/routing_reader.js','utf8')+'\nglobalThis.Reader=SpiderRoutingReader;globalThis.le=LE;globalThis.u=U32;globalThis.unpack=unpack;',context);
const r=new context.Reader(()=>{});r.ids={GuitarProc:884,AmpEnable:835,GuitProcOutputGain:899,USBOutLevel:900,USBInLevel:901};r.ready=true;r.output={send:packet=>sent.push(packet)};
const le=context.le;
(async()=>{
 for(const op of [5,6,7,8,10,11,12,99])assert.throws(()=>r.request(op,[]));
 for(const[g,p]of [[42,899],[884,33],[0xffffffff,37]])assert.throws(()=>r.request(9,[...le(g),...le(p)]));
 for(const p of [899,900,901])for(const g of [0xffffffff,884]){
  const promise=r.request(9,[...le(g),...le(p)]);
  const raw=context.unpack(sent.at(-1).slice(12,-1));assert.equal(context.u(raw),9);assert.equal(context.u(raw,4),8);assert.equal(context.u(raw,8),g);assert.equal(context.u(raw,12),p);
  assert.throws(()=>r.request(9,[...le(g),...le(p)]));
  const q=r.pending;r.pending=null;q.resolve([255,255,255,255]);await promise;
 }
 const logs=[];r.log=s=>logs.push(s);let n=0;
 r.request=async()=>{n++;return n===1?[255,255,255,255]:[0,0,0,0,4,0,0,0,0,0,0,63];};
 await r.inspectRouting();assert.equal(n,6);assert(logs.some(s=>s.includes('estado=-1')));assert(logs.some(s=>s.includes('valor=0.5')));assert(logs.at(-1).startsWith('FIN'));
 console.log('PASS: six bounded group/parameter hypotheses, op9 only, setters rejected, sequential requests, negative status and float/raw reporting. No real device.');
})().catch(e=>{console.error(e);process.exitCode=1;});
