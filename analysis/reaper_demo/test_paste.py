#!/usr/bin/env python3
"""Execute the real script under Lua 5.4 with a simulated REAPER host."""
import sys,json,csv
from pathlib import Path
sys.path.insert(0,'/workspace/analysis/tools/python')
from lupa.lua54 import LuaRuntime
ROOT=Path('/workspace/analysis/reaper_demo');source=(ROOT/'Spider_Gateway_Pegar.lua').read_text()
MOCK=r'''
clock=0; queued=nil; registered=nil; calls={}; messages={}; values={[0]=.5,[1]=.5,[2]=.5,[3]=.5,[4]=.5,[5]=.7}
initial={[0]=.5,[1]=.5,[2]=.5,[3]=.5,[4]=.5,[5]=.7}; closed=false; key=0
track={}; names={[0]="Bypass",[1]="Input",[2]="Threshold",[3]="Bass",[4]="Middle",[5]="Treble"}
record_arm=0;monitor=0;automation=0;global_automation=-1;playstate=1;formatter=true;actual_guid="GATEWAY-TEST"
reaper={}
function reaper.MB(s) messages[#messages+1]=s;return 0 end
function reaper.CountSelectedTracks()return 1 end
function reaper.GetSelectedTrack()return track end
function reaper.GetPlayState()return playstate end
function reaper.GetGlobalAutomationOverride()return global_automation end
function reaper.GetMediaTrackInfo_Value(_,k) if k=="I_RECARM"then return record_arm elseif k=="I_RECMON"then return monitor else return automation end end
function reaper.TrackFX_GetCount()return 1 end
function reaper.TrackFX_GetFXName()return true,"VST3: Gateway" end
function reaper.TrackFX_GetFXGUID()return actual_guid end
function reaper.ValidatePtr2()return true end
function reaper.TrackFX_GetNumParams()return 6 end
function reaper.TrackFX_GetParamName(_,_,p)return true,names[p] end
function reaper.TrackFX_GetParamNormalized(_,_,p)return values[p] end
function reaper.TrackFX_FormatParamValueNormalized(_,_,p,n) if formatter and p==1 then return true,string.format("%.3f",-36+72*n) else return false,"" end end
function reaper.TrackFX_SetParamNormalized(_,_,p,v) values[p]=v;calls[#calls+1]={p=p,v=v,t=clock};return true end
function reaper.get_action_context()return false,SCRIPT_PATH end
function reaper.ShowConsoleMsg(s) end
function reaper.GetUserInputs()return false,"" end
function reaper.atexit(f)registered=f end
function reaper.time_precise()return clock end
function reaper.defer(f)queued=f end
gfx={w=620,h=185,x=0,y=0}
local function noop()end
gfx.init=noop;gfx.set=noop;gfx.rect=noop;gfx.setfont=noop;gfx.drawstr=noop;gfx.update=noop
function gfx.quit()closed=true end
function gfx.getchar()return key end
'''
def run(name,setup='',stop_at=None,change=None):
 lua=LuaRuntime(unpack_returned_tuples=True);lua.globals().SCRIPT_PATH=str(ROOT/'Spider_Gateway_Demo.lua');lua.execute(MOCK);lua.execute(setup)
 lua.execute(source);g=lua.globals();steps=0
 while g.queued is not None:
  fun=g.queued;g.queued=None;g.clock=steps*.02;steps+=1
  if stop_at is not None and g.clock>=stop_at:g.key=27
  if change and g.clock>=change[0]:lua.execute(change[1]);change=None
  fun()
  assert steps<10000,'Runaway loop'
 if g.registered is not None:g.registered()
 calls=[dict(p=g.calls[i]['p'],v=g.calls[i]['v'],t=g.calls[i]['t'])for i in range(1,len(g.calls)+1)]
 messages=[g.messages[i]for i in range(1,len(g.messages)+1)]
 return lua,calls,messages
results=[]
lua,calls,msg=run('normal');g=lua.globals();assert not msg and g.closed
assert all(abs(g["values"][i]-g.initial[i])<1e-12 for i in range(6))
assert set(c['p']for c in calls)=={1,3,4,5},'Unexpected parameter changed'
assert len([c for c in calls if c['p']==1])>=50
assert all(-12.002<=-36+72*c['v']<=6.002 for c in calls if c['p']==1),'Input gain escaped bounds'
assert all(0<=c['v']<=1 for c in calls)
# EQ phases must actually traverse both endpoints, not merely be detected.
for p in (3,4,5):assert min(c['v']for c in calls if c['p']==p)<.1 and max(c['v']for c in calls if c['p']==p)>.9
results.append({'case':'normal playback, parameter selection, gain bounds and restoration','passed':True,'set_calls':len(calls)})
lua,calls,msg=run('cancel',stop_at=7);g=lua.globals();assert g.closed and calls and all(g["values"][i]==g.initial[i]for i in range(6))
results.append({'case':'Esc cancels mid-demo and restores','passed':True})
lua,calls,msg=run('no formatter','formatter=false');g=lua.globals();assert not msg and not any(c['p']==1 for c in calls) and g.closed
results.append({'case':'unsupported dB formatter omits Drive safely','passed':True})
for setting in ['record_arm=1','monitor=1','automation=3','global_automation=3','playstate=5']:
 lua,calls,msg=run('guard',setting);assert msg and not calls
 results.append({'case':'guard '+setting,'passed':True})
lua,calls,msg=run('recording starts during playback',change=(7,'playstate=5'));g=lua.globals();assert g.closed and all(g["values"][i]==g.initial[i]for i in range(6))
results.append({'case':'recording begins mid-demo: abort and restore','passed':True})
lua,calls,msg=run('FX replaced',change=(7,'actual_guid="DIFFERENT-FX"'));g=lua.globals();assert g.closed and max(c['t']for c in calls)<7
results.append({'case':'FX identity changed: stop without writing replacement FX','passed':True})
import re
samples=re.findall(r'\d+\.\d+',source.split('local datos={',1)[1].split('\n}',1)[0]);assert len(samples)==40
report={'runtime':'Lua 5.4 via lupa; simulated REAPER API, not real Gateway','cases':results,'captured_sample_points':len(samples),
 'live_reaper_validation':False,'usb_access':False,'all_passed':True}
(ROOT/'validation_paste.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
