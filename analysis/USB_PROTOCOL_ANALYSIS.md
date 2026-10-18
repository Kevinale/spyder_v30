# Análisis USB y software Windows

**Integración funcional confirmada por el propietario:** en el ensayo integrado20s escuchó Gateway al activar el bypass y confirmó que las cuatro perillas movían sus controles. La combinación guitarra USB sin modelado Amp audible + NAM/Gateway en PC + controles físicos está demostrada funcionalmente para esa sesión, sin modificar firmware. No implica NAM interno, transparencia bit a bit, latencia medida ni producto de uso continuo. Restauración comprobada en ensayos anteriores; sin log final de esta ejecución concreta. Evidencia: `integrated_trial/OWNER_RESULT.json`.

**Entrada USB con bypass comprobada funcionalmente por el propietario:** grabó guitarra desde Spider en REAPER con Gateway apagado, durante la prueba AmpEnable1→0→1, y al reproducir informó distorsionada→limpia→distorsionada. Esto respalda bypass audible de la captura USB reteniendo el modelo, además de las cuatro perillas identificadas en ensayos anteriores (Drive físico como Gain37 en Line6BigBottom). No es prueba bit a bit ni medida objetiva; falta integración simultánea completa con Gateway y comprobación de monitorización directa. No se modificó firmware. Registro: `amp_enable_reader/OWNER_TRIAL_RESULT.json`.

**Drive también identificado durante bypass:** el diagnóstico real del propietario con Line6BigBottom/modelo180 recibió `Amp.Gain`, grupo42/parámetro37/tipo4, rango0–1. AmpEnable permaneció0 tras los movimientos y se restauró1. El contador anterior sólo contaba Drive38 y por eso mostraba0. El puente Lua ahora acepta37 y38 como la perilla de entrada/Drive; comprobación con fixtures sintéticos basados en esos datos y regresiones de capturas en `live_bridge/gain_alias_validation.json`. El script actualizado todavía debe copiarse al Windows del usuario. Ya hay evidencia de los cuatro controles a través de las pruebas; la captura USB limpia con el flag0 y su integración completa con Gateway siguen pendientes.

**Prueba posterior del propietario: bypass audible conseguido.** El programa puso AmpEnable=0, verificó el mismo modelo, recibió Bass19/Mid26/Treble27 eventos, releyó0 al final y restauró1 con lectura confirmada. El propietario informó guitarra limpia durante la prueba. Drive registró0 y sigue pendiente; tampoco se ha confirmado todavía la captura USB limpia con este flag ni NAM/Gateway y cuatro controles simultáneos. No se modificó firmware. Evidencia y límites: `amp_enable_reader/OWNER_TRIAL_RESULT.json`. Esta prueba supera las conclusiones históricas de ausencia de un bypass identificado.

**Lecturas reales posteriores del propietario:** el lector verificó identidad/versión/CRC y obtuvo `GuitarProc/AmpEnable` booleano1 con Amp activo y también1 con No Amp. No se cambió ese valor. Hay una prueba activa separada preparada para0 temporal y restauración verificada, aún sin autorización ni ejecución en el dispositivo; alcance y límites en `amp_enable_reader/TRIAL_REVIEW.md`. No interpretar ambos1 como prueba de bypass funcional.

**Corrección y hallazgo posterior:** la falta de traducción `amp/@enabled` en Remote NO implica ausencia de `AmpEnable` en el equipo. La tabla recibida contiene `AmpEnable` índice835 y `AmpEnableState`821; un edit buffer real (mensaje18, frames1281–1351) contiene `GuitarProc/AmpEnableState` booleano1, separado del modelo Amp. No se ha probado lectura directa ni escritura de ese control ni su efecto sobre audio/perillas. Evidencia y consulta descrita pero NO enviada: `firmware/revisit/amp_enable_evidence.json` y `REVISIT_REPORT.md`.

**Actualización de pruebas en vivo y revisión de entrada limpia:** el propietario confirmó los cuatro controles físicos en Gateway con el puente `live_bridge/` (Remote abierto, Amp activo), y confirmó que con No Amp no se mueven mediante ese puente. La grabación reproducida desde REAPER no cambia con Amp; la entrada de guitarra sí. La revisión de las tres configuraciones USB encuentra un único par de captura estéreo y un endpoint de feedback, sin otra entrada anunciada ni selector limpio identificado. No se prueba inexistencia de rutas no documentadas. Evidencia y límites: `dry_input/DRY_INPUT_REVIEW.md`; comprobación reproducible: `dry_input/check_routing.py`. Esta actualización sustituye los estados históricos de puente en vivo pendiente de las secciones siguientes.

