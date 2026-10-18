# No Amp: audio presente, pero sin cuatro controles diferenciados

Se recibió `SpiderV_NoAmp_Perillas.7z.001`, archivo 7z de un solo volumen, 3220800 bytes. Extracción estática correcta a **SpiderV_NoAmp_Perillas.pcapng**, **84637284 bytes**, CRC32 `BE6CE0CF` coincidente con el contenedor, SHA-256 **`4ebbb7faced38403cad610e93d3cf8dc97407b5e07a711e6e03b7f5c85834018`**. No se ejecutaron binarios ni se enviaron solicitudes al dispositivo. Los originales se conservan intactos.

## Resultado

La captura contiene **650 notificaciones float del amplificador hacia el PC**, todas con el mismo payload de identificadores:

```text
group_index     = 42       (Amp, referencia de la tabla previa)
parameter_index = 0xffffffff  (no resuelto)
type            = 4        (float32)
value           = variable, valores observados entre 0 y 1
```

**No aparecen los IDs separados Drive=38, Bass=33, Mid=35 ni Treble=36** de las capturas anteriores. Los mensajes registrados no permiten enrutar cuatro perillas de forma independiente: falta un identificador de origen distinto en esos payloads. Esto es una limitación de la configuración/sesión observada; no demuestra que todas las rutas posibles del firmware estén agotadas ni que NAM interno sea imposible.

La selección No Amp/No Cabinet procede de las capturas de pantalla y del relato del propietario. Este archivo empieza con una sesión ya abierta y no contiene lectura de preset/modelo que verifique por sí misma esa selección. La comparación se atribuye a la configuración indicada por el usuario, sin inventar un marcador de cambio de modelo.

## Validación del archivo y transporte

| Comprobación | Resultado |
|---|---|
| Frames / intervalo relativo | 470865 / 117,386209 s |
| Identidad target | Descriptor `0e41:5068`, bus 2, dirección 4 |
| Frames target | 470847 |
| ISO target | 469541 frames; hay tráfico isócrono de audio/feedback |
| Bulk target | 1300 frames; 650 completions IN con payload |
| SysEx | 650 IN, cero OUT; sin mensajes incompletos |
| Parsers independientes | Coinciden en los 650 SysEx, bytes, dirección, frames y tiempos |
| Roundtrip Parker M | 650 decode→encode binariamente idénticos |
| Stream API | 650 mensajes completos, opcode 4 / payload 16, cero residuo |
| Tipo | 650 float32, todos parámetro `0xffffffff` |
| Estado USB registrado | Cero en todos los frames target |

Los streams IN tienen una completion inicial sin submission dentro del archivo y una lectura pendiente al terminar, compatibles con bordes de captura. No se inventan sus tiempos anteriores o posteriores.

El tráfico isócrono explica buena parte del tamaño sin comprimir. No se ha analizado ni exportado su contenido de audio. Que exista ISO no prueba transparencia de la ruta, latencia ni ausencia de procesamiento. `target_frames.json` conserva únicamente control/bulk con `--control-midi-only`; el PCAP, audio y datos de otros dispositivos no se incluyen en el ZIP de resultados.

## Evidencia de los valores

Primer evento: **frame 63398**, t=15,844476 s; mensaje API:

```text
04 00 00 00 10 00 00 00 2a 00 00 00 ff ff ff ff
04 00 00 00 60 38 51 3e
```

Notificación opcode 4, payload de 16 bytes, grupo 42, parámetro no resuelto `0xffffffff`, tipo 4, float **0,2043166161**.

Último evento: **frame 415667**, t=103,586714 s; mismos identificadores, float **0,0**. Hay 404 valores float distintos. Separando por pausas mayores de dos segundos aparecen seis grupos temporales, pero **los grupos de tiempo no son identificadores de perilla**. No se reasignan a Drive/Bass/Mid/Treble por orden o por forma de la curva.

## No se ha identificado como Volume

