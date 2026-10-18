# Análisis estático de recursos de Spider V Remote 2.01

Fuentes originales extraídas: `analysis/remote/extracted/Spider V Remote/`; originales preservados. No se ejecutó código de los instaladores ni se contactó al amplificador. Los offsets son bytes desde cero en el archivo indicado. La evidencia se genera con `python analysis/remote/resources/analyze_resources.py`; inventario SHA-256 en `resources/inventory.json`.

## Tabla de símbolos: estructura validada

Los siete archivos `res/defaultSymbolTable*.bin` son tablas estructuradas legibles, no blobs que requieran hipotetizar cifrado. Confianza alta: 5.740 registros verificados, sin errores de límites/terminador ni discrepancias CRC32.

| Offset | Tipo little endian | Interpretación comprobada |
|---|---|---|
| 0x00 | uint32 | número N de registros |
| 0x04 | uint32 | tamaño total del archivo, coincide en los siete |
| 0x08+12*i | uint32 | offset relativo al pool de cadenas |
| 0x0c+12*i | uint32 | CRC32 IEEE de los bytes UTF-8 de la cadena, sin NUL |
| 0x10+12*i | uint32 | longitud de la cadena, sin NUL |
| 8+12*N | bytes | pool de cadenas terminadas en NUL |

El CRC32 es un identificador/hash por símbolo; su coincidencia no demuestra autenticación ni firma criptográfica del software. Los nombres `defaultSymbolTable_*` son variantes de tablas del cliente, no tablas de símbolos de depuración ni imágenes ejecutables del DSP.

| Variante | Registros | Bytes | Pool |
|---|---:|---:|---:|
| sin sufijo | 611 | 15.764 | 0x1cac |
| AEON | 1.152 | 28.815 | 0x3608 |
| Dio | 629 | 16.199 | 0x1d84 |
| FX100 | 629 | 16.197 | 0x1d84 |
| Firebird | 1.180 | 29.577 | 0x3758 |
| Parker | 910 | 22.074 | 0x2ab0 |
| TT | 629 | 16.199 | 0x1d84 |

Evidencia completa por registro, con posición del registro, posición de cadena, longitud y CRC: `resources/defaultSymbolTable*.bin.json`. Resultados agregados en `resources/summary.json`.

## Asociación Parker / Spider V

La combinación de nombres SpiderV explícitos y preset `Spider Remote` ofrece evidencia alta de que Parker es la variante de recursos para la familia Spider V; no prueba identidad de CPU ni revisión exacta MkII/firmware 2.05.0. Firebird es otra variante presente, sin evidencia en estos recursos suficiente para identificarla como Spider V.

Cadenas de `res/defaultSymbolTable_Parker.bin`:

| Offset cadena | CRC32/ID | Nombre |
|---|---|---|
| 0x2bd2 | 0x13a20468 | SpiderV30_Crossover |
| 0x2be6 | 0x8b017378 | SpiderV60_Crossover |
| 0x43ca | 0x3dca88de | SharcPodFixedComp |
| 0x502b | 0x6742cabf | SpiderVGuitarFlow |
| 0x540c | 0x306f0655 | SpiderV30_OutputLimiter |
| 0x5481 | 0xce9a5e4a | SpiderVMain |
| 0x5584 | 0x837ea250 | USBOutLevel |
| 0x5590 | 0xe2b4d7d3 | USBInLevel |
| 0x55b2 | 0x56a56d48 | SpiderV30_CrossoverBoiling |

Estos símbolos aportan candidatos para seguimiento en código descompilado y capturas USB. `SharcPodFixedComp` es un nombre de modelo compartido: **no identifica por sí solo un procesador SHARC físico**. `USBInLevel`/`USBOutLevel` indican parámetros nombrados, sin revelar por sí mismos endpoints, formato de mensajes, direcciones de audio, controles físicos ni posibilidad de desactivar la ruta interna.

## Presets y parámetros

`res/default_preset_parker.json` es JSON `schema=L6Preset`, `version=5`. `data.meta.application=Spider Remote`, preset `Arachnid Rhythm`. Campos:

