# Seguimiento estático del consumidor SVU y fuente adicional necesaria

No se ejecutaron PE ni se inició actualización ni comunicación con el Spider.

## Trabajo nuevo

- TargetEvidence.java exportó funciones del motor de actualización en update_preparation.txt/log y image_archive.txt/log.
- UpdateClasses.java enumeró vtables/slots y sus referencias de constructores (update_classes.txt/log).
- Se inspeccionó selección de interfaces de Parker y clases comunes: parker_update_paths.txt/log.

## Hechos

FUN_1005d140 extrae HEAD/dinf/data y aplica inflate si HEADword3==1; esto coincide con el parser Python propio y no revela por sí solo una transformación posterior del payload.

FUN_1005c680, método del motor llamado L6AmplifiUsbControlPortUpdateEngine, extrae datos mediante slot+0x24/FUN_1005cf70, crea PlatformMemoryInStream e ImageArchive, y llama FUN_1005e5d0. El método de lectura de ImageArchive FUN_1005d790 compara un DWORD con0x4c364941 antes de leer versión y registros. La identificación de un parser L6IA en esta ruta no demuestra que sea el motor elegido para V30/0x220000, ni autoriza aplicar ese formato a un payload sin esa estructura reconocida.

FUN_1005dad0 asigna un nodo de lista; no es una rutina criptográfica. Nombres de clases como ImageArchive o FirmwareService no prueban descifrado ni identidad del algoritmo. ToneMatchFirmwareService se usa como base de servicios editor/librarian en FUN_10078e90; no equiparar automáticamente la palabra Firmware a un flasher del SVU.

El inventario de archivos extraídos de Driver y Remote no contiene ejecutable identificado como Line6Updater. El PDF oficial aportado por el propietario (Spider V Pilot's Guide, páginaPDF3) indica que las actualizaciones están disponibles mediante Line6Updater en Mac/PC. Por tanto el instalador Windows original de Line6Updater constituye una fuente estática adicional pertinente: puede aportar otra biblioteca/versión/parser específico del producto; no garantiza descifrar la carga ni encontrar un mute.

## Siguiente entrada requerida

Instalador oficial de Line6Updater para Windows, adjunto sin ejecutarlo, conservado con SHA256 y procedencia/versión. Extraer estáticamente y comparar sus motores con los ya inspeccionados. No se requiere conectar el Spider, iniciar updater, hacer un flash oficial ni modificado, ni obtener memoria del dispositivo.
