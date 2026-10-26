# AUDIT_REPORT — alerta_temprana_v2 (después de corregir)
- Archivos: `main.py`, `src/config.py`, `src/datos.py`, `src/modelos.py`, `src/validacion.py`, `src/alerta.py`, `src/auditoria.py` en la rama `correccion/auditoria-subgrupos` · Fecha: 2026-10-25 · Skill: auditoria-modelos (Tarea 4.1)
- Objetivo: `no_completo` (positiva = 1, no completó) · Subgrupos: `genero`, grupo de edad (16-24, 25-39, 40+), `region`, `cohorte`
- Supuestos: (1) se audita el modelo que la herramienta elige y despliega, "Regresión logística (balanced)"; (2) cada script cuenta como una celda y las citas usan `archivo.py, l. L`; (3) la evidencia de ejecución se generó con los comandos de la propia herramienta y se guardó en `evidencia/`.

## Resumen
PASA: 15 · FALLA: 1 · NSPD: 1 — Quedan corregidos V1.2, V1.4 y V4.1. Sigue en FALLA la brecha del grupo de 40 años o más (V4.2), que es estable con 5 semillas; no se corrigió y queda explicada en el README.

## Verificaciones
| ID | Verificación | Resultado | Evidencia |
|---|---|---|---|
| V0.1 | Ejecución sin errores | PASA | `evidencia/salida_main_evaluar_v2.txt` y `evidencia/salida_main_auditar_v2.txt`: ambos comandos terminan sin error |
| V1.1 | Métricas en rango | PASA | `salida_main_evaluar_v2.txt`: medias entre 0.335 y 0.666; `salida_main_auditar_v2.txt`: exhaustividades por subgrupo entre 0.508 y 0.761 |
| V1.2 | Coherencia con la matriz | PASA | `salida_main_auditar_v2.txt`: VN=720 FP=298 FN=188 VP=314; 314/502 = 0.625 y 314/612 = 0.513, iguales a lo impreso y a la CV (0.625 / 0.514, ±0.01). La prueba `tests/test_auditoria.py::test_matriz_de_confusion_cuadra_con_las_metricas` lo comprueba en cada ejecución |
| V1.3 | Desbalance | PASA | p_min = 0.330 < 0.40 (`salida_main_evaluar_v2.txt`: "no completó = 33.0%"); se reportan exhaustividad, precisión, F1 y exactitud balanceada (`src/validacion.py, l. 7-12`) |
| V1.4 | Costo del error | PASA | `src/config.py, l. 10-14`: el falso negativo (no detectar a quien abandona) es más costoso que el falso positivo, y por eso la métrica prioritaria es la exhaustividad, con precisión ≥ 0.50; el README lo repite en la sección Problema |
| V2.1 | Orden de transformaciones | PASA | `StandardScaler` y `OneHotEncoder` dentro de `Pipeline` (`src/modelos.py, l. 30-36, 44-52`), evaluado con `cross_validate` (`src/validacion.py, l. 25`) y `cross_val_predict` (`src/auditoria.py, l. 28`) |
| V2.2 | Semilla | PASA | `src/validacion.py, l. 18` (`shuffle=True, random_state=SEMILLA`); `src/modelos.py, l. 42` y `l. 51`. El inventario vuelve a marcar `l. 50` por el mismo falso positivo de la v1 (la semilla está en la línea siguiente) |
| V2.3 | Estratificación | PASA | `src/validacion.py, l. 18`: `StratifiedKFold` |
| V2.4 | Misma partición | PASA | `src/validacion.py, l. 25` y `src/auditoria.py, l. 28` usan la misma `particion()` |
| V2.5 | Hiperparámetros | NSPD | Ningún hiperparámetro se presenta como elegido por validación: los del Random Forest y el umbral 0.75 de la regla están fijados y declarados (`src/modelos.py, l. 15-16, 50-51`) |
| V3.1 | Fuga por transformaciones | PASA | La CV y la matriz de confusión usan predicciones fuera de pliegue (`src/validacion.py, l. 25`; `src/auditoria.py, l. 28`). La validación temporal ajusta solo con las cohortes 2022-1 a 2025-1 (`src/auditoria.py, l. 64-65`) y evalúa en 2025-2. `entrenar()` ajusta con todo solo para el modelo final (`src/alerta.py, l. 30`); su promedio de referencia (`l. 31`) se usa para explicar las alertas, no para medir |
| V3.2 | Columnas del futuro | PASA | `src/config.py, l. 16-24` (solo información de la semana 3); `l. 27` excluye `asistencia_total`, `semanas_completadas` y `empleo_q2`; `src/datos.py, l. 45` lo comprueba con `assert`, y la prueba `test_columnas_del_futuro_y_sensibles_no_son_predictores` también |
| V4.1 | Cálculo por subgrupo | PASA | `src/auditoria.py, l. 42-58` calcula la exhaustividad por género, grupo de edad, región y cohorte con el umbral de la Skill; `main.py, l. 71` la imprime en `python main.py auditar` |
| V4.2 | Brecha | FALLA | `salida_main_auditar_v2.txt`: 40+ = 0.541 (n=544, 185 positivos, −0.085, cociente 0.75); Norte 0.570, Este 0.574, Metro (cociente 0.79); cohortes 2022-1 = 0.508 y 2023-2 = 0.535. `evidencia/verificacion_estabilidad_edad.py (salida)`: 40+ = 0.557 a 0.578 con 5 semillas, frente a una media global de 0.636. **La brecha de edad es estable, no es ruido** |
| V5.1 | Dependencias | PASA | `datos/participantes_sinteticos.csv` está en el repositorio; `tests/test_datos.py::test_generador_es_reproducible_y_coincide_con_el_csv` comprueba que el generador lo reproduce |
| V5.2 | Estado aleatorio | PASA | `datos/generar_datos.py, l. 27`: `rng` local a la función |
| V6.1 | Divisiones seguras | PASA | El inventario no encuentra `division_por_columna` en ningún archivo. Las únicas divisiones están en `src/auditoria.py, l. 34` (`vp / (vp + fn)`, `vp / (vp + fp)`) y `l. 57` (`r / mejor`): con estos datos hay 502 positivos, 612 predicciones positivas y la mejor exhaustividad es mayor que 0, así que ningún denominador vale 0 |
| V6.2 | Validación antes de entrenar | PASA | `main.py, l. 23` y `l. 59`, `src/alerta.py, l. 28` y `l. 60` llaman `validar_datos()` antes de `fit` y de `predict` |

