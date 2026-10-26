# Alerta temprana de no completación — Adiestramiento laboral (WIOA, Puerto Rico)

Herramienta de línea de comandos que, al cierre de la **semana 3** de un programa de adiestramiento, estima qué participantes tienen más riesgo de no completarlo y explica cada alerta con los tres factores que más pesan, para que la coordinación ofrezca apoyo a tiempo.

## Problema

En el desarrollo de fuerza laboral en Puerto Rico, los proveedores de adiestramiento financiados por WIOA se evalúan por sus tasas de completación, empleo e ingresos después de salir del programa. Hoy, a quien está en riesgo de abandonar se le detecta cuando ya faltó varias semanas, y entonces es tarde para intervenir. La herramienta apoya una sola decisión: **a quién ofrecer primero apoyo (transporte, cuido, tutoría) en la semana 3**. La usarían coordinadores y manejadores de caso del programa. **No decide elegibilidad, permanencia ni expulsión.**

**Qué error es más costoso.** No detectar a alguien que va a abandonar (falso negativo) cuesta más que ofrecer apoyo a alguien que lo habría completado igual (falso positivo): el primero pierde el adiestramiento y el programa pierde un resultado de desempeño; el segundo solo cuesta una llamada o un pase de transporte. Por eso la métrica prioritaria es la **exhaustividad (recall) de la clase "no completó"**, con una precisión mínima de 0.50 para que las alertas sigan siendo manejables.

## Datos

- **Fuente:** conjunto **sintético** generado por `datos/generar_datos.py` (semilla fija), con la estructura de los registros administrativos que describe la propuesta del Módulo 5: datos de admisión, asistencia de las semanas 1 a 3, desempeño en el módulo 1 y resultado final.
- **Permiso de uso:** los datos son sintéticos y no contienen a ninguna persona real, así que se pueden publicar y reutilizar libremente. Los registros reales de participantes son confidenciales: no pueden salir del proveedor ni subirse a GitHub ni a herramientas de IA.
- **Descripción:** 1,520 participantes en 8 cohortes (2022-1 a 2025-2); el 33.0 % no completó (clases desbalanceadas).

| Tipo | Columnas | Uso |
|---|---|---|
| Objetivo | `no_completo` (1 = no completó el programa) | lo que se predice |
| Predictores (semana 3) | `asistencia_sem1..3`, `puntuacion_modulo1`, `meses_desempleo`, `empleado_al_ingreso`, `barrera_transporte`, `barrera_cuido`, `ingreso_bajo`, `programa`, `area_adiestramiento`, `escolaridad` | entran al modelo |
| **Prohibidas por fuga** | `asistencia_total`, `semanas_completadas`, `empleo_q2` | se conocen después de la semana 3; nunca entran al modelo |
| Sensibles | `edad`, `genero`, `region` | solo para **auditar** (brechas por subgrupo), nunca para decidir |
| Identificadores | `id_participante`, `cohorte` | no predicen; `cohorte` se usa para la validación temporal |

## Cómo funciona

```
datos/participantes_sinteticos.csv
        │
        ▼
src/datos.py ── validar_datos(): columnas, vacíos, rangos y valores 0/1  (falla con un mensaje claro)
        │
        ▼
src/modelos.py ── 4 modelos bajo el mismo protocolo:
        │          · línea base 1: azar estratificado
        │          · línea base 2: regla actual de asistencia (< 75 % en semanas 1-3)
        │          · regresión logística (class_weight="balanced")   ← preparación dentro del Pipeline
        │          · Random Forest (class_weight="balanced")
        ▼
src/validacion.py ── CV estratificada de 5 pliegues (media ± desviación) + criterio de elección
        │
        ├──► src/alerta.py ──── probabilidad, alerta y los 3 factores que más suben el riesgo
        └──► src/auditoria.py ─ matriz de confusión, validación temporal y brechas por subgrupo
```

**Criterio de elección:** entre los modelos con precisión media ≥ 0.50, el de mayor exhaustividad media. Si la diferencia con la regresión logística es menor que una desviación estándar, gana la regresión logística, porque cada alerta debe poder explicarse factor por factor.

## Resultados

Validación cruzada estratificada de 5 pliegues (`python main.py evaluar`):

