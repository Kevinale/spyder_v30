# Primera demo: capturas Spider → Gateway en REAPER

Esta demo **no escucha las perillas en vivo**. Reproduce 1146 valores entrantes de tus capturas con modelo Amp activo: Drive, Bass, Mid y Treble. No utiliza los 650 valores no resueltos de No Amp. No transmite USB/MIDI, no cambia el Spider y no modifica firmware.

## Preparación en Windows

1. Extrae todo el ZIP en una carpeta. `Spider_Gateway_Demo.lua` y `controls_demo.csv` deben quedar juntos.
2. En REAPER usa la pista con tu **guitarra ya grabada** y Gateway. Desarma su botón rojo de grabación y apaga monitorización de entrada. Selecciona sólo esa pista.
3. Activa Gateway con el `.nam` que ya probaste. Activa su EQ para oír Bass/Middle/Treble. Baja el volumen de escucha y deja la automatización en **Trim/Read** o **Read**; la demo rechaza grabación/Touch/Write/Latch.
4. Abre **Actions → Show action list → New action → Load ReaScript** (o el botón **Load** de ReaScript según tu versión) y carga `Spider_Gateway_Demo.lua`.
5. Reproduce la guitarra grabada y ejecuta esa acción con **Run**. La ventana muestra una cuenta atrás de tres segundos. Mira cómo cambia Gateway: **Drive → Input**, después **Bass**, **Mid → Middle** y **Treble**. La demo dura unos 35 segundos. Cierra su ventana o pulsa Esc para detenerla.

No tienes que mover las perillas durante esta demo. El Spider puede conservar No Amp/No Cabinet: aquí los datos de control proceden del CSV. **No hace falta otra captura para esta prueba.**

## Qué modifica

- Sólo los cuatro parámetros identificados de un único Gateway en la pista seleccionada.
- Drive se convierte a **ganancia de entrada entre −12 y +6 dB** usando el formato de parámetros del propio plugin. No modifica el Drive interno del modelo entrenado.
- Si el plugin no ofrece un formato dB verificable, **Drive se omite**, sin recorrer a ciegas todo el rango de ganancia. La ventana lo indica.
- Bass/Mid/Treble recorren sus rangos normalizados de Gateway; esto no promete la misma EQ del Spider.
- Cada fase restaura los valores iniciales antes de probar el siguiente control. Al terminar o cerrar, restaura los valores iniciales de los parámetros mapeados. No cambies manualmente esos parámetros durante la demo. No cambia volumen de pista, modelo, IR, dispositivos o rutas.
- No inicia ni detiene el transporte: pulsa Play/Stop tú. No guarda el proyecto ni escribe automatización. Si Gateway se elimina o cambia de posición/identidad durante la prueba, se detiene para no modificar otro efecto.

## Si no encuentra los parámetros

La detección usa nombres explícitos Input/Input Gain/Input Level, Bass, Mid/Middle y Treble. Si no reconoce todos, abre la consola con la lista de índices **base 0** y pide cuatro números; `-1` omite un control. No adivines: copia los índices junto a los nombres correspondientes. Envía esa lista si necesitas ayuda. Si no encuentra Gateway, comprueba pista seleccionada y nombre del plugin; no cambies a otro efecto sin revisar el mapeo.

## Validación y alcance

Se comprobó sintaxis y lógica con Lua embebido y un entorno REAPER simulado: parsing de 1146 eventos, detección de parámetros, ganancia acotada, fases independientes, restauración, cancelación, exclusión de grabación y omisión segura cuando no hay formato dB. **No se ejecutó en tu instalación de REAPER/Gateway**; esa compatibilidad se comprueba con esta prueba. El ensayo no demuestra latencia, estabilidad ni escucha USB en vivo.

Los tiempos de captura originales se conservan en CSV, pero cada fase de demostración se escala a ocho segundos, con un segundo entre fases. No es una medición ni reproducción de tiempos físicos originales. Las dos capturas fuente son sesiones distintas y no se presentan como una sola grabación.

Una vez confirmada la compatibilidad Gateway, la siguiente etapa es implementar el receptor pasivo USB en vivo. No se presenta esta demo como ese receptor ni resuelve la falta de cuatro IDs separados en modo No Amp.
