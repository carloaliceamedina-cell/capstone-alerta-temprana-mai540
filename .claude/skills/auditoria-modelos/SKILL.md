---
name: auditoria-modelos
description: Audita un proyecto de machine learning (notebook .ipynb o script .py) sin modificarlo y emite AUDIT_REPORT_<proyecto>.md con veredictos PASA / FALLA / NO SE PUEDE DETERMINAR, cada uno con evidencia citada, sobre ejecución, métricas reportadas, partición de datos, fuga de información, disparidad entre subgrupos, integridad de características y reproducibilidad. Usar cuando el usuario pida auditar, revisar o validar un modelo o notebook de clasificación, o invoque /auditoria-modelos.
---

# Propósito

Verificar, con evidencia citada y sin modificar el proyecto, que un modelo de ML se ejecuta, reporta métricas válidas y adecuadas al costo del error, divide los datos sin fuga y no oculta disparidad entre subgrupos.

# Entradas esperadas

| Entrada | Obligatoria | Si falta |
|---|---|---|
| Ruta del notebook `.ipynb` o script `.py` | Sí | Pedirla. No auditar "de memoria". |
| Columna objetivo y clase positiva | Sí | Buscarla en el código (`y = df[...]`) y declararla como **supuesto** en el encabezado. |
| Columna(s) de subgrupo | No | V4 = NO SE PUEDE DETERMINAR. No inventar subgrupos. |
| Nombre corto del proyecto | No | Usar el nombre del archivo sin extensión. |
| Descripción del problema (costo de cada error) | No | Tomarla de las celdas de texto del propio notebook. |

# Reglas de diseño (obligatorias)

1. **Solo lectura.** No se edita, reformatea ni vuelve a guardar ningún archivo del proyecto. Si hace falta ejecutar algo para obtener evidencia, se hace sobre una **copia** en un directorio temporal o en `auditorias/<proyecto>/evidencia/`, y el script queda guardado junto al informe.
2. **Tres veredictos y nada más:** `PASA`, `FALLA`, `NO SE PUEDE DETERMINAR` (NSPD).
3. **Sin evidencia no hay PASA.** Un PASA exige evidencia **observada** (una salida del notebook, una línea de código que demuestra la propiedad o una ejecución de verificación). "No encontré nada que lo contradiga" es NSPD, nunca PASA.
4. **Toda cita usa el formato estable** `celda N (id XXXXXXXX), l. L`, donde N cuenta **solo celdas de código** desde 1 y L es la línea dentro de la celda. Para scripts: `archivo.py, l. L`. Las celdas de texto se citan como `texto N` (contando solo celdas Markdown desde 1). Usar el inventario del paso 2 para obtener estas referencias.
5. **Un veredicto por sub-verificación.** No agrupar.
6. **La regla de decisión es la tabla de cada criterio**, no la intuición del auditor. Si ninguna fila de la tabla aplica, el veredicto es NSPD y se explica por qué.

# Pasos

1. Confirmar entradas (tabla de arriba). Escribir los supuestos.
2. Generar el inventario de evidencia (solo lectura):
   `python .claude/skills/auditoria-modelos/scripts/extraer_evidencia.py <archivo>`
   Da celdas numeradas, errores en salidas, celdas sin salida y señales (`split`, `fit_transform`, `transformador`, `pipeline`, `metrica`, `division_por_columna`, `rng_global`, `estimador_sin_semilla`, `derivada_de_otra_columna`).
3. Leer el archivo completo, incluidas las celdas de texto y las salidas. El inventario orienta; no reemplaza la lectura.
4. Aplicar V0 → V6 en ese orden. V0 condiciona a V1 y V4.
5. Si V1.2, V1.3 o V4 necesitan números que el notebook no produjo, se puede ejecutar una **verificación reproducida** sobre una copia (regla 1) y citarla como `evidencia/<script>.py (salida)`.
6. Escribir `AUDIT_REPORT_<proyecto>.md` con la plantilla de **Salida**.
7. Antes de entregar, revisar el propio informe: cada fila tiene evidencia con el formato de la regla 4; ningún PASA descansa en ausencia de evidencia; cada FALLA tiene una acción recomendada.

# Criterios de verificación

## V0. Ejecución (condiciona V1 y V4)
| ID | PASA | FALLA | NSPD |
|---|---|---|---|
| V0.1 | Todas las celdas de código tienen salida o no producen salida por diseño, y ninguna salida es un error | Alguna salida es un error (`ValueError`, `NameError`, …) | El notebook no tiene salidas guardadas |

