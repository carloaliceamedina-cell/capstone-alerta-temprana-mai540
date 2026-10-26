# AUDIT_REPORT — alerta_temprana (versión 1, antes de corregir)
- Archivos: `main.py`, `src/config.py`, `src/datos.py`, `src/modelos.py`, `src/validacion.py`, `src/alerta.py` en el commit `e654306` (rama `main`) · Fecha: 2026-10-25 · Skill: auditoria-modelos (Tarea 4.1)
- Objetivo: `no_completo` (positiva = 1, no completó el programa) · Subgrupos: `genero`, grupo de edad (16-24, 25-39, 40+ a partir de `edad`), `region`, `cohorte`
- Supuestos: (1) el modelo auditado es el que la herramienta elige y despliega, "Regresión logística (balanced)" (`main.py` lo imprime como elegido); (2) como el proyecto son scripts y no un notebook, cada archivo cuenta como una sola "celda" y las citas usan `archivo.py, l. L`; (3) los subgrupos los indicó el autor; la herramienta v1 no los calcula.

## Resumen
PASA: 11 · FALLA: 3 · NSPD: 3 — El hallazgo más grave es la disparidad: la exhaustividad del grupo de 40 años o más (0.541) queda 0.085 por debajo del global (0.625), y la herramienta no mide ningún subgrupo.

## Verificaciones
| ID | Verificación | Resultado | Evidencia |
|---|---|---|---|
| V0.1 | Ejecución sin errores | PASA | `evidencia/salida_main_evaluar_v1.txt`: `python main.py evaluar` termina e imprime la tabla y "Modelo elegido: Regresión logística (balanced)" |
| V1.1 | Métricas en rango | PASA | `evidencia/salida_main_evaluar_v1.txt`: todas las medias y desviaciones están entre 0.032 y 0.666 |
| V1.2 | Coherencia con la matriz | NSPD | La v1 no produce matriz de confusión. Verificación reproducida: `evidencia/verificacion_subgrupos_v1.py (salida)`: VN=720 FP=298 FN=188 VP=314 → exhaustividad 314/502 = 0.625 y precisión 314/612 = 0.513, iguales a las medias de CV (0.625 / 0.514, ±0.01) |
| V1.3 | Desbalance | PASA | p_min = 0.330 < 0.40 (`salida_main_evaluar_v1.txt`: "no completó = 33.0%"); se reportan exhaustividad, precisión, F1 y exactitud balanceada (`src/validacion.py, l. 7-12`) |
| V1.4 | Costo del error | FALLA | El dominio tiene costos asimétricos: perder a un participante que abandona es más grave que ofrecer apoyo de más. `src/validacion.py, l. 8` dice que la exhaustividad es "la prioritaria", pero ningún texto del proyecto dice por qué (el README v1 tiene 3 líneas) |
| V2.1 | Orden de transformaciones | PASA | `StandardScaler` y `OneHotEncoder` viven dentro de `Pipeline` (`src/modelos.py, l. 30-36, 44-52`), evaluado con `cross_validate` (`src/validacion.py, l. 25`) |
| V2.2 | Semilla | PASA | `src/validacion.py, l. 18`: `StratifiedKFold(..., shuffle=True, random_state=SEMILLA)`; `src/modelos.py, l. 42` (Dummy) y `l. 51` (Random Forest) con `random_state=SEMILLA`. El inventario marcó `estimador_sin_semilla` en `l. 50`, pero es un falso positivo: la llamada sigue en la línea 51, donde está la semilla |
| V2.3 | Estratificación | PASA | `src/validacion.py, l. 18`: `StratifiedKFold` |
| V2.4 | Misma partición | PASA | `src/validacion.py, l. 25`: todos los modelos usan `cv=particion()`, la misma función con la misma semilla |
| V2.5 | Hiperparámetros | NSPD | Ningún hiperparámetro se presenta como elegido por validación: `n_estimators=300`, `min_samples_leaf=5` (`src/modelos.py, l. 50-51`) y el umbral 0.75 de la regla (`l. 15-16`, "fijado de antemano, no ajustado") son fijos y están declarados |
| V3.1 | Fuga por transformaciones | PASA | Las métricas de CV salen de `cross_validate`, que clona y ajusta el Pipeline en cada pliegue (`src/validacion.py, l. 25`). `entrenar()` ajusta con todos los datos solo para el modelo final, después de evaluar (`src/alerta.py, l. 24-28`) |
| V3.2 | Columnas del futuro | PASA | `src/config.py, l. 9-18` define los predictores como información de la semana 3; `l. 21` excluye `asistencia_total`, `semanas_completadas` y `empleo_q2`, y `src/datos.py, l. 45` lo comprueba con `assert` antes de separar X |
| V4.1 | Cálculo por subgrupo | FALLA | Se indicaron subgrupos y ningún archivo de la v1 calcula la exhaustividad por subgrupo (el inventario no tiene `groupby` ni métricas fuera de `src/validacion.py`) |
| V4.2 | Brecha | FALLA | `evidencia/verificacion_subgrupos_v1.py (salida)`: 40+ = 0.541 (n=544, 185 positivos; −0.085 frente a 0.625; cociente 0.75); Norte = 0.570 (−0.055); Este = 0.574 (cociente 0.75); Metro (cociente 0.79); cohortes 2022-1 = 0.508 y 2023-2 = 0.535. Género sin brecha (0.622 / 0.631) |
| V5.1 | Dependencias | PASA | `datos/participantes_sinteticos.csv` está en el repositorio y lo genera `datos/generar_datos.py` |
| V5.2 | Estado aleatorio | PASA | `datos/generar_datos.py, l. 27`: `rng = np.random.default_rng(semilla)` es local a la función |
| V6.1 | Divisiones seguras | PASA | El inventario no encontró ninguna `division_por_columna` en los seis archivos |
| V6.2 | Validación antes de entrenar | PASA | `main.py, l. 23` y `src/alerta.py, l. 26` llaman `validar_datos()` antes de `evaluar_cv` y de `fit` |