| Modelo | Exhaustividad (media ± desv.) | Precisión | F1 | Exactitud balanceada | Observación |
|---|---|---|---|---|---|
| Línea base: azar estratificado | 0.335 ± 0.065 | 0.343 ± 0.065 | 0.339 ± 0.065 | 0.509 ± 0.048 | referencia trivial |
| Línea base: regla de asistencia < 75 % | 0.514 ± 0.060 | 0.576 ± 0.040 | 0.543 ± 0.051 | 0.664 ± 0.035 | lo que se hace hoy |
| **Regresión logística (balanced)** | **0.625 ± 0.041** | 0.514 ± 0.040 | 0.564 ± 0.039 | 0.666 ± 0.033 | **elegido** |
| Random Forest (balanced) | 0.600 ± 0.044 | 0.517 ± 0.037 | 0.555 ± 0.039 | 0.662 ± 0.032 | sin ventaja |

- El modelo elegido detecta **11 puntos más** de quienes abandonan que la regla actual de asistencia (0.625 frente a 0.514), a cambio de algo menos de precisión.
- **Validación temporal** (entrenar con 2022-1 a 2025-1 y probar con 2025-2, como pedía la propuesta): exhaustividad 0.639 y precisión 0.575. Es similar a la CV, así que mezclar cohortes no infla el resultado.
- **Meta no alcanzada:** la propuesta pedía exhaustividad ≥ 0.75 con precisión ≥ 0.50. Bajar el umbral a 0.40 da 0.77 de exhaustividad, pero la precisión cae a 0.45. Ningún umbral cumple ambas metas con estos datos, así que se mantiene 0.50.

