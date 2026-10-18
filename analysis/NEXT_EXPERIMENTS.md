# Próximos experimentos: sólo lectura

**Integración funcional confirmada por el propietario:** en el ensayo integrado20s escuchó Gateway al activar el bypass y confirmó que las cuatro perillas movían sus controles. La combinación guitarra USB sin modelado Amp audible + NAM/Gateway en PC + controles físicos está demostrada funcionalmente para esa sesión, sin modificar firmware. No implica NAM interno, transparencia bit a bit, latencia medida ni producto de uso continuo. Restauración comprobada en ensayos anteriores; sin log final de esta ejecución concreta. Evidencia: `integrated_trial/OWNER_RESULT.json`.

**Entrada USB con bypass comprobada funcionalmente por el propietario:** grabó guitarra desde Spider en REAPER con Gateway apagado, durante la prueba AmpEnable1→0→1, y al reproducir informó distorsionada→limpia→distorsionada. Esto respalda bypass audible de la captura USB reteniendo el modelo, además de las cuatro perillas identificadas en ensayos anteriores (Drive físico como Gain37 en Line6BigBottom). No es prueba bit a bit ni medida objetiva; falta integración simultánea completa con Gateway y comprobación de monitorización directa. No se modificó firmware. Registro: `amp_enable_reader/OWNER_TRIAL_RESULT.json`.

**Drive también identificado durante bypass:** el diagnóstico real del propietario con Line6BigBottom/modelo180 recibió `Amp.Gain`, grupo42/parámetro37/tipo4, rango0–1. AmpEnable permaneció0 tras los movimientos y se restauró1. El contador anterior sólo contaba Drive38 y por eso mostraba0. El puente Lua ahora acepta37 y38 como la perilla de entrada/Drive; comprobación con fixtures sintéticos basados en esos datos y regresiones de capturas en `live_bridge/gain_alias_validation.json`. El script actualizado todavía debe copiarse al Windows del usuario. Ya hay evidencia de los cuatro controles a través de las pruebas; la captura USB limpia con el flag0 y su integración completa con Gateway siguen pendientes.

**Prueba posterior del propietario: bypass audible conseguido.** El programa puso AmpEnable=0, verificó el mismo modelo, recibió Bass19/Mid26/Treble27 eventos, releyó0 al final y restauró1 con lectura confirmada. El propietario informó guitarra limpia durante la prueba. Drive registró0 y sigue pendiente; tampoco se ha confirmado todavía la captura USB limpia con este flag ni NAM/Gateway y cuatro controles simultáneos. No se modificó firmware. Evidencia y límites: `amp_enable_reader/OWNER_TRIAL_RESULT.json`. Esta prueba supera las conclusiones históricas de ausencia de un bypass identificado.

**Lecturas reales posteriores del propietario:** el lector verificó identidad/versión/CRC y obtuvo `GuitarProc/AmpEnable` booleano1 con Amp activo y también1 con No Amp. No se cambió ese valor. Hay una prueba activa separada preparada para0 temporal y restauración verificada, aún sin autorización ni ejecución en el dispositivo; alcance y límites en `amp_enable_reader/TRIAL_REVIEW.md`. No interpretar ambos1 como prueba de bypass funcional.

**Prioridad nueva basada en evidencia propia:** investigar lectura de `GuitarProc/AmpEnable` y comparar con el estado de No Amp antes de abrir hardware o modificar SVU. Los símbolos existen y un preset capturado incluye AmpEnableState=1. `firmware/revisit/amp_enable_evidence.json` describe una consulta opcode9 NO enviada y sus límites; no contiene transporte. No usar como setter ni prometer bypass/perillas a partir de un nombre. Cualquier futura prueba activa de cero/restauración debe delimitarse por separado; no forma parte del análisis ejecutado.

**Pruebas ya completadas por el propietario:** cuatro perillas→Gateway en vivo con Amp activo; ninguna de las cuatro mediante el puente en No Amp; grabación reproducida por USB estable frente al cambio de Amp; entrada de guitarra procesada con Amp. No repetir estas pruebas rutinarias. Revisión de ruta limpia realizada en `dry_input/DRY_INPUT_REVIEW.md`: no hay segunda pareja de captura anunciada ni selector identificado. No se proponen setters especulativos. Pendiente una hipótesis concreta respaldada por documentación oficial o código para bypass independiente o controles FX sin procesamiento; ninguna de esas opciones está probada. Los experimentos anteriores que figuran abajo conservan su contexto histórico.

