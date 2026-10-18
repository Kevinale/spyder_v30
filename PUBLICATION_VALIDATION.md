# Validación del archivo publicado — 2026-10-18

- `analysis/continuous_app/test_continuous.js`: PASS, dispositivo simulado; temporizador continuo, cuatro controles, lease por página, parada/restauración y desconexión.
- `analysis/integrated_trial/test_link.js`: PASS, Gain37/Drive38, estado autenticado, IDs desconocidos ignorados y OFF antes de restaurar.
- `analysis/continuous_app/test_lua.py`: PASS con Lua 5.4 real y REAPER simulado (lupa); ocho comprobaciones de parámetros, heartbeat, parada, restauración y aislamiento de sesión. Se ajustó solamente la raíz de rutas en memoria para ejecutar la copia archivada. Dependencia Python disponible en el entorno original, no incluida.
- 150 JSON válidos; sintaxis Python comprobada por AST para los scripts archivados.
- Sin coincidencias de los patrones examinados de tokens GitHub, claves AWS o claves privadas. No es una auditoría exhaustiva de datos personales.
- Originales comerciales, binarios de firmware, PCAP completos, clones de terceros y toolchains fuera de esta publicación. Inventarios/hashes y resultados derivados conservados.
- No se ejecutaron instaladores ni firmware; no se conectó un dispositivo desde la nube. PowerShell/REAPER Windows no se ejecutaron en este entorno Linux. Las pruebas físicas previamente comunicadas por el propietario permanecen como evidencia separada.
- Algunos scripts de investigación conservan rutas del entorno original. El archivo es un expediente de investigación y contiene etapas históricas, no una suite portable completa ni un instalador de firmware.

Se conservaron literalmente finales CRLF y espacios en logs, CSV y pseudocódigo generado. `git diff --check` los señala; no se normalizó evidencia para ocultar esas advertencias.
