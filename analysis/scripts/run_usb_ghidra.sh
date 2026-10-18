#!/bin/bash
# Ejecutar sólo analizadores de confianza; nunca ejecutar PE extraídos.
set -euo pipefail
export XDG_CONFIG_HOME=/workspace/analysis/usb/config
export XDG_CACHE_HOME=/workspace/analysis/usb/cache
export JAVA_HOME=/workspace/analysis/usb/jdk/usr/lib/jvm/java-21-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
gh=/workspace/analysis/tools/ghidra_12.1.4_PUBLIC/support/analyzeHeadless
for f in '/workspace/analysis/driver/extracted/Tools/Driver2 Archive/SpiderV/l6SpiderV.sys' '/workspace/analysis/driver/extracted/Tools/Driver2 Archive/SpiderV/l6SpiderV_AvsFilter.sys' '/workspace/analysis/driver/extracted/Tools/Driver2 Archive/SpiderV/$SYSDIR/InterposerBackEnd64.dll' '/workspace/analysis/driver/extracted/$APPDATA/Line 6/Interposer/$SYSDIR/SpiderVAsio_OnInterposer_x64.dll'; do
 n=$(basename "$f")
 project="project_${n//./_}"
 out="/workspace/analysis/usb/$n.ghidra.txt"
 extra=()
 if [[ "$n" == l6SpiderV.sys ]]; then
  project=project
  out=/workspace/analysis/usb/l6SpiderV.ghidra.txt
  extra=(-postScript UsbFollowup.java /workspace/analysis/usb/l6SpiderV.followup.txt)
 fi
 "$gh" /workspace/analysis/usb "$project" -import "$f" -overwrite -scriptPath /workspace/analysis/scripts -postScript UsbEvidence.java "$out" "${extra[@]}" -analysisTimeoutPerFile 180 -log "/workspace/analysis/logs/ghidra/$n.log" > "/workspace/analysis/logs/ghidra/$n.stdout" 2>&1
done
