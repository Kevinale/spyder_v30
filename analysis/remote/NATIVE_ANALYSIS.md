# Análisis estático nativo de Spider V Remote 2.01

## Alcance y método

Se importaron en Ghidra 12.1.4, sin ejecutar su código, `remote/extracted/Spider V Remote/APIV3EngineDLL.dll`, `Interposer.dll` y `EngineCLIWrapper.dll`. JDK21 y scripts locales de análisis de confianza. APIV3 e Interposer son PE x86 nativos; EngineCLIWrapper es mixto CLR/nativo: Ghidra cubre su cara nativa y no sustituye análisis IL. Ningún dispositivo conectado ni comando USB emitido. Originales sin modificar.

Evidencias reproducibles: `native/api_ghidra.txt` (inventario, cadenas, referencias y pseudocódigo), `native/api_targets.txt` (funciones enfocadas), `native/zlib_targets.txt`, `native/interposer_targets.txt`, `native/interposer_ghidra.txt`, `native/wrapper_ghidra.txt`. Scripts Java, logs y proyectos conservados en `remote/native/` y `remote/ghidra/`. `native/pe_inventory.json`, `native/string_offsets.json`, `native/function_offsets.json` contienen direcciones calculadas mediante secciones PE, no búsqueda de strings sin contexto. Las VA presuponen base preferida 0x10000000; ASLR puede desplazarlas. FUN_* son nombres automáticos Ghidra, no nombres recuperados del fabricante.

Las importaciones y exportaciones originales se ejecutaron por etapas, con logs conservados. `bash /workspace/analysis/remote/native/run_native_ghidra.sh` reúne esas operaciones para repetirlas con las herramientas locales; se comprobó su sintaxis, sin repetir innecesariamente todo el análisis. El ZIP omite los proyectos/runtimes grandes, por lo que fuera de esta máquina hay que obtener Ghidra/JDK y ajustar rutas. Las funciones seleccionadas son un análisis dirigido, no una revisión exhaustiva de todos los algoritmos de las DLL.

## Hallazgos de alta confianza

| Evidencia APIV3 | VA / RVA / offset archivo | Interpretación observada |
|---|---|---|
| `FUN_10050660` | 0x10050660 / 0x50660 / 0x4fa60 | Lector IFF verifica FOURCC FORM=0x464f524d y L6FF=0x4c364646; acepta contenedores FORM/LIST/RIFF internamente. RTTI/vtable `L6DevLibIFFReader`. |
| `FUN_100507c0` | 0x100507c0 / 0x507c0 / 0x4fbc0 | Lee tipo/tamaño/subtipo, convierte bytes de enteros, conserva/restaura posición. |
| `FUN_1005bf70` | 0x1005bf70 / 0x5bf70 / 0x5b370 | Extrae HEAD de 0x34 bytes y convierte a nativo words 0,1,2,3,4,9; los otros bytes se conservan. |
| `FUN_1005c080` | 0x1005c080 / 0x5c080 / 0x5b480 | Busca y recorre dinf, extrae 0x10 bytes y convierte sus cuatro words big-endian. |
| `FUN_1005d140` | 0x1005d140 / 0x5d140 / 0x5c540 | Extrae HEAD, varios dinf y data; si HEAD word[3]==1, descomprime data con destino del tamaño HEAD word[4]. Sólo sustituye buffer si retorno cero y tamaño exacto. |
| `FUN_10001000` | 0x10001000 / 0x1000 / 0x400 | Envoltorio de descompresión zlib: inicializa con versión string `1.2.3` y z_stream 0x38 bytes; llamada al motor con flush4 (Z_FINISH), espera retorno1 (Z_STREAM_END), finaliza estado. No es evidencia de descifrado. |
| `FUN_10055150` | 0x10055150 / 0x55150 / 0x54550 | Switch del campo PID en descriptor: 0x5068→0x220000 y texto Spider V30; 0x5069→0x220001 Spider V60; 0x506a→0x220002 Spider V120. |
| `FUN_10078e90` | 0x10078e90 / 0x78e90 / 0x78290 | Selecciona `defaultSymbolTable_Parker.bin` para IDs 0x220000≤id<0x220006. `Firebird` se selecciona para 0x200006. |
| `FUN_10052fb0` | 0x10052fb0 / 0x52fb0 / 0x523b0 | Envoltorio libusb_control_transfer. Construye bmRequestType con dirección0x80, tipo vendor0x40 o clase0x20, destinatario0–3. Timeout5000ms, reintentos específicos. Los códigos concretos aún dependen de los llamadores/vtables. |

