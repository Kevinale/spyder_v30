# Análisis estático .NET de Spider V Remote 2.01

Los dos binarios se leyeron con dnfile/dncil, sin cargar ni ejecutar sus ensamblados. Se desensamblaron 1527 cuerpos IL de `extracted/Spider V Remote/Spider V Remote.exe` (1620 MethodDef) y 304 de `EngineCLIWrapper.dll` (389 MethodDef; 351 con RVA, los restantes incluyen código nativo y delegados runtime). Ningún cuerpo identificado como IL falló al analizarse. Este informe complementa el análisis Ghidra nativo: no convierte IL en instrucciones x86.

## Evidencia de eventos originados por el dispositivo

**Confianza alta:** la aplicación posee una ruta explícita de notificaciones del motor nativo hacia la interfaz, transportando `groupID`, `paramID`, `value` y un booleano llamado literalmente `deviceTriggered`. Los nombres proceden de la tabla Param de los binarios, no son nombres inventados por el analista.

`EngineCLIWrapper.dll`:

| Función | Token | RVA / offset archivo | Evidencia IL |
|---|---|---|---|
| EngineWrapper::.ctor | 0600014B | 2E0C / 220C | ldftn Native*ParamValueReceiver; call createEngine a +009F |
| NativeFloatParamValueReceiver | 0600015A | 2974 / 1D74 | +0045 obtiene SendFloat; +0052 ldarg.2 (value); +0053 ldarg.3 (deviceTriggered); +0054 Invoke |
| NativeIntParamValueReceiver | 0600015B | 2A7C / 1E7C | mismo flujo hacia sendInt |
| NativeBoolParamValueReceiver | 0600015C | 2B84 / 1F84 | callback booleano |
| NativeStringParamValueReceiver | 0600015D | 2C8C / 208C | callback cadena |
| setFloatParamValue | 0600014D | 30A4 / 24A4 | +0054 llama APIV3EngineInterface.Functions.setFloatParamValue |

La firma metadata de `setFloatParamValue` es `2003080e0e0c`: instancia, tres parámetros string/string/float32, retorno int32. La firma de NativeFloatParamValueReceiver es `0004010f1f808d1185040f1f808d1185040c02`: estática, cuatro parámetros, retorno void, termina float32 y bool. Sus primeros parámetros son punteros a tipos nativos con modificadores; el IL construye System.String desde ellos antes de invocar al delegado administrado.

En `Spider V Remote.exe`, `ParamValueServer::createEngine` (0600000D, RVA 239C, offset 59C) suscribe setFloatValue/setIntValue/setBoolValue/setStringValue/setDictionaryValue a los eventos del wrapper. `setFloatValue` (06000012, RVA 27E4, offset 9E4) reenvía los cuatro argumentos a `processSetParamValue` (06000011, RVA 2758, offset 958). Éste selecciona suscriptores mediante groupID/paramID y llama `ParamValueContainerInterface::setParamValue` a +0059, preservando deviceTriggered. La firma de setFloatValue es `2004010e0e0c02`.

`ParamControlManager::setParamValue` (0600032C, RVA 1BCC0, offset 19EC0) acepta esta interfaz, valida grupo/parámetro, guarda valores y actualiza la representación visual; no usa deviceTriggered en su propio cuerpo. Esto impide atribuir todas las actualizaciones visuales a controles físicos sólo por observar la UI.

**Límite:** existe un indicador nominal de origen dispositivo, pero este análisis administrado no demuestra qué camino nativo lo marca, qué perillas generan mensajes, ni si hay notificaciones espontáneas frente a respuestas a consultas. Tampoco identifica bytes, endpoints, MIDI CC ni frecuencia de eventos. Eso requiere seguir código nativo y capturas comparativas.

## Eventos de ratón: ruta distinta

**Confianza alta:** `SingleSlider::onMouseMove` (06000340, RVA 1CE64, offset 1B064) comprueba IsMouseCaptured, lee `MouseEventArgs.GetPosition`, calcula diferencia X/Y y llama `mouseDraggedOnControlWithID`. Esto describe interacción gráfica, no lectura de potenciómetros.

