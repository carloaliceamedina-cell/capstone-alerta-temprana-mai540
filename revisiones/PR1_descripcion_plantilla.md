# Pull request: pruebas automáticas con pytest y ejecución en GitHub Actions

## Qué cambia

Agrega 12 pruebas (15 casos con la parametrización) en `tests/` y un flujo de GitHub Actions que ejecuta `pytest -v` en cada push y en cada pull request, antes de integrar a `main`. Incluye las correcciones que pidió la revisión: `src/alerta.py` ahora explica cada alerta frente al participante promedio.

## Por qué

La herramienta no tenía pruebas. Estas comprueban lo que, si se rompe, importa: que ninguna columna del futuro ni sensible entre al modelo (fuga), que el modelo elegido supere las dos líneas base, que el resultado sea estable, que una entrada inválida se rechace y que los factores de la alerta de verdad suban el riesgo.

## Cómo se probó

- [x] `pytest -v` pasa: **15 passed**
- [x] Ejecuté la herramienta y el resultado es el esperado (`python main.py evaluar`, `python main.py alertar datos/ejemplo_semana3.csv`)
- [x] Pegué aquí la salida

```
test_alerta.py::test_alertas_con_formato_valido PASSED             [  6%]
test_alerta.py::test_alerta_rechaza_entrada_invalida PASSED        [ 13%]
test_alerta.py::test_mas_riesgo_con_barreras_y_menos_asistencia PASSED [ 20%]
test_alerta.py::test_factores_suben_el_riesgo_frente_al_promedio PASSED [ 26%]
test_datos.py::test_columnas_del_futuro_y_sensibles_no_son_predictores PASSED [ 33%]
test_datos.py::test_generador_es_reproducible_y_coincide_con_el_csv PASSED [ 40%]
test_datos.py::test_validar_datos_acepta_los_datos_del_proyecto PASSED [ 46%]
test_datos.py::test_validar_datos_rechaza_entradas_invalidas[asistencia_sem1-1.5-fuera de] PASSED [ 53%]
test_datos.py::test_validar_datos_rechaza_entradas_invalidas[puntuacion_modulo1-None-vac\xedos] PASSED [ 60%]
test_datos.py::test_validar_datos_rechaza_entradas_invalidas[barrera_cuido-2-0 o 1] PASSED [ 66%]
test_datos.py::test_validar_datos_detecta_columna_faltante PASSED  [ 73%]
test_modelo.py::test_modelo_elegido_supera_las_dos_lineas_base PASSED [ 80%]
test_modelo.py::test_resultado_estable_entre_pliegues PASSED       [ 86%]
test_modelo.py::test_metricas_en_rango PASSED                      [ 93%]
test_modelo.py::test_preparacion_dentro_del_pipeline PASSED        [100%]
============================== 15 passed in 4.79s ==============================
```

## Lista de revisión

- [x] El cambio es pequeño y tiene un solo propósito (pruebas, CI y lo que pidió la revisión)
- [ ] El README está al día → se actualiza en el PR de `funcionalidad/readme`
- [x] No hay datos personales, claves ni información confidencial (datos sintéticos)
- [x] Las pruebas nuevas cubren el cambio
- [x] Los mensajes de commit explican qué hizo cada uno

---

## Revisión (la completa quien revisa)

**Revisor:** Skill `auditoria-modelos`, sobre el diff de la rama, **antes** de los cambios (commit `be277fb`). Documento completo: `revisiones/PR1_revision_skill.md`.

**Qué revisó:** los 4 archivos del diff, la lista de la guía y `src/alerta.py`, que las pruebas ejercitan.

**Hallazgos y comentarios:**
1. **[Cambio pedido] `tests/test_alerta.py`, l. 27:** la prueba no comprueba que los factores suban el riesgo. N001, que estaba empleado, recibe "empleo al ingresar" como factor de riesgo. La causa está en `src/alerta.py`, l. 48: la contribución no resta el participante promedio, y empleo y meses sin empleo están casi duplicados (coeficiente +0.122).
2. **[Cambio pedido] `tests/test_datos.py`, l. 11-12:** `sys.path` duplicado con `conftest.py`.
3. **[Pregunta] `tests/test_modelo.py`, l. 30:** ¿por qué 0.08?
4. **[Pregunta] `.github/workflows/pruebas.yml`, l. 14:** ¿fijar versiones exactas?
5. **[Cambio pedido] `src/alerta.py`, l. 34:** código muerto.

**Cambios que se pidieron y cómo se resolvieron:**
1. **Hecho** (`fc0ab85`): contribución `coef x (valor - promedio)`, empleo y meses como un solo factor, y una prueba nueva que **falla con el código anterior** y pasa con el nuevo.
2. **Hecho** (`ff914c9`): las rutas se preparan solo en `conftest.py`.
3. **Respondido** (`16662ae`): la desviación observada es 0.041. El límite es aproximadamente el doble y queda por debajo de la ventaja sobre la línea base (0.111).
4. **No se hará:** los mínimos (`>=`) permiten instalar con Python 3.10 a 3.13. Las pruebas comprueban relaciones, no cifras exactas: 15 passed con 3.11 (CI) y con 3.13 (local).
5. **Hecho** (`fc0ab85`): la función completa se reemplazó.

**Decisión:** primera pasada: cambios solicitados → segunda pasada (`18181dc`): **aprobado**.
