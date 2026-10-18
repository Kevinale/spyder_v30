# Correlación estática del protocolo con la captura de perilla

Análisis exclusivamente offline. No se ejecutaron los DLL ni se enviaron comandos al equipo. Entrada: `SpiderV_USB2perilla.pcapng .pcapng`, analizada por el parser USBPcap del proyecto. El código correlacionado es `remote/extracted/Spider V Remote/APIV3EngineDLL.dll`, PE x86, base preferida 0x10000000. FUN_* son nombres automáticos Ghidra; no identificadores originales del fabricante. Las direcciones pueden desplazarse en ejecución por ASLR.

## Framing Parker demostrado por código y captura — confianza alta

`L6ParkerMidiMsgPortMultiplexor::vftable` VA0x101737ec referencia emisor `FUN_10057810` y receptor `FUN_10057aa0`. El emisor construye explícitamente:

| Offset dentro del SysEx | Campo observado en el código |
|---|---|
| 0–4 | F0 00 01 0C 22 |
| 5 | Selector del dispositivo/contexto; cero en esta captura |
| 6 | 4D, carácter M |
| 7 | Canal lógico del multiplexor |
| 8 | Contador de secuencia, limitado con &0x7f |
| 9 | Índice de fragmento de esta escritura |
| 10–11 | Dos nibbles de longitud original menos1: n=((b10&15)<<4\|(b11&15))+1 |
| 12… | Datos empaquetados: cada7 bytes originales→8 bytes MIDI |
| último | F7 |

En cada bloque de8 bytes, el primero guarda los MSB de los7 siguientes: bit6→MSB del primer byte, bit5→segundo, …, bit0→séptimo. Los otros7 bytes guardan sus bits0–6. Los grupos parciales se rellenan con ceros, pero sólo deben conservarse n bytes originales.

`FUN_1005b470` contiene el empaquetador y `FUN_10057aa0` hace la transformación inversa de forma explícita. No es cifrado ni checksum. El emisor anfitrión divide una escritura en fragmentos de hasta210 bytes (0xd2); eso **no** establece un máximo simétrico del dispositivo: se observan256 bytes originales IN y el campo de longitud puede representarlos.

El script `decode_parker.py` reproduce este algoritmo y verifica 3216 mensajes M con decode→encode idéntico, incluidos longitud y padding; conserva resultado en `native_decoded_packets.json`. Los otros3 SysEx son intercambio de identidad/versiones. El script sólo transforma archivos; no contiene transporte USB.

## Una trama M no equivale a un mensaje API

`FUN_100991b0` serializa primero8 bytes `{operation:uint32LE,payload_size:uint32LE}` mediante una llamada de escritura y después el payload mediante otra llamada. Esto explica los dos SysEx OUT por cambio Drive. Debe reconstruirse el flujo por dirección y canal antes de interpretar operaciones. El contador SysEx o el índice de fragmento no deben confundirse con operation ni con un parámetro.

La reconstrucción offline en `reassemble_protocol.py` obtiene2307 mensajes API,4 flujos sin bytes pendientes. Las813 escrituras Drive OUT contienen operation0x0a, payload_size16; las140 notificaciones Drive IN contienen operation0x04, payload_size16. Los tiempos y frames precisos están en los CSV/JSONL de Drive del mismo directorio; no se infieren tiempos de acción manual a partir del código.

## Serialización de valores y notificaciones

`FUN_100998e0` (ruta con espera de respuesta) y `FUN_100999a0` (sin espera local equivalente) pasan operation10 al serializador y forman16 bytes:

```
asset_id:uint32LE | parameter_id:uint32LE | value_type:uint32LE | value_bits:uint32LE
```

En esta captura Drive utiliza asset_id42 y parameter_id38. La tabla de916 símbolos recuperada de la respuesta del propio amplificador identifica42 como `Amp` y38 como `Drive`; se validaron los916 CRC32. La coincidencia con los recursos Parker de la app ya no es la única evidencia de esos nombres. Los primeros910 símbolos coinciden con la tabla Parker incluida en Remote.

Para el evento final de Drive, frame7947, t131.116743s, el mensaje reensamblado IN es:

```
04 00 00 00 10 00 00 00  # operación4, payload16
2a 00 00 00 26 00 00 00  # Amp42, Drive38
04 00 00 00 f0 f0 f0 3d  # tipo4, bits IEEE754LE=0.11764705181121826
```

