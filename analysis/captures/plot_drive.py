#!/usr/bin/env python3
"""Plot measured captured values, without inferring physical movement latency."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/spiderv-mpl-config')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/spiderv-plot-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path('/workspace/analysis/captures');events=json.loads((R/'drive_events.json').read_text())
fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained')
for direction,color,label in [('OUT','#3269b8','App → amplificador (813 cambios)'),('IN','#bc4e19','Amplificador → PC (140 cambios)')]:
 es=[e for e in events if e['direction']==direction]
 ax.plot([e['time_seconds'] for e in es],[e['value_float32'] for e in es],color=color,lw=1.4,marker='.',ms=3,label=label)
ax.axvspan(0,60.250494,color='#eeeeee',zorder=0)
ax.text(30,.50,'Sin tráfico MIDI\nregistrado',ha='center',va='center',color='#666666')
ax.axvline(60.250494,color='#999999',ls='--',lw=.9)
ax.annotate('Inicio de comunicación USB MIDI',xy=(60.25,.98),xytext=(47,1.14),fontsize=9,arrowprops={'arrowstyle':'-','color':'#888888'})
ax.set(xlim=(0,135),ylim=(0,1.2),xlabel='Segundos desde el primer paquete de la captura',ylabel='Valor Drive recibido (float32)',title='Spider V 30: Drive desde la app y desde el amplificador')
ax.set_yticks([0,.25,.5,.75,1]);ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
ax.legend(loc='lower left',bbox_to_anchor=(.02,1.02),frameon=False,fontsize=9,ncol=2)
fig.savefig(R/'drive_timeline.png',dpi=160)
fig.savefig(R/'drive_timeline.svg')
