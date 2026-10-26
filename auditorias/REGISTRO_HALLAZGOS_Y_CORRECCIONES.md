# Registro de la auditoría: hallazgos, correcciones y comprobación

Skill aplicada: `auditoria-modelos` (Tarea 4.1, copiada en `.claude/skills/auditoria-modelos/`).
- Antes: `auditorias/v1_antes/AUDIT_REPORT_alerta_temprana_v1.md` (commit `e654306`): 11 PASA · 3 FALLA · 3 NSPD.
- Después: `auditorias/v2_despues/AUDIT_REPORT_alerta_temprana_v2.md`: 15 PASA · 1 FALLA · 1 NSPD.

| Revisión de la guía | ID | Qué encontró | Qué se corrigió | Cómo se comprobó |
|---|---|---|---|---|
| Fuga de datos | V3.1 / V3.2 | **Sin fuga.** La preparación está dentro del Pipeline y las tres columnas del futuro (`asistencia_total`, `semanas_completadas`, `empleo_q2`) están fuera de los predictores | Nada que corregir. Se agregaron pruebas para que siga así | `test_columnas_del_futuro_y_sensibles_no_son_predictores` y `test_preparacion_dentro_del_pipeline` (pytest) |
| Partición | V2.1-V2.4 + observación | CV estratificada con semilla y la misma partición para todos (PASA), pero **sin la validación temporal por cohorte** que prometía la propuesta | Se agregó `validacion_temporal()` (`src/auditoria.py`): entrena con 2022-1 a 2025-1 y prueba con 2025-2 | Exhaustividad 0.639 y precisión 0.575, similares a la CV (0.625 / 0.514): mezclar cohortes no inflaba el resultado. Prueba `test_validacion_temporal_no_entrena_con_la_cohorte_de_prueba` |
| Partición (métricas) | V1.2 | No había matriz de confusión | `python main.py auditar` la imprime con predicciones fuera de pliegue | VN 720, FP 298, FN 188, VP 314 → 0.625 / 0.513. Prueba `test_matriz_de_confusion_cuadra_con_las_metricas` |
| Métricas | V1.4 | No se justificaba por qué la exhaustividad es la métrica prioritaria | Texto en `src/config.py` (l. 10-14) y en el README: el falso negativo es el error más costoso | Segunda auditoría: V1.4 = PASA |
| Subgrupos | V4.1 | La herramienta no medía ningún subgrupo | `exhaustividad_por_subgrupo()` con el umbral de la Skill (0.05 por debajo del global o cociente < 0.80, con ≥ 30 positivos) | Segunda auditoría: V4.1 = PASA. Prueba `test_tabla_de_subgrupos_aplica_el_umbral_de_la_skill` |
| Subgrupos | V4.2 | Brecha en el grupo **40+: 0.541** frente a 0.625 global; brechas menores en Norte, Este, Metro y en dos cohortes | **No corregida; queda explicada.** Usar la edad como predictor queda descartado (variable sensible), y bajar el umbral rompe la precisión mínima (0.45 < 0.50). Mitigación en el README: en 40+, "seguimiento normal" no equivale a "sin riesgo" | `verificacion_estabilidad_edad.py`: 0.557 a 0.578 con 5 semillas, así que la brecha es real y no ruido. `python main.py auditar` la muestra en cada reentrenamiento |

Falso positivo de la propia Skill: el extractor marcó `estimador_sin_semilla` en `src/modelos.py, l. 50`, pero la semilla está en la línea 51 (la llamada ocupa dos líneas). Se dejó anotado en ambos informes en lugar de cambiar el código para "complacer" al extractor.