## Acciones recomendadas
1. (V4.2) **Brecha de 40+: no corregida, explicada.** Lo que se probó: (a) usar la edad como predictor queda descartado, porque es una variable sensible que solo se usa para auditar (`src/config.py`, `COLUMNAS_SENSIBLES`); (b) bajar el umbral de decisión a 0.40 sube la exhaustividad a 0.77, pero la precisión baja a 0.45, por debajo del mínimo de 0.50 de la propuesta, y el umbral tendría que elegirse con validación interna (V2.5). La causa no está del todo clara: la asistencia temprana del grupo 40+ es algo mayor (0.84 / 0.77 frente a 0.82 / 0.75 en 16-24), así que su abandono da menos señal en las semanas 1-3. Mitigación documentada en el README: en participantes de 40+, "seguimiento normal" no equivale a "sin riesgo", y la coordinación mantiene su contacto habitual. Con datos reales, este debe ser el primer punto que se revise.
2. (V4.2, región y cohorte) Las brechas por región (Norte, Este, Metro) y cohorte (2022-1, 2023-2) se basan en 55 a 145 positivos y no se repiten de forma consistente entre cohortes vecinas. Hay que vigilarlas en cada reentrenamiento con `python main.py auditar`.
3. (V2.5, NSPD) Si se decide ajustar el umbral o los hiperparámetros, hacerlo con `GridSearchCV` dentro de la CV (validación anidada), nunca mirando la cohorte de prueba.

## Limitaciones de esta auditoría
Los datos son sintéticos: la auditoría comprueba el método, no la realidad de un programa WIOA. El extractor de la Skill trata cada script como una sola celda y repite un falso positivo en V2.2. No se auditaron subgrupos cruzados (por ejemplo, mujeres de 40+ en el Centro) porque tienen menos de 30 positivos.
