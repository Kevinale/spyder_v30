# Prueba propuesta: AmpEnable0 temporal

## Nueva evidencia comunicada por el propietario

El lector real completó identidad SpiderV30/version2.05.0, tabla con CRC válidos, handshake y GET9. AmpEnable respondió booleano1 con un modelo activo y volvió a responder1 después de seleccionar No Amp desde Remote y reconectar. Este dato confirma lectura directa, y que seleccionar No Amp no pone este flag en0 en esas dos sesiones. No demuestra que escribir0 sea aceptado, que quite DSP ni que preserve perillas.

## Experimento concreto preparado; autorizado por el propietario, no enviado desde la nube

Archivos separados `bypass_trial.js`, `trial_ui.js`, `Spider_Bypass_Trial.html`, `Start_Bypass_Trial.ps1`; el lector original conserva su lista de solo lectura y no carga este componente.

Accion explicita propuesta: con modelo Amp activo distinto de Bypass/No Amp, leer modelo (GET7) y AmpEnable (GET9); exigir estado inicial1; enviar setter10 exclusivamente a GuitarProc/AmpEnable, tipo3(bool), valor0; comprobar ACK, GET9==0 y mismo modelo por GET7. Mantener20 segundos y registrar notificaciones físicas identificadas Drive/Bass/Mid/Treble sin cambiarlas desde el PC. Enviar1 y verificar GET9==1. No cargar modelos, guardar presets, actualizar firmware ni acceder a memoria. Los giros del propietario pueden cambiar parámetros del modelo como en las pruebas previas; no se promete restaurarlos, sólo AmpEnable.

La escucha inicial debe hacerse por el propio Spider con guitarra, modelo distorsionado, sin cabina ni otros FX; no usa NAM ni REAPER. Comparar sonido antes/durante/después; si falta telemetría no atribuirlo automáticamente a perillas deshabilitadas: podría faltar suscripción fuera de Remote. Antes de integrar Gateway debe comprobarse retorno/audio limpio, perillas y sesión por separado.

El programa sólo cambia el flag después de otro botón y confirmación explícita en la UI. Se propone al propietario autorizar ese experimento activo, distinto de las lecturas ya hechas. La página de prueba no se ha entregado ni se ejecutó en Windows. No hay envío al amplificador desde la nube.

## Restauración y límites

Temporizador20s, Restaurar ahora y cierre normal del puerto intentan restaurar y leer confirmación. ACK negativo, readback distinto o escritura incierta disparan intento de restauración. Un fallo de restauración queda marcado y no se etiqueta como éxito ni cierra voluntariamente los puertos; admite reintento. beforeunload advierte y tab oculta dispara intento. **No se garantiza restauración si desaparece USB, se mata proceso o navegador, se suspende el equipo o se interrumpe alimentación.** Mantener página visible y pedir mensaje de restauración antes de cerrar. No se presume que volver a encender el equipo revierta el estado.

## Verificación aquí

`node test_bypass_trial.js`: exige accion expresa; rechaza No Amp antes de escribir; snapshot1/set0/readback/modelo estable/eventos/restore1; cierre normal; cero ignorado; ACK fallido; fallo de restauración retenido; gate bloquea otros parámetros y escrituras fuera de fase. Host simulado, no equipo real. `trial_validation.json` conserva resultados. Los positivos no prueban semántica DSP.


## Entrega posterior

El propietario autorizó la prueba temporal con «ok que hago» y preparó Amp distorsionado/No Cabinet/FX apagados/Remote y REAPER cerrados. `Start_Trial_From_Reader.ps1` obtiene exclusivamente la página del lector local ya ejecutado por el usuario en localhost8766, comprueba estructura esperada y agrega la prueba en otra página localhost8767. Requiere OTRA ventana PowerShell y deja intacto el lector original. No ejecutado en Windows aquí. Se añadió lectura inmediatamente antes de restaurar para detectar reactivación del flag por giros físicos.


## Resultado real comunicado por el propietario

AmpEnable pasó1→0; modelo retenido; eventos Bass19/Mid26/Treble27/Drive0; antes de restaurar seguía0; restauración1 confirmada. El propietario oyó guitarra limpia. Resultado funcional audible favorable, sin medida objetiva ni prueba USB grabada con el flag0. Drive y simultaneidad completa pendientes. Registro estructurado en OWNER_TRIAL_RESULT.json.

## Segunda prueba física Drive

El propietario repitió el test para Drive: AmpEnable0 confirmado, mismo modelo, cero contadores de las cuatro perillas, estado final previo a restore0 y restauración1 confirmada. El programa sólo contaba nombres Drive/Bass/Mid/Treble; no mostraba Gain u otros parámetros. No se interpreta contador0 como ausencia de toda telemetría. El catálogo propio declara Gain en varios modelos Amp en lugar de Drive. Se preparó Add_Drive_Diagnostic.ps1 para agregar registro acotado de todas las notificaciones tipo4, nombres/IDs/tipos/valores y modelo actual al ensayo ya autorizado; no agrega escrituras ni amplía duración. Su envío requiere reutilizar la ventana8767 tras Ctrl+C, conservando html en memoria. Pruebas de diagnóstico en test_drive_diagnostic.js.


## Captura de audio USB comprobada por el propietario

Con Gateway apagado, grabación REAPER antes/durante/después del ensayo. El propietario informa reproducción distorsionada→limpia→distorsionada. Confirma bypass funcional audible de entrada USB durante flag0 en esa configuración. Audio no subido aquí, sin prueba de transparencia bit a bit ni medidas objetivas. No se presenta como integración de Gateway en vivo con los cuatro controles; ese ensayo conjunto sigue pendiente.
