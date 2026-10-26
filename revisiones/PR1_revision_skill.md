# Revisión del pull request `funcionalidad/pruebas` → `main`

**Revisor:** Skill `auditoria-modelos` (Tarea 4.1), aplicada con Claude Code sobre el diff de la rama (`git diff main...funcionalidad/pruebas`) · 25 de octubre de 2026

**Qué revisó:** los 4 archivos del diff (`tests/test_datos.py`, `tests/test_modelo.py`, `tests/test_alerta.py`, `.github/workflows/pruebas.yml`), la lista de la guía (las pruebas pasan, README al día, sin datos personales, cambio pequeño y de un solo propósito) y el código que las pruebas ejercitan (`src/alerta.py`).

**Lista de la guía:** las pruebas pasan (`pytest -v`: 14 passed) ✔ · sin datos personales ni claves (datos sintéticos) ✔ · un solo propósito (pruebas y CI) ✔ · el README todavía no documenta las pruebas (pendiente; va en la rama `funcionalidad/readme`).

## Hallazgos y comentarios (archivo y línea)

1. **[Cambio pedido] `tests/test_alerta.py`, l. 27.** La prueba solo cuenta cuántos factores hay (≤ 3); no comprueba que suban el riesgo. Al ejecutar `python main.py alertar datos/ejemplo_semana3.csv`, el participante N001, que estaba empleado al ingresar, recibe **"empleo al ingresar"** como factor de riesgo. La causa está en `src/alerta.py`, l. 48: `contrib = Z * clf.coef_[0]` no resta el participante promedio. Además, `empleado_al_ingreso` y `meses_desempleo` están casi duplicadas (quien estaba empleado tiene 0 meses sin empleo), así que el coeficiente de empleo sale positivo (+0.122) para compensar el de los meses. Se pide: (a) centrar la contribución en el promedio de entrenamiento, (b) agrupar las dos columnas en un solo factor y (c) agregar una prueba: un participante empleado con 0 meses sin empleo no debe recibir ese factor.
2. **[Cambio pedido] `tests/test_datos.py`, l. 11-12.** `sys.path.insert(...)` + `# noqa: E402` duplica lo que ya hace `tests/conftest.py`. Se pide exponer `generar` desde `conftest.py`, para que la ruta se prepare en un solo lugar.
3. **[Pregunta] `tests/test_modelo.py`, l. 30.** ¿De dónde sale el límite de 0.08 para la desviación de la exhaustividad? Sin justificación parece arbitrario.
4. **[Pregunta] `.github/workflows/pruebas.yml`, l. 14.** CI usa Python 3.11 y `requirements.txt` solo fija mínimos (`>=`). ¿Conviene fijar versiones exactas?
5. **[Cambio pedido] `src/alerta.py`, l. 34 (fuera del diff, pero lo ejercitan las pruebas).** `base, valor = col.rsplit(...)` nunca se usa: es código muerto.

**Decisión:** cambios solicitados (1, 2 y 5); responder 3 y 4.

## Respuestas del autor y cómo se resolvió cada comentario

| # | Comentario | Respuesta | Commit |
|---|---|---|---|
| 1 | Factores que no suben el riesgo ("empleo al ingresar") | **Hecho.** `src/alerta.py` ahora guarda el participante promedio de entrenamiento (`modelo.referencia_`, l. 31) y calcula `coeficiente x (valor - promedio)` (l. 45). Empleo y meses sin empleo forman un solo factor, "situación de empleo al ingresar" (l. 13), y las categorías se suman por variable. Prueba nueva `test_factores_suben_el_riesgo_frente_al_promedio`: **falla con el código anterior** (`AssertionError: 'empleo al ingresar' ...`) y pasa con el nuevo. En el ejemplo, N001 ya no recibe el factor de empleo. | `fix(revision PR #1, hallazgos 1 y 5)` |
| 2 | `sys.path` duplicado en `tests/test_datos.py` | **Hecho.** `tests/conftest.py` prepara las dos rutas (raíz y `datos/`) en un solo lugar, y `test_datos.py` ya no toca `sys.path`. | `refactor(revision PR #1, hallazgo 2)` |
| 3 | ¿Por qué 0.08? | **Respondido en el código.** La desviación observada es 0.041. El límite es aproximadamente el doble, y queda por debajo de la ventaja sobre la regla de asistencia (0.111). Si se superara, esa ventaja ya no se distinguiría del ruido. Está en el docstring de la prueba. | `docs(revision PR #1, pregunta 3)` |
| 4 | ¿Fijar versiones exactas? | **No lo haré en este PR.** Los mínimos (`>=`) permiten instalar con el Python que tenga quien siga el README (3.10 a 3.13); fijar versiones exactas obligaría a una versión concreta de Python. Las pruebas no comparan cifras exactas: comprueban relaciones (supera la línea base, desviación < 0.08) que se mantienen entre versiones. Se verifica en CI con 3.11 y localmente con 3.13 (15 passed en ambos). | — |
| 5 | Código muerto en `src/alerta.py`, l. 34 | **Hecho.** La función `_nombre_factor` se reemplazó completa por la tabla `FACTORES`; la línea ya no existe. | `fix(revision PR #1, hallazgos 1 y 5)` |

**Nueva ejecución de `pytest -v` después de los cambios:** 15 passed (antes 14; la nueva es la prueba del hallazgo 1).

**Decisión final del revisor (Skill `auditoria-modelos`, segunda pasada sobre el diff):** **aprobado**. Los tres cambios pedidos están resueltos con evidencia y las dos preguntas tienen respuesta razonada.
