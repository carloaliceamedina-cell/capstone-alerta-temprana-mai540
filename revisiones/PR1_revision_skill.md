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