**Actualización No Amp:** la captura de esa configuración no conserva los cuatro IDs: sólo 650 eventos `Amp/0xffffffff/float`, no resueltos. No pedir rutinariamente otra repetición de las cuatro perillas ni asignar el valor a Volume. La prueba del puente de cuatro controles puede hacerse con una DI ya grabada y un modelo Amp activo en Spider, separando entrada de audio y control. Esa prueba requiere implementar el puente; aún no se ha probado en vivo. Para seguir tocando NAM con el audio No Amp disponible, usar los controles de Gateway/REAPER mientras se investiga la limitación.

**Mapa básico completado:** ya hay evidencia de Drive/Bass/Mid/Treble con Remote en sesión. No se necesitan más capturas de esos cuatro controles. El siguiente paso es definir y probar un prototipo de escucha para el host externo: receptor pasivo, resolución de IDs de sesión y salida de control hacia el host NAM/EQ, sin reenviar setters al amplificador. Todavía faltan la selección del host/plugin y validar acceso de lectura compatible con Remote; no se presenta el exportador offline como un puente en vivo.

## Estado y límites

Actualización: 17 de octubre de 2026, zona America/Mexico_City. No hay amplificador conectado a este entorno. El propietario ya aportó una captura de su sesión, analizada offline; no hemos emitido solicitudes al dispositivo. Las pruebas nuevas aquí propuestas siguen pendientes. Los únicos ejecutables ejecutados durante nuestro análisis son herramientas de análisis obtenidas de fuentes públicas; ningún EXE, DLL, SYS o CPL aportado o extraído se ha ejecutado ni cargado por nuestras herramientas.

**Resultado nuevo:** 140 notificaciones Drive amplificador→PC identificadas con Remote en sesión, separadas de 813 setters de la app. La tabla recibida del equipo confirma índices 42/Amp y 38/Drive. Ya no hace falta repetir Drive para probar que existe telemetría en esa condición. El siguiente experimento útil es mapear otras perillas una a una, sin tocar controles de la app durante el intervalo y sin guardar presets. Informe: `captures/CAPTURE_ANALYSIS.md`.

El bloqueo de Remote por tamaño quedó resuelto con las cuatro partes aportadas. Se reconstruyó un EXE de 93.761.728 bytes, SHA-256 `1f8291548abbd72ba73322e8d8916fdc8083badc2dc15d49933a87c4dc17a613`, y se extrajeron 46 archivos sin ejecutar el instalador. El CRC32 coincide con el 7z; no se recibió un hash de origen independiente. Scripts y manifiestos en `remote/`. Las partes y los originales iniciales se conservaron intactos.

No flashear, entrar en bootloader, hacer factory reset, enviar comandos vendor desconocidos, probar IOCTL arbitrarios, escribir memoria, cargar payloads ni reproducir paquetes capturados. No ejecutar el actualizador ni iniciar una sesión de actualización. Las etiquetas «GET» o «read» de una función desconocida no garantizan que sea inocua.

## 1. Repetir el análisis local del firmware

**Objetivo:** confirmar integridad y estructura sin dispositivo. Ejecutar `sha256sum -c /workspace/analysis/originals.sha256` y el parser documentado en `FIRMWARE_ANALYSIS.md`. Comparar tamaños, MD5 del contenido, Adler-32 y SHA-256 con el informe. Guardar stdout, versión de herramientas y hora. Resultado esperado ya observado: límites exactos de FORM/chunks, 24 bloques almacenados DEFLATE y checksums coincidentes.

**Extensión pendiente:** comparar con otra imagen oficial original de una versión cercana, obtenida legalmente y con procedencia registrada. Correlacionar cambios de HEAD/dinf y contenido; diferencias de entropía o tamaño no identifican cifrado ni CPU. No generar ni cargar una imagen modificada.

## 2. Ampliar el análisis estático del editor

**Objetivo:** ampliar el seguimiento desde el consumidor ya localizado de `FORM/L6FF`, `HEAD`, `dinf` y zlib, buscar verificaciones criptográficas adicionales y separar las capas de firmware, presets y transporte.

El inventario, extracción y análisis inicial ya están realizados: ver `remote/NATIVE_ANALYSIS.md`, `remote/MANAGED_ANALYSIS.md` y `remote/RESOURCE_ANALYSIS.md`. Los recursos incluyen tablas Parker con nombres Spider V 30, presets y parámetros de tweak; los callbacks del wrapper distinguen `deviceTriggered`. El trabajo restante es seguir el origen nativo de estos eventos y relacionarlo con paquetes observados, sin convertir callbacks o IDs de recursos en mensajes USB por suposición. Registrar siempre nombre/hash de binario, VA/RVA o token IL, offset de archivo y referencias cruzadas.