La ruta receptora `FUN_1009ae80`, alcanzada desde `FUN_100851a0`, lee8 bytes de cabecera, selecciona operation4, lee el payload declarado y entrega los primeros2 words como identificadores y el resto como pareja tipada al callback registrado. Esto es corroboración estática de que la trama IN es una notificación del servicio, sin necesitar reproducir el paquete.

**Tipo4 corroborado estáticamente (confianza alta):** `FUN_10097720` comprueba `*param_1==4` antes de reenviar el segundo word. `FUN_10097750`, para ese mismo discriminante4, interpreta explícitamente `param_1[1]` como float y hace una comparación en punto flotante; para discriminante2 sigue una rama entera separada. `FUN_100981d0` registra esos callbacks. Evidencia: `native_value_callbacks.txt` y `native_value_adapter.txt`. Esto corrobora que el discriminante4 de la pareja es float32 y no un tamaño, un CRC ni el valor entero4. No se atribuye a esos dos callbacks concretos el parámetro Drive: el nombre Drive procede de los índices de la tabla recuperada y la secuencia de captura. El booleano administrado `deviceTriggered` no aparece como tal en estos16 bytes. La ruta anterior `FUN_1002d800` consume diccionarios `onDevice`, `groupID`, `paramID`, `value`; conserva el origen al entregar callbacks, coherente con el análisis IL, pero no se debe afirmar que se capturó directamente ese booleano en USB.

## Evidencia y direcciones

| Función | VA | RVA | Offset PE | Evidencia |
|---|---|---|---|---|
| Emisión framing M | 10057810 | 57810 | 56c10 | native_parker.txt |
| Recepción/decodificación M | 10057aa0 | 57aa0 | 56ea0 | native_parker.txt |
| Empaquetado MSB | 1005b470 | 5b470 | 5a870 | native_serializers.txt |
| Serializador operation/length | 100991b0 | 991b0 | 985b0 | native_setters.txt |
| Setter con respuesta | 100998e0 | 998e0 | 98ce0 | native_setters.txt/native_typed_values.txt |
| Setter sin espera local | 100999a0 | 999a0 | 98da0 | native_setters.txt/native_typed_values.txt |
| Despacho de notificaciones operation4 | 1009ae80 | 9ae80 | 9a280 | native_typed_values.txt |
| Wrapper de recepción Editor | 100851a0 | 851a0 | 845a0 | native_editor_service.txt |
| Callback que valida tipo4 | 10097720 | 97720 | 96b20 | native_value_callbacks.txt |
| Callback que interpreta tipo4 como float | 10097750 | 97750 | 96b50 | native_value_callbacks.txt |
| Evento nativo hacia callbacks de aplicación | 1002d800 | 2d800 | 2cc00 | native_transport.txt |

Los offsets se obtienen de las secciones PE con pefile; `native_function_offsets.json` conserva la conversión de las funciones iniciales. Los pseudocódigos incluyen las referencias de entrada y los logs documentan análisis Ghidra sin ejecución de código de la muestra.

## Reproducción

```
python /workspace/analysis/captures/decode_parker.py
```

Para exportar de nuevo pseudocódigo de funciones concretas desde el proyecto ya analizado, ejecutar con los argumentos de direcciones necesarios:

```
export XDG_CONFIG_HOME=/workspace/analysis/usb/config
export XDG_CACHE_HOME=/workspace/analysis/usb/cache
export JAVA_HOME=/workspace/analysis/usb/jdk/usr/lib/jvm/java-21-openjdk-amd64
/workspace/analysis/tools/ghidra_12.1.4_PUBLIC/support/analyzeHeadless \
 /workspace/analysis/remote/ghidra Native -process APIV3EngineDLL.dll -noanalysis \
 -scriptPath /workspace/analysis/remote/native \
 -postScript TargetEvidence.java /workspace/analysis/captures/native_selected.txt \
 10057810 10057aa0 1005b470 100991b0 100998e0 100999a0 1009ae80
```

No ejecutar varias instancias sobre el mismo proyecto a la vez. `RangeEvidence.java` permite exportar un intervalo de funciones: los ejemplos y sus logs quedan en `native_setters.log` y `native_api_wire.log`. No se han invocado setters reales ni callbacks del DLL.

## Límite de la conclusión

La captura y el código permiten extraer pasivamente valores Drive emitidos por el amplificador durante la etapa con Remote abierto. No prueban que el equipo emita esos eventos sin sesión/inicialización, que exista ya un puente NAM operativo, ni que NAM pueda ejecutarse en el DSP interno. Esta interpretación no autoriza reenviar setters, suscribirse mediante comandos nuevos, resetear el USB, actualizar firmware ni escribir memoria.