El modelo No Amp sólo declara `@volume` en los recursos, lo que motivó comprobar esa posibilidad. Sin embargo el código no permite etiquetar estos mensajes como Volume:

- `FUN_100987c0` contempla `parameter_id=-1 → @model` únicamente con pareja de tipo 1, simbólica. Esta captura lleva tipo 4, por lo que no aplica ese caso.
- El lookup SDB normal `FUN_100ac720` usa comparación unsigned con el número de símbolos; `0xffffffff` no es un índice válido de la tabla.
- La tabla especial Parker relaciona `ChannelVolume → amp/@volume`; `ChannelVolume` tiene índice 804 en la tabla previa. No constituye una traducción de `0xffffffff` a volumen.

Informe estático completo con VA/RVA/offset y pseudocódigo: `RESERVED_PARAMETER_ANALYSIS.md`. Se conserva el parámetro como **no resuelto**; tampoco se le adjudica automáticamente la semántica de default, error, modelo o control físico crudo.

## Consecuencia práctica

| Ruta | Estado actual |
|---|---|
| Audio USB con No Amp/No Cabinet → Gateway/NAM en REAPER | El propietario comprobó sonido sin distorsión audible al desactivar Gateway y distorsión al activarlo. Prueba funcional relatada; no medida bit a bit de señal DI |
| Drive/Bass/Mid/Treble con modelo Amp activo | Cuatro IDs separados demostrados en las capturas previas |
| Esos cuatro controles independientes con No Amp | No demostrados: esta captura sólo ofrece un ID no resuelto |
| NAM dentro del DSP del Spider | Sigue sin demostrar; CPU/memoria/ruta de ejecución desconocidas |

No hay que repetir por rutina otra captura de las cuatro perillas. Para seguir tocando NAM se puede conservar No Amp/No Cabinet y manejar Gateway desde REAPER. Para ensayar el puente de cuatro controles **sin comprar nada**, se puede usar una guitarra DI ya grabada en REAPER mientras el Spider vuelve a un modelo Amp activo que emita los cuatro IDs: esa prueba separa el control de la entrada de guitarra en directo. El puente aún debe implementarse y probarse; no basta reproducir el PCAP hacia el dispositivo.

Si el objetivo exige guitarra en directo más las cuatro perillas físicas simultáneamente, una alternativa de arquitectura es una interfaz independiente para la guitarra y el Spider como controlador con modelo activo. Otra sería investigar una ruta documentada de audio/control separada. Ninguna alternativa autoriza comandos vendor desconocidos ni firmware modificado, y no se presenta aquí como integración ya funcionando.

## Artefactos y reproducción

- `control_events.csv/json`: los 650 valores no resueltos con frames/tiempos y bytes originales.
- `unresolved_events.jsonl`: los 650 eventos, **sin** asignarlos a controles NAM.
- `nam_control_events.jsonl`: vacío deliberadamente; no hay controles nombrados que exportar automáticamente en esta captura.
- `summary.json`, `independent_validation.json`, `controls_summary.json`, logs de extracción y validación.

```bash
python /workspace/analysis/captures/analyze_capture.py \
  /workspace/analysis/captures_noamp/input/SpiderV_NoAmp_Perillas.pcapng \
  --out /workspace/analysis/captures_noamp --control-midi-only
python /workspace/analysis/captures/independent_validate.py \
  --input /workspace/analysis/captures_noamp/input/SpiderV_NoAmp_Perillas.pcapng \
  --directory /workspace/analysis/captures_noamp
python /workspace/analysis/captures/decode_parker.py --directory /workspace/analysis/captures_noamp
python /workspace/analysis/captures/analyze_controls.py \
  --directory /workspace/analysis/captures_noamp --symbols /workspace/analysis/captures/device_symbols.json
```

No hay una tabla de símbolos nueva en esta captura; la referencia de nombres es explícitamente la tabla del primer archivo. El reconocimiento de `0xffffffff` como no resuelto no depende de atribuirle un nombre de esa tabla.
