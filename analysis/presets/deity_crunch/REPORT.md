# Deity Crunch SVL6P — static analysis, 2026-10-17

Original: 1670 bytes, SHA-256 `fdbbfdc376bdfda3fd6e507a284e61b1455a5bb0a3cf892e4bc9dc7fe5e7baa0`. Entire input parses as UTF-8 JSON, schema `L6Preset`, version 5. No import, target connection or execution performed. Original hash verified unchanged.

`data.meta.name`: Deity Crunch. `data.tone` contains named effect/model references and scalar parameters, not an executable, neural network weights/architecture, impulse response samples or downloadable DSP algorithm.

## Cross-check against installed Remote resources

- `data.tone.amp.@model = BomberXTC`: Remote `amps.models.json` identifies 2002 Bomber X-TC, catalog ID 131120. Gain 0.68, Bass 0.63, Mid 0.35, Treble 1, Presence 0.74, volume 0.3710801. These are stored scalar values, not measured knob behavior.
- `data.tone.cab.@model = 4x12BritV30Studio`: existing 4x12 Brit V30, catalog ID 16908309; mic selector 1, Level 0. Level is the catalog's Early Reflections control, not a claim of muted output.
- `data.tone.fx1.@model = ClassicDistortion`: existing Classic Distortion, catalog ID 33882117; `@enabled=false`, so the stored stomp block is disabled. Gain 0.43, Drive 0.68, Tone 0.5.
- Other blocks refer to Gate, MediumHall, L6SineChorus, L6DigitalDelay, SharcPodFixedComp, ParaGraphic4_band, VolumePedal and Weeper. Their model names do not identify the physical CPU. Several @enabled flags are false.

Device metadata is `0x220004`, while owner live V30 identity is `0x220000`; importing compatibility was not tested and no device model is inferred from this metadata alone. `device_version` is stored as `0x01040000`, not a statement that the owner's current firmware changed.

## Conclusion

High confidence for this sample: downloading this tone transfers a recipe selecting already catalogued models and values. It does not install a new distortion implementation. Substituting an unknown @model or embedding NAM weights would require firmware support for that model/engine, which has not been demonstrated. Renaming or converting NAM to this JSON schema cannot supply missing DSP execution support.

The preset remains useful as a reference tone for recreating or comparing an internal Spider sound to external NAM. This observation is limited to the supplied sample and does not establish that all Line 6 products or every schema version forbid additional resources.

Evidence: `preset.pretty.json`, `analysis.json`, `analyze.py`, and installed Remote `amps.models.json`, `stomps.models.json`, `cabs.models.json` under `/workspace/analysis/remote/resources`.
