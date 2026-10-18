'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {SpiderReadOnly,CRC,LE,U32}=require('./reader.js');
const fixture=JSON.parse(fs.readFileSync(__dirname+'/test_fixture.json','utf8'));
const table=[...Buffer.from(fixture.table,'hex')];
function encodeInbound(body,kind=1,seq=0){
 const message=[...LE(kind),...LE(body.length),...body],packets=[];
 for(let start=0;start<message.length;start+=256){
  const frag=message.slice(start,start+256),end=start+frag.length-1;
  const s=[240,0,1,12,34,0,77,0,seq,(end>>8)&127,(end>>4)&15,end&15];
  for(let i=0;i<frag.length;i+=7){let mask=0,a=[];for(let j=0;j<7;j++){const v=frag[i+j]||0;mask|=(v>>7)<<(6-j);a.push(v&127);}s.push(mask,...a);}
  packets.push([...s,247]);
 }
 return packets;
}
function decodeOutbound(s){
 const raw=[];for(let i=12;i<s.length-1;i+=8)for(let j=1;j<8&&i+j<s.length-1;j++)raw.push(s[i+j]|((s[i]>>(7-j)&1)<<7));
 return{op:U32(raw),body:raw.slice(8,8+U32(raw,4))};
}
const results=[];
const parser=new SpiderReadOnly(),actual=[];parser.onmessage=(kind,body)=>actual.push({kind,body:Buffer.from(body).toString('hex')});
for(const hex of fixture.sysex_in)parser.feed(Buffer.from(hex,'hex'));
assert.deepEqual(actual,fixture.messages_in_ch0);
results.push('Actual capture: every IN/channel0 reply and notification reassembled byte-for-byte, including fragmented 22175-byte symbol table.');
const ids=parser.parseSymbols(table);assert.equal(ids.AmpEnable,835);assert.equal(ids.GuitarProc,884);assert.equal(ids.AmpEnableState,821);
results.push('All 916 symbol entry CRCs validated; IDs match the device capture.');
const damaged=table.slice();damaged[damaged.length-2]^=1;assert.throws(()=>parser.parseSymbols(damaged),/CRC/);
results.push('Damaged symbol table rejected.');
const blocked=new SpiderReadOnly();blocked.output={send(){throw Error('Should never send');}};
for(const op of[8,10,12,13,18,19,22])assert.throws(()=>blocked.request(op,Array(16).fill(0)),/bloqueada/);
assert.throws(()=>blocked.request(9,[...LE(884),...LE(835)]),/bloqueada/);
results.push('Model/preset/parameter setters and query before verified session blocked before transport.');
async function session({value=1,type=3,status=0,version=0x02050030}={}){
 const log=[],r=new SpiderReadOnly(s=>log.push(s));let seq=0;const sent=[];
 const input={name:'Spider V',open:async()=>{},close:async()=>{},onmidimessage:null};
 const output={name:'Spider V',open:async()=>{},close:async()=>{},send(s){
  if(s.join(',')==='240,126,127,6,1,247'){sent.push('identity');queueMicrotask(()=>input.onmidimessage({data:[240,126,127,6,2,0,1,12,34,0,0,0,48,0,5,2,247]}));return;}
  const m=decodeOutbound(s);sent.push(m);
  let body;
  if(m.op===1)body=LE(version);
  else if(m.op===2)body=LE(table.length);
  else if(m.op===3)body=table;
  else if(m.op===4){assert.equal(U32(m.body),CRC(table));body=LE(0);}
  else if(m.op===9){assert.deepEqual(m.body,[...LE(884),...LE(835)]);body=[...LE(status),...LE(type),...LE(value)];}
  else throw Error('Unexpected opcode '+m.op);
  queueMicrotask(()=>{for(const p of encodeInbound(body,1,seq++))input.onmidimessage({data:p});});
 }};
 Object.defineProperty(globalThis,'navigator',{configurable:true,value:{requestMIDIAccess:async options=>{assert.deepEqual(options,{sysex:true});return{inputs:new Map([[0,input]]),outputs:new Map([[0,output]])};}}});
 let error=null,answer=null;try{answer=await r.connect();}catch(e){error=e;}
 await r.close();assert.equal(input.onmidimessage,null);assert.equal(r.output,null);
 return{sent,log,error,answer};
}
(async()=>{
 for(const value of[0,1]){const x=await session({value});assert.equal(x.error,null);assert.equal(x.answer,value);assert.deepEqual(x.sent.slice(1).map(m=>m.op),[1,2,3,4,9]);}
 results.push('Mock sessions read boolean0 and1 using only identity / GET1,2,3 / handshake4 / GET9; disconnect releases ports.');
 let x=await session({status:-7});assert.match(x.error.message,/estado -7/);
 x=await session({type:4});assert.match(x.error.message,/tipo\/valor inesperado/);
 results.push('Negative device status and unexpected float type rejected.');
 x=await session({version:0x02020000});assert.match(x.error.message,/Version distinta/);assert.deepEqual(x.sent.slice(1).map(m=>m.op),[1]);
 results.push('Other firmware version stops before table/handshake/parameter query.');
 fs.writeFileSync(__dirname+'/validation.json',JSON.stringify({passed:results,real_windows_device_test:'PENDING',browser_midi_permission:'PENDING'},null,2)+'\n');
 for(const s of results)console.log('PASS:',s);
})().catch(e=>{console.error(e);process.exitCode=1;});
