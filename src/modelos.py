"""Modelos candidatos y líneas base. Toda la preparación vive dentro de un Pipeline."""
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import PREDICTORES_BIN, PREDICTORES_CAT, PREDICTORES_NUM, SEMILLA


class ReglaAsistencia(BaseEstimator, ClassifierMixin):
    """Línea base sencilla que ya usan los coordinadores: alerta si la asistencia
    promedio de las semanas 1-3 es menor que el umbral (75 %, fijado de antemano, no ajustado)."""

    def __init__(self, umbral=0.75):
        self.umbral = umbral

    def fit(self, X, y):
        self.classes_ = np.array([0, 1])
        return self

    def predict(self, X):
        promedio = X[["asistencia_sem1", "asistencia_sem2", "asistencia_sem3"]].mean(axis=1)
        return (promedio < self.umbral).astype(int).to_numpy()


def _preparacion(escalar):
    num = StandardScaler() if escalar else "passthrough"
    return ColumnTransformer([
        ("num", num, PREDICTORES_NUM),
        ("bin", "passthrough", PREDICTORES_BIN),
        ("cat", OneHotEncoder(handle_unknown="ignore"), PREDICTORES_CAT),
    ])


def construir_modelos():
    """Devuelve los modelos comparados, todos bajo el mismo protocolo de validación."""
    return {
        "Línea base: azar estratificado": DummyClassifier(strategy="stratified", random_state=SEMILLA),
        "Línea base: regla de asistencia < 75 %": ReglaAsistencia(umbral=0.75),
        "Regresión logística (balanced)": Pipeline([
            ("prep", _preparacion(escalar=True)),
            ("modelo", LogisticRegression(class_weight="balanced", max_iter=2000)),
        ]),
        "Random Forest (balanced)": Pipeline([
            ("prep", _preparacion(escalar=False)),
            ("modelo", RandomForestClassifier(n_estimators=300, min_samples_leaf=5,
                                              class_weight="balanced", random_state=SEMILLA)),
        ]),
    }