**Límite nuevo, prueba No Amp:** 650 notificaciones IN opcode 4, payload `[42,0xffffffff,4,float]`; cero notificaciones con parámetros 33/35/36/38 y cero SysEx OUT. No se resuelve `0xffffffff` como Volume: la rama especial del cliente sólo lo convierte a `@model` con tipo 1, no tipo 4. El mapa de cuatro controles sigue validado para las capturas con modelo Amp activo, sin garantía en bypass. Evidencia y offsets en `captures_noamp/CAPTURE_ANALYSIS.md` y `RESERVED_PARAMETER_ANALYSIS.md`.

**Segunda captura analizada:** Bass, Mid y Treble también tienen telemetría física comprobada con Remote en sesión: **293 / 356 / 357** notificaciones IN, respectivamente, y ningún SysEx OUT. Grupo Amp=42; parámetros Bass=33, Mid=35, Treble=36, además de Drive=38. Los nombres se correlacionan con la tabla validada de la captura anterior; este segundo archivo no incluye otra tabla. Véanse `captures_tone/CAPTURE_ANALYSIS.md` y `CONTROLS_MAP.json`.

**Resultado actualizado, 17 de octubre de 2026:** la captura del usuario confirma **140 notificaciones `Amp.Drive` amplificador→PC**, separadas de 813 cambios app→amplificador. El protocolo observado es SysEx Parker sobre USB MIDI, no MIDI CC. Los IDs 42/Amp y 38/Drive se verificaron contra una tabla de 916 símbolos recibida del propio equipo, con todos los CRC32 válidos. Esto demuestra telemetría de Drive con Remote en sesión; no prueba independencia de Remote ni ejecución interna de NAM. Informe, offsets y valores en [captures/CAPTURE_ANALYSIS.md](captures/CAPTURE_ANALYSIS.md).

## Alcance y método

Análisis estático, sin ejecutar instaladores, DLL ni controladores y sin dispositivo conectado. Extraídos con 7-Zip; inventario, SHA-256, secciones PE, imports/exports y certificados: `artifact_inventory.json`. Strings con offsets de archivo: `driver/strings/`. Ghidra **12.1.4 PUBLIC** ejecutado headless sobre `l6SpiderV.sys`, `l6SpiderV_AvsFilter.sys`, `InterposerBackEnd64.dll` y `SpiderVAsio_OnInterposer_x64.dll`; resultados en `usb/*.ghidra.txt`, proyectos en `usb/`, logs en `logs/ghidra/`. Script reproducible: `scripts/UsbEvidence.java` y `scripts/run_usb_ghidra.sh`. Las funciones `FUN_*` son nombres automáticos, no símbolos originales recuperados. Las direcciones VA son del PE Windows, nunca direcciones de memoria del amplificador.

Base de rutas: `driver/extracted/Tools/Driver2 Archive/SpiderV/` (abreviada D). `InterposerBackEnd64.dll` está en `D/$SYSDIR/`; ASIO en `driver/extracted/$APPDATA/Line 6/Interposer/$SYSDIR/`. Los cuatro PE son AMD64 (`Machine=0x8664`): esto identifica el **host Windows**, no el DSP.

**Actualización del 15 de octubre:** el bloqueo de Remote se resolvió con las cuatro partes 7z aportadas. El EXE reconstruido tiene 93.761.728 bytes y SHA-256 `1f8291548abbd72ba73322e8d8916fdc8083badc2dc15d49933a87c4dc17a613`; CRC32 `C3C1B3A2` coincide con el archivo 7z. Se extrajeron 46 archivos sin ejecución y se analizaron tres DLL con Ghidra y dos ensamblados con herramientas IL estáticas. Los resultados de Remote se distinguen del driver en la actualización al final y en `remote/NATIVE_ANALYSIS.md`, `remote/MANAGED_ANALYSIS.md` y `remote/RESOURCE_ANALYSIS.md`. El hash no fue cotejado con uno calculado en el ordenador de origen.

## Evidencias comprobadas

