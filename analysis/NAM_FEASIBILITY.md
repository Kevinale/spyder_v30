# Factibilidad de Neural Amp Modeler en Spider V 30 MkII

**Integración funcional confirmada por el propietario:** en el ensayo integrado20s escuchó Gateway al activar el bypass y confirmó que las cuatro perillas movían sus controles. La combinación guitarra USB sin modelado Amp audible + NAM/Gateway en PC + controles físicos está demostrada funcionalmente para esa sesión, sin modificar firmware. No implica NAM interno, transparencia bit a bit, latencia medida ni producto de uso continuo. Restauración comprobada en ensayos anteriores; sin log final de esta ejecución concreta. Evidencia: `integrated_trial/OWNER_RESULT.json`.

**Entrada USB con bypass comprobada funcionalmente por el propietario:** grabó guitarra desde Spider en REAPER con Gateway apagado, durante la prueba AmpEnable1→0→1, y al reproducir informó distorsionada→limpia→distorsionada. Esto respalda bypass audible de la captura USB reteniendo el modelo, además de las cuatro perillas identificadas en ensayos anteriores (Drive físico como Gain37 en Line6BigBottom). No es prueba bit a bit ni medida objetiva; falta integración simultánea completa con Gateway y comprobación de monitorización directa. No se modificó firmware. Registro: `amp_enable_reader/OWNER_TRIAL_RESULT.json`.

**Drive también identificado durante bypass:** el diagnóstico real del propietario con Line6BigBottom/modelo180 recibió `Amp.Gain`, grupo42/parámetro37/tipo4, rango0–1. AmpEnable permaneció0 tras los movimientos y se restauró1. El contador anterior sólo contaba Drive38 y por eso mostraba0. El puente Lua ahora acepta37 y38 como la perilla de entrada/Drive; comprobación con fixtures sintéticos basados en esos datos y regresiones de capturas en `live_bridge/gain_alias_validation.json`. El script actualizado todavía debe copiarse al Windows del usuario. Ya hay evidencia de los cuatro controles a través de las pruebas; la captura USB limpia con el flag0 y su integración completa con Gateway siguen pendientes.

**Prueba posterior del propietario: bypass audible conseguido.** El programa puso AmpEnable=0, verificó el mismo modelo, recibió Bass19/Mid26/Treble27 eventos, releyó0 al final y restauró1 con lectura confirmada. El propietario informó guitarra limpia durante la prueba. Drive registró0 y sigue pendiente; tampoco se ha confirmado todavía la captura USB limpia con este flag ni NAM/Gateway y cuatro controles simultáneos. No se modificó firmware. Evidencia y límites: `amp_enable_reader/OWNER_TRIAL_RESULT.json`. Esta prueba supera las conclusiones históricas de ausencia de un bypass identificado.

**Pista nueva antes de modificar firmware:** `AmpEnable`/`AmpEnableState` existen en la tabla del Spider y el edit buffer capturado contiene el estado booleano1 en GuitarProc, independiente del campo de modelo Amp. Debe comprobarse si permite bypass manteniendo controles; no está demostrado ni se ha cambiado. La ruta genérica `amp/@enabled` del cliente no cubre esa posibilidad y su ausencia no la descarta. NAM interno continúa sin arquitectura/ejecución demostradas. Véase `firmware/revisit/REVISIT_REPORT.md`.

**Estado actualizado tras pruebas del propietario:** Gateway/NAM en PC recibe los cuatro controles del Spider en vivo con Amp activo. Con No Amp, el puente actual no recibe esos cuatro parámetros distinguibles. El retorno USB reproduce la grabación sin cambiar al seleccionar Amp; la entrada USB de guitarra sí lleva ese modelado. No se halló un selector limpio independiente en la revisión dirigida de descriptores, recursos e IL/Ghidra. Usar No Amp con controles desde REAPER es funcional; señal limpia + cuatro controles Amp simultáneos sigue sin resolver. NAM interno continúa sin demostrar. Véase `dry_input/DRY_INPUT_REVIEW.md`. Los estados de integración pendiente que siguen son históricos.

