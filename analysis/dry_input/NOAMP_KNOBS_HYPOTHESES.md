# No Amp con cuatro perillas: hipótesis y límites

**Corrección posterior importante:** se encontró AmpEnable en la tabla recibida del dispositivo y AmpEnableState=1 dentro de GuitarProc en un preset real. El límite de la traducción amp/@enabled descrito aquí NO descarta ese control directo. Aún no se ha leído/escrito en vivo ni demostrado su efecto. La revisión que sustituye esa interpretación está en `../firmware/revisit/REVISIT_REPORT.md`.

## Localización del problema observado

`check_noamp_identity.py` comprueba los 650 cuerpos IN/opcode4 de `captures_noamp/logical_messages.json`: los primeros 12 bytes son idénticos, `[42,0xffffffff,4]`; sólo los últimos 4 bytes (float32) varían. Hay movimiento comunicado por el equipo; no se afirma que las perillas estén eléctricamente desactivadas. Lo que falta en ese cuerpo es una identidad distinta para cada control. El puente ya lee USBPcap antes del consumidor de Remote, de modo que dibujar más sliders en Remote no añade a esos paquetes una identidad perdida. Tampoco se usan secuencia/tiempo para adivinar la perilla; son metadatos de transporte, no identificación física demostrada.

`FUN_100987c0` en `captures_noamp/native_reserved_focused.txt` recibe esos IDs y sólo trata -1 como @model si type==1, que aquí no se cumple (type4). No se ha reconstruido la rutina del firmware que produce el -1; no se sabe si el equipo admite telemetría alternativa de ADC/encoders o reasignación de controles.

## Bypass manteniendo el modelo activo

Es una hipótesis técnica razonable: mantener un modelo que reconozca cuatro parámetros, pero evitar su DSP en la ruta de guitarra. Hace falta una función real en el firmware, no sólo una propiedad del editor. No se demuestra su existencia/ausencia por completo.

Nueva evidencia IL en `amp_enable_ui.il.txt`:

- `Editor::onEnableControlClicked`, token `0x0600029f`, RVA `0x176c4`, offset PE `0x158c4`: si el grupo actual es `amp` o `cab`, invierte `ampIsVisible`, llama a `setAmpCabMode` y retorna. Ese botón cambia la vista Amp/Cab; no solicita un bypass.
- Para otros grupos, la misma función consulta y escribe `graphSlot_EnabledState` mediante ParamValueServer. Existe por tanto un mecanismo genérico de activación en el cliente, pero la UI lo evita expresamente en la rama amp/cab. Esto no prueba que forzar esa propiedad en Amp funcione.
- `DeviceSpecificSignalFlowUtils::getSignalFlowItemEnabledStateForGroupID`, token `0x060004f1`, RVA `0x272ec`, offset `0x254ec`, consulta `graphSlot_EnabledState`. Una consulta genérica no demuestra soporte para todos los grupos/productos.
- Las traducciones nativas incluyen `graphSlot_EnabledState` y `@enabled` (`captures_noamp/native_reserved.txt`, `FUN_10020590`); ni esas traducciones ni el estado de UI son un contrato USB de bypass Amp validado.

No se envían mensajes @enabled/graphSlot_EnabledState arbitrarios al dispositivo. Para sostener esa vía se necesitaría seguir su despacho de familia Parker y handler del equipo o encontrar un uso real en una sesión oficial; falta ese soporte en la evidencia actual.

## Agregar un modelo neutro con cuatro controles

Los `.models` y AssetDefs son catálogos de nombres/IDs/parámetros del host. Editarlos puede cambiar lo que dibuja/envía Remote, pero no demuestra instalación de un algoritmo nuevo en el amplificador ni modificación de las asociaciones de controles del firmware. No Amp es ID131072 con único @volume declarado. Inventar otro ID o añadir Drive/Bass/Mid/Treble a ese catálogo no garantiza que el equipo los reconozca o que genere cuatro notificaciones distintas. No se realizó esa modificación ni se cargó un preset experimental.

Crear un modelo/patch que pase audio intacto pero siga notificando cuatro controles requeriría una capacidad de carga de DSP o un cambio en firmware que aún no se ha identificado. No se declara imposible; no hay método probado ni se autoriza flashear como parte de esta revisión.

