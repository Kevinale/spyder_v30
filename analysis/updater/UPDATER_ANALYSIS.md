# Line 6 Updater v1.28: análisis estático del Spider V

## Reconstrucción y límites

Se recibieron tres volúmenes7z (25MiB,25MiB,135947bytes). Se conservaron intactos; nombres/hashes en received_volumes.json. `7z t` validó los volúmenes y el instalador reconstruido. Instalador52976568bytes, hashes/CRC en reconstruction.json. Se extrajeron223archivos,108654929bytes, sin ejecutar instalador, EXE ni DLL. Inventario completo con SHA256: inventory.json. La integridad del archivo no autentica el origen del fabricante.

El ejecutable propio es `extracted/Line 6 Updater/Line 6 Updater.exe` (PE32/x86, base0x00400000); los DLLQt y recursos son del host, no firmware del BF707. Ghidra importó ese EXE en proyecto Updater. Nombres FUN son automáticos; los nombres de métodos citados derivan de RTTI y cadenas de diagnóstico. Logs de análisis preservan advertencias del descompilador; no se afirma revisión exhaustiva del binario.

## Hallazgo: ruta principal distinguida de conversión G10T

| Evidencia | Función/VA | Archivo de evidencia |
|---|---|---|
| Inicio de actualización Parker | FUN_0049c400 y FUN_0049ad20 | native/parker_converter.txt |
| Componente0 selecciona Spider V.bin; rama inalámbrica selecciona Spider V G10Tx.bin | FUN_0049ad20 | native/parker_converter.txt |
| Constructor del motor realmente usado | FUN_004cee20, RTTI L6MidiFileDumpUpdateEngine | native/make_update.txt y update_classes.txt |
| Lectura FORM/L6FF/HEAD/dinf/data e inflate zlib | FUN_004cad00 y FUN_004cec90 | native/component_dispatch.txt |
| Procesamiento que usa esa extracción y llama a conversión de componente | FUN_004cfaa0 | native/component_dispatch.txt y midi_file_dump.txt |
| convertUpdateImage | FUN_00497880 | native/parker_converter.txt; converter_entry.asm.txt |
| make_update | FUN_0049cfa0 | native/make_update.txt |
| Empaquetado de datos MIDI | FUN_004cf4b0 | native/file_dump_packet.txt |

El convertidor encontrado inicialmente no debe presentarse como un descifrador del SVU principal:

1. FUN_00496f00 instala la interfaz secundaria de L6ParkerDevice en offset0xd0. Tabla secundaria VA0x007f7f04, slot0xc→FUN_00497880. Constructor y tablas: native/component_dispatch.txt y parker_class.txt.
2. FUN_0049c400 almacena el identificador de componente en offset0xf4 del objeto principal; FUN_0049ad20 distingue0(main) frente a la rama inalámbrica.
3. FUN_00497880 comprueba DWORD[ecx+0x24]==1; ecx es la interfaz secundaria0xd0, por lo que ese campo corresponde a0xf4 del objeto principal. Para componente0 retorna sin sustituir buffer. Para1 crea temporales l6logic/bin y llama make_update.
4. Por tanto la conversión lógica corresponde a componenteG10T, no a una transformación descubierta de la imagen principal de nuestro Spider. No confundir su campo0x24 con HEADword9: pertenece al objeto/interfaz, no al header SVU.

Confianza alta en este flujo estático y aritmética de objetos; no se ejecutó la actualización ni se validó tráfico de flash en un equipo.

## Qué se prepara para la imagen principal

El lector comprueba FORM/L6FF, extrae HEAD y dinf y descomprime data si el flag lo indica. En la ruta principal inspeccionada no se observó otra transformación de representación antes del empaquetador de transferencia MIDI. No concluye ausencia de transformaciones dentro del amplificador ni prueba un cipher concreto.

FUN_004cf4b0 toma bytes del buffer en secuencia, separa sus MSB para producir datos7bit, añade secuencia, XOR del cuerpo empaquetado y delimitadores SysEx. Constante de fabricante leída del EXE00010c. El constructor se invoca con capacidad32bytes codificados (28bytes crudos por paquete completo). Esto es codificación de transporte reversible, no descifrado del payload.

`transport_roundtrip.py` modela solo esa codificación: pruebas de todos los valores/bordes de grupo, rechazo de checksum corrupto y roundtrip sobre393192bytes del payload real. Resultado transport_validation.json:14043paquetes modelados, igualdad exacta y SHA256idéntico58b058a7310a8f397d5c029f6dc0c0b07e5128dbd027548c060eba797647a0b4. No es captura del equipo, no replica todos los estados/reintentos del Updater y no genera mensajes listos para enviar.

## Comprobación de constantes

native/algorithm_constants.json contiene búsqueda acotada de prefijos canónicos AES/Blowfish/ChaCha, constantesTEA y series MD5/SHA. No se hallaron los patrones probados. Esto no excluye implementaciones alternativas ni demuestra que el firmware esté o no cifrado; solo evita atribuir un algoritmo sin código que lo respalde. El texto de licencia extraído se trató como contenido del archivo, no como instrucciones del usuario.

## Resultado y siguientes pasos de lectura

- Se identificó la ruta host específica Parker y su motor MIDI; no se reutiliza como hecho el motor Amplifi/L6IA del Remote antiguo.
- La extracción previa de393192bytes sigue siendo consistente con el Updater. Este programa no nos ha proporcionado un decodificador de código Blackfin de esa carga.
- No se identificó rutina de mezcla/mute independiente ni se demostró NAM interno. Identificar BF707 y el transporte de actualización no significa poder compilar/cargar un modelo NAM de forma compatible.
- Trabajo adicional no invasivo posible: contrastar documentación de imagen/bootROM BF70x y comparar otra versión oficial original del SVU (sin instalar) con hipótesis estructurales y controles positivos. Sin offsets/métodos desconocidos contra el dispositivo, sin lecturas arbitrarias, sin entrar en updater/bootloader y sin flash como experimento.
- Las pruebas Volume0, gain0 y afinador que cortan también USB siguen descartadas como soluciones comprobadas del limpio. No se cambiarán USBIn/Out por deducción del nombre.
