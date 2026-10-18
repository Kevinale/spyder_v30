# Validación independiente de captura USB Spider V

Se examinó **offline** `SpiderV_USB2perilla.pcapng .pcapng`, 664000 bytes, SHA-256 `101c25061d62c511b61a8635903da0b277a4379d918fde3e5f5a6167cea4c536`. Ningún acceso al equipo, reproducción de tráfico, ejecución de aplicaciones ni solicitud USB. No se publican payloads ni identidad de otros dispositivos.

## Integridad del contenedor y selección

`scripts` de esta validación: `captures/independent_validate.py`; resultado: `captures/independent_validation.json`. No importa ni ejecuta el parser principal. Lee PCAPNG con offsets propios y contrasta solamente el resultado final con `sysex_messages.json`.

- Un Section Header little endian, un Interface Description y 7950 Enhanced Packet Blocks. Tamaños de bloques y trailers coinciden, sin bytes residuales. Captured length = original length en todos los paquetes: ninguna truncación registrada por snaplen. Esto no demuestra que el capturador no perdiera tráfico antes de escribir el archivo.
- Linktype 249 = USBPcap; resolución de timestamp 10⁻⁶ s. Header común de 27 bytes; headers de control de 28 bytes incluyen stage. El campo dataLength concuerda con longitud capturada menos header.
- VID/PID del descriptor de dispositivo target: `0x0e41:0x5068`, bus 2, dirección 4. Se filtran exclusivamente esos dos campos después de identificar el dispositivo: 7932 frames. Los números de frame siguen siendo los del archivo original.
- Todos los **status USBPcap del target** son cero; no equivale a que todos los mensajes de aplicación hayan tenido éxito.
- 3962 parejas bulk submission/completion coinciden por IRP ID y endpoint. Frame 27 (`0x82` IN) tiene completion sin submission capturada; frame 7950 deja una lectura IN pendiente al finalizar. Son bordes de captura compatibles con operaciones iniciadas antes del intervalo y pendientes después; no se inventan sus tiempos de inicio.

## Reensamblado independiente USB MIDI

Se toman datos OUT en submission y datos IN en completion. Cada bloque bulk con datos tiene longitud múltiplo de cuatro. Cada evento contiene cable 0; CIN observados exclusivamente 4, 5, 6 y 7. El algoritmo independiente usa F0/F7 como límites de mensaje tras quitar bytes del encabezado MIDI y bytes fuera de la longitud definida por CIN; mantiene buffers por endpoint y cable.

Resultado: **3219 mensajes**, exactamente iguales al parser principal en bytes, dirección, primer/último frame y tiempos: 1901 OUT y 1318 IN. No quedaron mensajes abiertos. Total 46308 eventos; no hay CIN de Control Change (`0xb`) ni Program Change (`0xc`) en esta captura. Eso no excluye que un SysEx codifique parámetros o acciones de preset.

**Detalle importante:** 12 eventos finales contienen bytes no cero fuera de la longitud válida de su CIN. Son padding que se ignora correctamente; no deben añadirse al SysEx ni considerarse errores de reensamblado. Una primera comprobación de padding=0 se sustituyó por el conteo explícito, porque el contrato de longitud CIN es lo que determina los bytes significativos.

|Endpoint|CIN 4|CIN 5|CIN 6|CIN 7|
|---|---:|---:|---:|---:|
|`0x02` OUT|19528|813|1083|5|
|`0x82` IN|23561|43|890|385|

## Descriptores del target

Frame 20: descriptor de dispositivo de 18 bytes, offset de payload PCAPNG **2636** (`0xa4c`). `bcdUSB=0x0200`, `bDeviceClass=0`, EP0 max packet 64, VID/PID indicados, `bcdDevice=0x0100`, una configuración. bcdDevice no es una identificación del firmware 2.05.0, y bcdUSB no demuestra velocidad efectiva del bus.

Frame 22: descriptor completo de configuración de **290 bytes**, offset PCAPNG **2784** (`0xae0`), `wTotalLength=290`, cinco números de interfaz. La cadena se recorre por bLength y termina exactamente al final, sin descriptor truncado. `bmAttributes=0xc0` anuncia alimentación propia; bMaxPower=0. Los offsets de la tabla son relativos al principio de esta configuración.