|Hallazgo|Evidencia exacta|Confianza y alcance|
|---|---|---|
|Identidad USB Spider V 30|`D/l6SpiderV.inf:39`, `:157`: `USB\\VID_0e41&PID_5068`, descripción `Line 6 Spider V 30`|Alta para asociación del driver; no demuestra revisión MkII ni interfaces reales enumeradas|
|Puertos de audio y MIDI en Windows|INF líneas 82–89, 97–101, 117–123: Audio Capture/Render y MidiCapture/MidiRender|Alta para configuración del paquete|
|Creación efectiva de filtros MIDI y audio en el código|`l6SpiderV_AvsFilter.sys`, `FUN_14000bf4c`, VA `0x14000bf4c`, archivo `0x974c`; llama `KsCreateFilterFactory` con `GLOBAL`, `AudioRender`, `MidiCapture`, `MidiRender` y descriptores distintos. `usb/l6SpiderV_AvsFilter.sys.ghidra.txt:293`|Alta; creación condicionada al arranque y capacidades; no sustituye enumeración física|
|MIDI USB tiene representación de Code Index Numbers|`l6SpiderV.sys`, `FUN_1400031dc`, VA `0x1400031dc`, archivo `0x25dc`: traduce 4 a SysEx start/continue, 5/6/7 a finales de 1/2/3 bytes, 0xb a Control change y 0xc a Program change. Strings archivo `0x38f50`, `0x39020`, `0x39030`|Alta para tabla diagnóstica compatible con CIN de USB MIDI 1.0. No demuestra que las perillas emitan CC|
|IOCTL internos de MIDI|`FUN_140034f44`, VA `0x140034f44`, archivo `0x34344`: nombres de `0x80002400` ACTIVATE, `0x80002404` DEACTIVATE, `0x80002430` RENDER_STREAMPOINTER, `0x80002436` RETRIEVE|Alta para traducción valor→nombre; no es el protocolo USB sobre el cable|
|Mensajería host→driver|`InterposerBackEndMessage`, VA `0x180003ed0`, archivo `0x32d0`; despacha llamada virtual. `FUN_180004bc0`, VA `0x180004bc0`, archivo `0x3fc0`, usa `DeviceIoControl(...,0x80002000,param_2,*param_2,...)`|Alta. Primer DWORD de buffer se usa como longitud; segundo como ID en trazas. Estructura completa pendiente|
|Control IOCTL genérico|`InterposerBackEndDeviceControl`, VA `0x180004200`; `FUN_180005510`, VA `0x180005510`, archivo `0x4910`, termina en `DeviceIoControl` con código recibido|Alta; API host. No se ejecutó|
|Consulta descriptor/status en nombres internos|`l6SpiderV.sys/FUN_140034f44`: `0x80002800` GET_DEVICE_DESCRIPTOR y `0x80002804` GET_DEVICE_STATUS|Alta para nombres; requiere rastrear handlers antes de considerar seguros o equivalentes USB estándar|
|Ajustes de latencia ASIO|Strings DLL ASIO archivo `0xe568` `inputLatency`, `0xe588` `outputLatency`; driver cadenas `InputLatencyAdjustment`, `OutputLatencyAdjustment` y funciones `FUN_1400270d4`/`FUN_14002729c`|Alta para mecanismos host; ninguna medida real de latencia ni tamaño de buffer validado|

## Mensajes internos: pistas, no comandos autorizados

`l6SpiderV.sys/FUN_1400350c4` (VA `0x1400350c4`, archivo `0x344c4`) es un traductor de enteros a nombres, no el handler que realiza cada operación. Entre sus correspondencias:

|ID interno host|Nombre encontrado|
|---|---|
|`0x200` / `0x201`|`IM_BRANDI_MMREAD` / `IM_BRANDI_MMWRITE`|
|`0x202` / `0x203`|`IM_BRANDI_GETSTATUS` / `IM_BRANDI_GETVERSION`|
|`0x204` / `0x205`|`IM_BRANDI_GETDECRYPTKEY` / `IM_BRANDI_GETSHARCFWVERSION`|
|`0x206` / `0x207`|`IM_BRANDI_RAWUSB` / `IM_USB_CONTROL_PACKET`|
|`0x24b` / `0x24c`|`IM_ASIO_GET_BUFFER_BOUNDS` / `IM_ASIO_GET_LATENCIES`|
|`0x280` / `0x281`|`IM_HWCFG_SET_ON_BOARD_MONITOR_GAIN` / `IM_HWCFG_GET_ON_BOARD_MONITOR_GAIN`|

No convertir estos números en payloads USB: son códigos de una capa host y faltan layout, destino, validación y handlers. **GETSHARCFWVERSION no identifica un SHARC instalado**: la tabla también incluye Variax y funciones de una biblioteca potencialmente compartida. GETDECRYPTKEY tampoco prueba que SVU esté cifrado. MMREAD no se propone como experimento: leer memoria arbitraria del dispositivo no es necesario para la primera fase y su semántica no está validada.

## Presets, firmware y controles físicos

En el driver no se identificó una función que decodifique presets Spider V, asigne parámetros de amplificador o procese eventos de perillas. `CHANNEL_PARAMETERS` en IOCTL se refiere a audio AVStream; no equivale a parámetros de tono. Remote sí aporta APIs de presets, catálogos y callbacks de parámetros, descritos al final. Aún no se reconstruyó un protocolo de actualización completo ni la verificación criptográfica de firmware.

