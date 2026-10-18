#!/usr/bin/env python3
"""Publish the observed controls map and plot; does not access USB or send MIDI."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/spiderv-mpl-config')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/spiderv-plot-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path('/workspace/analysis/captures_tone');root=R.parent
s=json.loads((R/'controls_summary.json').read_text());drive=json.loads((root/'captures/drive_summary.json').read_text())
controls=[{'group':'Amp','group_index':42,'parameter':'Drive','parameter_index':38,'type':4,'encoding':'float32LE',
 'observed_min':drive['directions']['IN']['min'],'observed_max':drive['directions']['IN']['max'],'incoming_events':140,
 'capture_sha256':'101c25061d62c511b61a8635903da0b277a4379d918fde3e5f5a6167cea4c536'}]
for c in s['controls']:
 controls.append({'group':c['group'],'group_index':c['group_index'],'parameter':c['parameter'],'parameter_index':c['parameter_index'],
 'type':4,'encoding':'float32LE','observed_min':c['min'],'observed_max':c['max'],'incoming_events':c['count'],'capture_sha256':s['input_sha256']})
(root/'CONTROLS_MAP.json').write_text(json.dumps({'scope':'Observed telemetry while Remote was already in session; not a live NAM bridge.',
 'protocol':'Parker SysEx via USB MIDI','notification_opcode':4,'parameter_layout':'group_index:uint32LE, parameter_index:uint32LE, type:uint32LE, float32LE',
 'symbol_source':'captures/device_symbols.json from first capture; second capture did not include a new symbol table.',
 'warning':'Resolve current session symbols before assuming these indices on another firmware/model. These controls are not automatically internal parameters of a NAM model.',
 'controls':controls},indent=2)+'\n')
events=json.loads((R/'control_events.json').read_text())
fig,axs=plt.subplots(3,1,figsize=(10,6),sharex=True,layout='constrained')
for ax,name,col in zip(axs,['Bass','Mid','Treble'],['#3269b8','#18805f','#ad4a20']):
 es=[e for e in events if e['parameter']==name]
 ax.plot([e['time_seconds'] for e in es],[e['value'] for e in es],color=col,lw=1,marker='.',ms=2.5)
 ax.set(ylim=(-.05,1.05),ylabel=name);ax.set_yticks([0,.5,1]);ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
 ax.text(.01,.85,f'{len(es)} notificaciones IN',transform=ax.transAxes,fontsize=9)
axs[-1].set(xlim=(0,175),xlabel='Segundos desde el primer paquete de la captura')
fig.suptitle('Spider V 30: controles físicos recibidos por USB — valores float32')
fig.savefig(R/'tone_timeline.png',dpi=160);fig.savefig(R/'tone_timeline.svg')