Observación del auditor (fuera de la tabla de la Skill): la propuesta del Módulo 5 prometía validar **por cohorte en el tiempo** (entrenar con cohortes anteriores y probar con la más reciente). La v1 solo usa CV estratificada que mezcla cohortes. No es FALLA según V2, pero conviene comprobar que mezclar cohortes no infla el resultado.

## Acciones recomendadas
1. (V4.1) Integrar en la herramienta el cálculo de exhaustividad por género, grupo de edad, región y cohorte con el umbral de la Skill, para que cada reentrenamiento lo muestre.
2. (V4.2) Investigar la brecha de 40+: comprobar si es estable con otras semillas. Si lo es, corregirla sin usar la edad como predictor; si no se puede, documentarla como limitación con una mitigación concreta para los coordinadores.
3. (V1.4) Escribir en el README y en `src/config.py` qué error es más costoso y por qué la exhaustividad es la métrica prioritaria.
4. (V1.2, NSPD) Imprimir la matriz de confusión fuera de pliegue para poder comprobar las métricas.
5. (Observación) Agregar la validación temporal (cohortes 2022-1 a 2025-1 → 2025-2) prometida en la propuesta.
6. (V2.5, NSPD) Si en el futuro se ajustan hiperparámetros, hacerlo con `GridSearchCV` dentro de la CV.

## Limitaciones de esta auditoría
Los datos son sintéticos: la auditoría comprueba el método, no la realidad de los programas WIOA de Puerto Rico. El extractor de evidencia trata cada script como una sola celda y produjo un falso positivo (V2.2). Las brechas por región y cohorte se basan en 55 a 145 positivos por grupo, así que tienen más ruido que la de edad.