| Campo | Offset de clave | Valor |
|---|---|---|
| data.device | 0x150 | 2228226 = 0x00220002 |
| data.device_version | 0xe75 | 16778081 = 0x01000361 |
| data.tone.global.@tweakparam | 0x899 | @mix |
| data.tone.global.@tweakgroup | 0x8c2 | fx3 |
| data.tone.global.@speakermode | 0x957 | 0.0 |
| data.tone.amp | 0xc20 | BritPlexiJumpLead; Bass, Mid, Treble, Drive, Presence, @volume |

`@tweakmin=0`, `@tweakmax=1`, `@pedal2assign=0`, `@tempo=142.563` aparecen en global. Son parámetros de asignación/configuración en un preset de ejemplo, sin prueba de eventos enviados al mover perillas. `device` es un identificador dentro del preset: **no debe reinterpretarse automáticamente como VID/PID USB**. Tampoco se establece aquí cómo codificar `device_version` ni su correspondencia con 2.05.0; es un preset distribuido con el cliente y su fecha meta es 2016.

El preset genérico usa `device=0x00200002`, `device_version=7471224` y metadatos `song=AMPLIFi`; AEON usa `device=0x00200004`, `device_version=0` y añade `variax`/`fx4`. Esto demuestra que recursos presentes en el instalador cubren familias distintas; no son capacidades automáticamente atribuibles al Spider V 30. Correlación posterior con código nativo: `FUN_10055150` asocia el ID `0x220002` del preset Parker al Spider V **120**, no al 30. La asociación Parker→familia Spider V sí queda respaldada por la selección de tabla en `FUN_10078e90`; detalle en `NATIVE_ANALYSIS.md`.

## Catálogos de modelos y AssetDefs

Los 11 archivos `*.models` son JSON de metadatos: 79 amps, 29 amps_hd, 26 cabs, 15 delay, 9 fixed, 23 mod, 15 reverbs, 12 reverbs_mclass, 31 stomps, 14 stomps_hd y 8 wahs. Sus entradas declaran IDs/nombres y parámetros min/max/default/tipo. Son catálogos de la aplicación; no coeficientes NAM, código DSP ni demostración de que todos esos modelos se ejecuten en este amplificador.

`AssetDefs.plist` es XML plist parseable; `Categories/.../assets` contiene 200 assets y 953 parámetros. La propiedad `canBeExternallyBound` es `true` en 309 y `false` en 644. Ejemplo `engineID=FacialFuzz`, parámetro Drive: rango engine y control [0,1], visual [0,100], externamente enlazable. Primera cadena `FacialFuzz` en offset 0xc3cab; estructura completa y jerarquía en `resources/assets.json`.

Confianza alta en el contenido de campos; baja en atribuir `canBeExternallyBound` a las perillas físicas o a MIDI: la semántica de "externally" necesita seguimiento de código. No establece por sí sola una API pública ni notificaciones USB bidireccionales.

## Implicaciones prácticas y comprobaciones de lectura

1. Comparar CRC32 calculados con referencias de APIV3EngineDLL/Interposer para resolver nombres de parámetros numéricos; mantener separados los IDs de modelos de `.models`, CRC32 de símbolos y `device` del preset.
2. Capturar primero movimientos de una perilla sin Remote ni actualizador. Si se dispone de una captura legítima previa del editor, analizarla offline para distinguir notificaciones espontáneas, consultas periódicas y cambios locales. No iniciar una sesión del editor como experimento de lectura hasta demostrar que su inicialización no escribe estado. Aún no se ha realizado ninguna captura.
3. Identificar `USBInLevel` y `USBOutLevel` mediante lecturas documentadas o captura de la aplicación; no probar escrituras especulativas a IDs descubiertos.
4. Contrastar `@tweakgroup/@tweakparam` con la selección visible en Remote y con mensajes ya capturados. La existencia de esos campos permite formular una hipótesis comprobable, no concluir que un motor NAM externo puede controlarse ya.
