# Arquitectura del Spider V 30 MkII: evidencia y límites

**Revisión posterior:** las comprobaciones adicionales del SVU no identificaron CPU/DSP/RAM ni código de perillas. Se leyeron proyectos públicos para AMPLIFi TT y POD Go; sus procesadores y loaders no se atribuyen al Spider. La pista nueva comprobada en el equipo del propietario es un estado booleano `AmpEnableState` dentro de GuitarProc, no una identificación de silicio. Evidencia: `firmware/revisit/REVISIT_REPORT.md`.

La prueba posterior No Amp aporta tráfico de audio isócrono y 650 notificaciones de un mismo ID no resuelto, sin los cuatro IDs de controles anteriores. No aporta identificación nueva de CPU, RAM, buses de UI ni ruta de ejecución de código propio. La prueba audible de Gateway valida procesamiento externo en el PC, no NAM en el DSP. Ver `captures_noamp/CAPTURE_ANALYSIS.md`.

Fecha de consulta: 14 de octubre de 2026 (zona del usuario). Alcance: archivos aportados y fuentes públicas alcanzables. **No se ha conectado ni abierto físicamente el amplificador.**

Actualización Remote: 15 de octubre de 2026. El análisis adicional identifica familia/IDs lógicos y controles, pero no añade una identificación de silicio o memoria.

Actualización de captura: 17 de octubre de 2026. Un PCAP aportado por el propietario confirma descriptores `0e41:5068`, transporte MIDI y notificaciones reales de Drive. No se conectó físicamente un dispositivo a este entorno de análisis. No se añade identificación de CPU/DSP/RAM; los formatos de audio USB anunciados no son capacidad interna del DSP.

Una segunda captura confirma también notificaciones de Bass/Mid/Treble (293/356/357), sin mensajes de parámetros salientes. Es evidencia adicional de interfaz física/control remoto, no de CPU, RAM, precisión de ADC o capacidad de ejecutar modelos NAM. `CONTROLS_MAP.json` reúne los cuatro controles de las dos capturas.

## Resultado

La identidad exacta de CPU, DSP, RAM, flash, convertidores y controlador de pantalla permanece **sin verificar**. No hay base para afirmar que contiene SHARC, Blackfin, ARM, un procesador concreto o una cantidad concreta de memoria. El nombre de un firmware compatible con 30/60 tampoco demuestra que las placas o sus poblaciones sean idénticas.

| Elemento | Evidencia disponible | Conclusión | Confianza |
|---|---|---|---|
| Equipo y versión objetivo | Declaración del usuario: Spider V 30 MkII, 2.05.0 | Identidad objetivo; aún falta lectura de identidad del equipo real | Alta como dato aportado; no validación física |
| Imagen común denominada 30/60 | Nombre `/workspace/attachments/1cef6881-5b69-4396-8afa-a13ba64b248f/SpiderV_30_60_2.05.0.svu` | Etiqueta de distribución; no identifica silicio ni memoria | Alta sobre el nombre; baja sobre equivalencia de placas |
| CPU/DSP e ISA | Ninguna identificación de componente verificada en las fuentes consultadas | Desconocidos | Alta sobre la ausencia de verificación |
| RAM/flash y memoria libre | Sin esquema, BOM, marcados legibles o mapa de enlace verificado | Desconocidas; tamaño del archivo ≠ RAM ni capacidad de flash | Alta |
| Pantalla y perillas | Hardware original descrito por el usuario | Existencia declarada; bus, dirección, codificación y propietario del control pendientes | Media |
| Camino de audio USB y control | INF del paquete y captura aportada, frames 20/22 y 7669–7947 | Descriptores `0e41:5068`, endpoints MIDI/audio y notificaciones reales de Drive identificados; sin audio activo medido | Alta para los bytes de la captura; no prueba de ruta/latencia de audio |

La nueva captura identifica MIDI interfaz 1 bulk `0x02`/`0x82`, audio isócrono anunciado `0x83` IN/`0x04` OUT y feedback `0x84` IN. PCM anunciado estéreo, 16 bits, 44,1/48 kHz; no se observaron transferencias de audio activas ni se midió latencia. Se recibió una tabla de 916 símbolos válida y se identificaron 140 notificaciones físicas de Drive en sesión Remote. Detalles en `captures/USB_CAPTURE_VALIDATION.md` y `captures/CAPTURE_ANALYSIS.md`.

## Investigación pública y trazabilidad

