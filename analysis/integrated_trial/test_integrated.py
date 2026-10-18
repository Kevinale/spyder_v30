"""Run real integrated Lua with a simulated REAPER host and a real temp state file."""
from pathlib import Path
import sys,ast,json
sys.path.insert(0,'/workspace/analysis/tools/python')
from lupa.lua54 import LuaRuntime
R=Path('/workspace/analysis');HERE=R/'integrated_trial';file=Path('/tmp/spider-integrated-test.txt');token='a'*32
module=ast.parse((R/'reaper_demo/test_paste.py').read_text());mock=next(ast.literal_eval(n.value)for n in module.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='MOCK'for t in n.targets))
extra='''record_arm=1;mon_calls={};function reaper.TrackFX_GetEnabled()return true end
function reaper.SetMediaTrackInfo_Value(_,k,v) if k=="I_RECMON"then monitor=v;mon_calls[#mon_calls+1]=v end end
'''
source='\n'.join('local path="/tmp/spider-integrated-test.txt"'if l.startswith('local path=')else l for l in(HERE/'Spider_Gateway_Integrado.lua').read_text().splitlines())
def write(seq,active,*values,session=token):file.write_text(','.join(map(str,[session,seq,active,*values]))+'\n')
def run_start():
 lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(mock);lua.execute(extra);lua.execute(source);return lua,lua.globals()
def tick(g,clock):g.clock=clock;fn=g.queued;g.queued=None;assert fn;fn()
write(1,1,1,.2,.3,.4);lua,g=run_start();assert g.monitor==0 and not len(g.calls),'History should not enable monitor or replay values'
write(2,1,1,.2,.3,.4);tick(g,.1);assert g.monitor==1 and len(g.calls)==4
assert set(g.calls[i]['p']for i in range(1,5))=={1,3,4,5};assert abs((-36+72*g['values'][1])-6)<.003
# Heartbeat expires; unchanged last state must not remain live.
tick(g,1.7);assert g.monitor==0
for p in [1,3,4,5]:assert abs(g['values'][p]-g.initial[p])<1e-12
write(3,1,0,.8,.7,.6);tick(g,1.8);assert g.monitor==1;assert abs((-36+72*g['values'][1])+12)<.003
write(4,0,0,.8,.7,.6);tick(g,1.9);assert g.monitor==0
for p in[1,3,4,5]:assert abs(g['values'][p]-g.initial[p])<1e-12
write(5,1,.5,.5,.5,.5);tick(g,2);assert g.monitor==1
g.key=27;tick(g,2.1);assert g.closed and g.monitor==0
# A different page session cannot take over a running FX bridge.
write(1,0,-1,-1,-1,-1);lua,g=run_start();write(2,1,.1,.2,.3,.4,session='b'*32);tick(g,.1);assert g.closed and g.monitor==0
# Malformed values cannot control the plugin.
write(1,0,-1,-1,-1,-1);lua,g=run_start();write(2,1,99,.2,.3,.4);tick(g,.1);assert not len(g.calls)and g.monitor==0
g.key=27;tick(g,.2)
result={'passed':['old state not replayed','four controls reach actual Gateway parameter host calls','Input bounded-12..+6dB','heartbeat stale>1.5s disables monitor and restores FX','OFF disables monitor and restores FX','Escape disables monitor and restores FX','session change stops bridge','out-of-range state rejected'],'real_windows_reaper_browser_test':'PENDING'}
(HERE/'lua_validation.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS:', '; '.join(result['passed']))
