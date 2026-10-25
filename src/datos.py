"""Carga y validación de los datos de participantes."""
import numpy as np
import pandas as pd

from src.config import COLUMNAS_FUTURO, OBJETIVO, PREDICTORES, PREDICTORES_BIN, PREDICTORES_NUM, RUTA_DATOS

RANGOS = {
    "asistencia_sem1": (0, 1), "asistencia_sem2": (0, 1), "asistencia_sem3": (0, 1),
    "puntuacion_modulo1": (0, 100), "meses_desempleo": (0, 600),
}


def cargar_datos(ruta=RUTA_DATOS):
    """Lee el CSV de participantes."""
    return pd.read_csv(ruta)


def validar_datos(df, con_objetivo=True):
    """Lanza ValueError con un mensaje claro si los datos no sirven para entrenar o predecir."""
    requeridas = PREDICTORES + ([OBJETIVO] if con_objetivo else [])
    faltan = [c for c in requeridas if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas obligatorias: {faltan}")

    nulos = df[requeridas].isna().sum()
    if nulos.any():
        raise ValueError(f"Hay valores vacíos: {nulos[nulos > 0].to_dict()}")

    for col in PREDICTORES_NUM:
        if not np.isfinite(df[col].astype(float)).all():
            raise ValueError(f"La columna {col} tiene valores infinitos")
        lo, hi = RANGOS[col]
        fuera = df[(df[col] < lo) | (df[col] > hi)]
        if len(fuera):
            raise ValueError(f"La columna {col} tiene {len(fuera)} valores fuera de [{lo}, {hi}]")

    for col in PREDICTORES_BIN + ([OBJETIVO] if con_objetivo else []):
        if not df[col].isin([0, 1]).all():
            raise ValueError(f"La columna {col} solo puede valer 0 o 1")
    return True


def separar_X_y(df):
    """Devuelve (X, y) usando SOLO los predictores permitidos."""
    assert not set(COLUMNAS_FUTURO) & set(PREDICTORES), "Una columna del futuro está entre los predictores"
    return df[PREDICTORES].copy(), df[OBJETIVO].copy()
