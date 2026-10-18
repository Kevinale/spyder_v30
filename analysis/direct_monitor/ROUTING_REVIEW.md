# Investigación: separar guitarra directa del retorno NAM

## Estado

El propietario confirmó audio Gateway y cuatro controles en modo continuo. Posteriormente confirmó guitarra directa audible al bajar Output de Gateway. Con el puente desconectado, bajar Volume del modelo Amp silenció guitarra y entrada en medidor REAPER, conservando reproducción de una grabación USB. Evidencia funcional comunicada, sin captura instrumental. El comportamiento de Volume con AmpEnable0 no se midió por separado. No se ha resuelto escucha exclusiva de NAM.

## Parámetros y límites

Tabla capturada `captures/device_symbols.json`: `GuitProcOutputGain`899/CRCbd42b89b/cadena21945; `USBOutLevel`900/CRC837ea250/cadena21964; `USBInLevel`901/CRCe2b4d7d3/cadena21976. Son índices de símbolos, no opcodes, unidades ni evidencia de posición en ruta. La tabla Parker suministrada por Remote coincide para esos nombres/índices. `scan_parameters.py` no encontró esos nombres exactos terminados enNUL, sus versiones UTF16 ni los CRC LE en los EXE/DLL/SYS/CPL/PLIST de los directorios extraídos examinados. Esto no descarta referencias dinámicas, recursos externos o estructuras comprimidas. Inventario en `parameter_occurrences.json`.

## Nuevo seguimiento estático nativo

Ghidra APIV3EngineDLL.dll readOnly/noanalysis; no ejecución de PE. `global_gain_xrefs.txt`:

- Cadena `GuitOutputGain`: VA0x10174ecc, archivo0x1734cc; `GuitarVolume`: VA0x10175624, archivo0x173c24.
- FUN_10079a50 y FUN_10079f30 traducen el nombre externo GuitarVolume a GuitOutputGain; MasterVolume a Master. No equivalen automáticamente a GuitProcOutputGain. GuitOutputGain y GuitarVolume no aparecen en la tabla del Spider capturado. No se propone leerlos/escribirlos por equivalencia inventada.
- FUN_10083aa0/10083b50 eligen tabla VA0x1018e490 para IDs0x220000..0x220005. `decode_native_tables.py` reconstruye esa tabla: GuitarProc sin representación de grupo de preset, bloques Gate/VolumePedal/Amp/StudioCab/etc. No contiene posición del envío USB. Resultado `native_group_maps.json`.
- `global_get_set_paths.txt`: FUN_10097c00 resuelve nombres de grupo y parámetro mediante FUN_100ac660 y despacha getter vtable+0x28; permite un grupo vacío cuyo resultado puede ser0xffffffff. La ruta de settings genéricos llama a ese getter con grupo vacío. Es fundamento para una hipótesis de lectura global; no prueba que los tres parámetros candidatos sean globales.
- El control de Monitor Gain del driver sigue sin implementación funcional en los10 vtables revisados (ver `../dry_input/DIRECT_MONITOR_REVIEW.md`). No confundir con una capacidad del firmware completo.

Confianza alta para cadenas, flujo host y tablas reconstruidas; desconocida para alcance de audio de los tres parámetros.

## Experimento preparado: exclusivamente consultas

`routing_reader.js` extiende el lector validado, sin cargar la clase activa SpiderBypassTrial. Mantiene validación de identidad V30/version2.05.0, tabla completa y CRC, handshake y lectura inicial AmpEnable. Ejecuta como máximo seis consultas GetDspModelParam (opcode9): tres nombres exactos en dos contextos explícitos, global(-1) y GuitarProc. No recorre otros IDs, no accede a memoria, no manda setters/opcode10, no cambia modelos/presets/firmware/niveles. Un error de estado del dispositivo se registra; una ausencia de respuesta aborta. Imprime tipo/raw y float o bool si corresponde, sin asignar unidades. Cierra MIDI al terminar.

`Preparar_Lectura.ps1`: lee app.html de instalación existente; extrae solo el prefijo y clase SpiderReadOnly, excluye clase de ensayo/setter; crea una carpeta nueva del Escritorio y servidor local de lectura puerto8771. No modifica la instalación continua. Depende de formato reconocible del lector: si no coincide aborta antes de crear carpeta. Lanzamiento elevado para HttpListener, RemoteSigned solo por proceso.

Validación: Node ejecutó compuerta, rechazo de setters/otros destinos, serialización de seis pares y reporte de errores/float. Sintaxis del bundle y extracción verificadas contra app.html local. No ejecutado en Windows ni hardware en nube. El propietario aún debe obtener las lecturas; ningún resultado se presupone. Una lectura exitosa no establece topología ni autoriza elegir un valor de mute.

