# Revisión del SVU, arquitectura y pista AmpEnable

Fecha: 17 de octubre de 2026, zona America/Mexico_City. Alcance: análisis de archivos existentes, herramientas propias de lectura y Ghidra estático del cliente Windows; búsqueda pública y lectura de código de terceros fijado por commit. No se ejecutaron instaladores/DLL del usuario ni software de terceros que se comunique con dispositivos. No se escribió memoria/presets/firmware del amplificador. No se accedió físicamente al equipo.

## Resultado principal y corrección

**Existe una pista de bypass más concreta que la ruta amp/@enabled examinada antes.** La tabla recibida del Spider contiene AmpEnable y AmpEnableState. Un preset recibido del mismo equipo contiene AmpEnableState booleano1 en el bloque raíz GuitarProc, separado del modelo Amp. Esto corrige cualquier lectura de los informes anteriores que equiparase «no hay traducción amp/@enabled en Remote» con «no hay propiedad AmpEnable en el dispositivo».

No demuestra que ponerla en0 produzca bypass, que el comando sea aceptado, ni que las perillas sigan notificando IDs distinguibles. No se ha cambiado ese valor.

### Evidencia propia (confianza alta en bytes/nombres/estado almacenado)

| Hallazgo | Fuente y posición |
|---|---|
| AmpEnable | `captures/device_symbols.json`, índice835, registro10028, cadena21127, CRC32`cda80a0c` |
| AmpEnableState | misma tabla recibida, índice821, registro9860, cadena20922, CRC32`61205541` |
| GuitarProc | misma tabla, índice884, registro10616, cadena21717, CRC32`184726db` |
| AmpEnableState=1 | `captures/logical_messages.json`, mensaje18, respuesta IN/canal1, frames1281–1351, payload1281 bytes; offset de key367, valor373; bytes`35030000010001000000` |
| Ubicación del valor en stream | el registro se encuentra en SysEx110, frames1295–1307; no se confunde offset del payload decodificado con offset del PCAP físico |
| Modelo Amp separado | mismo preset, subbloque GuitarProc/Amp, clave estructural Model en offset939; ref124=`Line6SuperSparkle` |

`read_captured_preset.py` consume exactamente las132 entradas/1281 bytes, valida límites/tipos/cadenas/bloques, y produce `captured_edit_buffer.json`/`.bin`. `amp_enable_evidence.py` coteja el registro con los bytes originales y genera un inventario; no contiene transporte USB/MIDI.

La distinción entre estado persistido `<nombre>State` y parámetro de control `<nombre>` aparece también en el código público Spider V citado abajo; no se presupone que toda propiedad almacenada sea escribible. El símbolo de objeto raíz coincide con el recibido de nuestro equipo, no se copia un ID de otra unidad.

### Próxima comprobación, sin cambios de estado

Describir/validar una consulta del parámetro AmpEnable en GuitarProc y comparar el valor devuelto con un modelo activo frente a No Amp. El formato de lectura del cliente se corrobora en `captures/native_setters.txt`, `FUN_10099810`, VA0x10099810/RVA0x99810/offset PE0x98c10: opcode9, cuerpo de dos IDs/8 bytes. El setter es una función distinta `FUN_100998e0`, opcode10.

`amp_enable_evidence.json` guarda una **descripción de consulta no enviada**, no un programa para ejecutarla. Falta sesión/transporte de lectura validado en Windows; un GET es una solicitud USB, no mera captura pasiva, y la seguridad del flujo debe delimitarse incluyendo inicialización. No se adopta el handshake o el cliente entero de terceros sin revisión.

Sólo después de confirmar lectura y semántica debe diseñarse una prueba reversible del estado de edición, con snapshot/restauración y observación de audio/perillas. Eso sería un experimento activo distinto, no una prueba ya realizada ni modificación del SVU.

## Resultado de la investigación del SVU

Original393422 bytes SHA256`5301e9c582fab5bf1ddcbe321cf642e293dbaf62fc90a70de923b8b4fec6c00b`; carga inflate393192 bytes SHA256`58b058a7310a8f397d5c029f6dc0c0b07e5128dbd027548c060eba797647a0b4`. Integridad de FORM/HEAD/dinf/zlib/MD5/Adler previamente descrita en `FIRMWARE_ANALYSIS.md`, revalidada con los cinco controles de parser (original aceptado, cuatro copias alteradas rechazadas). Hash original antes/después idéntico; log `svu_validation.log`.

