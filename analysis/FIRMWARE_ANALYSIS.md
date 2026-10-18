# Firmware Spider V 2.05.0: análisis estático

**Revisión posterior del 17 de octubre:** se revalidó el SVU y se probaron once representaciones/estructuras de arranque sin identificar ISA. La investigación encontró una pista ajena al payload pero verificada en la captura del propietario: `GuitarProc/AmpEnableState=1`, separado del modelo Amp, y los símbolos `AmpEnable`/`AmpEnableState`. Esto abre una vía de lectura para investigar bypass sin modificar firmware; no demuestra que sea escribible ni que conserve perillas. Informe y scripts: `firmware/revisit/REVISIT_REPORT.md`.

## Alcance e integridad

Se analizó exclusivamente el archivo recibido `attachments/1cef6881-5b69-4396-8afa-a13ba64b248f/SpiderV_30_60_2.05.0.svu`, sin modificarlo ni comunicarse con el amplificador. Tiene **393422 bytes**, SHA-256 `5301e9c582fab5bf1ddcbe321cf642e293dbaf62fc90a70de923b8b4fec6c00b`. Las rutas de este informe son relativas a `/workspace`. Todos los offsets son de archivo, sin dirección de carga implícita.

## Contenedor y validaciones

**Confianza alta:** es un contenedor IFF `FORM` de tipo `L6FF`, con campos de tamaño big-endian. `file` informa `IFF data`. En 0x04, `0x000600c6` = 393414; sumado a los 8 bytes iniciales coincide exactamente con el tamaño físico. No quedan bytes ajenos a los chunks.

| Chunk | Cabecera | Datos | Longitud | Final exclusivo |
|---|---:|---:|---:|---:|
| HEAD | 0x0c | 0x14 | 52 / 0x34 | 0x48 |
| dinf | 0x48 | 0x50 | 16 / 0x10 | 0x60 |
| data | 0x60 | 0x68 | 393318 / 0x60066 | 0x600ce |

`HEAD` contiene `00 01 00 00 02 05 00 30 00 22 00 00` en 0x14–0x1f. El patrón 02 05 00 es compatible con la versión del nombre; la interpretación completa de la versión empaquetada permanece sin validar. El análisis posterior de Remote permite asociar el DWORD de 0x1c, `0x00220000`, al ID interno de Spider V 30; véase la actualización al final. Los campos big-endian de 0x24 y 0x5c son ambos `0x0005ffe8` = 393192, tamaño real del contenido descomprimido.

**Confianza alta:** `data` comienza `78 da`, un stream zlib válido. Se descomprime completamente, con fin de stream y sin bytes sobrantes. El stream consta de **24 bloques DEFLATE de tipo 0, almacenados sin compresión**, con pares LEN/NLEN complementarios válidos; por tanto el envoltorio zlib no reduce este contenido. Esto explica que el archivo empaquetado sea ligeramente mayor que los datos. Detalles por bloque: `analysis/firmware/deflate_blocks.json`.

| Verificación | Valor | Resultado |
|---|---|---|
| Longitud de datos descomprimidos | 393192 | Coincide con HEAD y dinf |
| MD5 de datos descomprimidos | `b81b5f67e318dbe1c690a7f2ab422259` | Coincide byte a byte con 0x28–0x37 de SVU |
| Adler-32 zlib | `bfe4be09` | Coincide con los últimos 4 bytes del stream |
| SHA-256 de datos descomprimidos | `58b058a7310a8f397d5c029f6dc0c0b07e5128dbd027548c060eba797647a0b4` | Identificador del artefacto extraído |

MD5 y Adler-32 validan consistencia del archivo; **no prueban autenticidad del fabricante ni constituyen una firma digital**. No se ha identificado un campo de firma criptográfica; tampoco puede descartarse autenticación dentro de la carga opaca.

## Firmas, recursos y entropía

