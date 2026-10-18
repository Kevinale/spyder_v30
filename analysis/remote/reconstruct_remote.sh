#!/bin/bash
# Read archives with trusted tools; never execute the reconstructed installer.
set -euo pipefail
root=/workspace/analysis
seven="$root/tools/7zip/usr/lib/7zip/7z"
mkdir -p "$root/remote/volumes" "$root/remote/reconstructed" "$root/remote/extracted"
python - <<'PY'
from pathlib import Path
import hashlib,json
r=Path('/workspace/analysis/remote')
for row in json.loads((r/'volume_manifest.json').read_text()):
 p=Path(row['path'])
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],str(p)
 link=r/'volumes'/p.name
 if not link.exists(): link.symlink_to(p)
 assert link.resolve()==p.resolve()
PY
"$seven" t "$root/remote/volumes/Spider V Remote 2.01 Installer.7z.001" > "$root/logs/remote_volume_test.txt"
"$seven" x -aos "-o$root/remote/reconstructed" "$root/remote/volumes/Spider V Remote 2.01 Installer.7z.001" > "$root/logs/remote_reconstruct_repeat.txt"
python - <<'PY'
from pathlib import Path
import hashlib,json
r=Path('/workspace/analysis/remote')
row=json.loads((r/'reconstruction.json').read_text())
p=Path(row['file'])
assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
PY
"$seven" t "$root/remote/reconstructed/Spider V Remote 2.01 Installer.exe" > "$root/logs/remote_installer_test.txt"
"$seven" x -aos "-o$root/remote/extracted" "$root/remote/reconstructed/Spider V Remote 2.01 Installer.exe" > "$root/logs/remote_extract_repeat.txt"
python "$root/remote/audit_remote.py" > "$root/logs/remote_audit_summary.txt"