**Prueba No Amp posterior:** el propietario comprobó audio sin distorsión audible con No Amp/No Cabinet y Gateway desactivado, y distorsión al activarlo. Esto valida funcionalmente NAM/Gateway **en el PC**, no dentro del Spider ni una señal bit a bit transparente. La captura en esa condición contiene 650 eventos tipo float con parámetro no resuelto `0xffffffff`; no aparecen los IDs separados de las cuatro perillas. La ruta de audio y el mapa de controles no deben darse por simultáneamente resueltos. Ver `captures_noamp/CAPTURE_ANALYSIS.md`.

**Ampliación de controles:** una segunda captura prueba Bass/Mid/Treble con 293/356/357 notificaciones IN, rangos observados 0–1, sin setters salientes. Ahora están identificados **Drive, Bass, Mid y Treble** en sesión Remote. Esto completa el mapa básico para diseñar un puente externo, pero no equivale a ejecutar NAM dentro del amplificador. Ver `CONTROLS_MAP.json` y `captures_tone/CAPTURE_ANALYSIS.md`.

**Actualización, 17 de octubre de 2026:** hay telemetría real de la perilla Drive hacia el PC con Remote en sesión: 140 valores identificados y exportados offline. Esto resuelve la existencia de datos de ese control para investigar un puente NAM externo. No se ha implementado/probado el puente en vivo y no cambia la conclusión sobre NAM interno: DSP, memoria y ejecución siguen sin verificar. Evidencias en `captures/CAPTURE_ANALYSIS.md`.

Fecha de consulta inicial: 14 de octubre de 2026. **Conclusión: no se puede demostrar ejecución interna de NAM con la información disponible. Tampoco se ha demostrado que sea imposible.** Falta identificar procesador, memoria libre, periféricos de audio, toolchain y mecanismo de ejecución. Un motor externo conserva una vía experimental más accesible; Drive ya tiene evidencia USB en la actualización del 17 de octubre, mientras las demás perillas y la integración en vivo siguen pendientes.

Actualización del 15 de octubre tras analizar Remote: la conclusión interna no cambia. Ahora hay evidencia de callbacks nativo→UI con `groupID`, `paramID`, valor y booleano nominal `deviceTriggered`, y recursos Parker con controles `@tweakgroup/@tweakparam` y niveles USB. Esto hace más concreta la investigación de un puente externo, pero no demuestra que una perilla física emita paquetes espontáneos, sus IDs ni formato. Los 11 `.models` del editor son catálogos JSON; no contienen un motor NAM ni prueban soporte para cargar `.nam`. Evidencias en `remote/MANAGED_ANALYSIS.md` y `remote/RESOURCE_ANALYSIS.md`.

## Fuentes de implementación verificadas

Se descargaron, sin ejecutar, archivos de NeuralAmpModelerCore upstream:

| Fuente URL | Copia local | Evidencia |
|---|---|---|
| https://raw.githubusercontent.com/sdatkinson/NeuralAmpModelerCore/main/README.md | `research/nam_readme.txt` | Biblioteca DSP C++, Eigen, herramientas `loadmodel` y `benchmodel`; advertencia de alineamiento/vectorización |
| https://raw.githubusercontent.com/sdatkinson/NeuralAmpModelerCore/main/NAM/lstm.h | `research/nam_lstm.txt` | LSTM con matrices float, estados recurrentes, varias capas y tamaño oculto configurable |
| https://raw.githubusercontent.com/sdatkinson/NeuralAmpModelerCore/main/NAM/lstm.cpp | `research/core_NAM_lstm.cpp` | Implementación concreta para verificar layout, operaciones y activaciones |
| https://raw.githubusercontent.com/sdatkinson/NeuralAmpModelerCore/main/NAM/wavenet/model.h | `research/core_NAM_wavenet_model.h` | WaveNet por arreglos de capas, condicionamiento y buffers |
| https://raw.githubusercontent.com/sdatkinson/NeuralAmpModelerCore/main/NAM/wavenet/model.cpp | `research/core_NAM_wavenet_model.cpp` | Implementación WaveNet |
| https://raw.githubusercontent.com/sdatkinson/NeuralAmpModelerCore/main/NAM/convnet.h | `research/core_NAM_convnet.h` | ConvNet con canales, dilataciones, grupos y bloques |
| https://raw.githubusercontent.com/sdatkinson/NeuralAmpModelerCore/main/NAM/dsp.h | `research/core_NAM_dsp.h` | Interfaz DSP y frecuencia esperada del modelo |
| https://raw.githubusercontent.com/sdatkinson/neural-amp-modeler/main/nam/models/wavenet/_wavenet.py | `research/nam_configs.txt` | Campo receptivo, configuración y exportación de frecuencia |

