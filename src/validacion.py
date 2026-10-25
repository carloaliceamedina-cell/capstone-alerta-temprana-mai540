"""Validación cruzada (media ± desviación) y criterio explícito para elegir el modelo."""
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate

from src.config import SEMILLA

METRICAS = {
    "exhaustividad": "recall",           # de la clase 1 (no completa): la prioritaria
    "precision": "precision",
    "f1": "f1",
    "exactitud_balanceada": "balanced_accuracy",
}
PRECISION_MINIMA = 0.50   # criterio de éxito de la propuesta (Módulo 5)


def particion():
    """La MISMA partición para todos los modelos comparados."""
    return StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)


def evaluar_cv(modelos, X, y):
    """Devuelve una tabla con media y desviación estándar de cada métrica por modelo."""
    filas = []
    for nombre, modelo in modelos.items():
        res = cross_validate(modelo, X, y, cv=particion(), scoring=METRICAS, error_score="raise")
        fila = {"modelo": nombre}
        for m in METRICAS:
            fila[f"{m}_media"] = res[f"test_{m}"].mean()
            fila[f"{m}_desv"] = res[f"test_{m}"].std()
        filas.append(fila)
    return pd.DataFrame(filas)


def elegir_modelo(tabla):
    """Criterio: entre los modelos (no líneas base) con precisión media >= 0.50, el de mayor
    exhaustividad media. Si dos quedan a menos de una desviación estándar, gana el más
    interpretable (la regresión logística), porque cada alerta debe poder explicarse."""
    candidatos = tabla[~tabla["modelo"].str.startswith("Línea base")]
    candidatos = candidatos[candidatos["precision_media"] >= PRECISION_MINIMA]
    if candidatos.empty:
        raise ValueError("Ningún modelo alcanza la precisión mínima de 0.50")
    mejor = candidatos.sort_values("exhaustividad_media", ascending=False).iloc[0]
    logistica = candidatos[candidatos["modelo"].str.startswith("Regresión logística")]
    if not logistica.empty and mejor["modelo"] != logistica.iloc[0]["modelo"]:
        if mejor["exhaustividad_media"] - logistica.iloc[0]["exhaustividad_media"] < mejor["exhaustividad_desv"]:
            return logistica.iloc[0]["modelo"]
    return mejor["modelo"]
