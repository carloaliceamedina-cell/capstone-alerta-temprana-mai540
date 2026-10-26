"""Pruebas del modelo: supera la línea base, es estable y la preparación no filtra información."""
from functools import lru_cache

from sklearn.pipeline import Pipeline

from src.datos import cargar_datos, separar_X_y
from src.modelos import construir_modelos
from src.validacion import PRECISION_MINIMA, elegir_modelo, evaluar_cv


@lru_cache(maxsize=1)
def tabla():
    X, y = separar_X_y(cargar_datos())
    return evaluar_cv(construir_modelos(), X, y).set_index("modelo")


def test_modelo_elegido_supera_las_dos_lineas_base():
    t = tabla()
    elegido = elegir_modelo(t.reset_index())
    rec = t["exhaustividad_media"]
    assert rec[elegido] > rec["Línea base: regla de asistencia < 75 %"]
    assert rec[elegido] > rec["Línea base: azar estratificado"]
    assert t.loc[elegido, "precision_media"] >= PRECISION_MINIMA


def test_resultado_estable_entre_pliegues():
    """La desviación de la exhaustividad entre pliegues es pequeña (resultado estable).
    Por qué 0.08 (revisión del PR #1, pregunta 3): la desviación observada es 0.041. El límite es
    aproximadamente el doble, y queda por debajo de la ventaja sobre la regla de asistencia (0.111).
    Si la desviación lo superara, esa ventaja ya no se distinguiría del ruido entre pliegues."""
    t = tabla()
    elegido = elegir_modelo(t.reset_index())
    assert t.loc[elegido, "exhaustividad_desv"] < 0.08


def test_metricas_en_rango():
    t = tabla()
    medias = t[[c for c in t.columns if c.endswith("_media")]]
    assert ((medias >= 0) & (medias <= 1)).all().all()


def test_preparacion_dentro_del_pipeline():
    """Escalado y codificación viven dentro del Pipeline: se ajustan en cada pliegue, sin fuga."""
    for nombre, modelo in construir_modelos().items():
        if not nombre.startswith("Línea base"):
            assert isinstance(modelo, Pipeline)
            assert list(modelo.named_steps) == ["prep", "modelo"]