Se intentaron las fuentes oficiales `https://line6.com/spider-v-mkii/`, `https://www.line6.com/spider-v-mkii/` y `https://line6.com/support/manuals/spiderv30_mkii/`. El proxy del entorno respondió **403 Forbidden / Tunnel connection failed**. Por tanto no se presenta su contenido como leído ni como prueba. Esto limita la investigación pública; no significa que la documentación no exista. Una URL supuesta de PDF no resuelta tampoco cuenta como fuente.

Los documentos comerciales y manuales de usuario, incluso cuando se obtengan, suelen servir para funciones y conectividad; no sustituyen una foto de PCB, esquema o documentación técnica para identificar componentes. No se ha encontrado una fuente técnica primaria verificable que permita completar la tabla de silicio durante esta investigación.

Se hicieron además búsquedas de repositorios GitHub (`line6 spiderv`, `line6 "spider" firmware`, `spider v amplifier dsp`), que devolvieron listas vacías en esta consulta; copias `research/github_query_0.html` a `github_query_2.html`. Una búsqueda sin resultados no demuestra ausencia de proyectos ni documentación.

## Pista estática sobre SHARC: no identificación de chip

Ghidra recupera en `l6SpiderV.sys` una función de traducción de códigos a nombres, `FUN_1400350c4`, que devuelve `IM_BRANDI_GETSHARCFWVERSION` para `0x205` y `IM_BRANDI_GETDECRYPTKEY` para `0x204`. Es evidencia de nomenclatura dentro del driver. **Confianza baja** para extrapolarla al silicio instalado: el paquete incluye código compartido entre familias y una tabla de nombres no demuestra que esa rama se ejecute en el Spider V 30 MkII. No identifica modelo, reloj, RAM, FPU ni algoritmo de transformación del SVU. Las referencias y offsets están en `USB_PROTOCOL_ANALYSIS.md` y `usb/l6SpiderV.ghidra.txt`.

Los `.sys` del host son PE AMD64; esa ISA corresponde al ordenador Windows, no al procesador del amplificador. Tampoco se infiere arquitectura del tamaño de la carga del SVU.

## Parker y la identidad del producto

Remote aporta una correspondencia concreta en `APIV3EngineDLL.dll/FUN_10055150` (VA `0x10055150`, RVA `0x55150`, archivo `0x54550`): PID USB `0x5068` → `Spider V 30` → ID interno `0x220000`. Ese último valor coincide con HEAD del SVU en offset `0x1c`. `FUN_10078e90` (VA `0x10078e90`, archivo `0x78290`) selecciona `defaultSymbolTable_Parker.bin` para IDs de `0x220000` a `0x220005`; Firebird se selecciona para otro ID, `0x200006`. Confianza alta para estas asociaciones del software, sin validación del dispositivo físico. Detalle en `remote/NATIVE_ANALYSIS.md`.

La tabla Parker contiene 910 símbolos con longitudes/CRC32 válidos y nombres explícitos `SpiderV30_Crossover`, `SpiderV30_OutputLimiter`, `USBInLevel` y `USBOutLevel`; offsets en `remote/RESOURCE_ANALYSIS.md`. Esto corrobora recursos destinados a la familia y revela controles nombrados, pero no capacidades de RAM, reloj, ISA, rutas de bypass ni eventos de perillas por USB. `SharcPodFixedComp` sigue siendo sólo nomenclatura de un modelo.

## Arquitectura que debe reconstruirse (hipótesis de trabajo)

Camino conceptual a verificar: entrada analógica → conversión A/D → procesamiento → conversión D/A → etapa de potencia. USB y controlador de interfaz pueden residir en el mismo componente que el audio o en otros: ambas posibilidades siguen abiertas. Ningún bloque conceptual identifica un chip real ni demuestra que el usuario pueda cargar código allí.

Para reutilizar pantalla y perillas dentro del amplificador se necesitan además: ISA/ABI y toolchain, mapa de memoria, acceso a buses/GPIO, inicialización del codec y clocks, DMA/interrupciones, arranque, y ruta de carga aceptada. La ausencia de una firma aparente en un contenedor no demuestra arranque libre; su presencia tampoco basta para concluir que bloquea toda ejecución externa.

## Evidencias de lectura que faltan

1. Leer modelo, versión e identificadores USB del equipo; guardar descriptores completos y topología, sin peticiones de actualización.
2. Obtener fotografías de ambas caras de PCB de una fuente pública identificable o documentación de servicio autorizada. Una inspección física sólo si el propietario la autoriza y se planifica seguridad eléctrica; no se necesita para los primeros experimentos USB.
3. Transcribir marcados íntegros y contrastarlos con datasheets del fabricante; no elegir una ISA únicamente por desensamblado visual de bytes.
4. Correlacionar cadenas y referencias del firmware con periféricos, direcciones y formatos mediante varias evidencias independientes.
5. Determinar capacidad total y memoria libre por separado; la memoria necesaria para NAM debe coexistir con audio, UI, buffers y firmware.

