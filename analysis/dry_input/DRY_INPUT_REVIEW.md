# Revisión dirigida: señal limpia USB conservando controles Amp

**Corrección posterior importante:** se encontró AmpEnable en la tabla recibida del dispositivo y AmpEnableState=1 dentro de GuitarProc en un preset real. El límite de la traducción amp/@enabled descrito aquí NO descarta ese control directo. Aún no se ha leído/escrito en vivo ni demostrado su efecto. La revisión que sustituye esa interpretación está en `../firmware/revisit/REVISIT_REPORT.md`.

## Resultado

No se identificó una ruta USB limpia independiente del modelo Amp ni un selector de grabación documentado en el material inspeccionado. Esto no demuestra que el firmware carezca de una ruta no documentada. No se propone habilitarla mediante setters, IOCTL ni transferencias vendor especulativas.

La revisión usa exclusivamente archivos existentes y Ghidra estático; no se ejecutaron binarios Windows extraídos, ni se comunicó con el dispositivo. No se modificaron originales.

## Evidencia de descriptores, confianza alta para lo anunciado

`check_routing.py` verifica las tres capturas (Drive, tono y No Amp). En las tres, frame 22, el descriptor de configuración comienza en offset absoluto PCAPNG 2784 (`0xae0`), longitud 290 (`0x122`). Los bytes de configuración son idénticos. Ver `routing_evidence.json`, con hashes de fuentes y todos los descriptores.

| Offset dentro de configuración | Evidencia | Interpretación y límite |
|---|---|---|
| 171 / 180 | Interfaz 3, alternates 0 / 1 | Sólo un alternate de captura con datos |
| 196 | `0e2402010202100280bb0044ac00` | Formato tipo I, 2 canales, 2 bytes/muestra, 16 bits, 48.000/44.100 Hz |
| 210 | `09058325c400010000` | Endpoint isócrono IN `0x83`, paquete máximo 196; usage 2 (datos con feedback implícito) |
| 226 / 235 | Interfaz 4, alternates 0 / 1 | Reproducción host→equipo |
| 251 | `0e2402010202100280bb0044ac00` | Mismo formato estéreo de reproducción |
| 265 | `09050405c400010084` | Endpoint isócrono OUT `0x04`, asociado a sincronización `0x84` |
| 281 | `090584110400010400` | Endpoint IN `0x84`, usage 1, máximo 4 bytes: feedback, no audio DI adicional |

No hay una segunda pareja de canales de captura ni un Selector Unit estándar (subtipo AudioControl 5) en esta configuración. Esto descarta una segunda entrada **anunciada** en estos descriptores; no excluye un cambio de origen dentro de los dos canales mediante firmware. El tipo de terminal no prueba si el audio es limpio/procesado. El propietario ya había probado ambos canales y comunicado cambios con Amp; no se infiere señal limpia sólo por ser Left/Right.

## Recursos y código, confianza alta en contenido, limitada en capacidades ocultas