El análisis estático por sí solo dejaba perillas→NAM externo sin demostrar. La captura posterior sí prueba notificaciones de **Drive** durante la sesión de Remote, con IDs y float32 resueltos; no se ha implementado un puente NAM en vivo. No hay evidencia para un mapa de todas las perillas, independencia de sesión, números MIDI CC, modelo completo de suscripción ni escritura de pantalla.

## Experimentos iniciales exclusivamente de observación

1. Enumerar descriptores y endpoints con herramientas del SO (sin enviar vendor requests construidas); guardar VID/PID, configuración, clases/subclases, direcciones, tipo de transferencia, tamaños y cadenas. Conservar número de serie de forma privada.
2. Capturar USBPcap/usbmon de enumeración normal y de giro manual de **una sola perilla por vez**, sin Remote ni reproducciones USB. Registrar tiempo, perilla, posición inicial/final y cambios locales. Leer entradas MIDI en modo monitor, sin MIDI out.
3. Comparar tráfico frente a reposo, arranque y cambio manual de preset. Comprobar si aparecen paquetes USB MIDI de cuatro bytes y reensamblar SysEx solo cuando el formato y endpoint lo corroboren. Publicar offsets del PCAP y bytes observados, nunca inferir mensajes ausentes.
4. Seguir offline las referencias nativas de Remote a los callbacks `deviceTriggered` y contrastarlas con capturas ya existentes. Los cambios de presets o parámetros desde Remote **son escrituras de estado**; no forman parte de la fase exclusivamente de lectura solicitada.
5. Evaluar captura de audio ya proporcionada por el dispositivo sin reproducción ni actualización. La prueba de retorno USB/monitorización y el control de NAM con traducción de mensajes requieren una fase posterior acordada; no se realizaron.

No se instaló el driver, no se ejecutaron binarios extraídos, no se abrió el hardware, no se envió firmware ni se escribió memoria del equipo.

## Direcciones y metadatos de procedencia

|Binario / función|VA|RVA|Offset archivo|
|---|---|---|---|
|l6SpiderV.sys / traductor CIN|`0x1400031dc`|`0x31dc`|`0x25dc`|
|l6SpiderV.sys / traductor IOCTL|`0x140034f44`|`0x34f44`|`0x34344`|
|l6SpiderV.sys / traductor mensaje|`0x1400350c4`|`0x350c4`|`0x344c4`|
|l6SpiderV_AvsFilter.sys / PnpStart inferido|`0x14000bf4c`|`0xbf4c`|`0x974c`|
|InterposerBackEnd64 / mensaje exportado|`0x180003ed0`|`0x3ed0`|`0x32d0`|
|InterposerBackEnd64 / envío IOCTL mensaje|`0x180004bc0`|`0x4bc0`|`0x3fc0`|
|InterposerBackEnd64 / envío IOCTL genérico|`0x180005510`|`0x5510`|`0x4910`|

`artifact_inventory.json` contiene el resto de los SHA-256. Los drivers incluyen tablas PE de certificados en archivo `0x44a00`/25256 bytes (`l6SpiderV.sys`) y `0x1c200`/23816 bytes (`l6SpiderV_AvsFilter.sys`). El certificado extraído tiene sujeto/emisor `CN=WDKTestCert svc-bamboo-bld,133084311811413260`. Se ha leído metadata PKCS#7; **no** se validó autenticidad, cadena de confianza, revocación, sello de tiempo ni firma de catálogo. Un checksum PE coincidente es integridad estructural, no autenticación. El checksum PE de InterposerBackEnd64 es cero (permitido para DLL); no se presenta como corrupción.

Ghidra usa un JDK extraído localmente, sin instalar nada en el SO: OpenJDK `21.0.12.1+1-1~deb13u1`, URL `https://deb.debian.org/debian/pool/main/o/openjdk-21/openjdk-21-jdk-headless_21.0.12.1+1-1~deb13u1_amd64.deb`, SHA-256 observado `f3abafb6c644b03df042824e707cd211ea33254761d7f7b75be3f8dc0df97c7a`. Transporte HTTPS verificado; ese hash es inventario local y no se cotejó con un manifiesto Debian firmado. JRE del sistema 21.0.12.1; configuración/cache de Ghidra bajo `usb/config`, `usb/cache`.

En `SpiderVAsio_OnInterposer_x64.dll/FUN_180007340`, `inputLatency` y `outputLatency` se leen mediante `RegGetValueW` desde configuración del host (VA strings `0x18000f768`/`0x18000f788`); no proporcionan la latencia física del amplificador.