Confianza alta para estas propiedades del código capturado. `main` es mutable: las copias locales y sus hashes en el manifiesto de investigación permiten conservar la evidencia; no se atribuye una versión inmutable ni se afirma compatibilidad con todos los modelos históricos. No se recibió un archivo `.nam` objetivo, por lo que **no hay tamaño o rendimiento medido de un modelo concreto**.

## Cómputo y memoria: presupuesto explícito

MAC significa multiplicación y acumulación; no equivale automáticamente a un ciclo. Las siguientes cifras son cálculos de arquitectura, **no benchmarks**, y excluyen overhead, activaciones, transporte, cabinet IR, efectos y UI. Ejemplos mono a 48 kHz, float32 y una capa LSTM con entrada escalar y salida escalar:

`MAC/muestra ≈ 4 H (I + H) + H`; `pesos ≈ 4 H (I + H) + 4 H + H + 1`.

| Ejemplo hipotético | MAC/muestra | MAC/s a 48 kHz | Pesos float32 aproximados |
|---|---:|---:|---:|
| LSTM H=8, I=1 | 296 | 14,208 millones | 1.316 bytes |
| LSTM H=16, I=1 | 1.104 | 52,992 millones | 4.676 bytes |
| LSTM H=32, I=1 | 4.256 | 204,288 millones | 17.540 bytes |

Los puntos son separadores de miles y la coma es decimal. Las activaciones sigmoid/tanh y estados se suman al coste; varias capas usan como entrada la salida oculta previa y elevan considerablemente el coste. Estos tamaños no son clases oficiales «nano/lite/standard», ni garantizan calidad suficiente.

Los cálculos de esta sección se reproducen con `python /workspace/analysis/nam_budget.py`; salida de esta ejecución en `research/nam_budget.json`. El script no ejecuta redes ni accede al dispositivo.

Para convolución causal densa por capa: `MAC/muestra ≈ K × Cin × Cout`; pesos float32 `≈ 4 × K × Cin × Cout` más sesgos. Ejemplo hipotético: 10 capas, K=3 y 16 canales en cada capa interna: término principal 7.680 MAC/muestra, 368,64 millones MAC/s a 48 kHz y 30.720 bytes de pesos. Primera/última capa reales y proyecciones cambian el resultado. No se presenta como un preset NAM existente.

En WaveNet deben sumarse convoluciones dilatadas, proyecciones residuales, skip/head y posibles gates/condicionamiento según el JSON concreto; los modelos con más canales cuestan aproximadamente cuadráticamente en los términos densos. Etiquetas comerciales de tamaño no sustituyen leer la configuración.

La dilatación no reduce el número de pesos de una convolución de ancho fijo, pero aumenta su historia. Para una cadena causal simple de stride 1: `R = 1 + Σ (K_l−1) d_l`. Un presupuesto de buffers de historia sin optimización es `4 Σ Cin_l (K_l−1) d_l` bytes, además de pesos, estados y scratch. Diez capas de K=3, C=16 y d=1,2,...,512 requieren aproximadamente 130.944 bytes sólo para esos historiales float32 y tienen R=2.047 muestras. La implementación concreta puede reservar más memoria por bloques/alineación o organizarla de otra forma. RAM libre, ancho de banda y caché son tan importantes como tamaño del `.nam` en disco.

## Latencia y requisitos de portabilidad

Una red causal no necesita esperar todo el campo receptivo: historia de 2.047 muestras no implica 42,65 ms adicionales de latencia. Sí requiere inicialización/estado y quizá calentamiento. La latencia extremo a extremo suma conversiones, buffers de dispositivo/host, USB, ejecución y cualquier resampling. A 48 kHz, un bloque dura 1,333 ms (64 muestras), 2,667 ms (128) o 5,333 ms (256); ida y vuelta puede involucrar varios buffers. No hay una cifra de latencia medida para este amplificador.

Hay que respetar la frecuencia de entrenamiento/exportación del modelo. Ejecutar una red recurrente a otra tasa cambia su comportamiento; cualquier resampling necesita coste y latencia presupuestados. Para tiempo real, el peor tiempo de ejecución por bloque, más servicios compartidos, debe quedar por debajo de N/fs con margen; un promedio favorable no descarta underruns.