**Resultado buscado:** framing, validación de longitud/checksum, discriminadores de producto, comandos de consulta y relación entre IDs de parámetros y UI. Una rutina de escritura de presets o actualización se documenta, pero no se invoca. La rutina de verificación del contenedor podría revelar transformaciones adicionales de la carga; no es evidencia hasta localizarla y analizar su flujo.

## 3. Inventario USB del equipo real

**Objetivo:** confirmar que el dispositivo físico corresponde al ID esperado por el driver, no dar por hecho que MkII tiene exactamente el descriptor del paquete.

En un host de laboratorio confiable que ya pueda enumerar el amplificador, guardar `lsusb`, `lsusb -t` y `lsusb -v -d 0e41:5068` (Linux), o el informe equivalente de descriptores de Windows. `lsusb -v` envía peticiones estándar de lectura de descriptores: no es captura completamente pasiva. No cambiar configuración alternativa, no separar el kernel driver ni reclamar interfaces desde un script de prueba. La enumeración USB habitual tiene transacciones de configuración del sistema operativo; esto es distinto de escribir firmware o parámetros.

Registrar VID/PID reales, bcdDevice, cadenas, configuraciones, interfaces/altsettings, clases/subclases, endpoints, direcciones IN/OUT, atributos y tamaños máximos. Registrar velocidad, sample rates/formatos **sólo si se describen realmente**. Redactar número de serie antes de compartirlo. La ausencia de 0e41:5068 no es permiso para forzar el driver: investigar el ID observado.

**Éxito:** descriptores completos identifican transporte y direcciones. El INF aporta una expectativa de audio/MIDI, no un descriptor real ni una garantía de protocolo MIDI CC.

## 4. Captura pasiva de perillas, sin editor

**Objetivo inicial:** determinar si mover controles físicos produce mensajes dispositivo→host. Ya hay resultado positivo para Drive con Remote en sesión; el intervalo sin Remote no permite concluir que no existan eventos, porque puede faltar lectura pendiente o inicialización. Para nuevas perillas usar usbmon/Wireshark o USBPcap ya instalado y confiable. El capturador observa; no utilizar funciones de inyección. No ejecutar los instaladores aportados desde nuestras herramientas para preparar este experimento.

1. Capturar primero 30 s sin acciones y sin Remote/actualizador. Guardar modelo/firmware, host, driver, reloj de captura y software abierto.
2. Observar por separado cada perilla: anotar nombre, modo visible de UI y tiempos de tres movimientos lentos, extremos y vuelta a una posición marcada. No guardar presets. La manipulación física cambia el estado sonoro transitorio; el experimento informático se limita a observar tráfico y no envía escrituras de parámetros. Conservar una referencia visual de la posición inicial.
3. Repetir en otra toma y comparar con el ruido de fondo. Registrar endpoint, dirección, tipo de transferencia, longitud y bytes variables. Correlacionar orden y valores; evitar confundir audio isócrono o polling periódico con eventos de control.
4. Para un candidato, comprobar monotonía, resolución, saturación, independencia entre perillas y repetibilidad. Un único paquete correlacionado no basta. No dar por hecho CC MIDI, SysEx, escala 0–127 ni IDs consecutivos.

**Éxito:** mensajes IN reproducibles con ID/valor correlacionado al control, distinguibles del tráfico basal. **Resultado negativo limitado:** no hay eventos observados en esa configuración; no demuestra que ninguna sesión de editor pueda habilitarlos.

Si sólo hubiera tráfico con Remote, primero analizar estáticamente su inicialización. No abrir una sesión desconocida bajo el supuesto de que es de sólo lectura: puede sincronizar o escribir estado. Una captura de una sesión previa legítima aportada por el propietario permite avanzar sin iniciar nuevas escrituras. No reproducir su handshake.

La segunda captura de **la sesión habitual del propietario** ya contiene Bass, Mid y Treble en intervalos separados y sin SysEx OUT; sus IDs/valores quedan en `captures_tone/`. Esta prueba no necesita repetirse. No demuestra independencia de Remote; investigar esa independencia exige resolver la inicialización/lectura antes de probar un cliente propio.

## 5. Inferir protocolo a partir de capturas