Se ejecutó Binwalk del repositorio oficial ReFirmLabs, tag `v2.3.4`, commit `cddfede795971045d99422bd7a9676c8803ec5ee` (metadatos internos 2.3.3+cddfede), con 411 firmas y sin extracción automática ni ejecución de payload. Se utilizó Python 3.11 por incompatibilidad de `imp` con Python 3.12. Log: `analysis/firmware/binwalk.txt`.

- SVU: única detección, zlib en 104 / 0x68.
- Datos descomprimidos: ninguna firma reconocida por Binwalk.
- Escaneo Python complementario: sin magic ELF, gzip, xz, 7z, ZIP, bzip2, SquashFS, uImage, FDT, PNG, JPEG o texto PEM.
- Hay tres coincidencias de dos bytes `MZ` en offsets **del descomprimido** 95535, 299713 y 304682. Son candidatos débiles, no ejecutables PE validados; Binwalk no los identifica como PE. Igualmente, las coincidencias `30 82` no prueban objetos DER o certificados.
- 388 cabeceras candidatas zlib dentro del descomprimido fueron probadas con salida limitada a 4 MiB; ninguna produjo un stream completo válido.
- Entropía Shannon: 7.99834 bits/byte global; ventanas de 4096 bytes, 7.94038–7.96462. Se registraron 107 secuencias ASCII imprimibles de al menos 8 caracteres; no se identificaron nombres de funciones ni textos inequívocos de producto. Los listados son candidatos, no símbolos.

**Conclusión limitada, confianza alta:** la carga aún no ofrece código, tablas, pantalla, presets ni ISA identificables con estos métodos. **No se concluye cifrado a partir de entropía**: puede haber codificación, scrambling, datos empaquetados u otra transformación. Tampoco se infieren direcciones, CPU, instrucciones, algoritmo DSP ni capacidad de ejecutar NAM.

## Artefactos reproducibles

`analysis/firmware/analyze_svu.py` usa biblioteca estándar de Python; valida límites, tamaños, zlib, MD5 y Adler-32; extrae copias de chunks y genera `analysis.json`, `summary.json`, `deflate_blocks.json` y listados de cadenas. Ejecutar desde cualquier directorio:

```bash
python /workspace/analysis/firmware/analyze_svu.py \
  /workspace/attachments/1cef6881-5b69-4396-8afa-a13ba64b248f/SpiderV_30_60_2.05.0.svu \
  /workspace/analysis/firmware
```

Binwalk:

```bash
XDG_CONFIG_HOME=/workspace/analysis/tools/binwalk-config \
PYTHONPATH=/workspace/analysis/tools/binwalk-deps \
/workspace/analysis/tools/python/cpython-3.11-linux-x86_64-gnu/bin/python3.11 \
/workspace/analysis/tools/binwalk-deps/bin/binwalk -B \
/workspace/attachments/1cef6881-5b69-4396-8afa-a13ba64b248f/SpiderV_30_60_2.05.0.svu \
/workspace/analysis/firmware/data.decompressed.bin
```

El consumidor del contenedor se localizó posteriormente en Remote, como se documenta abajo. Sigue pendiente establecer cualquier transformación posterior y la cadena completa de autenticación/arranque. La comparación con otro firmware oficial original y documentado puede separar campos constantes de metadatos y payload. Nada aquí justifica escribir en el dispositivo.

## Controles de la validación

Se ejecutó `python /workspace/analysis/validate_analysis.py`: el parser acepta el original y rechaza cuatro copias temporales deliberadamente alteradas (truncado, MD5 de cabecera cambiado, tamaño declarado cambiado y Adler-32 cambiado). Cinco resultados esperados de cinco; diagnóstico y hash del original antes/después en `analysis/logs/parser_validation.json`. Las copias se crearon en un directorio temporal separado y se eliminaron. Esto verifica que el procedimiento detecta esos fallos; no establece autenticidad ni es un parser universal de todas las variantes SVU. Ejecutar sin `python -O`, pues las validaciones usan assertions.