Los rótulos de modelo se muestran con espacios originales en el pseudocódigo. La asignación PID→modelo es explícita; no se afirma que esta versión de Remote identifique separadamente revisión MkII. El preset de recurso `device:0x220002` corresponde al ID Spider V120 en este binario; no demuestra que el equipo objetivo sea ese modelo.

## Correlación con el SVU proporcionado

El offset0x20 del SVU corresponde a HEAD+0xc, word[3] (flag de compresión), y offset0x24 a HEAD+0x10, word[4] (longitud de salida). La ruta nativa confirma la interpretación de la descompresión ya reproducida con Python. No llamar al tamaño «decrypted_size» por una string de otro componente: aquí el consumidor hace inflate. El bloque resultante de 393192 bytes puede contener su propia representación o transformaciones; este análisis no demuestra ni descarta una fase posterior de cifrado, ni reconoce todavía una ISA de DSP.

El parser de la app no permite atribuir todos los campos HEAD sólo por su ubicación. Tampoco se ha localizado un verificador de firma/MD5 en esta ruta. La validación MD5/Adler previamente reproducida verifica consistencia de esos archivos, no autenticidad de firmware. No se han encontrado constantes canónicas MD5 en búsqueda directa de este DLL; su ausencia no prueba que no haya verificación en otro componente o dispositivo.

## USB, presets y controles físicos

APIV3 importa libusb-1.0, WINMM y la API Interposer. En `native/pe_inventory.json` se conservan IAT y exports. `FUN_10052d50`/`FUN_10052f40` liberan interfaz0 y cierran handle libusb. `FUN_10052f90` llama libusb_reset_device: no debe invocarse para exploración exclusivamente de lectura.

Interposer exporta `InterposerInit` VA100013f0, `InterposerOpenPipe`10001730, `InterposerClosePipe`10001850, `InterposerMessage`10001a10, `InterposerRegisterCallback`10001b70, `InterposerGetDevCaps`10001dd0, `InterposerGetDescriptorCount`10001f10 e `InterposerGetDescriptors`10002040. Son interfaces del transporte anfitrión; los exports por sí solos no especifican comandos seguros de dispositivo.

Existen cadenas `kMKSysexOpcode_FileDumpDataPacket`, HandshakeACK/NAK/Wait/Cancel/EOF, modos kUsbControlEndpointMode/kUsbBulkEndpointMode/kEditorMode/kUpdateMode y RTTI `L6AmplifiUsbControlPortUpdateEngine`. Se conservan offsets exactos en string_offsets.json. Es evidencia de funcionalidades compartidas del SDK; no demuestra que todos los transportes o comandos pertenezcan a Spider V30.

Se observan rutas de presets `l6device://0x%08x:/preset/0/%d` y `/presetBinary/0/%d`, eventos EditBuffer_PresetChanged y firmwareUpdateStarted/Failed/Completed. Los consumidores se exportan en api_ghidra.txt. Esto demuestra sincronización de estado en la biblioteca, pero todavía no demuestra qué giro físico produce qué paquete USB. Los callbacks administrados `deviceTriggered` deben correlacionarse con capturas pasivas antes de afirmar control NAM externo.

## Próximas comprobaciones exclusivamente de lectura

1. Capturar descriptores estándar y tráfico pasivamente con USBPcap/Wireshark mientras una persona gira una perilla, sin invocar actualización/reset ni comandos vendor nuevos.
2. Seguir la vtable de `L6UsbControlEndpointMsgPort` y comparar mensajes recibidos con callbacks de parámetros; distinguir mensajes iniciados por UI de notificaciones iniciadas por panel.
3. Comparar otros SVU oficiales originales y documentados contra HEAD/dinf, manteniendo sus hashes y tamaños; no cargar ninguno al equipo.
4. Identificar CPU/DSP/RAM mediante fotografías existentes o documentación de servicio trazable. No abrir el amplificador en la fase inicial; una futura inspección requeriría un plan separado de seguridad eléctrica. Parker es nombre de familia de software; no un procesador.
5. Continuar el seguimiento estático desde `FUN_1005d140` hacia transporte y motor de actualización para localizar cualquier transformación posterior; nunca llamar la función del DLL.