Si V0.1 ≠ PASA, toda métrica que dependa de una celda con error o sin salida se marca NSPD en V1.1-V1.2 (no se supone su valor por el código).

## V1. Métricas reportadas
Definiciones: *K* = número de clases; *p_min* = proporción de la clase menos frecuente. Hay **desbalance** si `p_min < 0.8 × (1/K)` (binaria: `p_min < 0.40`; tres clases: `p_min < 0.267`).

| ID | PASA | FALLA | NSPD |
|---|---|---|---|
| V1.1 Rango | Todas las métricas **impresas** están en [0, 1] (clasificación) | Alguna fuera de rango, `nan` o `inf` | No hay métricas impresas (V0 ≠ PASA o celda sin salida) |
| V1.2 Coherencia con la matriz | Hay matriz de confusión y precisión/exhaustividad/F1 reportadas coinciden con VP/FP/FN (±0.01) | No coinciden | No hay matriz, o no hay métricas derivadas que comparar |
| V1.3 Desbalance | No hay desbalance, **o** lo hay y se reporta al menos una métrica por clase (precisión, exhaustividad, F1, *balanced accuracy*) | Hay desbalance y solo se reporta accuracy | No se puede calcular *p_min* (no hay distribución de clases visible ni código que la muestre) |
| V1.4 Costo del error | Una celda de texto nombra qué error es más costoso y la métrica prioritaria es coherente con eso; **o** clases balanceadas y el problema no menciona costos asimétricos (se cita la celda que describe el problema) | El dominio tiene costos asimétricos (salud, crédito, fraude, contratación…) o hay desbalance, y la métrica elegida no lo refleja o no hay justificación | No hay descripción del problema |

## V2. Partición de datos
| ID | PASA | FALLA | NSPD |
|---|---|---|---|
| V2.1 Orden | Todo transformador que aprende (`fit`/`fit_transform` de escalado, imputación, codificación, selección) se ajusta solo con entrenamiento: dentro de un `Pipeline` evaluado con CV, o `fit` sobre `X_train` después del `split` | Algún transformador se ajusta sobre `X` completo antes del `split`/CV y ese resultado se usa para evaluar | No hay forma de ver el orden (código en otro archivo no provisto). **Si no hay transformadores, PASA** citando la línea del `split` |
| V2.2 Semilla | Toda fuente de aleatoriedad que afecta la evaluación tiene semilla: `split`/CV con `shuffle`, y estimadores aleatorios (árboles, bosques, boosting) | Alguna sin `random_state` | — |
| V2.3 Estratificación | Clasificación con `stratify=y` o `StratifiedKFold` (o `cross_val_score` con `cv` entero y clasificador, que estratifica por defecto) | `train_test_split` o `KFold` sin estratificar en clasificación | Regresión (no aplica: escribir "no aplica" en la evidencia y marcar NSPD) |
| V2.4 Misma partición | Todos los modelos **comparados** se evalúan con el mismo objeto/parámetros de partición | Particiones distintas entre modelos comparados | Solo hay un modelo (no hay comparación) |
| V2.5 Hiperparámetros | Cada hiperparámetro que el proyecto dice haber **elegido** (k, `max_depth`, `C`…) se elige con validación interna (`GridSearchCV` dentro de la CV, o sobre un conjunto de validación separado de prueba), y el código coincide con lo que dice el texto o la etiqueta | Se elige mirando el puntaje de prueba, **o** el texto/etiqueta dice "elegido por validación" pero el código lo fija a mano | Ningún hiperparámetro se presenta como elegido (valores por defecto o fijados y declarados como tales) |

## V3. Fuga de información
| ID | PASA | FALLA | NSPD |
|---|---|---|---|
| V3.1 Transformaciones | Ninguna **métrica reportada como generalización** (prueba, CV) se calcula con predicciones de un modelo o transformador que vio esas filas | Alguna métrica de prueba/CV proviene de un ajuste que incluyó las filas evaluadas | — |
| V3.2 Columnas del futuro | Para cada predictor hay evidencia de que existe antes de la predicción (origen en el código o en la descripción) | Un predictor **se construye a partir del objetivo** (señal `derivada_de_otra_columna` sobre el objetivo) **o** la descripción dice que se registra después del resultado | Un predictor es sospechoso por dominio pero el código/descripción no permite fechar cuándo se conoce: marcar NSPD y pedir confirmación en Acciones |