## Actualización del 15 de octubre: consumidor SVU en Remote

Evidencia estática de `remote/extracted/Spider V Remote/APIV3EngineDLL.dll`; direcciones del PE host (ImageBase `0x10000000`), no del amplificador. Descompilados y referencias en `remote/native/api_targets.txt` y `remote/native/zlib_targets.txt`; detalle en `remote/NATIVE_ANALYSIS.md`.

| Hallazgo | Función / VA | RVA / offset archivo | Confianza |
|---|---|---|---|
| Lectura de FORM/L6FF | `FUN_10050660` / `0x10050660` | `0x50660` / `0x4fa60` | Alta, compara magics en el lector |
| Consumidor de HEAD de 52 bytes y dinf de 16 bytes, endianess big endian | `FUN_1005d140` / `0x1005d140` | `0x5d140` / `0x5c540` | Alta |
| Transformación elegida si HEAD DWORD[3] vale 1; usa tamaño DWORD[4] | `FUN_1005d140` → `FUN_10001000` | Transformación `0x1000` / `0x400` | Alta para descompresión zlib, no descifrado demostrado |
| PID `0x5068` → `Spider V 30`, ID interno `0x220000` | `FUN_10055150` / `0x10055150` | `0x55150` / `0x54550` | Alta para mapeo dentro de Remote |

El lector confirma de forma independiente la estructura observada por Python. En esta muestra, DWORD[3] de HEAD está en SVU `0x20` y vale 1; DWORD[4] está en `0x24` y vale 393192. El helper usa inicialización/ejecución/finalización de inflate zlib, con cadena de versión `1.2.3`. No se atribuye a esa función un descifrado criptográfico.

La correspondencia de ID interno `0x220000` con PID 5068 permite identificar con confianza alta el destino declarado del contenedor como Spider V 30, **sin identificar CPU ni garantizar compatibilidad de toda revisión MkII**. El preset Parker de ejemplo usa `0x220002`: el mismo switch lo asocia a Spider V 120, no al 30. No se debe convertir un preset compartido en prueba de configuración de la unidad del usuario.

El contenido opaco después de inflate sigue sin código/ISA identificado. Nombres como `decrypted_size` o GETDECRYPTKEY en otros caminos no prueban que este payload concreto esté cifrado ni completan la verificación de firma/arranque.

## Correlación con captura del dispositivo, 17 de octubre

El PCAP aportado posteriormente identifica VID/PID `0e41:5068`, emite texto `L6ImageType:main`/`L6Version:2.0.5.0.0` y una respuesta de versión API con DWORD LE `0x02050030`, coincidente con el DWORD big-endian del SVU en `0x18`. Esto relaciona la versión reportada en esa sesión con el archivo analizado; no prueba por sí solo que todos los bytes de memoria del equipo sean idénticos al archivo ni que sea posible cargar código nuevo. Ver `captures/CAPTURE_ANALYSIS.md`.


## Estado tras las pruebas de monitorización directa

Revisión dirigida de rutas: `direct_monitor/FIRMWARE_ROUTING_LIMITS.md`. SVU y payload conservan hashes iniciales; no se identificó código ejecutable ni dirección de rutina de mezcla. No hay patch ni conclusión de cifrado.


## Identificación física posterior de U6

Fotos nuevas del propietario revelan **Analog Devices ADSP-BF707KBCZ-4**, con marcado Blackfin legible. Evidencia de alta confianza: `hardware_photos/PROCESSOR_IDENTIFICATION.json` y `bf707_marking_detail.png`. Esto sustituye las menciones anteriores de CPU/DSP totalmente desconocido. Reloj efectivo, memoria libre, formato ejecutable/carga y viabilidad NAM siguen sin establecer. Siguiente análisis debe contrastar BF70x/Blackfin con documentación de boot y formato del SVU; no asumir que identificar ISA convierte el payload opaco en código válido ni identifica punto de mute. No se modificó/cargó firmware.


