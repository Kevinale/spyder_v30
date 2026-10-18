# Lector experimental AmpEnable (Windows10)

## Alcance

Lee la identidad universal MIDI, la versión, la tabla de símbolos y sus CRC; abre sesión con handshake de CRC y consulta exclusivamente GuitarProc/AmpEnable. La lista de operaciones admite Editor1/2/3/4/9 y valida cuerpos; no permite setters, carga de modelos/presets, actualizaciones ni acceso a memoria. El handshake establece estado transitorio de sesión; no se describe como captura puramente pasiva ni como ausencia de toda comunicación host→equipo.

El código es propio. No importa ni ejecuta el editor de terceros usado como referencia. No usa internet/CDN, no sube datos y no instala dependencias. La página se sirve desde un HttpListener Windows enlazado a localhost8766, no en la nube. No se cambia política de ejecución. No hay firmware modificado.

## Uso

1. Seleccionar un modelo Amp activo desde Remote. Guardar el proyecto REAPER si corresponde y cerrar Remote, REAPER, Spider_Live y otros consumidores MIDI para liberar los puertos.
2. Abrir WindowsPowerShell como administrador como ya se hizo para USBPcap. Pegar TODO el contenido de Start_Reader.ps1 directamente; no es necesario ejecutarlo como archivo .ps1 ni cambiar ExecutionPolicy.
3. Abrir la dirección que imprime el programa en Edge/Chrome actual, dar acceso MIDI/SysEx cuando el navegador lo pida y pulsar Conectar y leer. El permiso MIDI es una capacidad del navegador; no autoriza operaciones adicionales a las de este lector.
4. Copiar el resultado o error. No hay temporizador global de2min; cada solicitud tiene timeout10s.
5. Para cambiar a No Amp, pulsar Desconectar, cerrar pestaña, abrir Remote, seleccionar No Amp, cerrar Remote; reabrir la página y Conectar y leer. El servidor puede quedar abierto. No mantener ambos clientes MIDI conectados simultáneamente. Comparar resultados etiquetados por modo.
6. Al terminar, Desconectar y cerrar la ventana PowerShell para detener el servidor local.

Si hay una versión diferente, identidad diferente, CRC inválido, más de una pareja de puertos o una respuesta desconocida, se detiene en vez de adivinar. No interpretar un error de lectura como prueba de inexistencia de AmpEnable o de bypass. Un resultado0/1 tampoco demuestra efecto en audio ni conservación de perillas.

## Comprobaciones hechas en la nube

`node test_reader.js`: todos los mensajes IN/canal0 de la captura propia reensamblados byte a byte, incluyendo la tabla de22175bytes; 916CRC válidos y tabla alterada rechazada; setters bloqueados antes de enviar; sesiones simuladas con booleanos0/1; estado negativo y tipo inesperado rechazados; versión distinta detiene antes del handshake/consulta. Desconexión libera puertos en simulación. Resultados en validation.json.

Pendiente prueba REAL de WindowsPowerShell/HttpListener, permisos WebMIDI, driver y amplificador. No se presenta el host simulado como prueba del dispositivo. El lector aún no ha obtenido ningún valor nuevo del equipo real.