## Otras vías aún sin demostrar

- Telemetría de controles físicos independiente del asset: no localizada en capturas actuales.
- Controles en modo FX usando parámetros que no afecten al audio con No Amp: hipótesis distinta. No está demostrado que permanezcan identificables con efectos desactivados ni que un giro no reactive efectos. No afirmar que ofrece cuatro controles limpios sin comprobarlo.
- REAPER/ReaScript puede recibir datos identificables y mapearlos, como ya hace el puente. No puede por sí solo implementar una ruta DSP ni crear un modelo dentro del Spider.

No se ejecutaron binarios originales ni se escribieron presets, firmware, memoria ni comandos de dispositivo durante estas comprobaciones.

## Seguimiento posterior de la pista graphSlot_EnabledState

Se exportó Ghidra adicional, sin ejecutar Windows ni acceder al equipo: `enable_dispatch.txt` y `enable_dispatch.log`. `FUN_10083c50` (VA0x10083c50) detecta parámetros que comienzan por `@`, llama a `FUN_10084570` y sólo traduce a `GuitarProc/<nombre firmware>` si la búsqueda devuelve un nombre. En esa rama no se observa un fallback de `amp/@enabled` hacia un parámetro ordinario.

En `FUN_10084570` (VA0x10084570), para @enabled y IDs Parker0x220000..0x220005 se elige el rango inclusivo0..10 de triples. Sus grupos son cab, gate, compressor, eq, wah, volume, fx1, fx2, fx3, reverb, looper. No hay amp ni AmpEnable. Cab sí tiene CabEnable. `check_enable_mapping.py` verifica el segmento contra los triples extraídos y genera `enable_mapping_validation.json`.

Esto estrecha la conclusión: la ruta de traducción examinada del cliente no resuelve amp/@enabled; no es sólo un botón oculto de la UI. No demuestra inexistencia de otra API/handler del firmware ni autoriza inventar AmpEnable o enviar Enable882 a Amp42. El símbolo genérico Enable del dispositivo no prueba que ese tuple tenga soporte o preserve perillas.

También se inspeccionaron `FUN_10097e50` (binding de grupo/modelo/estado para footswitch) y `FUN_100842c0` (clasificación por categoría). Son rutas de configuración; no identifican una opción de bypass Amp independiente para el objetivo. No se ejecutan ni se publican como instrucciones USB.

Siguiente hipótesis separada: comprobar mediante la UI oficial si modo FX del panel produce parámetros distinguibles con No Amp. Primero observar qué controles cambian en Remote; no afirmar que el audio permanece limpio ni que el puente actual los mapea. Un giro puede activar efectos. Sólo si hay telemetría distinguible y una asignación que preserve audio se justifica ampliar el puente. No se solicita otra captura general antes de esa observación concreta.

## Observación posterior del modo FX

El propietario informa que con No Amp los controles de comp/mod/delay/reverb/stomp cambian valores visibles en Remote; al mínimo se apaga el bloque. Si se apaga desde Remote con perilla en posición intermedia, un giro vuelve a activarlo. Esto descarta asumir bloque desactivado persistente mientras se gira. No se han obtenido todavía IDs USB de esos movimientos ni se ha modificado el puente para ellos.

Revisión del IL de `TweakSettings::.ctor`, token0x06000344/RVA0x1d17c/offset0x1b37c: registra `systemState/assetParamBinding_BoundToPedal`, `assetParamBindingChanged`, `presetDidChange`. `sendValuesToEngine` token0x0600034c escribe el booleano de asignación al pedal. Esta clase no prueba que las perillas FX sean libremente reasignables; no confundir binding a pedal con asignación a cada encoder.

Hipótesis de observación acotada siguiente: poner Mix de Mod en cero desde la UI oficial y observar si un giro físico mueve ese mismo Mix o un parámetro distinto conservando Mix=0. Si Mix aumenta, ese experimento no conserva mezcla seca y se descarta para ese modelo/asignación. Si Mix permanece cero, verificar después audio y telemetría antes de declarar solución. Mix cero no constituye por sí solo prueba bit a bit de transparencia ni solución para cuatro controles.
