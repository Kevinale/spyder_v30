# SpiderGateway continuo

Extensión de la prueba integrada de 20 segundos confirmada por el propietario: sonido de Gateway y cuatro perillas. NAM continúa en el PC; no demuestra NAM dentro del DSP.

## Instalación Windows 10

Mantener disponible la página integrada anterior en http://localhost:8768/ para crear la copia una sola vez. Ejecutar el contenido de Crear_SpiderGateway.ps1 en PowerShell. Lee esa página y el script Spider_Gateway_Integrado.lua, crea una carpeta nueva SpiderGateway en Escritorio y un acceso directo. Si no encuentra el Lua abre un selector de archivos. No reemplaza originales.

Después, restaurar y desconectar la página anterior. Abrir INICIAR SpiderGateway; cargar Spider_Gateway_Continuo.lua mediante Actions > New action > Load ReaScript en REAPER y ejecutarlo con una pista seleccionada y armada, Gateway habilitado. No ejecutar simultáneamente el Lua anterior. En la nueva página: Conectar > Iniciar NAM continuo. No necesita USBPcap.

Mantener página visible: ocultarla intenta restaurar. Detener apaga monitorización antes de AmpEnable1 y verifica la lectura. Restaurar y cerrar termina el servidor. No se garantiza restauración si desaparece USB o muere navegador; recuperar explícitamente Amp a1 al reconectar. No guarda presets ni modifica firmware.

## Validación

Node comprobó sintaxis del conjunto y ejecución con dispositivo simulado: eliminación de temporizador, cuatro controles, identificador de cliente, publicación OFF y restauración/reinicio/desconexión. Lua real ejecutado con REAPER simulado: caducidad, restauración de parámetros, rechazo de estado histórico/inválido y cambio de sesión. Se revalidó la compuerta de setters del prototipo. No se ejecutó PowerShell Windows ni probó hardware en la nube: esas comprobaciones quedan pendientes para esta versión.

El servidor local usa token por arranque, dueño de sesión de navegador y secuencia propia. Lanzador solicita elevación para HttpListener y RemoteSigned por proceso; no cambia política global. Puerto8770, archivo temporal separado SpiderGateway-continuous.txt. El instalador depende del prototipo solo durante creación; los siguientes arranques son independientes.