## Prueba estructural Blackfin tras identificar BF707

Revisión reproducible nueva en `firmware/blackfin/REPORT.md`: lector estático de hipótesis LDR16bytes, seis controles sintéticos y11representaciones del payload, sin cadena multibloque reconocida. Detector ELF reconoce ejemplo público BF707; no se ejecutó. Los ejemplos/port EZ-Kit no se confunden con firmware/placa Spider y no aportan un mute directo. Sigue sin reconstruirse transformación/carga del SVU.


## Seguimiento del preparador de actualización

Nuevos exports Ghidra en `firmware/blackfin/UPDATE_PATH_REVIEW.md`: se rastreó motor común con ImageArchive/L6IA sin demostrar que sea ruta del V30. El manual oficial aportado, páginaPDF3, remite a Line6Updater. Falta su instalador Windows como fuente de análisis estático: no está entre los ejecutables extraídos de Remote/Driver. Obtenerlo sin ejecutarlo es el próximo paso acotado; no implica actualizar el amplificador ni garantiza descifrar SVU.


## Line6Updater1.28 aportado: análisis estático completado

Tres volúmenes validados, instalador reconstruido y223archivos extraídos sin ejecutar PE. Se identificó ruta específica Parker/SpiderV: motor L6MidiFileDumpUpdateEngine, extracción/inflate SVU y codificación7bit reversible. La pista convertUpdateImage/make_update pertenece a ramaG10T(componente1), no al firmware principal(componente0). No se obtuvo decodificador del payload Blackfin ni mute independiente ni viabilidad NAM interna. Informe con funciones, fuentes, validaciones y límites: `updater/UPDATER_ANALYSIS.md`. Originales intactos: `updater/final_integrity.json`.


## Actualización: comparación oficial declarada 2.02 / 2.05 (2026-10-17)

La muestra aportada como 2.02 tiene HEAD 0x02020030, producto 0x220000 y checksums coherentes. El payload extraído mide 3.060.448 bytes frente a 393.192 del 2.05. Hay regiones idénticas; la mayor a igual offset mide 163 bytes. No se ha identificado código ejecutable ni una vía para NAM interno. La espera de una segunda muestra queda resuelta. Evidencias, límites y siguiente análisis de lectura: `firmware/comparison/COMPARISON_REPORT.md`. No se ejecutó ni modificó firmware.


## Seguimiento de estructura interna — 2026-10-17

Se probaron once máscaras XOR periódicas inferidas del byte modal de 2.02 y aplicadas a ambas versiones; ninguna produjo una cadena Blackfin validada. No hay evidencia de un decodificador recuperado ni conclusión sobre cifrado. Los prefijos compartidos tampoco aparecen literalmente en los cuatro módulos host examinados. Detalles y límites: `firmware/structure/STRUCTURE_REPORT.md`. Se verificaron de nuevo ambos SHA-256 originales sin cambios. El siguiente requisito técnico es identificar el formato o implementación de carga del lado DSP mediante una fuente verificable. NAM interno sigue sin demostrarse.


## Revisión del cargador BF70x — 2026-10-17

Se encontró una referencia específica BF70x (`majbthrd/ldrshrink`) que respalda la estructura de cabecera de 16 bytes y checksum XOR. La búsqueda ampliada sin firma AD fija no identifica cadenas de tres o más bloques en ninguna versión. El helper público `bf70x-bootloader` exige escribir RAM y está diseñado para BF706 EZ-Mini, por lo que no es un procedimiento pasivo para el Spider. La evidencia que falta es la interpretación del payload del lado del dispositivo. Detalles, commits y límites: `firmware/structure/LOADER_REVIEW.md`. Ambos SVU originales mantienen su SHA-256.