|Offset config|Interfaz / alterno|Clase / subclase|Endpoints y significado|
|---:|---|---|---|
|9|0 / 0|Audio / AudioControl|Sin endpoints|
|27|1 / 0|Audio / MIDIStreaming|`0x02` OUT y `0x82` IN, bulk, max packet 64; sus descriptores comienzan en 73 y 87|
|101|2 / 0|Audio / AudioControl|Sin endpoints|
|171 / 180|3 / 0 y 1|Audio / AudioStreaming|Alt 0 sin endpoints; alt 1 `0x83` IN isócrono, atributos `0x25`, max packet 196, intervalo 1|
|226 / 235|4 / 0 y 1|Audio / AudioStreaming|Alt 0 sin endpoints; alt 1 `0x04` OUT isócrono, atributos `0x05`, max packet 196, intervalo 1; feedback `0x84` IN, atributos `0x11`, max packet 4|

Los descriptores de formato en offsets **196** y **251** anuncian Type I, **2 canales**, subframe **2 bytes**, resolución **16 bits**, frecuencias discretas **48000 y 44100 Hz**. Las interfaces AudioControl anuncian PCM en su ruta terminal. Confianza alta en lo anunciado por descriptores; **no** demuestra resolución interna ADC/DAC, precisión DSP, tasa interna del algoritmo ni una sesión de audio activa. Esta captura no contiene transferencias isócronas target ni evidencia de selección de alt 1 durante el intervalo observado. Tampoco es una medición de latencia.

## Tiempos iniciales, snapshot y alcance del silencio

Los frames target **19–24** (descriptores device/configuración y configuración 1) tienen exactamente el mismo timestamp, **IRP ID cero** y aparecen antes del primer bulk. Es un **indicio fuerte de snapshot inicial de estado sintetizado por el capturador**, no prueba de enumeración física real ni de SET_CONFIGURATION ejecutado al empezar la captura. No se asigna causalidad de conexión o arranque al tiempo relativo cero. Confianza alta en los campos, media en la interpretación snapshot hasta cotejar implementación exacta/version del capturador.

Primer bulk target: frame **25**, **t=60.250494 s**, OUT identity request Universal Non-Realtime `f0 7e 7f 06 01 f7`. Primera completion IN frame **27**, **t=60.250775 s**. Contiene respuesta identity y el inicio de un segundo SysEx; el reensamblado independiente respeta ese cambio de mensaje dentro del mismo URB. Frame **29** completa ese segundo mensaje, que incluye texto de versión. Las transacciones posteriores de Remote empiezan alrededor de t=61.715 s. Estas horas son relativas al primer paquete del archivo; no son anotaciones de acciones humanas.

**No hay bulk target registrado entre el snapshot y t=60.250494 s.** El relato del usuario sitúa un giro físico antes de abrir Remote. Sin marcas sincronizadas de ese giro, sin conocer si existía lectura pendiente y dado que la primera completion IN carece de submission capturada, el silencio no prueba que el firmware nunca emita cambios sin Remote. USB es sondeado por el host: ausencia de completion con payload no distingue ausencia de evento, ausencia de lectura, buffering, suscripción u otra condición.

El relato de que la UI sigue la perilla con Remote abierto aporta una observación funcional; la atribución de mensajes concretos a Drive necesita comparar secuencias y marcas temporales. Esta validación confirma transporte y bytes del corpus, **no** establece por sí sola IDs de parámetro, unidades, escala, petición de suscripción ni causalidad app→perilla. No identifica tráfico MIDI CC estándar en este archivo: los cambios viajan dentro de SysEx, si se demuestra su correlación.

## Referencias y límites

El formato común se contrasta con el disector Wireshark ya conservado en `captures/wireshark_packet_usb.c`, que distingue control stages Setup=0 y Complete=3. La interpretación de los descriptores usa estructuras USB estándar y USB Audio/MIDI; los bytes originales y offsets quedan en `target_frames.json` y la cadena decodificada en `independent_validation.json`. Ninguna propiedad inferida de otro dispositivo se trasladó al target.

No se observa aquí el protocolo vendor control `bRequest=0x67` estudiado estáticamente para GETDECRYPTKEY: no debe mezclarse con estos SysEx MIDI ni usarse para explicar su semántica sin una evidencia adicional. No se requiere enviar mensajes para completar la presente validación.
