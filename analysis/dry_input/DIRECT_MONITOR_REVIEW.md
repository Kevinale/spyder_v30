# Separación de guitarra directa y retorno USB

## Observaciones del propietario

Con AmpEnable0 y Gateway activo, bajar Output de Gateway deja guitarra limpia audible. La mezcla directa persiste. En una prueba posterior con SpiderGateway desconectado y Remote abierto, bajar Volume del modelo Amp a0 conservó reproducción de una grabación por USB, silenció guitarra local y dejó sin movimiento el medidor de entrada de REAPER al tocar. No se proporcionó una captura de audio de esta última prueba; evidencia funcional del propietario, no medida instrumental. No demuestra el mismo comportamiento con AmpEnable0. Volume no está validado como solución.

## Revisión estática del controlador

Los nombres IM_HWCFG_SET_ON_BOARD_MONITOR_GAIN y IM_HWCFG_GET_ON_BOARD_MONITOR_GAIN existen en driver/strings/5ca96e84c4dc_l6SpiderV.sys.txt (offsets de archivo0x380e0/0x38110) y bibliotecas Interposer. Ya estaban catalogados en USB_PROTOCOL_ANALYSIS.md. Son nombres compartidos; no prueban implementación para este equipo.

Se reabrió el proyecto Ghidra en modo readOnly/noanalysis, sin ejecutar binarios Windows. Resultado usb/monitor_gain_targets.txt y log homónimo. FUN_1400307b0 comprueba un bit de capacidad para un ID solicitado en un objeto host, devolviendo0 si está habilitado o0xfffffffd si falta. FUN_140023940 consulta esa compuerta antes del despacho y contempla0x280/0x281 en su lista. Esto refuerza que la presencia del nombre no basta: queda resolver la tabla de capacidades concreta y el destino de despacho.

Confianza alta: nombres y compuerta host. Desconocido: soporte efectivo, estructura y unidades del gain, alcance sobre audio USB/guitarra, protocolo y persistencia. No enviar esos IDs directamente como USB/SysEx ni realizar setters especulativos.

## Siguiente análisis

Resolver inicialización de bitmap de capacidades y handler de monitor gain, correlacionar Interposer/ASIO/kernel y modelo5068. Si se identifica un getter acotado y soportado, diseñar consulta documentada de solo lectura antes de cualquier ajuste temporal con restauración. Alternativa independiente: entrada externa para guitarra, NAM enPC y retorno USB Spider; no está probada la coexistencia ASIO de dos dispositivos.

## Seguimiento: despacho real y stubs de monitor

Nuevo barrido Ghidra estático: usb/monitor_gain_scalar_scan.txt. Los únicos inmediatos0x280/0x281 asociados a mensajes están en despacho/nombres; otro0x280 es desplazamiento de método, no ID. En ensamblador FUN_140023940, 0x140023c66 compara0x280 y salta0x140023da9, que carga vtable+0x230. El caso0x281 salta0x140023e8d, que carga vtable+0x238.

Se extrajeron ambos slots de10 tablas (usb/monitor_gain_vtables.json). Sus límites se corroboraron posteriormente con constructores/destructores que asignan esas direcciones al primer campo de objeto: usb/monitor_gain_constructors.txt. En todas las10 tablas, ambos slots apuntan a FUN_140004680, que devuelve0xc0000010 (STATUS_INVALID_DEVICE_REQUEST). Esto constituye evidencia alta de que estos métodos concretos no están implementados en las clases inspeccionadas de este driver, incluso si superaran el bitmap de capacidad. No demuestra imposibilidad de otra ruta MIDI/firmware. No hay getter utilizable demostrado por esta vía.

No se hizo ninguna llamada al driver ni al dispositivo. No proponer enviar0x280/0x281 como experimento: el nombre era una pista compartida, no un control funcional encontrado.