## Seguimiento de referencias y distinción entre nombres y handlers

Segunda pasada Ghidra: `scripts/UsbFollowup.java`, salida `usb/l6SpiderV.followup.txt`, log `logs/ghidra/followup.stdout`. Busca referencias a los traductores y operandos escalares `0x204`/`0x205` sobre instrucciones, sin ejecutar código objetivo.

- `FUN_140023940` (VA `0x140023940`, RVA `0x23940`, archivo `0x22d40`) obtiene un buffer, comprueba un permiso/capacidad mediante `FUN_1400307b0`, compara su segundo DWORD con una lista que contiene `0x200`…`0x207` y otros IDs y despacha por llamada indirecta. Por tanto `0x204`/`0x205` aparecen también en validación de solicitudes, no solo como strings.
- `FUN_140020c10` (VA `0x140020c10`, RVA `0x20c10`, archivo `0x20010`) tiene una rama **real** para `0x204`: llama a `FUN_140022350(param_1,param_7[3],(byte *)(param_7+4),local_40+8)` y en caso de éxito construye una respuesta de `0x28` bytes con segundo DWORD `0x204`. La escritura del ID está en VA `0x140020e68` (RVA `0x20e68`, archivo `0x20268`). Esto prueba una operación host asociada al nombre GETDECRYPTKEY, sin establecer la naturaleza del algoritmo, origen del material devuelto ni relación con SVU.
- Para `0x205`, la búsqueda localiza traducción y whitelist; **no** se identificó un handler de lectura de versión SHARC ni transferencia USB correspondiente. No se concluye hardware SHARC.
- El traductor CIN tiene callers `FUN_140012cc4` y `FUN_140011120`; sus cuerpos procesan buffers y usan nibble bajo/alto y longitudes de mensajes. El seguimiento no identifica controles físicos ni valores CC. No se considera un decodificador semántico de parámetros Spider V.

Estos resultados profundizan la evidencia, pero no justifican enviar ninguno de los IDs al dispositivo. No se usaron IOCTL, MMREAD ni GETDECRYPTKEY en ejecución.

El helper `FUN_140022350` (VA `0x140022350`, RVA `0x22350`, archivo `0x21750`) no parece limitarse a computación local: según selector 1 o 2, llama dos veces a `FUN_140025750` con longitud 8 y constantes `0x80c5`/`0x80c8` o `0x80c1`/`0x8200`, seguido de `FUN_14002449c(...,0xc000,8,salida)`. La pasada posterior de esos dos helpers, documentada en la actualización siguiente, identifica campos de transferencias USB control vendor mediante el contrato WDF. Los valores `0x80c5`/`0x80c8`, `0x80c1`/`0x8200` y `0xc000` son campos wIndex en esa implementación, **no direcciones de memoria demostradas**. La secuencia incluye OUT con payload e IN; no prueba descifrado del SVU e implica escritura de datos de salida USB. Se excluye explícitamente de experimentos de lectura.

El instalador driver es NSIS y se extrajo sin ejecución a 22 archivos. `artifact_inventory.json` aporta hashes por archivo y `logs/` conserva extracción/inventario. Que el nombre del instalador contenga versión 2.00.0.0 no establece fecha de todos sus componentes: los PE incluyen timestamps de build no confiables y deben identificarse por hash.

## Actualización incremental: transporte de los helpers confirmado estáticamente

Se exportaron además `FUN_140025750` (VA `0x140025750`, RVA `0x25750`, archivo `0x24b50`), `FUN_14002449c` (VA `0x14002449c`, RVA `0x2449c`, archivo `0x2389c`), `FUN_140024100` (VA `0x140024100`, RVA `0x24100`, archivo `0x23500`), `FUN_140023138` y `FUN_1400215b0` en `usb/l6SpiderV.followup.txt`. Esta evidencia **resuelve la incertidumbre de transporte** descrita en la sección anterior, pero conserva la incertidumbre de destino lógico y relación con SVU.

Las llamadas virtuales de los dos primeros helpers usan el slot `0x2a0`. Las tablas de punteros compatibles con vtables del PE contienen en ese slot `FUN_140024100` o `FUN_140004680` (este último devuelve `STATUS_INVALID_DEVICE_REQUEST`). `FUN_140024100` construye argumentos compatibles con una transferencia control USB síncrona WDF. El ensamblado VA `0x140024237` carga un puntero de `WdfFunctions+0xa68`; `0xa68/8=333`, que el encabezado oficial Microsoft identifica como `WdfUsbTargetDeviceSendControlTransferSynchronouslyTableIndex`. El target procede del campo de objeto `+0xb8`. Archivo de evidencia de ensamblado: `usb/usb_transport_dispatch.asm.txt`. **Confianza alta** en transporte USB control para la implementación 24100; la tabla concreta usada por cada dispositivo sigue pendiente de resolver en el constructor/arranque.