Aclaraciones de V3.1 (para evitar falsos positivos): entrenar sobre todo el dataset **no es fuga** si ese modelo solo se usa para (a) visualizar fronteras, (b) medir accuracy de **entrenamiento** rotulada como tal, o (c) producir el modelo final después de evaluar. `cross_val_score` clona el estimador, así que evaluar un modelo previamente ajustado no filtra información.

Alcance de V3.2: se evalúan los predictores del modelo que el proyecto **reporta como resultado o guarda/despliega**. Un bloque que usa una columna de fuga a propósito y está rotulado como demostración (por ejemplo "con fuga vs. sin fuga") no es FALLA; se menciona en la evidencia.

Aclaración de V3.2: "correlación alta" o "en otro proyecto se consideró fuga" **no bastan** para FALLA. El criterio es temporal: ¿el valor existe en el momento de predecir?

## V4. Disparidad entre subgrupos
Umbral: se marca disparidad si, en la métrica prioritaria de V1.4 (por defecto, exhaustividad de la clase positiva), algún subgrupo con **n ≥ 30** en el conjunto evaluado está **más de 0.05 por debajo del global** o su cociente subgrupo/mejor subgrupo es **< 0.80**. Justificación: 0.05 es mayor que la variación típica entre particiones de un conjunto de algunos cientos de casos y menor que las brechas que cambian decisiones; 0.80 replica la regla de las cuatro quintas partes usada en auditorías de impacto dispar. Con n < 30 la estimación es demasiado inestable para decidir.

| ID | PASA | FALLA | NSPD |
|---|---|---|---|
| V4.1 Cálculo por subgrupo | El proyecto calcula la métrica prioritaria por subgrupo | No la calcula (y se indicó una columna de subgrupo) | No se indicó columna de subgrupo |
| V4.2 Brecha | Ningún subgrupo con n ≥ 30 supera el umbral (en el proyecto o en la verificación reproducida) | Algún subgrupo supera el umbral | No hay números por subgrupo, V0 impide reproducirlos o todos los subgrupos tienen n < 30 |

## V5. Reproducibilidad
| ID | PASA | FALLA | NSPD |
|---|---|---|---|
| V5.1 Dependencias | Los datos vienen de una librería o se generan en el proyecto, o el archivo referido está en el repositorio | Se lee un archivo que no está | — |
| V5.2 Estado aleatorio | Los datos no dependen de un generador global que se consume en varias llamadas (`rng_global` dentro de una función que se llama más de una vez) | Una función de carga usa un `rng` global y se llama más de una vez: cada llamada produce datos distintos | — |

## V6. Integridad de características
| ID | PASA | FALLA | NSPD |
|---|---|---|---|
| V6.1 Divisiones seguras | Cada `division_por_columna` tiene protección contra cero (`clip(lower=…)`, `replace(0, …)`, `np.where(den==0, …)`) o el denominador es estrictamente positivo por construcción (citar la línea) | Algún denominador puede valer 0 según el código que lo genera | No se puede ver cómo se genera el denominador |
| V6.2 Validación antes de entrenar | Hay una comprobación de nulos/infinitos que **se ejecuta** antes del `fit` | Existe una función de validación definida pero nunca llamada | No hay función de validación (anotar como acción, no como FALLA) |

# Salida

Archivo `AUDIT_REPORT_<proyecto>.md` junto al archivo auditado (o en `auditorias/<proyecto>/`):

```markdown
# AUDIT_REPORT — <proyecto>
- Archivo: <ruta> · Fecha: <AAAA-MM-DD> · Skill: auditoria-modelos v<versión>
- Objetivo: <columna> (positiva = <clase>) · Subgrupos: <columna o "no indicados"> · Supuestos: <lista>

## Resumen
PASA: n · FALLA: n · NSPD: n — <una frase con el hallazgo más grave>

## Verificaciones
| ID | Verificación | Resultado | Evidencia |
|---|---|---|---|
| V0.1 | Ejecución sin errores | FALLA | celda 9 (id 93d6fc8f): ValueError: Input X contains infinity |
...

## Acciones recomendadas
1. (<ID>) <acción concreta>  — una por cada FALLA, ordenadas por gravedad (fuga > partición > métricas > disparidad > resto)
2. (<ID>, NSPD) <qué información falta para decidir>

## Limitaciones de esta auditoría
<qué no se pudo ver y por qué>
```

Orden de gravedad para el resumen: V3 > V0 > V2 > V6 > V1 > V4 > V5.
