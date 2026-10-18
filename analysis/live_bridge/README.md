# Puente experimental Spider V30 -> Gateway

Windows 10: ejecutar contenido de Receiver.ps1 en Windows PowerShell elevado; mantener Spider V Remote abierto, USBPcap2 direccion 4 como en las capturas del usuario. No ejecutar simultaneamente otra captura. El receptor usa USBPcap instalado; no instala ni ejecuta paquetes recibidos. Guarda PCAP temporal compartido en TEMP, maximo 120 segundos / aproximadamente 128 MiB; captura limitada a direccion 4 con snaplen 128. El archivo local contiene trafico USB, posiblemente fragmentos de audio; no se transmite.

Crear Spider_Live.lua en REAPER Actions/New ReaScript. Seleccionar una sola pista con Gateway y grabacion/monitorizacion desactivadas; usar audio previamente grabado, Remote con modelo Amp activo. EQ de Gateway debe estar activo. Ejecutar despues del receptor; omite eventos anteriores al inicio. Esc/cerrar restaura parametros. No reejecutar receptor mientras Lua siga abierto: cerrar Lua primero. Drive controla Input (-12..+6 dB), no un parametro propio de Drive NAM. Los eventos No Amp desconocidos no se enrutan.

Probado aqui: Lua 5.4 contra las tres capturas: 140 Drive; 293 Bass, 356 Middle, 357 Treble; 650 No Amp ignorados. Host REAPER simulado: historial omitido, registro parcial esperado, 1006 cambios nuevos, restauracion con Escape y rechazo de pista armada. Pendiente: ejecucion real PowerShell/USBPcap/REAPER en Windows. Si no identifica el dispositivo no aplica controles; controlador/direccion pueden cambiar tras reconexion.


## Variante Gain37

El propietario confirmó Amp.Gain42/37 al mover Drive en Line6BigBottom180 durante AmpEnable0; el contador Drive38 del ensayo no lo reconocía. codec.lua y Spider_Live.lua aceptan ambos37/38 como Drive→Input. No cambia límites-12..+6dB ni envía comandos al equipo. `python test_gain_alias.py` usa cuatro valores comunicados en frames sintéticos (no una captura nueva), comprueba cambio real de GatewayInput en el host simulado y restauración. Regresiones existentes pasan. Falta actualizar la copia del script en el Windows del usuario.