Los ocho bytes de setup construidos permiten interpretar las siguientes transferencias, sin haberlas enviado:

|Helper|bmRequestType|bRequest|wValue|wIndex|wLength / datos|
|---|---|---|---|---|---|
|`FUN_140025750`|`0x40` (vendor OUT, device)|`0x67`|`0x0022`|argumento selector 16 bits|longitud de argumento, buffer entrada|
|`FUN_14002449c`|`0x40` (vendor OUT, device)|`0x67`|`0x21 \| (longitud << 8)`|argumento selector 16 bits|0; inicia operación y consulta estado después|
|`FUN_140023138`|`0xc0` (vendor IN, device)|`0x67`|`0x0012`|0|1 byte de estado|
|`FUN_1400215b0`|`0xc0` (vendor IN, device)|`0x67`|`0x0013`|0|longitud solicitada, límite comprobado ≤8|

En la ruta GETDECRYPTKEY observada, el selector 1 usa dos OUT con índices `0x80c5`/`0x80c8` y ocho bytes cada uno; selector 2 usa `0x80c1`/`0x8200`. A continuación inicia la operación con índice `0xc000`, longitud lógica 8 (wValue `0x0821`), consulta estado y solicita ocho bytes de entrada. Los helpers comparan estados `0xff`/`0xaa`, esperan y gestionan errores; el significado completo de esos estados no se adjudica aquí. Estos índices **son campos wIndex**, no direcciones de memoria demostradas. No se identifican los ocho bytes de respuesta como clave utilizable ni se vinculan con el firmware SVU. Esta ruta tiene OUT con payload y sigue excluida de todos los experimentos iniciales de lectura.

Contratos consultados, descargados por HTTPS y conservados localmente; identificadores URL con rama mutable `master`, por ello también se fijan hashes observados:

- `https://raw.githubusercontent.com/microsoft/Windows-Driver-Frameworks/master/src/publicinc/wdf/kmdf/1.15/wdffuncenum.h`, copia `usb/wdffuncenum.h`, SHA-256 `2042f92c5a6114d9a2d5443a2509e23e1ef0caebc52f5eacad37e25e1a0d4be7`; índice 333 en línea 358.
- `https://raw.githubusercontent.com/microsoft/Windows-Driver-Frameworks/master/src/publicinc/wdf/kmdf/1.15/wdfusb.h`, copia `usb/wdfusb.h`, SHA-256 `e12dd67ed9f97c7507d8ea472c8addf4e753555d89294620365402d3ecc7bded`; definición `WDF_USB_CONTROL_SETUP_PACKET` desde línea 149 y declaración de función WDF.

No se enviaron transferencias, ni consultas de estado vendor, ni IOCTL. La documentación de un OUT no autoriza su uso; únicamente permite distinguir evidencia de transporte de su semántica todavía incompleta.

La búsqueda de candidatos de vtable se reproduce con `PYTHONPATH=tools/python python scripts/scan_usb_vtables.py` desde `analysis/`; salida conservada `usb/vtable_candidates.txt`. Es una búsqueda de secuencias contiguas de punteros a código, no reconstrucción definitiva de clases.

## Actualización Remote: identidad, recursos y notificaciones

### Transporte y familia de producto

En `APIV3EngineDLL.dll`, `FUN_10055150` (VA `0x10055150`, RVA `0x55150`, archivo `0x54550`) mapea explícitamente PID `0x5068` → ID interno `0x220000` → `Spider V 30`; `0x5069` → `0x220001` → 60; `0x506a` → `0x220002` → 120. `FUN_10078e90` (VA `0x10078e90`, archivo `0x78290`) elige la tabla Parker para IDs `0x220000` a `0x220005`; Firebird corresponde a `0x200006`. Confianza alta para el mapeo del cliente, no lectura del equipo real ni distinción de revisión MkII.

`FUN_10052fb0` (VA `0x10052fb0`, RVA `0x52fb0`, archivo `0x523b0`) envuelve `libusb_control_transfer`, construyendo dirección, tipo vendor/clase y destinatario, con timeout de 5000 ms. La selección de request/value/index depende de llamadores; no se sustituye el protocolo sobre el cable por los IOCTL Windows. `FUN_10052f90` llama `libusb_reset_device` y queda excluida de experimentos de lectura. El wrapper contiene código compartido entre productos; su existencia no prueba que todas las rutas se usen en el Spider V 30.

### Presets y nombres de parámetros

