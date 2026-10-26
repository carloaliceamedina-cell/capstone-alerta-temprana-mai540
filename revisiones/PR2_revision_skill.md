# Revisión del pull request `correccion/auditoria-subgrupos` → `main`

**Revisor:** Skill `auditoria-modelos`, aplicada con Claude Code sobre el diff de la rama y sobre el proyecto completo en esa rama · 25 de octubre de 2026

**Qué revisó:** `src/auditoria.py` (nuevo), `main.py` (comando `auditar`), `src/config.py` (texto del costo del error), `tests/test_auditoria.py` (nuevo), los informes en `auditorias/` y la lista de la guía.

**Lista de la guía:** `pytest -v` = 18 passed ✔ · sin datos personales (las variables sensibles son sintéticas y solo se usan para medir) ✔ · un solo propósito: corregir los hallazgos de la auditoría ✔ · README: falta documentar `auditar` y las limitaciones (pendiente; va en la rama `funcionalidad/readme`).

## Hallazgos y comentarios (archivo y línea)

1. **[Comprobado] `src/auditoria.py`, l. 64-65.** La validación temporal entrena solo con `cohorte < 2025-2` y predice 2025-2: no hay fuga temporal (V3.1).
2. **[Comprobado] `src/auditoria.py`, l. 28.** La matriz de confusión usa `cross_val_predict` con la misma `particion()` que la CV (V2.4), así que sus métricas cuadran con la tabla de `evaluar` (V1.2).
3. **[Pregunta] `src/auditoria.py`, l. 37-39.** Los cortes de edad (16-24, 25-39, 40+): ¿por qué esos? → *Respuesta del autor:* 16-24 es el programa de jóvenes de WIOA; el resto se divide en dos grupos con más de 100 positivos cada uno, para cumplir el mínimo de 30 de la Skill con margen.
4. **[Observación] `main.py`, l. 60.** `auditar` usa el nombre del modelo fijo ("Regresión logística (balanced)") en lugar de `elegir_modelo()`. Hoy coincide con el elegido; si cambian los datos, podría auditar un modelo distinto del desplegado. → *Respuesta del autor:* de acuerdo, pero `alerta.entrenar()` también fija ese nombre. Cambiarlo en los dos lugares es otro propósito; queda anotado en las Limitaciones del README.
5. **[Hallazgo abierto] V4.2.** La brecha de 40+ sigue (0.541). El registro `auditorias/REGISTRO_HALLAZGOS_Y_CORRECCIONES.md` explica por qué no se corrigió y qué mitigación queda. Se acepta como hallazgo explicado.

**Decisión:** **aprobado**. No hay cambios bloqueantes; los puntos 4 y 5 quedan documentados como limitaciones.
