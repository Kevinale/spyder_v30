# Revisión de arranque Blackfin tras identificar ADSP-BF707

## Evidencia física

Las fotos del propietario identifican U6 como Analog Devices ADSP-BF707KBCZ-4/Blackfin. Ver ../../hardware_photos/PROCESSOR_IDENTIFICATION.json. Esto identifica familia del procesador, no reloj en operación, firmware cargado, RAM libre ni rutas de audio.

## Fuentes públicas revisadas como datos

Commits fijados en SOURCES.json. No se compilaron ni ejecutaron sus programas ni imágenes:

- https://github.com/neuschaefer/ldr-utils : `lfd_bf548.c` define header16bytes (code,target,count,argument), firmaAD en byte3, checksum XOR de cabecera cero, flags fill/first/final. `lfd_bf609.c` reutiliza formato para BF60x. No incluye soporte explícito BF707 y no se presenta como especificación exhaustiva BF70x.
- https://github.com/DAB-Embedded/adi-bf707-uboot : tiene `arch/blackfin+`, configuración BF707 EZ-Kit y `common/cmd_bootldr.c`. La comprobación genérica de firma para familias nuevas exige byte3AD y count0 inicial. Importante: el bloque de ejecución BF70x en `ldr_exec` está vacío; este port no es demostración de soporte completo de todas las modalidades de arranque BF707. RAM/relojes configurados en EZ-Kit no se atribuyen al Spider.
- https://github.com/flyingzhao/Gesture-Recognition-BF707 : se inspeccionó `Debug/handrecog5.dxe` con readelf y scripts propios. Es ELF32 little-endian/EM_BLACKFIN106; el detector propio lo identifica correctamente. No se ejecutó. Sus direcciones/SDK/runtime no constituyen mapa del Spider. Logs example_elf_header.txt, example_elf_validation.json; warnings de tabla de símbolos se preservaron aparte.

## Comprobación automatizada nueva

`probe_ldr.py` implementa únicamente la hipótesis de LDR16bytes anterior. Verifica firma/checksum, límites de datos, overflow de destino y progresión de bloques; fill no consume datos. No crea imagen de RAM, no carga código ni ejecuta instrucciones. Seis controles sintéticos pasan: cadena2bloques válida, checksum corrupto, truncado, ausencia de final, fill y overflow.

Se aplicó al payload inflate de393192bytes y las11 representaciones simples ya delimitadas (identidad, XORff, inversión de bits por byte, bytes invertidos en palabras2/4/6/8, rotaciones de byte1/2/3/4). Resultado ldr_probe.json: ninguna cadena multibloque completa reconocida, ninguna firma inicial según la comprobación U-Boot. Hay coincidencias aisladas de cabecera, sin estructura de ejecutable validada. En identidad, offset110844 da codead18c7fa, destino7855b6ca, count1991789332 con fill/first/final simultáneos: no se interpreta ese destino como memoria ni ese count como tamaño real.

La ausencia de una cadena en esta hipótesis no excluye código sin cabecera, otro contenedor, otra transformación, compresión o cifrado. No se declara cifrado por entropía. SHA256 del payload sigue58b058a7310a8f397d5c029f6dc0c0b07e5128dbd027548c060eba797647a0b4; original SVU intacto.

## Herramientas y límite

La instalación Ghidra actual no contiene módulo Blackfin en Ghidra/Processors. No se eligió otra ISA para desensamblar este payload y no hay funciones del firmware identificadas. Las funciones Ghidra de Remote/driver analizadas antes son ejecutables host Windows, no el código del BF707.

## Resultado

Se reduce incertidumbre de arquitectura y se añade una comprobación reproducible con fuente y controles positivos. No se ha identificado una rutina de mezcla/mute ni un patch ni una vía de ejecutar NAM en el DSP. Identificación de silicio no equivale a capacidad libre de cómputo ni compatibilidad del motor NAM. Sigue pendiente reconstruir transformación/carga del SVU y código del equipo antes de atribuir rutas o proponer cambios.