Se validaron 5740 entradas de siete tablas de símbolos por estructura, terminador, longitud y CRC32; Parker contiene 910. Ejemplos de `res/defaultSymbolTable_Parker.bin`: `SpiderV30_Crossover` offset `0x2bd2`, CRC `0x13a20468`; `SpiderV30_OutputLimiter` `0x540c`, CRC `0x306f0655`; `USBOutLevel` `0x5584`, CRC `0x837ea250`; `USBInLevel` `0x5590`, CRC `0xe2b4d7d3`. Un CRC de símbolo no se considera aún ID de paquete USB.

`default_preset_parker.json` contiene `@tweakgroup`, `@tweakparam`, límites y `@speakermode`; su `device=0x220002` corresponde al **120**, según el mapeo anterior. `AssetDefs.plist` contiene 200 assets/953 parámetros y declara 309 `canBeExternallyBound=true`. No se atribuye ese enlace a perillas frontales ni a MIDI sin seguir el código. Los `.models` son catálogos JSON, no algoritmos DSP.

La API y recursos incluyen exportación/importación de presets e IR, rutas `l6device://.../preset/0/...`, `presetBinary` y eventos de cambio de edit buffer. Su presencia en una biblioteca compartida no demuestra que todos sean compatibles con el 30. Los importadores, setters y comandos de actualización no se ejecutaron.

### Ruta entrante diferenciada de la interacción de ratón

En `EngineCLIWrapper.dll`, `NativeFloatParamValueReceiver` (token `0600015A`, RVA `0x2974`, archivo `0x1d74`) y sus equivalentes int/bool/string transmiten grupo, parámetro, valor y un booleano llamado literalmente **`deviceTriggered`** en la metadata. El constructor (token `0600014B`, RVA `0x2e0c`) registra callbacks en el motor nativo. El IL reenvía el indicador al delegado; no es un nombre inventado por el analista.

En `Spider V Remote.exe`, `ParamValueServer::createEngine` (token `0600000D`, RVA `0x239c`, archivo `0x59c`) conecta esos eventos; `setFloatValue` → `processSetParamValue` los propaga a controles registrados. Es evidencia alta de una arquitectura diseñada para notificaciones con indicador de origen dispositivo. **No demuestra** que un giro físico genere un paquete IN, ni espontaneidad, frecuencia, CC o SysEx concretos. El origen nativo y captura física siguen pendientes.

La ruta de ratón está separada: `SingleSlider::onMouseMove` (token `06000340`, RVA `0x1ce64`, archivo `0x1b064`) usa `MouseEventArgs.GetPosition`/captura del ratón; `sendLowParamValue` y `sendValuesToEngine` llaman setters salientes. No confundir esas actualizaciones con lectura de perillas. El detalle de tokens, firmas, offsets IL y cuerpos completos se conserva en `remote/managed/`.

### Implicación para NAM externo

Hay evidencia de control remoto y de un canal de notificación de parámetros en el software. La captura posterior permite comprobar la telemetría de Drive con una sesión ya abierta por el propietario; el exportador offline de sus valores está preparado. No se ha demostrado que sea posible actualizar la pantalla original desde un motor externo, obtener audio sin modelado interno o reutilizar las perillas sin inicialización que escriba estado.

## Actualización de captura: formato de notificación confirmado

La captura de 664000 bytes, SHA-256 `101c25061d62c511b61a8635903da0b277a4379d918fde3e5f5a6167cea4c536`, identifica bus 2/dirección 4, VID/PID `0e41:5068`. Los descriptores anuncian MIDIStreaming interfaz 1, endpoints bulk `0x02` OUT/`0x82` IN. También anuncian PCM estéreo 16 bits a 48000/44100 Hz en interfaces de audio; no hay audio isócrono activo observado, por lo que no se afirma calidad/ruta/latencia de audio medida.

Se recuperaron 3219 SysEx; dos parsers independientes coinciden exactamente. Los 3216 mensajes Parker `M` verifican decode→encode binario idéntico. El MSB-unpack reconstruye streams separados por dirección/canal; una cabecera API `<opcode:uint32LE, longitud:uint32LE>` puede estar en un SysEx y su payload en otro. Resultado: 2307 mensajes API y cuatro streams consumidos sin residuo.

Drive usa payload `<42,38,4,bits_float32>`: app→amplificador opcode `0x0a`/longitud 16; notificación amplificador→PC opcode `0x04`/longitud 16. El campo 4 se corrobora como tipo float en `FUN_10097750`, mientras `FUN_100991b0` confirma escritura separada de cabecera/payload y `FUN_1009ae80` recepción de notificaciones. Funciones, VA/RVA/offsets y código en `captures/NATIVE_PACKET_CORRELATION.md`.

