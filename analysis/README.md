# Spider V 30 MkII / NAM: expediente de análisis

**Integración funcional confirmada por el propietario:** en el ensayo integrado20s escuchó Gateway al activar el bypass y confirmó que las cuatro perillas movían sus controles. La combinación guitarra USB sin modelado Amp audible + NAM/Gateway en PC + controles físicos está demostrada funcionalmente para esa sesión, sin modificar firmware. No implica NAM interno, transparencia bit a bit, latencia medida ni producto de uso continuo. Restauración comprobada en ensayos anteriores; sin log final de esta ejecución concreta. Evidencia: `integrated_trial/OWNER_RESULT.json`.

**Prototipo REAPER disponible:** `reaper_demo/Spider_Gateway_Demo.lua` reproduce offline 1146 eventos de las capturas con modelo Amp activo sobre Gateway. Ganancia de entrada acotada a −12/+6 dB cuando el plugin permite verificar el formato, EQ por parámetros nombrados y restauración al cerrar. Diez casos pasan bajo Lua 5.4 con API REAPER simulada; falta validación en REAPER/Gateway real. No escucha USB ni es un puente en vivo. Instrucciones en `reaper_demo/LEEME.md`; paquete independiente `/workspace/Spider_Gateway_Demo.zip`.

**Resultado de la prueba No Amp:** el audio externo con Gateway fue comprobado funcionalmente por el propietario, pero la nueva captura entrega **650 notificaciones con un único ID de parámetro no resuelto `0xffffffff`**, no los cuatro IDs anteriores. No está demostrado combinar esa configuración de audio con cuatro perillas independientes. No se identifica el ID reservado como Volume. Ver [captures_noamp/CAPTURE_ANALYSIS.md](captures_noamp/CAPTURE_ANALYSIS.md); el PCAP/audio no se incluye en el ZIP.

**Resultado con modelo Amp activo:** mapa físico básico completado con dos capturas: Drive=38, Bass=33, Mid=35, Treble=36, grupo Amp=42; todos valores float32 recibidos con Remote en sesión. Segunda captura: **1006 notificaciones de tono** sin SysEx OUT. [Informe](captures_tone/CAPTURE_ANALYSIS.md), [gráfica](captures_tone/tone_timeline.png) y `CONTROLS_MAP.json`. No se ha probado un puente NAM en vivo ni ejecución interna; no extrapolar este mapa a No Amp.

**Resultado actual:** no está demostrada la viabilidad de ejecutar NAM dentro del amplificador, y tampoco está demostrada su imposibilidad. Se validó el contenedor SVU y se analizaron estáticamente el driver y Remote. Una captura aportada por el propietario ahora confirma **140 notificaciones físicas de Drive hacia el PC con Remote en sesión**, con IDs y valores decodificados. Hay entrada de control para diseñar un puente externo; todavía no existe una integración NAM en vivo probada. Siguen pendientes silicio/memoria, independencia de Remote y ruta/latencia de audio.

Informe inicial: 14 de octubre de 2026. Actualización Remote: 15 de octubre. Actualización de captura: **17 de octubre de 2026**, America/Mexico_City. Los logs automáticos conservan el reloj UTC del host. Ningún dispositivo está conectado a este entorno; se analizó offline la captura realizada por el propietario.

## Entregables

1. [FIRMWARE_ANALYSIS.md](FIRMWARE_ANALYSIS.md): FORM/L6FF, tabla de offsets, longitudes, MD5/Adler-32, Binwalk, entropía y límites.
2. [USB_PROTOCOL_ANALYSIS.md](USB_PROTOCOL_ANALYSIS.md): extracción NSIS, VID/PID, audio/MIDI, funciones Ghidra y límites de protocolo.
3. [HARDWARE_ARCHITECTURE.md](HARDWARE_ARCHITECTURE.md): hechos, indicios y componentes no identificados.
4. [NAM_FEASIBILITY.md](NAM_FEASIBILITY.md): presupuestos de cómputo/memoria/latencia y condiciones de las rutas interna y externa.
5. [NEXT_EXPERIMENTS.md](NEXT_EXPERIMENTS.md): experimentos de lectura ordenados y criterios de éxito.

Nuevo resultado de captura: [captures/CAPTURE_ANALYSIS.md](captures/CAPTURE_ANALYSIS.md), [gráfica Drive](captures/drive_timeline.png), `captures/drive_events.csv` y `captures/nam_control_events.jsonl` (140 eventos entrantes, sólo exportación offline).

## Archivos originales e integridad

| Original recibido y accesible | Bytes | SHA-256 |
|---|---:|---|
| `SpiderV_30_60_2.05.0.svu` | 393422 | `5301e9c582fab5bf1ddcbe321cf642e293dbaf62fc90a70de923b8b4fec6c00b` |
| `Line 6 Driver2_5 Spider V v2.00.0.0 Installer (3).exe` | 1645376 | `906705bf47a2e4d0ae33ca4d28efaf000d36d899653139a63e920af61cde35c5` |
| `Spider V Remote 2.01 Installer.exe`, reconstruido del 7z aportado | 93761728 | `1f8291548abbd72ba73322e8d8916fdc8083badc2dc15d49933a87c4dc17a613` |

Originales conservados en `/workspace/attachments/`; rutas exactas en `originals.sha256` y `artifact_inventory.json`. Verificación repetida al finalizar: ambos hashes coinciden. No se alteraron ni se agregaron archivos al checkout vacío `/workspace/spyder_v30`.