Los pasos de dispositivo se detallan en NEXT_EXPERIMENTS.md y no se han ejecutado. Se mantiene la restricción del usuario: sin escritura, carga de firmware ni arranque de payloads.


## Estado tras las pruebas de monitorización directa

Para avanzar en interpretación de la carga faltan chips/revisión de placa identificados con evidencia. La búsqueda pública acotada se registró en `direct_monitor/hardware_search.json`;0 resultados no prueba ausencia de documentación. No se trasladaron procesadores de otros productos.


## Búsqueda web posterior solicitada por el propietario

Se intentó ampliar la búsqueda fuera de GitHub: Google/Bing/DuckDuckGo, Line6, ManualsLib, YouTube, Elektrotanya, MusicElectronicsForum y Reverb fueron bloqueados por el proxy de la nube (túnel403, sin recibir páginas). No se debe concluir que Internet carezca de fotos o documentación. GitHub fue accesible, sin foto de placa/chips verificada y con falsos positivos de otras clases de Spider. Evidencia y límites: `hardware_web/SEARCH_STATUS.md`, `search_results.json`, `github_results.json`, `additional_access.json`.


## Nueva evidencia fotográfica aportada por el propietario

Cinco imágenes permiten leer placa hija LINE6 A39 Daughter RevA,35-00-0485, y base A39-1 25W Main-DB,35-00-0487. U6 muestra marca Analog Devices, pero su referencia está cubierta por etiqueta A43.2. U7 muestra Nanya NT5TU32M16FG-AC y U4 marca Winbond con familia provisional25Q256FV. No se identificó CPU/DSP/modelo/ISA/reloj. Tipo/capacidad exactos de memorias pendientes de cotejo documental; memoria libre sigue desconocida. El propietario confirmó posteriormente que las cinco fotos son de su propio Spider V30MkII (hardware_photos/OWNER_PROVENANCE.json). Informe de lecturas, confianza y originales: `hardware_photos/PHOTO_FINDINGS.md` y `ORIGINALS.json`. Las identificaciones por marca no se trasladan aún a una capacidad NAM ni a ruta de mute.


## Identificación física posterior de U6

Fotos nuevas del propietario revelan **Analog Devices ADSP-BF707KBCZ-4**, con marcado Blackfin legible. Evidencia de alta confianza: `hardware_photos/PROCESSOR_IDENTIFICATION.json` y `bf707_marking_detail.png`. Esto sustituye las menciones anteriores de CPU/DSP totalmente desconocido. Reloj efectivo, memoria libre, formato ejecutable/carga y viabilidad NAM siguen sin establecer. Siguiente análisis debe contrastar BF70x/Blackfin con documentación de boot y formato del SVU; no asumir que identificar ISA convierte el payload opaco en código válido ni identifica punto de mute. No se modificó/cargó firmware.


## Line6Updater1.28 aportado: análisis estático completado

Tres volúmenes validados, instalador reconstruido y223archivos extraídos sin ejecutar PE. Se identificó ruta específica Parker/SpiderV: motor L6MidiFileDumpUpdateEngine, extracción/inflate SVU y codificación7bit reversible. La pista convertUpdateImage/make_update pertenece a ramaG10T(componente1), no al firmware principal(componente0). No se obtuvo decodificador del payload Blackfin ni mute independiente ni viabilidad NAM interna. Informe con funciones, fuentes, validaciones y límites: `updater/UPDATER_ANALYSIS.md`. Originales intactos: `updater/final_integrity.json`.


## Revisión del cargador BF70x — 2026-10-17

Se encontró una referencia específica BF70x (`majbthrd/ldrshrink`) que respalda la estructura de cabecera de 16 bytes y checksum XOR. La búsqueda ampliada sin firma AD fija no identifica cadenas de tres o más bloques en ninguna versión. El helper público `bf70x-bootloader` exige escribir RAM y está diseñado para BF706 EZ-Mini, por lo que no es un procedimiento pasivo para el Spider. La evidencia que falta es la interpretación del payload del lado del dispositivo. Detalles, commits y límites: `firmware/structure/LOADER_REVIEW.md`. Ambos SVU originales mantienen su SHA-256.
