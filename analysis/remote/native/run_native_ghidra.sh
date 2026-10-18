#!/bin/bash
# Static PE imports only; this never invokes an entry point in any DLL.
set -euo pipefail
root=/workspace/analysis
export XDG_CONFIG_HOME="$root/usb/config"
export XDG_CACHE_HOME="$root/usb/cache"
export JAVA_HOME="$root/usb/jdk/usr/lib/jvm/java-21-openjdk-amd64"
export PATH="$JAVA_HOME/bin:$PATH"
gh="$root/tools/ghidra_12.1.4_PUBLIC/support/analyzeHeadless"
mkdir -p "$root/remote/ghidra"
for entry in 'Native|APIV3EngineDLL.dll|api' 'Interposer|Interposer.dll|interposer' 'Wrapper|EngineCLIWrapper.dll|wrapper'; do
 IFS='|' read -r project binary prefix <<< "$entry"
 extra=()
 if [[ "$project" == Native ]]; then
  extra=(-postScript TargetEvidence.java "$root/remote/native/api_targets.txt" 10001000 10050660 100507c0 1005bf70 1005c080 1005c260 1005cf70 1005d140 10055150 10052fb0 10052f90 10078e90
         -postScript TargetEvidence.java "$root/remote/native/zlib_targets.txt" 100012a0 100012c0 10002b10 1018a000)
 elif [[ "$project" == Interposer ]]; then
  extra=(-postScript TargetEvidence.java "$root/remote/native/interposer_targets.txt" 100013f0 10001730 10001850 10001a10 10001b70 10001dd0 10001f10 10002040)
 fi
 "$gh" "$root/remote/ghidra" "$project" -import "$root/remote/extracted/Spider V Remote/$binary" -overwrite -max-cpu 2 -analysisTimeoutPerFile 300 -scriptPath "$root/remote/native" -postScript RemoteEvidence.java "$root/remote/native/${prefix}_ghidra.txt" "${extra[@]}" > "$root/remote/native/${prefix}_ghidra_repeat.log" 2>&1
done