**Bloqueo de transferencia resuelto:** las cuatro partes 7z suman 91.159.854 bytes. El EXE reconstruido tiene CRC32 `C3C1B3A2`, coincidente con el 7z; `7z t` valida tanto el archivo dividido como el NSIS. No se recibió un SHA-256 calculado en el ordenador de origen: el hash de arriba identifica el archivo reconstruido aquí y no es una comprobación independiente de procedencia. Las partes permanecen intactas; hashes en `remote/volume_manifest.json`. Ambos instaladores se extrajeron sin ejecutarse.

## Evidencia conservada

- `firmware/`: parser Python, chunks extraídos, carga descomprimida, JSON de validación, distribución de bloques DEFLATE, strings y log de Binwalk.
- `driver/extracted/`: 22 archivos extraídos con 7-Zip sin ejecutar el instalador. `logs/driver_archive_listing.txt` conserva el inventario; `logs/driver_archive_test.txt` registra `7z t` sin errores reportados. Esto no autentica al fabricante.
- `driver/strings/` y `artifact_inventory.json`: offsets de cadenas, hashes, metadatos PE, imports/exports, checksums PE y certificados incrustados. Los certificados se analizaron estructuralmente; **no se verificó la confianza Authenticode ni se afirma autenticidad**.
- `usb/*.ghidra.txt`, `logs/ghidra/`, `scripts/`: funciones, xrefs, pseudocódigo y scripts de Ghidra. Son inferencias estáticas; no sustituyen ejecución ni captura USB.
- `research/`: fuentes NAM capturadas con sus hashes, resultados de búsquedas y presupuestos aritméticos. Las URLs `main` son mutables; se conservan las copias consultadas.
- `remote/`: inventario de 46 archivos extraídos, reconstrucción, scripts, Ghidra, IL .NET, tablas de símbolos y tres informes de soporte: `NATIVE_ANALYSIS.md`, `MANAGED_ANALYSIS.md`, `RESOURCE_ANALYSIS.md`. Redistribuibles de terceros se inventariaron, sin ejecutarlos ni atribuirles semántica de Spider V.
- `captures/`: 7950 frames PCAPNG analizados; 3219 SysEx reensamblados coinciden con un parser independiente; 3216 mensajes M tienen roundtrip exacto; cuatro streams producen 2307 mensajes API sin residuo. Tabla recibida del dispositivo: 916 símbolos/916 CRC32 válidos. Se publican sólo resultados del target, no el PCAP que incluye otros dispositivos.

## Reproducción local

```bash
sha256sum -c /workspace/analysis/originals.sha256
python /workspace/analysis/firmware/analyze_svu.py \
  /workspace/attachments/1cef6881-5b69-4396-8afa-a13ba64b248f/SpiderV_30_60_2.05.0.svu \
  /workspace/analysis/firmware
python /workspace/analysis/audit_artifacts.py
python /workspace/analysis/nam_budget.py
python /workspace/analysis/validate_analysis.py
bash /workspace/analysis/scripts/run_usb_ghidra.sh
bash /workspace/analysis/remote/reconstruct_remote.sh
python /workspace/analysis/remote/resources/analyze_resources.py
PYTHONPATH=/workspace/analysis/tools/python python /workspace/analysis/remote/managed/dump_managed.py
PYTHONPATH=/workspace/analysis/tools/python python /workspace/analysis/remote/managed/metadata_inventory.py
# Repetición opcional del análisis nativo ya conservado en logs:
bash /workspace/analysis/remote/native/run_native_ghidra.sh
```

Las herramientas se instalaron localmente bajo `tools/` o `usb/`, sin instalar el driver Windows. El inventario usa `pefile` de `tools/python`; Binwalk requiere el Python 3.11 local descrito en su informe. Ghidra requiere el JDK 21 local indicado por el script. Los scripts de análisis leen los originales y escriben exclusivamente resultados derivados. Una nueva ejecución puede actualizar esos resultados; conservar el manifiesto/ZIP previo si se desea comparar corridas.

Ghidra 12.1.4 se obtuvo de `https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.4_build/ghidra_12.1.4_PUBLIC_20260921.zip`; SHA-256 calculado `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db`, coincidente con el publicado en la página oficial de release conservada en `tools/ghidra_release.html`. 7-Zip 26.04 procede del paquete Debian servido por HTTPS en `https://deb.debian.org/debian/pool/main/7/7zip/7zip_26.04+dfsg-1_amd64.deb`. No se deshabilitó TLS ni verificación de paquetes.

El ZIP del expediente omite los runtimes/herramientas grandes, proyectos Ghidra internos y originales; incluye informes, scripts, evidencia textual y archivos derivados. Las rutas absolutas reflejan esta máquina. Tras descargarlo, ajustar rutas para reproducirlo en otro host, conservando los hashes de entrada.

## Qué no se hizo

Nuestras herramientas no ejecutaron instaladores ni binarios Windows aportados/extraídos; no conectaron el amplificador ni enviaron comandos USB, cargaron firmware, escribieron memoria o abrieron el equipo. El propietario sí abrió Remote durante su captura; su tráfico se estudió offline sin reproducirlo. No se inventó CPU, capacidad de RAM, mapeo CC, rendimiento ni mecanismo de firma/cifrado.
