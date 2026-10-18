#!/usr/bin/env python3
"""Reproduce hypothetical arithmetic budgets; no model inference or device access."""
import json
fs=48000
profiles=[]
for h in (8,16,32):
    i=1
    mac=4*h*(i+h)+h
    weights=4*h*(i+h)+4*h+h+1
    profiles.append({'kind':'hypothetical_1_layer_LSTM','input':i,'hidden':h,
                     'sample_rate':fs,'dense_mac_per_sample':mac,'dense_mac_per_second':fs*mac,
                     'weight_count_with_bias_and_mono_head':weights,'float32_weight_bytes':4*weights})
k,c,l=3,16,10
d=[2**i for i in range(l)]
profiles.append({'kind':'hypothetical_dense_causal_conv_stack','layers':l,'kernel':k,'channels':c,
                 'dilations':d,'dense_mac_per_sample':l*k*c*c,'dense_mac_per_second':fs*l*k*c*c,
                 'float32_conv_weight_bytes_excluding_bias':4*l*k*c*c,
                 'receptive_field_samples':1+sum((k-1)*x for x in d),
                 'float32_history_bytes_excluding_scratch':4*sum(c*(k-1)*x for x in d)})
print(json.dumps({'note':'Arithmetic examples, not NAM model classes or measured performance; activation and overhead costs excluded.',
                  'profiles':profiles,'block_duration_ms_at_48k':{n:1000*n/fs for n in (64,128,256)}},indent=2))