`ParamControlManager::sendLowParamValue` (0600031D, RVA 1A768, offset 18968) llama `ParamValueServer::setFloatParamValue` a +0044 y actualiza lastTransmittedLowParamValue. `sendValuesToEngine` (0600032A, RVA 1B8B4, offset 19AB4) llama setters float/int y contiene temporizadores para envíos diferidos. El setter EXE (06000017, RVA 2827, offset A27) llama al setter del wrapper; el setter wrapper llama a la API nativa. Las rutas entrante y saliente son distintas aunque comparten identificadores de parámetros.

## Presets, IR y controles externos

`EngineWrapper::setDictionaryParamValue` (06000151, RVA 331C, offset 271C) compara claves literales y despacha operaciones nativas, incluidas:

- `exportPresetFromDeviceAtIndex`, `_IndexKey`, `_FilePathKey`: call `exportDeviceTone` a +0090.
- `importPresetToDeviceAtIndex`: call `importDeviceTone` a +0143.
- `exportImpulseResponseFromDeviceAtIndex` y `importImpulseResponseToDeviceAtIndex`.

La superficie nativa declarada en el wrapper incluye bindAssetParamToExternalControl (060000EF, RVA 8178, offset 7578), reorderDevicePreset, setPresetNameAtDeviceIndex, get/setFloat/Int/Bool/StringParamValue. La existencia de `bindAssetParamToExternalControl` no demuestra acceso a perillas frontales ni compatibilidad MIDI: el nombre solo acredita una API genérica de enlace a controles externos.

No se hallaron literales `firmware` en instrucciones IL ni nombres MethodDef con Firmware en estos dos ensamblados. No equivale a ausencia de actualización: puede implementarse en APIV3EngineDLL, recursos o procesos externos.

## USB y P/Invoke

Los P/Invoke de la aplicación .NET son funciones UI de user32.dll (SetForegroundWindow, GetSystemMenu, TrackPopupMenuEx, PostMessage, EnableMenuItem). El wrapper es C++/CLI mixto: contiene referencias nativas APIV3EngineInterface y funciones de runtime. Las entradas ImplMap con biblioteca vacía no se deben interpretar como P/Invoke USB autónomos. El transporte requiere análisis de APIV3EngineDLL/Interposer/libusb; no se identificó transporte USB directo en el IL de la interfaz.

## Reproducción y evidencias

Directorio `managed/`:

- `dump_managed.py`: inventario MethodDef y desensamblado, RVA, VA preferida, offset de archivo; resolución de MethodDef/Field/MemberRef y cadenas US. Los tokens genéricos MethodSpec/TypeSpec quedan numéricos cuando no resueltos; no altera el IL.
- `metadata_inventory.py`: tipos, campos, firmas binarias y nombres/secuencias de parámetros.
- `Spider_V_Remote.json`, `EngineCLIWrapper.json`, sus `.il.txt`, `.pinvoke.txt` y `*.metadata.json`.
- `selected_evidence.txt`: cuerpos completos de funciones citadas, sin truncamiento de terminal.

Ejecutar analizadores: `PYTHONPATH=/workspace/analysis/tools/python python /workspace/analysis/remote/managed/dump_managed.py` y análogamente metadata_inventory.py. Los offsets IL mostrados por dncil son relativos al inicio del cuerpo, incluyen cabecera tiny/fat (primer opcode +1/+0C), no al primer opcode. Para instrucciones citadas: offset absoluto = offset archivo del método + desplazamiento mostrado. VA es ImageBase preferida + RVA, no una dirección observada en ejecución; wrapper base 10000000 y EXE base 00400000.

## Experimento posterior propuesto

Captura pasiva USB con dispositivo en estado conocido: primero reposo, luego una sola perilla frontal sin abrir Remote ni tocar UI. Si existe una captura previa legítima de la interacción equivalente del ratón, compararla offline; no producirla como parte de esta fase de lectura, ya que los setters pueden escribir parámetros. Registrar origen y tiempo; no reproducir ni enviar tramas extraídas, no invocar setters del wrapper ni importar presets/IR. El callback `deviceTriggered` es un ancla de ingeniería inversa para seguir el camino nativo, no una prueba de que un puente NAM ya funciona.