- `remote/resources/amps.models.json`, modelo `Bypass`, ID `131072`, nombre `No Amp`, declara únicamente `@volume`, default 0,57, y `cablink=@NoCabinet`. `AssetDefs.plist`/`resources/assets.json` coinciden en el único parámetro de esa entrada.
- Ninguno de los 79 assets de categoría Amp declara un parámetro `@enabled`. El preset Parker tampoco incluye ese campo en Amp; sí aparece en efectos. No hay aquí un bypass Amp separado que permita asegurar conservación de Drive/Bass/Mid/Treble. La ausencia de metadatos no prueba que el firmware rechace todos los parámetros no declarados.
- `captures/device_symbols.json` contiene símbolos recibidos del dispositivo: `GuitInputGain` índice 890/offset de cadena 21814; `GuitProcInputGain` 896/21900; `GuitProcOutputGain` 899/21945; `USBOutLevel` 900/21964; `USBInLevel` 901/21976. Son índices de tabla, no comandos. No se identificaron tipo, alcance ni semántica de selección de fuente para esos nombres; no se equiparan ajustes de nivel con un tap de audio limpio.
- Búsqueda de literales `ldstr` en el IL completo de Remote para USB/dry/unprocessed/reamp/recording/monitor: cero coincidencias. No hay una opción de UI demostrada por esa búsqueda; podrían existir rutas dinámicas o recursos sin literales.
- Ghidra adicional: `remote/native/audio_bypass_targets.txt`, `APIV3EngineDLL.dll`, cadena `BypassGlobalEQ` VA `0x10175af0`, offset de archivo `0x1740f0`, xref `0x10084235`. La función `FUN_10084100`, VA `0x10084100`, RVA `0x84100`, offset `0x83500`, contiene tabla de nombres GlobalLow*/GlobalMid*/GlobalHigh*/GuitarOnlyGlobalEQ/BypassGlobalEQ. El valor local asociado al último nombre es `0x1a`, **no identificado como opcode USB**. Es evidencia de nomenclatura de EQ global, no de bypass Amp o DI. El cliente contiene código compartido entre familias; no se demuestra disponibilidad en el 30.

La consulta al sitio oficial de manuales `https://line6.com/support/manuals/spiderv30mkii/` fue rechazada por el proxy de esta nube (403 al establecer túnel). No se consultó el manual ni se cita como evidencia de ausencia de DI.

## Pruebas reales comunicadas por el propietario en esta conversación

Estas observaciones son del propietario, no mediciones instrumentadas en esta nube:

1. Con Amp activo y Remote abierto, el puente en vivo mueve los cuatro parámetros en Gateway: Drive→Input, Bass→Bass, Mid→Middle, Treble→Treble.
2. Reproduciendo únicamente una grabación desde REAPER, sin guitarra sonando y con monitorización apagada, cambiar los modelos Amp no cambia el sonido reproducido. Compatible con retorno USB que evita ese modelado; no prueba ausencia de cualquier EQ/limitador ni topología completa.
3. La entrada de guitarra grabada sí cambia al cambiar el modelo Amp: captura procesada en esa condición.
4. Con No Amp, los cuatro controles de Gateway no se mueven mediante el puente actual. Concordante con captura No Amp: 650 notificaciones de parámetro `0xffffffff`, no cuatro IDs diferenciados. No se interpreta ese parámetro como Volume.

## Decisión práctica

La configuración funcional actual para NAM externo con entrada sin modelado Amp es No Amp + No Cabinet y efectos desactivados, con parámetros de Gateway manejados desde REAPER. Se llama limpia en sentido funcional, no DI bit a bit verificada.

Conservar simultáneamente cuatro controles Amp y una entrada limpia independiente no queda resuelto por esta revisión. Una entrada de guitarra externa separaría audio y control, pero es una alternativa de arquitectura, no una compra imprescindible ni una configuración ASIO dual ya validada. No tratar un modelo clean como señal sin procesamiento; mover sus perillas seguiría cambiando el audio antes de NAM.

Una futura investigación puede revisar controles en modo FX o documentación oficial accesible; ni un modo FX con cuatro valores independientes sin alterar audio ni un selector USB limpio están demostrados. Antes de pedir nuevas capturas, definir una hipótesis concreta y una comprobación reversible en la UI oficial. No enviar mensajes desconocidos para buscar un bypass.

NAM dentro del amplificador continúa sin demostrar: esta revisión no identifica CPU/DSP, RAM ni ejecución de código.

## Reproducción

`python /workspace/analysis/dry_input/check_routing.py`

Pasa las comprobaciones de las tres configuraciones, formatos/endpoints, No Amp y recursos Amp. Ghidra se ejecutó sobre el proyecto Native existente con `-process APIV3EngineDLL.dll -noanalysis -postScript TargetEvidence.java ... 10175af0`; log en `remote/native/audio_bypass_targets.log`.