`probe_image.py` prueba11 representaciones: original, XORff, bits invertidos dentro de cada byte, inversión de bytes en palabras2/4/6/8 y rotación de cada byte1/2/3/4 bits. Busca ELF/PE con límites/estructura y dos hipótesis de arranque ARM explícitas (tabla Cortex-M y vectores A32), sin ejecutar la carga. Cero candidatos en estas comprobaciones. Los controles sintéticos positivos ELF/PE/Cortex-M/A32 y cabeceras malformadas pasan. No se seleccionó una ISA en Ghidra para interpretar la carga como código.

Entropía global7,99834; por lanes de byte módulo4,7,99215–7,99586. No se hallaron repeticiones de bloques alineados6/8/16/32 bytes; hay3 duplicados de4 bytes. Longitud divisible por6 y8, resto8 módulo16. Estos datos **no identifican procesador ni algoritmo criptográfico**. Los negativos no excluyen otra ISA, código sin vectores, otra transformación o formato.

El formato L6IA y el magic del loader ARM0x230b0c5e descritos para AMPLIFi TT no aparecen en la carga. El header tag/count/address que ese proyecto sitúa en0x600 tampoco coincide en ese offset. No se atribuyen al Spider el LPC1820 ni el ADSP21489 del TT: son otro producto, con evidencia física ajena. `comparison_formats.json` conserva el alcance limitado de estas comparaciones.

## Consumidor de firmware en Remote

Exportación adicional Ghidra `consumer.txt`, log `consumer.log`; sólo PE host Windows. `FUN_1005d140` VA0x1005d140 sigue leyendo FORM/HEAD/dinf/data y usando inflate`FUN_10001000`. No se identificó una transformación de descifrado de esta muestra en esa función.

La pista literal `decrypted_size`, offset PE0x174a7c/VA0x1017647c, lleva a `FUN_100a0b70` VA0x100a0b70/RVA0xa0b70/offset0x9ff70. Esa función maneja un diccionario con `type`, `data`, `decrypted_size`, `crc32`; para datos string reserva `(len*6)>>3`, pasa por `FUN_1009ebc0` y L6Buffer, patrón de decodificación de texto binario. En el descompilado no se ve un cipher que podamos aplicar al SVU; no se demuestra correspondencia de esta función con la muestra. `FUN_100a0e30` crea metadatos zlib/CRC y comprime; `FUN_100a1010` infla/verifica CRC. El nombre decrypted_size sigue sin probar cifrado del SVU.

La búsqueda de «UI processor firmware» no proporciona una referencia de código que identifique un chip. Las rutas de identidad `main`/`updater` y selección de IDs Spider no identifican CPU ni RAM. Tampoco se localizó la rutina de firmware que convierte un giro en parameter_id0xffffffff. No se presentan funciones del host como funciones del DSP.

## Fuentes públicas nuevas, leídas como datos, sin ejecutar sus programas

Búsqueda GitHub web y respuestas guardadas `public_search_*.html`, resultados/hashes en `public_sources.json`. El endpoint API de GitHub y el sitio oficial Line6 consultados resultaron bloqueados por proxy; el buscador web GitHub sí fue accesible.

- `https://github.com/leevilaukka/spiderv-web-control`, commit`d392eea2a35bec47447481ccc1866db8b28cc174`. `PROTOCOL.md:153` menciona AmpEnable en GuitarProc; `app/src/lib/tone.ts:123` construye controles sólo si existen símbolo de control, símbolo State y entrada en el preset; `:76` incluye AmpEnable como candidato Amp. README declara pruebas con SpiderV20MkII2.0.1; protocolo compara con30MkI2.02. No se equipara eso a30MkII2.05.0 ni a comprobación nuestra. La evidencia propia de arriba confirma los nombres y estado para la sesión del usuario.
- `https://github.com/Jmainguy/line6-tt`, commit`1bce01b3f8dbaa4a472f48b330c7cc8883139287`. Sólo comparación de contenedores/loaders y lectura de mapas de **AMPLIFi TT**; no se portaron loaders, agentes, memoria, flashes, programas ni reglas de instalación al Spider.
- `https://github.com/MarByteBeep/podgo`, commit`7317864cb113d5fd9572b0651577a47358083192`. README describe FORM/L6FF y L6IA en **POD Go**, producto distinto; no ofrece una transformación validada para nuestra carga.

No se adoptaron instrucciones/skills de esos repositorios. Sus documentos y código son referencias no confiables hasta corroborarlos, no autorizaciones para ejecutar operaciones.

## Qué queda sin resolver

CPU/DSP/RAM, contenido ejecutable del SVU, ruta de carga/transformación y código de asignación de perillas siguen sin identificar. No hay patch de firmware, algoritmo NAM interno ni vía de flash validada. Antes de abrir hardware o pedir firmware adicional, la pista AmpEnable permite una siguiente pregunta más acotada: leer ese estado real y evaluar si ofrece bypass independiente sin cambiar firmware.
