# Opciones de bypass encontradas en Remote y en la tabla del equipo

**Integración funcional confirmada por el propietario:** en el ensayo integrado20s escuchó Gateway al activar el bypass y confirmó que las cuatro perillas movían sus controles. La combinación guitarra USB sin modelado Amp audible + NAM/Gateway en PC + controles físicos está demostrada funcionalmente para esa sesión, sin modificar firmware. No implica NAM interno, transparencia bit a bit, latencia medida ni producto de uso continuo. Restauración comprobada en ensayos anteriores; sin log final de esta ejecución concreta. Evidencia: `integrated_trial/OWNER_RESULT.json`.

**Entrada USB con bypass comprobada funcionalmente por el propietario:** grabó guitarra desde Spider en REAPER con Gateway apagado, durante la prueba AmpEnable1→0→1, y al reproducir informó distorsionada→limpia→distorsionada. Esto respalda bypass audible de la captura USB reteniendo el modelo, además de las cuatro perillas identificadas en ensayos anteriores (Drive físico como Gain37 en Line6BigBottom). No es prueba bit a bit ni medida objetiva; falta integración simultánea completa con Gateway y comprobación de monitorización directa. No se modificó firmware. Registro: `amp_enable_reader/OWNER_TRIAL_RESULT.json`.

**Drive también identificado durante bypass:** el diagnóstico real del propietario con Line6BigBottom/modelo180 recibió `Amp.Gain`, grupo42/parámetro37/tipo4, rango0–1. AmpEnable permaneció0 tras los movimientos y se restauró1. El contador anterior sólo contaba Drive38 y por eso mostraba0. El puente Lua ahora acepta37 y38 como la perilla de entrada/Drive; comprobación con fixtures sintéticos basados en esos datos y regresiones de capturas en `live_bridge/gain_alias_validation.json`. El script actualizado todavía debe copiarse al Windows del usuario. Ya hay evidencia de los cuatro controles a través de las pruebas; la captura USB limpia con el flag0 y su integración completa con Gateway siguen pendientes.

**Prueba posterior del propietario: bypass audible conseguido.** El programa puso AmpEnable=0, verificó el mismo modelo, recibió Bass19/Mid26/Treble27 eventos, releyó0 al final y restauró1 con lectura confirmada. El propietario informó guitarra limpia durante la prueba. Drive registró0 y sigue pendiente; tampoco se ha confirmado todavía la captura USB limpia con este flag ni NAM/Gateway y cuatro controles simultáneos. No se modificó firmware. Evidencia y límites: `amp_enable_reader/OWNER_TRIAL_RESULT.json`. Esta prueba supera las conclusiones históricas de ausencia de un bypass identificado.

**Lecturas reales posteriores del propietario:** el lector verificó identidad/versión/CRC y obtuvo `GuitarProc/AmpEnable` booleano1 con Amp activo y también1 con No Amp. No se cambió ese valor. Hay una prueba activa separada preparada para0 temporal y restauración verificada, aún sin autorización ni ejecución en el dispositivo; alcance y límites en `amp_enable_reader/TRIAL_REVIEW.md`. No interpretar ambos1 como prueba de bypass funcional.

**Hallazgo que amplía las conclusiones anteriores:** existe `AmpEnable`835 y `AmpEnableState`821 en la tabla recibida; el preset capturado contiene `GuitarProc/AmpEnableState=1`. La ausencia de `amp/@enabled` en la traducción de Remote sólo limita esa ruta del cliente, no demuestra ausencia de bypass en el equipo. Efecto runtime y conservación de perillas pendientes. `firmware/revisit/REVISIT_REPORT.md`.

**Prueba posterior realizada por el propietario:** seleccionó No Amp y No Cabinet en la UI; informó sonido sin distorsión con Gateway desactivado y distorsión al activarlo en REAPER. Es una prueba funcional de audio externo, no verificación de transparencia DI. La captura posterior sólo ofrece 650 eventos con parámetro `0xffffffff`/float, sin los cuatro IDs de las perillas. No se identifican esos eventos como Volume. Detalle en `captures_noamp/CAPTURE_ANALYSIS.md`.

Se revisaron los recursos originales, sin ejecutar el software ni enviar solicitudes al dispositivo, al evaluar la captura de pantalla del propietario.

## Evidencia

- `remote/extracted/Spider V Remote/res/amps.models`, entrada `symbolicID=Bypass`, `id=131072` (`0x20000`): nombre **No Amp**, enlace `cablink=@NoCabinet`. Sólo declara el parámetro `@volume`; no declara Drive/Bass/Mid/Treble en esa entrada.
- `remote/extracted/Spider V Remote/res/cabs.models`, entrada `symbolicID=@NoCabinet`, `id=16908288`: nombre **No Cabinet**, sin parámetros.
- La tabla recibida del dispositivo en la primera captura (`captures/device_symbols.json`) también contiene **Bypass**, índice 239/CRC32 `e8a48342`, cadena en offset 13518; y **No Amp**, índice 240/CRC32 `cece063c`, cadena en offset 13525. Por tanto no es únicamente una cadena hallada en una biblioteca compartida del host.

Confianza alta en la existencia de las entradas/nombres; el propietario ya seleccionó No Amp y comprobó funcionalmente el audio, como se indica arriba. No se identifica el botón o pestaña Amp/Cab de la imagen como interruptor de bypass por su apariencia.

## Prueba funcional siguiente

En la UI oficial del propietario, buscar el modelo No Amp fuera de la categoría British, y No Cabinet en selección de cabina. Desactivar los demás efectos en el estado de edición, sin guardar ni actualizar firmware. Registrar la configuración inicial para restaurarla. Se trata de cambios reversibles del estado de audio desde Remote, no de una prueba de USB estrictamente de lectura; el propietario ya está explorando ese flujo, pero nuestras herramientas no lo ejecutaron ni reprodujeron setters.

Grabar por USB con Gateway desactivado y monitorización apagada para comprobar la señal resultante. La selección debe quitar la simulación declarada de amp/cab; no prueba una ruta bit a bit transparente ni ausencia de todo filtro, ganancia o limitador interno.

**Dependencia del puente externo:** como No Amp sólo declara Volume, comprobar después si Drive/Bass/Mid/Treble siguen generando eventos en este modo. Las capturas previas prueban esos controles con un modelo de amplificador activo, no necesariamente con No Amp. No prometer señal sin modelado y todos los controles simultáneamente antes de observarlo.

La recomendación previa de interfaz externa fue prematura como siguiente paso: antes corresponde probar esta opción explícita. Una interfaz externa sigue siendo alternativa si No Amp no ofrece una señal adecuada o desactiva las perillas necesarias.


## Revisión posterior de ruta USB limpia

No se encontró un selector de entrada limpia independiente de Amp. El propietario verificó cuatro controles en vivo con Amp activo y ausencia de esos controles mediante el puente en No Amp. Descriptores, offsets, Ghidra y límites en `dry_input/DRY_INPUT_REVIEW.md`.
