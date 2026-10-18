# Comparable public projects — consulted 2026-10-17

Scope: GitHub repository search and project README review, not independent hardware reproduction or exhaustive Internet search. Source claims below are attributed to their authors. No third-party program or target firmware executed.

- GuitarML/Mercury: https://github.com/GuitarML/Mercury . README states real NAM inference via RTNeural-NAM on Daisy Seed/Funbox, nine custom-size models, mono processing, four-band EQ, no cabinet modelling. Designed for a programmable platform, not a replacement firmware for Spider or BF707. Valuable concrete embedded NAM precedent; cannot transfer clock budgets between CPUs. Local README Mercury.md.
- oyama/pico-neural-amp-modeler-demo: https://github.com/oyama/pico-neural-amp-modeler-demo . Author documents NAM A2-Lite with dual-core RP2350 at 300 MHz, USB loopback, one embedded model. README explicitly distinguishes demo from product and says analog codec hardware is outside scope. Claimed performance not independently reproduced. Does not demonstrate default-clock performance, arbitrary NAM models or BF707 support. Local README pico-nam.md.
- Jmainguy/line6-tt: https://github.com/Jmainguy/line6-tt . Public USB/firmware research for AMPLIFi TT, already locally inspected. Different device and internal architecture; no reviewed evidence of NAM executing on Spider's DSP.
- GuitarML/NeuralPi: https://github.com/GuitarML/NeuralPi . Neural modelling on Raspberry Pi 4/Elk, using GuitarML models; do not label it the NAM file-format engine merely because it uses neural networks.
- mikeoliphant/neural-amp-modeler-lv2: https://github.com/mikeoliphant/neural-amp-modeler-lv2 . README states NAM model support through NeuralAudio engine; Linux plugin workflow, not Spider firmware.

Searches for repositories mentioning Spider V with NAM/firmware and Blackfin with NAM returned zero in these specific repository metadata queries. This does not establish absence of forum posts, unpublished work, differently named projects or private results. No verified exact Spider V30 NAM internal port was found in the reviewed sources. Evidence: search.json and downloaded README files.

Implication: embedded NAM is demonstrably the subject of concrete implemented public projects, with model-size and hardware constraints. These precedents justify a BF707 feasibility investigation, not a claim that the Spider can host them unchanged. The unresolved loader and DSP resource measurements remain prerequisites.
