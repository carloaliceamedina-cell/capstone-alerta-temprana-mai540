"""Pruebas de la auditoría integrada (correcciones de los hallazgos V1.2, V4.1 y de la validación temporal)."""
from functools import lru_cache

from sklearn.metrics import precision_score, recall_score

from src.auditoria import (MIN_POSITIVOS, UMBRAL_BRECHA, UMBRAL_COCIENTE, exhaustividad_por_subgrupo,
                           matriz_confusion, predicciones_fuera_de_pliegue, validacion_temporal)
from src.datos import cargar_datos

MODELO = "Regresión logística (balanced)"


@lru_cache(maxsize=1)
def datos_y_pred():
    df = cargar_datos()
    return df, predicciones_fuera_de_pliegue(df, MODELO)


def test_matriz_de_confusion_cuadra_con_las_metricas():
    df, pred = datos_y_pred()
    m = matriz_confusion(df["no_completo"], pred)
    assert m["VN"] + m["FP"] + m["FN"] + m["VP"] == len(df)
    assert abs(m["exhaustividad"] - recall_score(df["no_completo"], pred)) < 1e-9
    assert abs(m["precision"] - precision_score(df["no_completo"], pred)) < 1e-9


def test_tabla_de_subgrupos_aplica_el_umbral_de_la_skill():
    df, pred = datos_y_pred()
    tabla, global_ = exhaustividad_por_subgrupo(df, pred)
    assert set(tabla["variable"]) == {"genero", "grupo_edad", "region", "cohorte"}
    for _, f in tabla.iterrows():
        esperado = f["positivos"] >= MIN_POSITIVOS and (
            global_ - f["exhaustividad"] > UMBRAL_BRECHA + 5e-4 or f["cociente_vs_mejor"] < UMBRAL_COCIENTE)
        if esperado:
            assert f["brecha"], f"{f['variable']}={f['subgrupo']} debió marcarse con brecha"


def test_validacion_temporal_no_entrena_con_la_cohorte_de_prueba():
    t = validacion_temporal(cargar_datos(), MODELO)
    assert t["prueba"].startswith("2025-2")
    assert "2025-2" not in t["entrenamiento"]
    assert 0 <= t["exhaustividad"] <= 1 and 0 <= t["precision"] <= 1
