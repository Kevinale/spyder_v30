# Spider V30 MkII: investigación y puente NAM

Proyecto de análisis del Line 6 Spider V30 MkII, firmware 2.05.0, y control de NAM/Gateway desde sus perillas originales. Estado consolidado: 18 de octubre de 2026.

## Qué funciona y qué falta

- El propietario confirmó NAM/Gateway ejecutándose en Windows/REAPER, con Drive, Bass, Mid y Treble físicos controlando el plugin mediante USB.
- El bypass temporal `AmpEnable=0` permite conservar el modelo seleccionado y recibir eventos de las perillas. NAM sigue ejecutándose en la computadora.
- Sigue sin resolverse la mezcla de guitarra limpia directa con el retorno de NAM. Los controles de volumen probados también cortaron la entrada USB; no son soluciones de monitorización independiente.
- Las fotos del propietario identifican un **Analog Devices ADSP-BF707KBCZ-4**. No se ha demostrado ejecución de código propio ni NAM dentro del DSP.
- Los SVU 2.02.0 y 2.05.0 pasan los checksums analizados. Su contenido interno todavía no se ha interpretado como un ejecutable válido.
- El preset `Deity Crunch.svl6p` contiene referencias a modelos y parámetros, no un motor NAM ni una distorsión ejecutable nueva.

## Aplicación Windows: SpiderGateway

Carpeta: [analysis/continuous_app](analysis/continuous_app).

1. Descarga este repositorio mediante **Code → Download ZIP** y extrae la carpeta completa.
2. Cierra Spider V Remote y otros clientes MIDI del amplificador. Conecta el Spider por USB y abre REAPER con Gateway y un modelo NAM en una pista seleccionada y armada.
3. En `analysis/continuous_app`, ejecuta `SpiderGateway.ps1` con PowerShell. El programa solicita elevación para su servidor local y abre su página en el navegador.
4. En REAPER: **Actions → New action → Load ReaScript**, carga `Spider_Gateway_Continuo.lua` de la misma carpeta y ejecútalo.
5. En la página del puente: **Conectar**, después **Iniciar NAM continuo**. Mantén la página visible. Usa **Detener** y restaura antes de cerrar.

Los archivos necesarios ya están en el repositorio. **No hace falta ejecutar `Crear_SpiderGateway.ps1`**, que conserva el procedimiento histórico de instalación desde el prototipo anterior.

El puente modifica temporalmente parámetros del amplificador; no instala firmware ni guarda presets. Los mecanismos de restauración no garantizan recuperación ante pérdida de USB o cierre forzado. Es un prototipo investigado con este equipo, no una herramienta validada para todos los Spider. La mezcla directa indicada arriba sigue pendiente.

## Informes

- [Firmware](analysis/FIRMWARE_ANALYSIS.md)
- [Protocolo USB](analysis/USB_PROTOCOL_ANALYSIS.md)
- [Arquitectura de hardware](analysis/HARDWARE_ARCHITECTURE.md)
- [Viabilidad NAM](analysis/NAM_FEASIBILITY.md)
- [Siguientes experimentos](analysis/NEXT_EXPERIMENTS.md)
- [Comparación 2.02 / 2.05](analysis/firmware/comparison/COMPARISON_REPORT.md)
- [Revisión de cargadores BF70x](analysis/firmware/structure/LOADER_REVIEW.md)
- [Preset Deity Crunch](analysis/presets/deity_crunch/REPORT.md)

Los informes conservan etapas históricas; las secciones fechadas más recientes y este README describen el estado actual. Las confirmaciones físicas proceden de las pruebas del propietario. La nube no tiene un amplificador conectado.

## Archivo del proyecto y reproducción

Se incluyen scripts Python/Java/Ghidra, JavaScript, PowerShell, Lua, resultados derivados, pruebas y referencias. Las rutas absolutas `/workspace/...` de algunos scripts y logs corresponden al entorno original; se conservan como evidencia y pueden requerir ajustes para repetir análisis en otra máquina.

No se incluyen instaladores comerciales, imágenes binarias de firmware, capturas USB originales, proyectos de Ghidra, toolchains descargadas ni clones completos de terceros. Sus inventarios y hashes permanecen en los informes. Los archivos originales no se modificaron. Para repetir extracción o comparación se deben aportar los archivos correspondientes y las herramientas indicadas.

- [Inventario de archivos archivados](ARCHIVE_MANIFEST.json)
- [Repositorios externos y commits consultados](THIRD_PARTY_REFERENCES.json)
- [Validación de esta publicación](PUBLICATION_VALIDATION.md)

No se adjunta una licencia general para código o material de terceros. Las referencias conservan sus licencias originales; una copia de evidencia no implica autoría del proyecto.