Un DSP con FPU/SIMD y C++ adecuado podría permitir un port del core o kernels equivalentes; uno de punto fijo requeriría cuantización/implementación y comparación numérica/auditiva. No basta copiar un plugin x86/Windows al firmware. Eigen, alineación, runtime, heap y soporte de activaciones deben revisarse; reducir precisión puede cambiar estabilidad/calidad. Falta evidencia para afirmar que el hardware del Spider cumple cualquiera de estas condiciones.

## Opciones y criterio de decisión

| Ruta | Estado | Prueba necesaria |
|---|---|---|
| NAM interno con DSP/CPU originales | No demostrado; alto trabajo de integración y arranque | Identidad de silicio, RAM libre, mapa y ABI, benchmark representativo, acceso seguro al audio y carga de código |
| NAM externo con audio USB del amplificador | Descriptores reales anuncian PCM estéreo 16 bits a 44,1/48 kHz; ruta de audio y latencia sin medir | Compatibilidad del host, captura/reproducción y latencia de bucle en una fase posterior; evitar realimentación y doble modelado |
| Perillas originales → NAM externo por USB | Cuatro IDs demostrados con modelo Amp activo; No Amp entrega un único parámetro no resuelto; puente NAM en vivo no probado | No asumir cuatro controles independientes en bypass; separar señal/control para un prototipo o investigar otra ruta documentada |
| Pantalla original como UI de motor externo | Sin evidencia | Saber si existe telemetría o protocolo documentado; no asumir control de pantalla por USB |

Los mensajes host→amplificador presentes en un editor no prueban que las perillas emitan eventos en sentido inverso. MIDI CC no debe asumirse: podría tratarse de transferencias vendor-specific, SysEx, polling o ningún evento. Un dispositivo USB tampoco actúa automáticamente como host de otro equipo USB.

La captura nueva sí aporta evidencia del sentido inverso para Drive: notificaciones SysEx, opcode `0x04`, valor float32; no es MIDI CC. `nam_control_events.jsonl` exporta los 140 eventos recibidos, sin enviar nada al amplificador. Un NAM no condicionado suele modelar una configuración fija: mapear Drive a ganancia de entrada u otro parámetro del host requiere diseñar y probar esa relación; no equivale automáticamente a variar el Drive del amplificador entrenado.

La segunda captura añade 1006 eventos de tono exportados en `captures_tone/nam_control_events.jsonl`. Para un NAM no condicionado, Bass/Mid/Treble tendrían que mapearse a un EQ del host u otros parámetros realmente disponibles; no se promete equivalencia con el circuito/algoritmo de tono del Spider. Los tiempos de las dos capturas son relativos a archivos distintos y no deben fusionarse como una sola sesión.

Para probar el puente sin otra interfaz se puede reproducir una DI ya grabada en REAPER y mantener un modelo Amp activo en el Spider para sus perillas: no se usa entonces su entrada de guitarra en directo como audio de prueba. Para guitarra en directo y cuatro controles, una interfaz de instrumento separada y Spider en modo Amp activo es una alternativa de arquitectura, todavía por integrar/probar. Con No Amp se puede seguir usando Gateway desde la UI del host; no hay evidencia de que esos 650 valores no resueltos sean cuatro controles ni de que sean Volume.

## Próxima validación útil

Seleccionar un `.nam` concreto, leer JSON/configuración/pesos sin ejecutarlo y calcular parámetros/historia; después usar `loadmodel`/`benchmodel` de fuente confiable en un host externo identificado, registrando CPU, commit, compilador, flags, sample rate, bloque y peor caso. Ese benchmark sólo valida ese host; no extrapola rendimiento al DSP desconocido. Las primeras mediciones sobre el amplificador deben ser de lectura, sin firmware modificado ni escrituras directas de memoria, como se detalla en NEXT_EXPERIMENTS.md.


## Estado tras las pruebas de monitorización directa

Modo continuo externo y cuatro perillas confirmados por propietario. Escucha exclusivamente NAM aún no resuelta: persiste guitarra directa y los tres mutes ensayados cortan también USB. NAM interno continúa sin demostrar. Informe actual `direct_monitor/FIRMWARE_ROUTING_LIMITS.md`.


## Identificación física posterior de U6

