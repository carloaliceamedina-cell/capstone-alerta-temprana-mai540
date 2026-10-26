# Pull request: README completo y prueba de instalación en una máquina limpia

## Qué cambia

`README.md` completo según la plantilla: problema, datos y permiso de uso, cómo funciona (con diagrama), resultados (media ± desviación frente a dos líneas base, validación temporal y errores por categoría), instalación, cómo ejecutar con la salida esperada, pruebas, limitaciones y estructura. Agrega el job `instalacion-segun-readme` de GitHub Actions, que sigue el README paso a paso en una máquina limpia.

## Por qué

Una persona que no conoce el proyecto debe poder instalarlo, ejecutarlo y entender sus límites sin preguntar nada.

## Cómo se probó

- [x] `pytest -v` pasa: **18 passed**
- [x] Cloné el repositorio en una carpeta limpia y seguí el README: `evaluar`, `alertar` y `auditar` dan exactamente la salida documentada
- [x] El job `instalacion-segun-readme` repite esos pasos en GitHub Actions (venv nuevo, `pip install -r requirements.txt`)

## Lista de revisión

- [x] El cambio es pequeño y tiene un solo propósito (documentación)
- [x] El README está al día
- [x] No hay datos personales, claves ni información confidencial
- [x] Las pruebas nuevas cubren el cambio (el job de CI ejecuta los comandos del README)
- [x] Los mensajes de commit explican qué hizo cada uno

---

## Revisión (la completa quien revisa)

**Revisor:** Skill `auditoria-modelos` (sección Limitaciones contra los informes de auditoría) y lista de la guía.

**Qué revisó:** que cada número del README coincida con la salida de los comandos y con `auditorias/v2_despues/`, y que las limitaciones incluyan los hallazgos abiertos.

**Hallazgos y comentarios:**
1. `README.md`, sección Resultados: las cifras (0.625 ± 0.041; 0.514 ± 0.060; 0.639 temporal; 0.541 en 40+) coinciden con `salida_main_evaluar_v2.txt` y `salida_main_auditar_v2.txt` ✔
2. `README.md`, sección Limitaciones: incluye la brecha de 40+ con su mitigación y el nombre fijo del modelo (comentario 4 del PR de auditoría) ✔
3. `README.md`, sección Cómo se trabajó: la prueba con una persona externa queda marcada como **pendiente**, sin inventar el resultado ✔

**Decisión:** aprobado.
