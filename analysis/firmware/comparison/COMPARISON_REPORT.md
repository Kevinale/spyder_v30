# Spider V 2.02.0 versus 2.05.0 — static evidence

Date: 2026-10-17. No firmware execution, device connection, flashing, or original-file changes.

## Input validation

The uploaded filename is supported by HEAD version word `0x02020030` (2.02.0 encoding, consistent with the existing 2.05.0 word `0x02050030`). Both have product `0x00220000`. This establishes header consistency, not cryptographic authenticity of the source.

| Property | 2.02.0 | 2.05.0 |
|---|---:|---:|
| File bytes | 3,061,494 | 393,422 |
| HEAD header offset / size | 0x0c / 52 | 0x0c / 52 |
| dinf header offset / size | 0x48 / 16 | 0x48 / 16 |
| data header offset / size | 0x60 / 3,061,389 | 0x60 / 393,318 |
| Inflated bytes | 3,060,448 | 393,192 |
| Stored DEFLATE blocks | 187 | 24 |

Both FORM lengths, chunk bounds, zlib termination/Adler-32, payload MD5 and HEAD/dinf length consistency passed the original static parser. 2.02 data has an IFF padding byte. The zlib streams store data without actual DEFLATE compression; size difference persists after inflation.

2.02 original SHA-256: `a87d0d5460d63688e5b78d8ba8712fb8cc944f097b31dd655a5446868cf675dc`.
2.02 inflated SHA-256: `273696a7715413625a7cb7ed6c05fe8b1c91118ec5145f5bc4f980b0f001af8f`.
2.02 MD5: `860b5885e04734bf26477a0eb98a643a`; Adler-32 `13689b9d`.
Original source: `/workspace/attachments/17bb55a3-25ed-48e3-83dc-c8e003ecbd62/SpiderV_30_60_2.02.0 (1).svu`.

## Differences and shared regions

Offsets below refer to inflated payloads, not SVU file offsets.

- First eight bytes match: `93 5a 3d 32 f9 51 31 67`; first difference at offset 8.
- 31,326 bytes match at corresponding positions over the shorter payload (393,192 bytes), or 7.9671%.
- Longest corresponding-position identical run: offset 209,813 (`0x33395`), length 163 bytes.
- With nonoverlapping 2.02 blocks indexed and searched at every byte in 2.05: 120 matches of 16 bytes; six of 64 bytes; zero of 256, 1024 or 4096 bytes. These counts concern this explicit indexing method, not every possible unaligned block pair.
- All six 64-byte block matches have identical offsets in both inputs: 32128, 32640, 209280, 209408, 209856, 210368.
- The size difference does not establish full versus incremental update, firmware partitions, missing components, memory use, or corruption. Checksums passing makes a truncation inconsistent with this envelope, but not every possible packaging error is excluded.

## Executable hypothesis

The existing bounded generic Blackfin LDR probe was applied to 2.02 in eleven representations (identity, XOR ff, byte-bit reversal, word byte reversals, per-byte rotations). No chain with two or more valid headers was found. Isolated header candidates are not evidence of executable blocks. This is not an exhaustive BF707 boot-format specification.

High entropy is measured (2.02 inflated: 7.9967 bits/byte) but does not establish encryption. Shared regions and nonuniform differential bytes likewise do not identify an obfuscation algorithm or prove its absence.

## Implication and next read-only work

High confidence: same outer container and product field; different version field; payload integrity checks pass; substantial size difference; shared byte regions exist.

Unresolved: payload transformation/structure, loader behavior on the DSP, actual code boundaries and load addresses, audio routing control that mutes only direct guitar, available DSP budget for NAM.

Next bounded step: analyze the common initial bytes and shared-region neighborhoods against an independently documented Blackfin image/container or Line 6 transformation. Do not infer function names or port NAM until executable structure and an authorized development path are established. No further owner hardware trial is required for this comparison.

Evidence: `2.02_vs_2.05.json`, `block_comparison.json`, `run_statistics.json`, `2.02_ldr_probe.json`, `../v2.02/analysis.json`, `../v2.02/deflate_blocks.json`. Reproduction scripts: `compare_svu.py`, `block_compare.py`, `probe_202.py`.