## Lectura real posterior del propietario

Registro en OWNER_GLOBAL_READS.json. V30/2.05.0, CRC de tabla válido, AmpEnable1. Grupo global(-1): GuitProcOutputGain float1/raw3f800000; USBOutLevel float0/raw00000000; USBInLevel float0/raw00000000. Grupo GuitarProc: los tres respondieron estado-1. Esto confirma alcance global consultable para estos tres parámetros en este equipo; no determina unidades ni punto de toma USB. No interpretar niveles USB0 como mute.

Se preparó núcleo de experimento separado output_gain_trial.js y test_output_gain_trial.js. Requiere consentimiento explícito start(true), lectura inicial exactamente float1, solo setter global de GuitProcOutputGain a float0, readback0 y restauración float1/readback1 tras15s en navegador activo o al cerrar normalmente. No cambia AmpEnable, USBIn/Out ni guarda presets. Falla de restauración conserva estado pendiente y no informa éxito. Validado con dispositivo simulado; sin ejecución Windows/hardware, sin instalación ni cambios enviados. Pendiente acuerdo para probar ese nuevo parámetro. El resultado podría silenciar también USB; no se presupone que sea una solución.

El propietario autorizó expresamente la prueba temporal de ese parámetro ("si que sigue"). Se prepararon UI y lanzador independientes: output_gain_ui.js, Preparar_Prueba_Salida.ps1, puerto8772, carpeta nueva SpiderSalida-fecha; no sustituye modo continuo ni lector. UI exige AmpEnable1 y gain1 iniciales, solo activa cambio tras clic Probar salida15s. Ocultar página solicita restauración; botón manual y desconexión también. No hay garantía ante caída de USB/navegador. Pendiente primera ejecución en Windows/hardware.

## Resultado real de prueba GuitProcOutputGain

El propietario ejecutó la prueba autorizada: identidadV30/2.05.0, AmpEnable1, gain float1 inicial, readback0 tras cambio, restauración confirmada1. Comunicó que la guitarra dejó de sonar y el medidor de entrada REAPER dejó de moverse. Registro OWNER_OUTPUT_GAIN_TRIAL.json. En esta condición poner gain0 no sirve como mute exclusivamente directo: también corta la captura de guitarra requerida por NAM. No fija por sí solo posición exacta del tap ni comportamiento con AmpEnable0. No repetir el setter de este parámetro como solución. No se han modificado USBOutLevel/USBInLevel, cuyo0 no se debe interpretar como mute.

## Seguimiento posterior al descarte de GuitProcOutputGain0

Revisada tabla completa de símbolos para mute/speaker/headphone/USB/route/routing/direct/output/input/proc/monitor/tuner/mode/aux/gain/bypass. No se encontró un símbolo inequívoco DirectMonitorMute o SpeakerMute; esto no prueba ausencia de función no simbolizada. Los nombres restantes se registraron en routing_candidate_symbols.json; no se cambiaron.

La opción @speakermode de recursos assets.json tiene dos estados (valueDisplayFormatIdentifier35). IL de Spider V Remote, ParamControlUtils::cabSpeakerModeStringForValue, RVA0x36ba/archivo0x18ba: valor0 muestra Classic, otro valor Full Range. No hay estado mute declarado en ese formato. Cadena nativa @speakermode VA0x1011722c y Speaker VA0x10175664; xrefs adicionales speaker_tuner_paths.txt. No proponemos ese selector como mute.

Prueba observacional siguiente: con reproducción detenida, pista armada, monitorización/FX NAM apagados y clientes MIDI desconectados, activar afinador desde el amplificador; observar guitarra local y medidor USB, salir y comparar. No cambia firmware ni usa setters desconocidos. Pendiente resultado; no se presupone tap USB antes/después del mute de afinador. El IL de MainContainer indica que Remote se bloquea cuando dispositivo está en tunerModeActiveState (mensaje The application is unavailable when the device is in tuner mode). Por tanto aun si el afinador conservase captura no está probado que preserve controles de perillas; no presentarlo como solución final.

## Resultado real del afinador

El propietario informó guitarra silenciada y medidor REAPER sin movimiento al activar afinador. Registro OWNER_TUNER_TEST.json. El afinador tampoco constituye mute exclusivamente directo que conserve captura USB en la configuración probada. Salir de afinador para restaurar funcionamiento normal. Con Volume del Amp0, GuitProcOutputGain0 y afinador, los tres ensayos cortaron también captura. Esto no demuestra que no exista otra ruta, pero no justifica prometer una solución con parámetros conocidos ni seguir probando ganancias al azar.
