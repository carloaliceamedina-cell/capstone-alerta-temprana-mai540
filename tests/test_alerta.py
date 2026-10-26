"""Pruebas de la alerta que recibe el coordinador del programa."""
from functools import lru_cache

import pandas as pd
import pytest

from src.alerta import entrenar, generar_alertas
from src.config import RAIZ
from src.datos import cargar_datos


@lru_cache(maxsize=1)
def modelo():
    return entrenar(cargar_datos())


def ejemplo():
    return pd.read_csv(RAIZ / "datos" / "ejemplo_semana3.csv")


def test_alertas_con_formato_valido():
    res = generar_alertas(modelo(), ejemplo())
    assert len(res) == len(ejemplo())
    assert res["prob_no_completar"].between(0, 1).all()
    assert set(res["alerta"]) <= {"OFRECER APOYO", "seguimiento normal"}
    assert (res["alerta"] == "OFRECER APOYO").eq(res["prob_no_completar"] >= 0.5).all()
    assert all(len(f.split("; ")) <= 3 for f in res["factores_principales"])


def test_alerta_rechaza_entrada_invalida():
    malo = ejemplo()
    malo.loc[0, "asistencia_sem2"] = 1.7
    with pytest.raises(ValueError):
        generar_alertas(modelo(), malo)


def test_mas_riesgo_con_barreras_y_menos_asistencia():
    """Un caso con barreras y asistencia baja recibe más probabilidad que uno sin barreras y asistencia alta."""
    base = ejemplo().iloc[[0, 0]].reset_index(drop=True)
    base.loc[0, ["barrera_transporte", "barrera_cuido", "asistencia_sem1", "asistencia_sem2", "asistencia_sem3"]] = [1, 1, 0.5, 0.45, 0.4]
    base.loc[1, ["barrera_transporte", "barrera_cuido", "asistencia_sem1", "asistencia_sem2", "asistencia_sem3"]] = [0, 0, 1.0, 1.0, 0.95]
    base["id_participante"] = ["riesgo", "sin_riesgo"]
    res = generar_alertas(modelo(), base).set_index("id_participante")
    assert res.loc["riesgo", "prob_no_completar"] > res.loc["sin_riesgo", "prob_no_completar"]


def test_factores_suben_el_riesgo_frente_al_promedio():
    """Revisión del PR #1: un factor solo se muestra si SUBE el riesgo frente al participante promedio.
    Quien estaba empleado al ingresar (0 meses sin empleo) no debe recibir 'situación de empleo' como factor."""
    caso = ejemplo().iloc[[0]].reset_index(drop=True)
    caso.loc[0, ["empleado_al_ingreso", "meses_desempleo"]] = [1, 0]
    res = generar_alertas(modelo(), caso)
    assert "situación de empleo" not in res.loc[0, "factores_principales"]
    assert "empleo al ingresar" not in res.loc[0, "factores_principales"]
