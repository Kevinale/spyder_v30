#!/usr/bin/env python3
"""Validate the Parker @enabled translation slice; does not talk to hardware."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
a=json.loads((root/'captures_noamp/parker_special_mapping.json').read_text())
# FUN_10084570 chooses iVar4=0, local_c=10 inclusive for Parker @enabled.
slice_=a[0:11]
assert len(slice_)==11 and all(x['application_parameter']=='@enabled'for x in slice_)
by_group={x['application_group']:x['firmware_name']for x in slice_}
assert by_group['cab']=='CabEnable' and by_group['fx1']=='FX1Enable'
assert 'amp' not in by_group
native=(root/'dry_input/enable_dispatch.txt').read_text()
assert 'if (*param_3 == 0x40)' in native and 'FUN_10084570' in native
result={'range_inclusive':[0,10],'mapping':by_group,'amp_mapping':None,'meaning':'This examined client translation does not resolve amp/@enabled. It is not proof that no undocumented firmware bypass exists.','source':'captures_noamp/native_reserved.txt FUN_10084570; dry_input/enable_dispatch.txt FUN_10083c50'}
(root/'dry_input/enable_mapping_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 11 Parker @enabled mappings; cab/effects resolve; amp does not.')
