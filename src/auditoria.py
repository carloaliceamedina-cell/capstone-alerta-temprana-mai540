"""Auditoría integrada en la herramienta (corrige los hallazgos V1.2 y V4.1 de la Skill auditoria-modelos).

- Matriz de confusión con predicciones fuera de pliegue (cross_val_predict): ninguna fila se predice
  con un modelo que la vio al entrenar.
- Exhaustividad por subgrupo (género, grupo de edad, región y cohorte) con el umbral de la Skill:
  brecha si un subgrupo con >= 30 casos positivos queda > 0.05 por debajo del global o su cociente
  frente al mejor subgrupo es < 0.80.
- Validación temporal: entrenar con las cohortes anteriores y probar con la más reciente, como
  pedía la propuesta (Módulo 5).
Las variables sensibles se usan aquí solo para medir; nunca entran al modelo.
"""
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from sklearn.model_selection import cross_val_predict

from src.config import OBJETIVO, PREDICTORES
from src.datos import separar_X_y
from src.modelos import construir_modelos
from src.validacion import particion

UMBRAL_BRECHA = 0.05
UMBRAL_COCIENTE = 0.80
MIN_POSITIVOS = 30


def predicciones_fuera_de_pliegue(df, nombre_modelo):
    X, y = separar_X_y(df)
    return cross_val_predict(construir_modelos()[nombre_modelo], X, y, cv=particion())


def matriz_confusion(y, pred):
    vn, fp, fn, vp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {"VN": int(vn), "FP": int(fp), "FN": int(fn), "VP": int(vp),
            "exhaustividad": vp / (vp + fn), "precision": vp / (vp + fp)}


def con_grupo_edad(df):
    grupo = pd.cut(df["edad"], [0, 24, 39, 120], labels=["16-24", "25-39", "40+"]).astype(str)
    return df.assign(grupo_edad=grupo)


def exhaustividad_por_subgrupo(df, pred, columnas=("genero", "grupo_edad", "region", "cohorte")):
    """Tabla con n, positivos, exhaustividad y si hay brecha, por cada subgrupo."""
    d = con_grupo_edad(df).assign(pred=pred)
    global_ = recall_score(d[OBJETIVO], d["pred"])
    filas = []
    for col in columnas:
        grupos = list(d.groupby(col, observed=True))
        recs = {g: recall_score(s[OBJETIVO], s["pred"]) for g, s in grupos}
        mejor = max(recs.values())
        for g, s in grupos:
            pos = int(s[OBJETIVO].sum())
            r = recs[g]
            brecha = pos >= MIN_POSITIVOS and (global_ - r > UMBRAL_BRECHA or r / mejor < UMBRAL_COCIENTE)
            filas.append({"variable": col, "subgrupo": str(g), "n": len(s), "positivos": pos,
                          "exhaustividad": round(r, 3), "diferencia_vs_global": round(r - global_, 3),
                          "cociente_vs_mejor": round(r / mejor, 2), "brecha": bool(brecha)})
    return pd.DataFrame(filas), global_


def validacion_temporal(df, nombre_modelo):
    """Entrena con todas las cohortes menos la última y evalúa en la última (la más reciente)."""
    cohortes = sorted(df["cohorte"].unique())
    entren, prueba = df[df["cohorte"] < cohortes[-1]], df[df["cohorte"] == cohortes[-1]]
    modelo = construir_modelos()[nombre_modelo].fit(entren[PREDICTORES], entren[OBJETIVO])
    pred = modelo.predict(prueba[PREDICTORES])
    return {"entrenamiento": f"{cohortes[0]} a {cohortes[-2]} ({len(entren)} casos)",
            "prueba": f"{cohortes[-1]} ({len(prueba)} casos)",
            "exhaustividad": recall_score(prueba[OBJETIVO], pred),
            "precision": precision_score(prueba[OBJETIVO], pred)}
