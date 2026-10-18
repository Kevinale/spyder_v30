# Ensayo integrado Spider/Gateway de20 segundos

Estado: además de los tests simulados, el propietario confirmó funcionamiento real integrado en Windows/REAPER/navegador: Gateway audible con bypass activo y las cuatro perillas moviendo sus controles. Ensayo limitado20s. Resultado en OWNER_RESULT.json; no hay medida de latencia ni separación del sonido directo.

## Componentes y propósito

- `Start_Integrated.ps1`: en OTRA consola Windows PowerShell elevada, lee la página local del ensayo anterior8767, agrega el enlace y sirve una copia independiente en localhost8768. No descarga programas de internet. Una vez copiada la página base, no depende de que8767 siga sirviendo, aunque sus puertos MIDI deben estar desconectados. La fuente debe contener el ensayo ya entregado con hook de notificaciones. Esta versión todavía requiere la página anterior al arrancar; no atribuir independencia de arranque total.
- `link.js`: reutiliza exactamente el ensayo20s autorizado (snapshot/GET/flag0/GET/modelo retenido/restore1). Publica por HTTP local estado activo y valores Drive/Gain, Bass, Mid, Treble; no añade comandos de dispositivo. Un token aleatorio local en cabecera evita aceptar POST ajenos. CSP sólo permite conexiones al mismo origen. El servidor valida longitud/campos/números/rangos antes de escribir un archivo TEMP compartido. No envía datos fuera del PC.
- `Spider_Gateway_Integrado.lua`: lee `%TEMP%/SpiderGateway-integrated.txt`, exige heartbeat nuevo, sesión estable, datos válidos y flag activo; escribe únicamente cuatro parámetros Gateway y monitorización de la pista. Drive/Gain va a Input acotado-12..+6dB; los demás a EQ. Se omite Input si el formato de dB no es válido. No envía MIDI ni USB; USBPcap ya no es necesario.

## Preparación y orden

1. Bypass anterior restaurado1 y página anterior Desconectada. Remote: modelo Amp activo, No Cabinet, FX apagados; cerrar Remote. Volumen bajo.
2. REAPER ASIO Spider, pista con Gateway activo y modelo NAM cargado; EQ de Gateway activo. Pista armada, monitor inicialmente apagado, transporte detenido. No ejecutar el puente viejo/SpiderLive/Demo junto a este script ni habilitar MIDI Spider en REAPER: el navegador necesita su puerto. Audio ASIO y MIDI del navegador deben comprobarse juntos en Windows.
3. Crear un NUEVO ReaScript con el nombre del archivo Lua; no reemplazar los anteriores. Iniciar el servidor/página integrada y el script Lua antes de pulsar prueba. Ambos comparten TEMP del mismo usuario de Windows; elevación con otro usuario puede romper esa ruta.
4. En página8768, Conectar y leer y Probar bypass20s. Mantener página visible. Lua enciende monitor únicamente mientras hay bypass confirmado publicado/heartbeat fresco. Tocar y mover cuatro perillas; comprobar parámetros de Gateway.
5. Al finalizar, la página publica OFF y espera500ms antes de ejecutar restauración original. Lua apaga monitor y restaura sus parámetros. Se requiere confirmación del flag1 antes de cerrar la página. El timer/browser suspendidos/USB perdido pueden impedir restaurar el equipo; no se afirma garantía. Expiración de heartbeat corta monitor de REAPER en hasta1,5s después del último cambio de secuencia, sin depender de reloj civil compartido.

## Límites

No es una sesión permanente: conserva límite20s de las pruebas autorizadas. No altera firmware ni guarda presets. Los giros cambian el estado de edición de parámetros originales como ya ocurría; sólo AmpEnable y los valores de Gateway son restaurados por los respectivos componentes. El script termina con monitor apagado; no restaura un monitor originalmente encendido.

La ruta de sonido directo del Spider puede mezclarse con el retorno procesado de Gateway: aún no se ha medido ni separado el nivel de monitor directo. Este ensayo verifica la combinación, no promete escuchar exclusivamente NAM ni latencia óptima. No se cambia un gain interno no verificado para silenciar la ruta directa.

## Verificación

`python test_integrated.py`: usa el Lua real en Lua5.4/host REAPER simulado y archivo temporal real. Rechaza historial, rango inválido y cambio de sesión; cuatro parámetros, límitesInput, heartbeat caducado y OFF/escape restauran FX y apagan monitor.

`node test_link.js`: Drive38/Gain37 convergen a Input, ID desconocido ignorado, publicación local tokenizada y OFF anterior a restauración original. Estos tests de laboratorio no demuestran PowerShell/Win32/ASIO por sí solos; la confirmación real posterior proviene del propietario, como se indica arriba.
