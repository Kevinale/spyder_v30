# Payload structure follow-up, 2026-10-17

Scope: static local files only. No installer, firmware or third-party target code execution. No device connection or memory writes.

## Periodic XOR hypothesis

`periodic_probe.py` infers one candidate repeating XOR mask per period from the most frequent byte at each phase in the larger 2.02 payload, assuming zero padding is common in the unknown plaintext. Periods: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024. The exact same inferred mask and phase are tested against both releases. This assumption is explicitly unverified.

All 22 outputs produced zero multi-block chains under the bounded generic Blackfin header test used previously and no exact occurrences of AmpEnable, GuitProcOutputGain, Blackfin or Line6. At period 1024, zero fractions were only approximately 0.0078 (training 2.02) and 0.0047 (held-out 2.05). Increasing the training zero count alone does not validate decoding. No transformed output is presented as a recovered executable.

Limits: these negative results do not exclude other periods, phase changes, other input offsets, other encodings, a non-zero-dominated plaintext, a nonperiodic transform, other boot formats, or cryptography. A magic hit alone would not establish a valid file either.

## Within-file lag statistics

`lag_statistics.json` compares bytes at lags 1 through 65536 for selected power-of-two values. The largest observed equal-byte fraction is approximately 0.004448, for lag 16 in 2.02. These tested lags show no large byte-repetition peak. This is descriptive, not an encryption test or proof of independence.

## Host-prefix cross-check

The shared first eight payload bytes, and separately their first four bytes, were searched exactly in four host modules: Updater main EXE, APIV3EngineDLL, Interposer and EngineCLIWrapper. No literal match was found. Paths, hashes and empty match lists are in `host_prefix_search.json`. This does not rule out computed constants or different modules.

## Public source lookup

Existing local public Line 6 container code confirms the outer FORM/L6FF convention but does not supply a demonstrated transformation for these two SVUs. Additional GitHub repository-search requests returned pages without a parsed result list; `public_search.json` therefore does not establish zero search results. No public decoder was identified by this limited lookup.

## Conclusion and bounded next steps

The common initial bytes and shared regions are real, but neither functions nor a loadable BF707 program have been recovered. The periodic XOR attempt is rejected as an unvalidated decoder. No conclusion about encryption is justified.

Next useful static work requires evidence of the target-side loader/container format, rather than further arbitrary masks: locate a documented BF707 image format or a directly relevant Line 6 loader implementation and test its full structural invariants on both SVUs. The actual device bootloader has not been acquired. Do not reinterpret the host-side G10T converter as the Spider DSP loader. Do not request firmware flashing or arbitrary device-memory access to fill this gap.

NAM on the original DSP remains unproven. External NAM plus original knobs has already been demonstrated; separating direct monitoring remains unresolved.
