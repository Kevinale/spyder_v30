# Semántica de parameter_id 0xffffffff en la captura No Amp

**Conclusión:** no está demostrado que `0xffffffff` sea `@volume` ni un parámetro genérico de volumen. El código de Remote distingue un caso especial `parameter_id==-1` **sólo cuando el tipo de valor es1**, que interpreta como `@model`. Las650 notificaciones de esta captura llevan tipo4, por lo que no entran en ese caso. Deben publicarse como **Amp / parámetro no resuelto0xffffffff / float**, conservando el número original, sin inventar nombre.

## Evidencia recibida de la captura

Root ha reconstruido650 mensajes IN operation4, payload16 bytes:

```
asset_id42 | parameter_id0xffffffff | type4 | float32LE
```

La tabla de símbolos recuperada del dispositivo en la captura anterior resuelve42 como `Amp`; `0xffffffff` queda fuera de su rango. Los IDs Drive38, Bass33, Mid35 y Treble36 no aparecen en esas650 notificaciones. El recurso `No Amp` expone `@volume`, pero la coincidencia contextual no establece la semántica del identificador capturado.

## Consumidor real de la notificación: FUN_100987c0

Evidencia Ghidra en `native_reserved_focused.txt`, función VA0x100987c0, RVA0x987c0, offset PE0x97bc0. Es código del archivo `remote/extracted/Spider V Remote/APIV3EngineDLL.dll`.

1. Recibe una pareja tipada y dos IDs. Para cada ID intenta resolver un nombre mediante tabla de símbolos: exige `id<count` con comparación **unsigned** y valida offset de cadena.
2. Para tipo4 copia el segundo word y construye la variante interna tipo6, coherente con float32.
3. Implementa expresamente:

```c
if ((ids[1] == 0xffffffff) && (typed_value[0] == 1)) {
    parameter_name = "@model";
    value = symbol_table_lookup(typed_value[1]);
    /* ... */
}
```

4. Para tipo4, esa condición es falsa. No hay otra rama que cambie el nombre a `@volume` ni a un parámetro predeterminado en esta función. La resolución ordinaria de `0xffffffff` no proporciona una cadena válida.
5. Si el primer ID es distinto de-1, la ruta final entrega al listener el nombre de parámetro obtenido, el nombre del asset y la variante. No se ha atribuido al listener una recuperación posterior de `@volume` para este caso.

Esto establece lo que hace este consumidor; no identifica qué intención interna del firmware produjo el ID fuera de tabla. No se ha localizado una definición de fabricante que lo nombre `invalid`, `unavailable` o `default`. Por ello se conserva la descripción «no resuelto».

## La ruta de @volume sí tiene otra correspondencia explícita

`FUN_10084570`, VA0x10084570/RVA0x84570/offset0x83970, selecciona la tabla especial Parker para los IDs de dispositivo0x220000–0x220005. La tabla contiene25 triples de nombres. El último, dirección VA0x1018e9c8/RVA0x18e9c8/offset0x18cfc8, es:

| Nombre firmware | Grupo de aplicación | Parámetro de aplicación |
|---|---|---|
| ChannelVolume | amp | @volume |

Las tres cadenas están apuntadas explícitamente por el triple. `ChannelVolume` existe con índice804 en la tabla SDB capturada del dispositivo; también existe en los recursos Parker. Esta correspondencia demuestra una traducción nominal real para `amp/@volume`; **no** convierte por sí misma el mensaje `[42,-1,4,float]` en ChannelVolume y no demuestra qué tuple completo usaría el dispositivo para notificarlo.

`extract_special_mapping.py` extrae esos25 triples desde los bytes PE sin ejecutar código y guarda `parker_special_mapping.json`. No modifica el DLL.

## Otras comprobaciones del sentinel

- `FUN_100ac720`, VA0x100ac720/RVA0xac720/offset0xabb20, resuelve un índice únicamente si `index<count` (unsigned). Con una tabla de916 símbolos, `0xffffffff` no es resoluble por esa función.
- Los setters nativos `FUN_100998e0` y `FUN_100999a0` retornan antes de serializar si su segundo identificador es-1. El código y sus direcciones se conservan en `../captures/native_setters.txt`. Esto impide asumir que-1 sea un parámetro ordinario intercambiable con Drive38.
- El caso de tipo1→`@model` no debe generalizarse a tipo2 ni tipo4. Tampoco se aplica al mensaje anterior operation3, `[group2,param-1,type2,int1]`, sin seguir su consumidor específico.

## Nivel de confianza

| Hallazgo | Confianza |
|---|---|
| Tipo4 es float32; la notificación tiene asset42 e ID de parámetro0xffffffff | Alta, captura y consumidor nativo |
| Caso especial -1+tipo1 se traduce a @model | Alta, condición y literal explícitos |
| Tabla Parker traduce ChannelVolume a amp/@volume | Alta, tabla de punteros y selector de familia |
| -1+tipo4 significa @volume o un parámetro predeterminado | No establecido |
| Por qué el firmware emite ese ID en No Amp | Pendiente |
| Los650 eventos identifican por separado Drive/Bass/Mid/Treble | No establecido por los IDs capturados |

## Reproducción y próximos pasos de lectura

```
python /workspace/analysis/captures_noamp/extract_special_mapping.py
```

Pseudocódigo, referencias y log de Ghidra: `native_reserved.txt`, `native_reserved_focused.txt`, `native_reserved.log`. Se utilizó `TargetEvidence.java` con las direcciones de las cadenas `@volume`0x10175824, `@enabled`0x10117000, `@model`0x10117040/0x10175964 y lookup0x100ac720, sobre el proyecto `remote/ghidra/Native`, opción `-noanalysis`. La exportación incluye referencias adicionales; el archivo focused contiene los tres consumidores necesarios. `native_reserved_offsets.json` conserva conversiones de direcciones con pefile.

El siguiente paso útil es seguir estáticamente el listener de `FUN_100987c0` para determinar si descarta nombres vacíos o tiene alguna recuperación específica. Los seis grupos temporales observados no identifican por sí solos controles: sin marcas de origen, no deben asignarse a Drive/Bass/Mid/Treble. Con el payload actual, no hay cuatro identificadores distintos que permitan enrutar esos cuatro controles por separado. Ninguno de estos hallazgos justifica reenviar comandos ni escribir firmware/memoria.

No se ejecutaron los DLL ni se accedió al dispositivo; sólo se leyeron la captura y copias originales del software con analizadores de confianza.
