# BF70x-specific loader source review — 2026-10-17

## New source evidence

1. `majbthrd/ldrshrink`, commit `daad8de9afa7c0cac8e77eac764590d142964fce`, explicitly targets BF70x as well as SC57x/SC58x. README explains DXE/ELF to boot-stream conversion by elfloader. `ldrshrink.c:53-73` describes the 16-byte block header; flags occupy bits 4–15, checksum bits 16–23, signature bits 24–31. Target, count and argument follow. `:324-334` specifies XOR of all 16 header bytes must equal zero. Its flag values operate on the extracted 12-bit flags field; shift by four to compare to full block-code constants. Thus FILL 0x010 in that field equals full-code 0x100, FIRST 0x400 equals 0x4000, FINAL 0x800 equals 0x8000. This independently supports the existing probe's layout for BF70x; it is third-party source, not a complete official BF707 specification.
2. `tabascoeye/ldr2dxe`, commit `b9d2a6c049f55b79439b9f3a5e93f6b402421b26`, README explicitly says the converter is not working yet. Its Python assumes AD signature and a default address not established for the Spider. Not executed or used as a recovered-code generator.
3. `deanm1278/bf70x-bootloader`, commit `bd8cb63e952ef568ba827f56673e1dd7447fcc1e`, README lines 4–12: BF706 EZ-Mini flash programming helper, first installed into target instruction RAM through a custom OpenOCD. The name does not identify the Spider bootloader. It cannot provide an unmodified-device read-only acquisition merely by selecting a read command. No OpenOCD command, target helper, or third-party code was executed.
4. Existing POD Go research describes an L6IA archive with multiple image records and undecoded data. Sharing the L6FF outer wrapper does not establish that the Spider has the same inner format or keys.

Exact local source hashes and commits: `loader_source_provenance.json`. Search queries and result counts: `loader_sources_search.json`, `bf70x_sources_search.json`. A fresh official Analog Devices product-page request failed at CONNECT with HTTP 403; current official manual was not retrieved.

## Expanded static test

`bf70x_header_probe.py` removes the fixed AD signature restriction for identity payloads. It requires a FIRST candidate, zero XOR header checksum, 4-byte-aligned address and length, no address overflow, bounded payload (or FILL), a consistent arbitrary signature across a chain, and FINAL termination. It reports chains with at least three headers. These are explicitly hypotheses, not complete executable validation.

- 2.02: 111 isolated FIRST candidates, zero final-terminated chains of at least three headers.
- 2.05: 11 isolated FIRST candidates, zero final-terminated chains of at least three headers.
- The initial 16-byte header XOR is 0xb5 in both samples, violating the reviewed clear boot-stream checksum requirement. Hence neither starts with an untransformed valid header under this layout.

The identical nonzero XOR is descriptive; it does not identify a mask, cipher, or checksum used by Line 6. Random isolated candidates are not mapped as executable code. Results do not exclude transformed images, other formats, or shorter streams. Previous transformed probes remain separate.

## What is actually missing

Need target-side interpretation evidence: a demonstrated payload transformation, an official description of the relevant Line 6 updater-side firmware format, or a legitimately acquired original loader/flash image. The Windows converter already examined only repackages main-image data for transmission; G10T conversion is not the BF707 loader.

A hardware acquisition is a separate unresolved experiment, not a demonstrated ready-to-run workflow. Before any read-only flash acquisition, identify the exact memory part and voltage from a verified datasheet, establish electrical isolation and whether in-circuit reading is supported, and ensure the reader does not auto-write status registers, erase, unlock, or program the device. No pin assignment, voltage, clip placement, or command is specified here because the present evidence does not justify them. Do not install a RAM helper or assume OpenOCD polling is passive. No firmware installation is needed for current static analysis.

The existing Windows files and two SVUs have not yielded executable BF707 code. NAM feasibility on the original DSP remains undetermined; no internal NAM prototype or direct-monitor-only mute has been established.