Exportar desde una captura conservada: número de frame, timestamp, bus/dirección, endpoint, tipo, longitud, payload hexadecimal y marcador de acción. Conservar PCAPNG y SHA-256. Separar submit/completion para no contar dos veces una transferencia. Crear una tabla de campos candidatos con offsets relativos al payload, endianess, significado propuesto, muestras positivas/negativas y confianza. No trasladar offsets del PE a offsets del paquete.

Reconstruir presets/parámetros sólo con exportaciones o capturas ya disponibles; no generar consultas vendor hasta demostrar su semántica de lectura mediante código y captura. Clasificar firmware update en un espacio separado y excluirlo de cualquier prueba inicial. No confundir capacidad de recibir cambios desde el editor con capacidad de emitir movimientos de perillas.

## 6. Arquitectura hardware, sin intervención eléctrica

Buscar documentación de servicio o fotografías públicas trazables de la revisión exacta de PCB. Anotar fuente, revisión y marcados íntegros de CPU/DSP, RAM y flash; contrastar con datasheets oficiales. Un firmware común 30/60 no establece placas idénticas ni RAM compartida.

En esta fase no abrir el amplificador, conectar JTAG/SWD/UART ni sondear buses. Incluso interfaces de depuración llamadas de lectura pueden detener el procesador o modificar registros. Una inspección interna futura exigiría un plan separado de seguridad eléctrica y autorización explícita; no es necesaria para los primeros experimentos USB.

## 7. NAM sin tocar el amplificador

Seleccionar y conservar un modelo `.nam` concreto y permitido. Leer su JSON, sample rate, arquitectura, pesos, capas, canales, dilataciones y gates; calcular pesos/estado/MAC por muestra con las fórmulas de `NAM_FEASIBILITY.md`. No equiparar MAC/s a capacidad del DSP desconocido. `nam_budget.py` reproduce los ejemplos hipotéticos y no ejecuta modelos.

En un host externo identificado, compilar NAM upstream de un commit fijado y ejecutar su benchmark sobre ese modelo. Registrar CPU, compilador/flags, precisión, sample rate, tamaño de bloque, consumo de memoria y percentiles/máximo de tiempo por bloque tras calentamiento. La comparación interna queda pendiente hasta identificar hardware y poder medirlo sin infringir las restricciones. No inferir rendimiento del amplificador a partir del host.

La prueba de audio USB bidireccional y latencia es una fase posterior: reproducir audio envía datos al dispositivo, por lo que **no pertenece a los experimentos iniciales de sólo lectura**. Antes de hacerla hay que verificar las rutas de audio y evitar realimentación/doble modelado. Un mapeo de eventos ya capturados a parámetros de NAM puede simularse enteramente offline sin enviar nada al amplificador.

## Criterios de decisión

- **NAM interno:** no declarar viable hasta verificar ISA/toolchain, ejecución admitida, memoria libre, acceso al audio/UI y presupuesto de tiempo real. No declarar imposible por tamaño del SVU o por entropía.
- **Perillas → NAM externo:** Drive ya cumple el criterio de telemetría IN consistente y mapeable en sesión Remote. Avanzar con un prototipo de lectura/escucha, sin modificar el equipo; resolver inicialización y conflictos de clientes antes de afirmar funcionamiento en vivo. Para otras perillas, obtener evidencia equivalente.
- **Pantalla original:** requiere evidencia distinta; eventos de perillas no prueban que se puedan renderizar nombres o valores externos.
- **Bloqueos actuales:** silicio y memoria sin verificar; independencia de Remote y puente en vivo sin probar; audio/latencia sin medir; acceso oficial Line6 desde este entorno devuelve 403. Ya existe una captura válida de identidad USB y Drive, y Remote es accesible y analizado. No hace falta escribir firmware ni memoria para ampliar la evidencia de controles externos.


## Estado tras las pruebas de monitorización directa

No repetir pruebas de mute descartadas ni cambiar USBInLevel/USBOutLevel sin semántica. Próxima evidencia útil: chips y revisión de placa mediante fotos públicas/documentación de servicio/imagen de técnico; o loader identificado del producto. No solicitar apertura ni lectura arbitraria de memoria como paso inmediato. No se justifica un flash experimental. Véase `direct_monitor/FIRMWARE_ROUTING_LIMITS.md`.


## Identificación física posterior de U6

