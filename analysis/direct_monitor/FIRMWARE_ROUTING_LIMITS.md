# Límite actual: mute directo independiente

## Hechos comprobados por el propietario

- AmpEnable0 deja entrada USB limpia funcional y cuatro controles físicos; Gateway/NAM externo y modo continuo funcionan.
- Persiste guitarra directa al reducir Output de Gateway.
- Volume del modelo Amp0, gain global GuitProcOutputGain0 y afinador silenciaron guitarra y dejaron sin movimiento el medidor USB, en sus respectivas pruebas. Gain global restaurado1 y verificado. No son solución de mute exclusivamente directo en esas condiciones.
- No está comprobado comportamiento de cada mute con AmpEnable0 ni un aislamiento objetivo de taps; no afirmar diagrama interno exacto.

## Seguimiento nuevo del cliente Windows

Se localizaron los serializadores de GetSystemSetting/SetSystemSetting: captures/native_api_wire.txt, FUN_1009aae0/FUN_1009ab90. El primero manda opcode0x15 con keyu32 y espera status/type/value; el segundo manda0x16. La presencia de getters no prueba keys de monitorización ni soporte para V30.

La tabla nativa en VA0x10176254 (APIV3EngineDLL.dll) contiene GetDspModelParam en slot+0x28 (FUN_10099810) y GetSystemSetting en slot+0x94 (FUN_1009aae0). SystemSettingEvidence.java inspecciona llamadas indirectas de slots+0x94/+0x98 y decompila sus funciones. Resultado system_setting_calls.txt/log. El uso visible que pasa por la interfaz de edición (FUN_10079f30, call0x1007a3d8) corresponde al caso VariaxConnected y está condicionado a familias0x200004/0x200006, no Spider0x220000. Otras llamadas con el mismo desplazamiento pertenecen a objetos distintos; no identificarlas como GetSystemSetting por coincidencia de slot. No se extrajo una key de mute directo para V30. No se consultaron IDs de settings desconocidos ni se escanearon setters.

## Firmware

firmware_routing_audit.json revalida SHA256 del original y payload: coinciden con los hashes iniciales. No hay ocurrencias exactas ASCII de ocho nombres candidatos en el payload. Se conserva el límite anterior: sin ISA ni formato ejecutable/carga confirmados; no hay dirección de rutina de mezcla identificada. Ausencia de cadenas no es ausencia de función; alta entropía no se toma como prueba de cifrado. No se presentan funciones Windows como funciones del DSP.

## Investigación pública y dato faltante

Búsqueda pública de repositorios GitHub, tres consultas hardware/SpiderV30/teardown, todas HTTP200 y0 resultados en ese buscador. Archivos hardware_search*.html y hardware_search.json permiten auditar alcance limitado; no equivalen a búsqueda exhaustiva de Internet ni a prueba de inexistencia de esquemas.

El siguiente dato de mayor valor sería identificación verificable de los chips de la placa principal y revisión (foto pública legible, documentación de servicio o imagen de técnico). No asignar SHARC/LPC de AMPLIFiTT a Spider por similitud. Identificar hardware ayuda a elegir hipótesis de carga/ISA, pero no garantiza decodificar SVU ni implementar mute/NAM interno. Otra fuente útil sería código de loader/firmware debidamente identificado para este producto, sin efectuar lecturas arbitrarias ni modificaciones del dispositivo.

## Conclusión

No se ha encontrado una solución demostrada de escucha exclusiva NAM conservando todo en Spider. No se ha demostrado imposibilidad. El siguiente avance requiere evidencia nueva o decodificar la carga con una hipótesis verificable; repetir mutes compartidos o probar offsets desconocidos no aporta una solución fundamentada. Ningún firmware fue alterado/cargado y los archivos originales permanecen intactos.
