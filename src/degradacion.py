"""Simulación de degradación: el modelo no cambia ni una línea, pero el mundo sí.

Se entrena con las cohortes 2022-1 a 2024-2 y se evalúa con las cohortes 2025 en tres escenarios:
  1. Sin cambios (referencia).
  2. Cambio en cómo se registra la asistencia: el programa pasa a modalidad híbrida y la asistencia
     virtual se registra con solo conectarse. La asistencia reportada sube 0.15 en promedio, pero el
     riesgo real no cambia. El modelo "ve" a participantes más comprometidos de lo que están.
  3. Cambio de población: un nuevo fondo amplía cupos en zonas rurales y los participantes con
     barrera de transporte pasan a ser mayoría. Se simula reemplazando la mitad de los casos sin
     barrera por casos con barrera tomados de las mismas cohortes (cambia la mezcla, no la regla).
La exhaustividad se mide contra el resultado real, que en la práctica se conoce al cerrar cada cohorte.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score

from src.config import OBJETIVO, PREDICTORES, SEMILLA
from src.modelos import construir_modelos

MODELO = "Regresión logística (balanced)"
ASISTENCIA = ["asistencia_sem1", "asistencia_sem2", "asistencia_sem3"]


def _medir(modelo, df):
    pred = modelo.predict(df[PREDICTORES])
    return recall_score(df[OBJETIVO], pred), precision_score(df[OBJETIVO], pred, zero_division=0)


def escenario_asistencia_inflada(df, aumento=0.15):
    d = df.copy()
    d[ASISTENCIA] = (d[ASISTENCIA] + aumento).clip(upper=1.0)
    return d


def escenario_mas_barreras(df, semilla=SEMILLA):
    rng = np.random.default_rng(semilla)
    con, sin = df[df["barrera_transporte"] == 1], df[df["barrera_transporte"] == 0]
    quedan = sin.sample(frac=0.5, random_state=semilla)
    extra = con.iloc[rng.integers(0, len(con), size=len(sin) - len(quedan))]
    return pd.concat([quedan, con, extra], ignore_index=True)


def simular(df):
    entren = df[df["cohorte"] < "2025-1"]
    futuro = df[df["cohorte"] >= "2025-1"]
    modelo = construir_modelos()[MODELO].fit(entren[PREDICTORES], entren[OBJETIVO])
    filas = []
    for nombre, datos in [
        ("1. Sin cambios (cohortes 2025)", futuro),
        ("2. Asistencia registrada de otra forma (+0.15)", escenario_asistencia_inflada(futuro)),
        ("3. Más participantes con barrera de transporte", escenario_mas_barreras(futuro)),
    ]:
        rec, prec = _medir(modelo, datos)
        filas.append({"escenario": nombre, "casos": len(datos), "tasa_no_completa": round(datos[OBJETIVO].mean(), 3),
                      "exhaustividad": round(rec, 3), "precision": round(prec, 3)})
    return pd.DataFrame(filas)
