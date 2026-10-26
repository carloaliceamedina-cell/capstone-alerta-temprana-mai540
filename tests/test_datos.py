"""Pruebas de los datos y de las reglas de columnas (fuga y variables sensibles)."""
import pandas as pd
import pytest
from generar_datos import generar  # la ruta la prepara tests/conftest.py

from src.config import COLUMNAS_FUTURO, COLUMNAS_SENSIBLES, OBJETIVO, PREDICTORES
from src.datos import cargar_datos, separar_X_y, validar_datos


def test_columnas_del_futuro_y_sensibles_no_son_predictores():
    """Fuga: nada que se conozca después de la semana 3, y ninguna variable sensible, entra al modelo."""
    assert not set(COLUMNAS_FUTURO) & set(PREDICTORES)
    assert not set(COLUMNAS_SENSIBLES) & set(PREDICTORES)
    assert OBJETIVO not in PREDICTORES
    X, _ = separar_X_y(cargar_datos())
    assert list(X.columns) == PREDICTORES


def test_generador_es_reproducible_y_coincide_con_el_csv():
    """El CSV del repositorio es exactamente lo que produce el generador con su semilla."""
    a, b = generar(), generar()
    pd.testing.assert_frame_equal(a, b)
    pd.testing.assert_frame_equal(a, cargar_datos(), check_dtype=False)


def test_validar_datos_acepta_los_datos_del_proyecto():
    assert validar_datos(cargar_datos()) is True


@pytest.mark.parametrize("columna, valor, mensaje", [
    ("asistencia_sem1", 1.5, "fuera de"),
    ("puntuacion_modulo1", None, "vacíos"),
    ("barrera_cuido", 2, "0 o 1"),
])
def test_validar_datos_rechaza_entradas_invalidas(columna, valor, mensaje):
    df = cargar_datos().head(20).copy()
    df[columna] = df[columna].astype(object)
    df.loc[df.index[0], columna] = valor
    with pytest.raises(ValueError, match=mensaje):
        validar_datos(df)


def test_validar_datos_detecta_columna_faltante():
    df = cargar_datos().drop(columns=["asistencia_sem3"])
    with pytest.raises(ValueError, match="Faltan columnas"):
        validar_datos(df)
