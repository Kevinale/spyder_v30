# Placas y marcados observados en cinco fotografías aportadas

Origen: cinco JPG adjuntos por el propietario. El propietario confirmó que son fotografías de su propio SpiderV30MkII; quedan vinculadas por esa declaración al equipo investigado. Originales intactos; hashes y rutas en ORIGINALS.json. Las imágenes inspection/detail son rotaciones/recortes ampliados exclusivamente para lectura visual, no nuevos detalles recuperados ni fotos originales modificadas.

## Evidencia física visible

| Elemento | Observación | Confianza y límite |
|---|---|---|
| Placa base | Serigrafía A39-1 25W Main-DB,35-00-0487,2022-JAN-13 CED-DL | Alta para texto. 25W no se usa para reclasificar modelo comercial ni potencia de salida medida. Fecha serigrafiada no prueba fecha de fabricación. |
| Placa hija | LINE6,A39 Daughter Rev A,35-00-0485,2016-MAY-10 CED-DL | Alta. Dos hileras de interconexión con placa base; no se deduce protocolo/bus de pines. |
| U6 | Encapsulado central muestra marca/logotipo Analog Devices parcialmente visible y etiqueta blanca A43.2 | Alta para marca visible/etiqueta; número comercial del IC está oculto. No identificar ADSP/SHARC/Blackfin/modelo/ISA/reloj a partir de marca, encapsulado o memoria adyacente. A43.2 es texto de etiqueta, no procesador ni firmware2.05.0. |
| U7 | NANYA,NT5TU32M16FG-AC; otras líneas2133 y códigos de lote | Alta para Nanya, buena lectura para parte base. Capacidad/tipo/timing requieren cotejo con datasheet exacto; no atribuir RAM libre ni topología al firmware. La organización32M x16 sugerida por el marcado daría512Mbit=64MiB si se confirma documentalmente. No presentar esa inferencia como memoria libre ni como especificación ya verificada. |
| U4 | winbond, familia aparente25Q256FV..., sufijo parcial, punto adhesivo rojo | Alta para fabricante, lectura provisional de familia. No asignar capacidad/partición/firmware de arranque sin confirmar parte y conexiones. No es una lectura del contenido de flash. |
| Circuitos de placa base | Marca CIRRUS visible en al menos un IC, referencia U13; otros marcados poco legibles | No identificar codec/DAC, cantidad de canales, bus o número exacto sin transcripción verificable. |
| CODEC_FS_SENSE | Texto de serigrafía en placa hija | Señal nombrada, no prueba de ruta USB/audio ni punto de mute. |

Fotos2/3/4/5 permiten corroborar la misma placa hija por referencias/etiqueta. Foto1 identifica base. No se solicitó retirar adhesivos, despegar módulos, alimentar abierto, medir ni modificar hardware.

## Implicación

Nueva evidencia física real de una placa modular Line6 con IC Analog Devices y memoria Nanya/Winbond, superior a inferencias anteriores por cadenas de software. Falta el número de parte del chip central y origen/modelo inequívoco de fotos. No prueba capacidad de ejecutar NAM, acceso a RAM/flash, herramienta de compilación ni que mute independiente exista. El paso inmediato es confirmar procedencia y buscar la referencia35-00-0485/35-00-0487 en documentación/fotos públicas, no modificar el amplificador.

## Actualización: marcado U6 descubierto

Dos nuevas fotos del mismo propietario muestran inequívocamente ADSP-BF707, KBCZ-4 y logotipo Blackfin en U6. Parte identificada ADSP-BF707KBCZ-4, Analog Devices. PROCESSOR_IDENTIFICATION.json conserva transcripción y hashes; bf707_marking_detail.png es ampliación solo de inspección. Esta evidencia sustituye la incertidumbre de U6 por etiqueta cubierta. La arquitectura pertenece a familia Blackfin; no elegir ARM/SHARC para decodificar esta imagen por analogía. No se ha medido reloj efectivo ni memoria libre ni descifrado firmware.