813 cambios salientes: 83,747070–97,246170 s. 140 notificaciones entrantes: 120,693903–131,116743 s. En la última fase no hay mensajes OUT con payload; sí hay lecturas IN del host. El relato del usuario sitúa allí los giros físicos y la UI siguiéndolos. No son nuevos setters de la app ni consultas OUT intercaladas. No se deduce latencia física del intervalo entre mensajes.

Durante los primeros 60,25 s no se registra bulk MIDI. Esto **no demuestra ausencia de eventos sin Remote**: no se conoce el estado de lecturas pendientes, suscripción o buffering; USB requiere sondeo del host. No se ejecutó el handshake ni se reprodujo ningún mensaje para analizar esta captura.

## Segunda captura: Bass / Mid / Treble

Entrada `SpiderV_Bass_Mid_Treble.pcapng`, 185548 bytes, SHA-256 `fa12988477ae3c2952b89f81a5b429cb92a4a0123ff2033536eb116e60a05a91`. Duración 174,134747 s; 2050 frames, 2032 del target `0e41:5068` en bus 2/dirección 4. Hay 1013 SysEx IN por `0x82` y cero SysEx OUT. Dos parsers coinciden exactamente y 1013 mensajes Parker verifican roundtrip; el stream produce 1006 notificaciones de parámetros opcode 4 y siete mensajes opcode 3 excluidos del mapa, sin residuo.

| Parámetro | IDs grupo/parámetro | Eventos IN | Intervalo relativo | Rango observado |
|---|---|---:|---|---|
| Bass | 42/33 | 293 | 38,554697–69,606882 s | 0–1 |
| Mid | 42/35 | 356 | 87,139158–121,710052 s | 0–1 |
| Treble | 42/36 | 357 | 139,883606–172,072504 s | 0–1 |

Todos usan pareja tipada 4/float32 como Drive. No se observan setters salientes de la app ni audio isócrono activo. Los IDs y el orden de movimientos respaldan los nombres, reutilizando explícitamente la tabla de 916 símbolos de la sesión anterior; no se inventa una consulta de símbolos en esta captura. No se atribuye una curva de EQ ni resolución ADC a los valores normalizados.

El mapa conjunto `CONTROLS_MAP.json` reúne cuatro controles físicos; sus exportaciones offline no son aún una integración NAM en vivo ni demuestran independencia de Remote. No hacen falta más capturas de estos cuatro controles para aceptar su telemetría en la condición observada.


## Seguimiento: mezcla directa durante NAM

El propietario confirmó modo continuo con cuatro perillas y audio Gateway; al bajar Output de Gateway persiste guitarra directa. La exclusividad de NAM no está resuelta. Nueva revisión con Ghidra, tabla Parker y diagnóstico acotado de solo lectura: `direct_monitor/ROUTING_REVIEW.md`. No se ha demostrado control de mute directo independiente.


## Estado tras las pruebas de monitorización directa

Ensayos del propietario: Volume0, GuitProcOutputGain global0 y afinador cortan también entrada USB. Revisado getter SystemSetting0x15 en cliente, sin key de mute directo validada paraV30. No se enviaron settings desconocidos. Véase `direct_monitor/FIRMWARE_ROUTING_LIMITS.md`.


## Line6Updater1.28 aportado: análisis estático completado

Tres volúmenes validados, instalador reconstruido y223archivos extraídos sin ejecutar PE. Se identificó ruta específica Parker/SpiderV: motor L6MidiFileDumpUpdateEngine, extracción/inflate SVU y codificación7bit reversible. La pista convertUpdateImage/make_update pertenece a ramaG10T(componente1), no al firmware principal(componente0). No se obtuvo decodificador del payload Blackfin ni mute independiente ni viabilidad NAM interna. Informe con funciones, fuentes, validaciones y límites: `updater/UPDATER_ANALYSIS.md`. Originales intactos: `updater/final_integrity.json`.


## Revisión del cargador BF70x — 2026-10-17

Se encontró una referencia específica BF70x (`majbthrd/ldrshrink`) que respalda la estructura de cabecera de 16 bytes y checksum XOR. La búsqueda ampliada sin firma AD fija no identifica cadenas de tres o más bloques en ninguna versión. El helper público `bf70x-bootloader` exige escribir RAM y está diseñado para BF706 EZ-Mini, por lo que no es un procedimiento pasivo para el Spider. La evidencia que falta es la interpretación del payload del lado del dispositivo. Detalles, commits y límites: `firmware/structure/LOADER_REVIEW.md`. Ambos SVU originales mantienen su SHA-256.