Fotos nuevas del propietario revelan **Analog Devices ADSP-BF707KBCZ-4**, con marcado Blackfin legible. Evidencia de alta confianza: `hardware_photos/PROCESSOR_IDENTIFICATION.json` y `bf707_marking_detail.png`. Esto sustituye las menciones anteriores de CPU/DSP totalmente desconocido. Reloj efectivo, memoria libre, formato ejecutable/carga y viabilidad NAM siguen sin establecer. Siguiente análisis debe contrastar BF70x/Blackfin con documentación de boot y formato del SVU; no asumir que identificar ISA convierte el payload opaco en código válido ni identifica punto de mute. No se modificó/cargó firmware.


## Prueba estructural Blackfin tras identificar BF707

Revisión reproducible nueva en `firmware/blackfin/REPORT.md`: lector estático de hipótesis LDR16bytes, seis controles sintéticos y11representaciones del payload, sin cadena multibloque reconocida. Detector ELF reconoce ejemplo público BF707; no se ejecutó. Los ejemplos/port EZ-Kit no se confunden con firmware/placa Spider y no aportan un mute directo. Sigue sin reconstruirse transformación/carga del SVU.


## Seguimiento del preparador de actualización

Nuevos exports Ghidra en `firmware/blackfin/UPDATE_PATH_REVIEW.md`: se rastreó motor común con ImageArchive/L6IA sin demostrar que sea ruta del V30. El manual oficial aportado, páginaPDF3, remite a Line6Updater. Falta su instalador Windows como fuente de análisis estático: no está entre los ejecutables extraídos de Remote/Driver. Obtenerlo sin ejecutarlo es el próximo paso acotado; no implica actualizar el amplificador ni garantiza descifrar SVU.


## Line6Updater1.28 aportado: análisis estático completado

Tres volúmenes validados, instalador reconstruido y223archivos extraídos sin ejecutar PE. Se identificó ruta específica Parker/SpiderV: motor L6MidiFileDumpUpdateEngine, extracción/inflate SVU y codificación7bit reversible. La pista convertUpdateImage/make_update pertenece a ramaG10T(componente1), no al firmware principal(componente0). No se obtuvo decodificador del payload Blackfin ni mute independiente ni viabilidad NAM interna. Informe con funciones, fuentes, validaciones y límites: `updater/UPDATER_ANALYSIS.md`. Originales intactos: `updater/final_integrity.json`.

## Differential comparison prepared — 2026-10-17

`firmware/comparison/compare_svu.py` and `firmware/comparison/STATUS.md` document the offline workflow. Baseline and corruption checks passed. Awaiting another official Spider V 30/60 SVU version: only 2.05.0 is available. Official download page access currently fails at the environment proxy with HTTP 403; no cross-version conclusions are available.


## Actualización: comparación oficial declarada 2.02 / 2.05 (2026-10-17)

La muestra aportada como 2.02 tiene HEAD 0x02020030, producto 0x220000 y checksums coherentes. El payload extraído mide 3.060.448 bytes frente a 393.192 del 2.05. Hay regiones idénticas; la mayor a igual offset mide 163 bytes. No se ha identificado código ejecutable ni una vía para NAM interno. La espera de una segunda muestra queda resuelta. Evidencias, límites y siguiente análisis de lectura: `firmware/comparison/COMPARISON_REPORT.md`. No se ejecutó ni modificó firmware.


## Seguimiento de estructura interna — 2026-10-17

Se probaron once máscaras XOR periódicas inferidas del byte modal de 2.02 y aplicadas a ambas versiones; ninguna produjo una cadena Blackfin validada. No hay evidencia de un decodificador recuperado ni conclusión sobre cifrado. Los prefijos compartidos tampoco aparecen literalmente en los cuatro módulos host examinados. Detalles y límites: `firmware/structure/STRUCTURE_REPORT.md`. Se verificaron de nuevo ambos SHA-256 originales sin cambios. El siguiente requisito técnico es identificar el formato o implementación de carga del lado DSP mediante una fuente verificable. NAM interno sigue sin demostrarse.


## Revisión del cargador BF70x — 2026-10-17

Se encontró una referencia específica BF70x (`majbthrd/ldrshrink`) que respalda la estructura de cabecera de 16 bytes y checksum XOR. La búsqueda ampliada sin firma AD fija no identifica cadenas de tres o más bloques en ninguna versión. El helper público `bf70x-bootloader` exige escribir RAM y está diseñado para BF706 EZ-Mini, por lo que no es un procedimiento pasivo para el Spider. La evidencia que falta es la interpretación del payload del lado del dispositivo. Detalles, commits y límites: `firmware/structure/LOADER_REVIEW.md`. Ambos SVU originales mantienen su SHA-256.
