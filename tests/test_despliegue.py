"""Pruebas de la demostración (sin necesitar Gradio instalado) y de la simulación de degradación."""
from functools import lru_cache

from app_gradio import evaluar
from src.datos import cargar_datos
from src.degradacion import simular


def test_demo_devuelve_alerta_legible():
    texto = evaluar(50, 45, 40, 55, 12, False, True, True, True, "jovenes", "Construccion", "sin_diploma")
    assert "Probabilidad de no completar" in texto
    assert "OFRECER APOYO" in texto


def test_demo_caso_de_bajo_riesgo_no_genera_alerta():
    texto = evaluar(98, 97, 96, 90, 0, True, False, False, False, "adultos", "Salud", "grado_universitario")
    assert "seguimiento normal" in texto


@lru_cache(maxsize=1)
def tabla_degradacion():
    return simular(cargar_datos()).set_index("escenario")


def test_degradacion_asistencia_inflada_cae_bajo_la_linea_base():
    """Si la asistencia se registra de otra forma, la exhaustividad cae por debajo de la regla de asistencia (0.514)."""
    t = tabla_degradacion()
    sin_cambios = t.iloc[0]["exhaustividad"]
    inflada = t.iloc[1]["exhaustividad"]
    assert inflada < sin_cambios - 0.10
    assert inflada < 0.514