Fotos nuevas del propietario revelan **Analog Devices ADSP-BF707KBCZ-4**, con marcado Blackfin legible. Evidencia de alta confianza: `hardware_photos/PROCESSOR_IDENTIFICATION.json` y `bf707_marking_detail.png`. Esto sustituye las menciones anteriores de CPU/DSP totalmente desconocido. Reloj efectivo, memoria libre, formato ejecutable/carga y viabilidad NAM siguen sin establecer. Siguiente análisis debe contrastar BF70x/Blackfin con documentación de boot y formato del SVU; no asumir que identificar ISA convierte el payload opaco en código válido ni identifica punto de mute. No se modificó/cargó firmware.


## Line6Updater1.28 aportado: análisis estático completado

Tres volúmenes validados, instalador reconstruido y223archivos extraídos sin ejecutar PE. Se identificó ruta específica Parker/SpiderV: motor L6MidiFileDumpUpdateEngine, extracción/inflate SVU y codificación7bit reversible. La pista convertUpdateImage/make_update pertenece a ramaG10T(componente1), no al firmware principal(componente0). No se obtuvo decodificador del payload Blackfin ni mute independiente ni viabilidad NAM interna. Informe con funciones, fuentes, validaciones y límites: `updater/UPDATER_ANALYSIS.md`. Originales intactos: `updater/final_integrity.json`.


## Actualización: comparación oficial declarada 2.02 / 2.05 (2026-10-17)

La muestra aportada como 2.02 tiene HEAD 0x02020030, producto 0x220000 y checksums coherentes. El payload extraído mide 3.060.448 bytes frente a 393.192 del 2.05. Hay regiones idénticas; la mayor a igual offset mide 163 bytes. No se ha identificado código ejecutable ni una vía para NAM interno. La espera de una segunda muestra queda resuelta. Evidencias, límites y siguiente análisis de lectura: `firmware/comparison/COMPARISON_REPORT.md`. No se ejecutó ni modificó firmware.


## Seguimiento de estructura interna — 2026-10-17

Se probaron once máscaras XOR periódicas inferidas del byte modal de 2.02 y aplicadas a ambas versiones; ninguna produjo una cadena Blackfin validada. No hay evidencia de un decodificador recuperado ni conclusión sobre cifrado. Los prefijos compartidos tampoco aparecen literalmente en los cuatro módulos host examinados. Detalles y límites: `firmware/structure/STRUCTURE_REPORT.md`. Se verificaron de nuevo ambos SHA-256 originales sin cambios. El siguiente requisito técnico es identificar el formato o implementación de carga del lado DSP mediante una fuente verificable. NAM interno sigue sin demostrarse.


## Revisión del cargador BF70x — 2026-10-17

Se encontró una referencia específica BF70x (`majbthrd/ldrshrink`) que respalda la estructura de cabecera de 16 bytes y checksum XOR. La búsqueda ampliada sin firma AD fija no identifica cadenas de tres o más bloques en ninguna versión. El helper público `bf70x-bootloader` exige escribir RAM y está diseñado para BF706 EZ-Mini, por lo que no es un procedimiento pasivo para el Spider. La evidencia que falta es la interpretación del payload del lado del dispositivo. Detalles, commits y límites: `firmware/structure/LOADER_REVIEW.md`. Ambos SVU originales mantienen su SHA-256.

## Precedentes públicos revisados — 2026-10-17

GuitarML/Mercury documenta NAM con modelos de tamaño específico en Daisy Seed/Funbox, mono y sin cabina. El demo de oyama para RP2350 documenta A2-Lite por USB con dos núcleos a 300 MHz; no es un pedal analógico completo. No se encontró un port interno NAM para Spider V30/BF707 en las fuentes revisadas. No extrapolar rendimiento ni compatibilidad. Fuentes, límites y README conservados en `research/similar_projects/FINDINGS.md`.

## Preset Deity Crunch — 2026-10-17

El SVL6P aportado es JSON L6Preset v5 de 1670 bytes. Selecciona modelos ya presentes en Remote: BomberXTC, 4x12BritV30Studio y ClassicDistortion (este último desactivado), además de sus parámetros. No contiene un ejecutable ni pesos/arquitectura NAM. Convertir NAM a este preset no agrega el motor que requeriría el DSP. Evidencia y límites: `presets/deity_crunch/REPORT.md`. Original conservado; no importado al dispositivo.