**Errores por categoría** (`python main.py auditar`, predicciones fuera de pliegue): matriz de confusión VN = 720, FP = 298, FN = 188, VP = 314. No hay brecha por género (0.622 F / 0.631 M). El grupo de **40 años o más** tiene exhaustividad **0.541**, 0.085 por debajo del global, y la brecha es estable con 5 semillas (0.557 a 0.578): quienes abandonan en ese grupo muestran menos señales tempranas (asistencia algo mayor en las semanas 1-3). Hay brechas menores en las regiones Norte y Este (0.570 y 0.574) y en las cohortes 2022-1 y 2023-2. Ver [Limitaciones](#limitaciones) y `auditorias/`.

## Instalación

Requisitos: Python 3.10 o más reciente y Git.

```bash
git clone https://github.com/carloaliceamedina-cell/capstone-alerta-temprana-mai540.git
cd capstone-alerta-temprana-mai540
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Cómo ejecutar

1. **Comparar los modelos y ver cuál se elige** (unos 10 segundos):

   ```bash
   python main.py evaluar
   ```
   Debes ver la tabla de la sección Resultados y, al final, `Modelo elegido: Regresión logística (balanced)`.

2. **Generar alertas para participantes nuevos.** El archivo debe tener las columnas de predictores de la semana 3; `datos/ejemplo_semana3.csv` trae 8 participantes de ejemplo:

   ```bash
   python main.py alertar datos/ejemplo_semana3.csv
   ```
   Salida esperada (primeras filas):
   ```
   id_participante  prob_no_completar             alerta                                                                                 factores_principales
           N002              0.748      OFRECER APOYO                     puntuación baja en el módulo 1; barrera de cuido; asistencia baja en la semana 3
           N004              0.639      OFRECER APOYO                      barrera de cuido; asistencia baja en la semana 3; escolaridad: algo universidad
           N001              0.470 seguimiento normal                      barrera de cuido; escolaridad: algo universidad; puntuación baja en el módulo 1
...
2 de 8 participantes con alerta. La alerta prioriza apoyo; no decide elegibilidad ni expulsión.
   ```

3. **Auditar la herramienta** (matriz de confusión, validación temporal y brechas por subgrupo):

   ```bash
   python main.py auditar
   ```

Para regenerar los datos sintéticos (opcional; produce exactamente el mismo CSV): `python datos/generar_datos.py`.

## Pruebas

```bash
pytest -v
```

Se espera **18 passed** (unos 5 segundos). GitHub Actions las ejecuta en cada push y en cada pull request antes de integrar (pestaña **Actions**). Qué comprueban:

| Archivo | Comprueba |
|---|---|
| `tests/test_datos.py` | que ninguna columna del futuro ni sensible sea predictor; que el generador sea reproducible y coincida con el CSV; que `validar_datos()` rechace rangos inválidos, vacíos, valores no binarios y columnas faltantes |
| `tests/test_modelo.py` | que el modelo elegido supere **ambas** líneas base con precisión ≥ 0.50; que el resultado sea estable entre pliegues (desv. < 0.08); que las métricas estén en [0, 1]; que la preparación viva dentro del Pipeline (sin fuga) |
| `tests/test_alerta.py` | el formato de la alerta; el rechazo de entradas inválidas; que más barreras y menos asistencia den más riesgo; que los factores mostrados realmente suban el riesgo frente al participante promedio |
| `tests/test_auditoria.py` | que la matriz de confusión cuadre con las métricas; que la tabla de subgrupos marque brechas con el umbral de la Skill; que la validación temporal no use la cohorte de prueba para entrenar |

## Limitaciones

- **No debe usarse para decidir sobre personas**: ni elegibilidad, ni permanencia, ni expulsión. Solo para priorizar a quién ofrecer apoyo, y siempre con la revisión de un coordinador.
- **Datos sintéticos.** Los números muestran que el método funciona, no cuánto acertaría con participantes reales. Antes de usarla en un programa hay que reentrenarla y auditarla con registros reales anonimizados, dentro del proveedor.
- **Detecta menos a quienes tienen 40 años o más** (0.541 contra 0.625 global). No se corrigió usando la edad como predictor, porque es una variable sensible, ni bajando el umbral, porque la precisión quedaría bajo 0.50. Mitigación: para participantes de 40 años o más, el coordinador no debe tomar "seguimiento normal" como señal de que no hay riesgo, y `python main.py auditar` muestra la brecha en cada reentrenamiento.
- **El nombre del modelo está fijo** en `src/alerta.py` y en `python main.py auditar` ("Regresión logística (balanced)"). Hoy coincide con el que elige `evaluar`; si al reentrenar con otros datos se eligiera otro, habría que cambiarlo en esos dos lugares (comentario 4 de la revisión del PR #2).
- **No es causal**: que un factor pese no prueba que el apoyo correspondiente funcione.
- **Qué cambiaría con el tiempo**: cambios de fondos o de política federal (la población atendida), nuevas áreas de adiestramiento o un cambio en cómo se registra la asistencia. Se notaría en que la exhaustividad medida con cohortes ya terminadas cae por debajo de la regla de asistencia (0.514).
- **Cuándo revisarla**: al cerrar cada cohorte (comparar alertas contra resultados reales con `python main.py auditar`) y siempre que cambie la población, el currículo o la forma de registrar asistencia.

## Estructura del repositorio

```
.
├── README.md
├── requirements.txt
├── pytest.ini
├── main.py                       # línea de comandos: evaluar / alertar / auditar
├── datos/
│   ├── generar_datos.py          # generador sintético (semilla fija)
│   ├── participantes_sinteticos.csv
│   └── ejemplo_semana3.csv       # entrada de ejemplo para alertar
├── src/
│   ├── config.py                 # columnas permitidas, prohibidas (fuga) y sensibles
│   ├── datos.py                  # carga y validación
│   ├── modelos.py                # líneas base y modelos (Pipeline)
│   ├── validacion.py             # CV y criterio de elección
│   ├── alerta.py                 # alerta con los 3 factores principales
│   └── auditoria.py              # matriz de confusión, validación temporal, subgrupos
├── tests/                        # pruebas pytest
├── auditorias/                   # informes de la Skill antes y después de corregir
├── revisiones/                   # revisión de cada pull request y respuestas
├── .claude/skills/auditoria-modelos/   # Skill de auditoría (Tarea 4.1)
└── .github/workflows/pruebas.yml # pytest en cada push y pull request
```

## Cómo se trabajó

El desarrollo se organizó en tres ramas por funcionalidad: `funcionalidad/pruebas`, `correccion/auditoria-subgrupos` y `funcionalidad/readme`. Cada una se revisó antes de integrarla a `main`, y cada integración es un *merge commit* que nombra su revisión.

- La revisión la hizo la Skill `auditoria-modelos`, con comentarios por archivo y línea, cambios pedidos, respuestas y decisión: `revisiones/PR*_revision_skill.md`. Los commits de corrección citan el número del comentario que atienden (por ejemplo, `fix(revision PR #1, hallazgos 1 y 5)`).
- La descripción de cada rama, con la plantilla de pull request del curso, está en `revisiones/PR*_descripcion_plantilla.md`.
- GitHub Actions ejecutó las pruebas en cada rama **antes** de integrarla (pestaña **Actions**: runs #1 a #3 en verde) y sigue este README paso a paso en una máquina limpia (job `instalacion-segun-readme`).

**Prueba con una persona que no conoce el proyecto:** *(pendiente: completar después de que alguien siga solo este README, anotando qué le costó)*.

## Autor

Carlo E. Alicea Medina · MAI 540: Machine Learning, Atlantis University · Profesor Kevin A. García Gallardo · 25 de octubre de 2026
