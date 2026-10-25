# Skill `auditoria-modelos`

Audita un proyecto de machine learning (`.ipynb` o `.py`) **sin modificarlo** y produce `AUDIT_REPORT_<proyecto>.md`. Cada verificación termina en `PASA`, `FALLA` o `NO SE PUEDE DETERMINAR` y cita su evidencia.

## Qué audita

| Bloque | Verificaciones |
|---|---|
| V0 Ejecución | El notebook corre sin errores; si no, las métricas no se dan por buenas |
| V1 Métricas | Rango válido, coherencia con la matriz de confusión, no solo accuracy con desbalance (p_min < 0.8/K), métrica acorde al costo del error |
| V2 Partición | División antes de todo `fit` que aprende, semillas, estratificación, misma partición entre modelos, hiperparámetros elegidos por validación |
| V3 Fuga | Ninguna métrica de prueba/CV sale de un ajuste que vio esas filas; ningún predictor se conoce solo después del resultado |
| V4 Disparidad | Métrica prioritaria por subgrupo; FALLA si un subgrupo con n ≥ 30 queda > 0.05 bajo el global o con cociente < 0.80 |
| V5 Reproducibilidad | Archivos disponibles; sin generador aleatorio global consumido en varias cargas |
| V6 Integridad | Divisiones protegidas contra cero; la validación de datos se ejecuta antes del `fit` |

## Cómo se invoca

En Claude Code, dentro del repositorio:

```
/auditoria-modelos auditorias/c_tercer_proyecto/App_Prediccion_Ingresos_Adult.ipynb objetivo=income_gt_50k positiva=1 subgrupos=sex
```

También se activa sola si pides "audita este notebook". Si no indicas la columna de subgrupos, V4 queda en `NO SE PUEDE DETERMINAR`: la Skill no inventa subgrupos.

El inventario de evidencia también se puede correr a mano (solo lectura):

```
python .claude/skills/auditoria-modelos/scripts/extraer_evidencia.py <archivo.ipynb> [--json]
```

## Cómo interpretar el informe

- **FALLA:** hay evidencia concreta de un defecto. Tiene una acción recomendada. Prioridad: V3 > V0 > V2 > V6 > V1 > V4 > V5.
- **PASA:** hay evidencia **observada** de que la propiedad se cumple. Nunca significa "no encontré nada".
- **NO SE PUEDE DETERMINAR:** falta información (sin salida, sin subgrupo, código ausente). No es un aprobado: la sección de acciones dice qué falta.
- **Cita** `celda N (id X), l. L`: N cuenta solo celdas de código desde 1; `texto N` cuenta celdas Markdown. El `id` permite ubicar la celda aunque se inserten otras.
- Las carpetas `evidencia/` guardan los scripts de **verificación reproducida**: ejecutan una copia en memoria, nunca el archivo original.

## Limitaciones conocidas

1. **V3.2 depende de conocer el dominio.** El script solo detecta columnas construidas con `np.where` sobre otra columna; una fuga que llega ya dentro del CSV no se ve en el código y queda en NSPD o depende de la descripción.
2. **El inventario es por patrones de texto** (regex): no sigue variables entre celdas ni código en otros módulos. Orienta la lectura, no la reemplaza.
3. **V4 necesita que el usuario nombre el subgrupo** y datos suficientes (n ≥ 30); con grupos pequeños el resultado es NSPD o excluye ese grupo.
4. **Solo clasificación.** Los criterios de V1 no cubren regresión (MAE, RMSE, R²).
5. **La estabilidad se probó en la misma sesión**, no con instancias independientes de Claude Code (ver `auditorias/ESTABILIDAD_Y_REFINAMIENTO.md`).
6. **Series de tiempo y datos agrupados** (pacientes repetidos, etc.) no se verifican: la Skill no exige `TimeSeriesSplit` ni `GroupKFold`.

## Historial

v1 (`1515d39`) → refinamientos 1-5 (`16f083b`, `c42e67d`, `978520f`, `ae67998`, `fe73cdc`). El detalle de cada fallo y su corrección está en `auditorias/ESTABILIDAD_Y_REFINAMIENTO.md`.
