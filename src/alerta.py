"""Alerta temprana: entrena el modelo elegido y explica cada alerta con los tres factores que más pesan."""
import numpy as np
import pandas as pd

from src.config import PREDICTORES
from src.datos import separar_X_y, validar_datos
from src.modelos import construir_modelos

NOMBRES_LEGIBLES = {
    "meses_desempleo": "meses sin empleo antes de entrar",
    "asistencia_sem1": "asistencia baja en la semana 1",
    "asistencia_sem2": "asistencia baja en la semana 2",
    "asistencia_sem3": "asistencia baja en la semana 3",
    "puntuacion_modulo1": "puntuación baja en el módulo 1",
    "empleado_al_ingreso": "empleo al ingresar",
    "barrera_transporte": "barrera de transporte",
    "barrera_cuido": "barrera de cuido",
    "ingreso_bajo": "ingreso bajo",
}
# En estas variables el riesgo SUBE cuando el valor BAJA: se nombran como "baja"
INVERSAS = {"asistencia_sem1", "asistencia_sem2", "asistencia_sem3", "puntuacion_modulo1"}


def entrenar(df, nombre_modelo="Regresión logística (balanced)"):
    """Entrena el modelo final con todos los datos históricos (después de evaluarlo con CV)."""
    validar_datos(df)
    X, y = separar_X_y(df)
    return construir_modelos()[nombre_modelo].fit(X, y)


def _nombre_factor(col_transformada):
    grupo, col = col_transformada.split("__", 1)
    if grupo == "cat":
        base, valor = col.rsplit("_", 1) if col.count("_") else (col, "")
        for c in ("area_adiestramiento", "escolaridad", "programa"):
            if col.startswith(c + "_"):
                return f"{c.replace('_', ' ')}: {col[len(c) + 1:].replace('_', ' ')}"
        return col
    return NOMBRES_LEGIBLES.get(col, col)


def factores(modelo, X, n=3):
    """Para un Pipeline de regresión logística: contribución de cada variable al logit
    (coeficiente x valor estandarizado). Devuelve, por fila, los n factores que más SUBEN el riesgo."""
    prep, clf = modelo.named_steps["prep"], modelo.named_steps["modelo"]
    Z = prep.transform(X)
    Z = Z.toarray() if hasattr(Z, "toarray") else np.asarray(Z)
    contrib = Z * clf.coef_[0]
    nombres = prep.get_feature_names_out()
    salida = []
    for fila in contrib:
        orden = np.argsort(fila)[::-1]
        salida.append([_nombre_factor(nombres[j]) for j in orden[:n] if fila[j] > 0])
    return salida


def generar_alertas(modelo, nuevos, umbral=0.5):
    """Recibe participantes en la semana 3 y devuelve probabilidad, alerta y factores principales."""
    validar_datos(nuevos, con_objetivo=False)
    X = nuevos[PREDICTORES]
    prob = modelo.predict_proba(X)[:, 1]
    resultado = pd.DataFrame({
        "id_participante": nuevos.get("id_participante", pd.Series(range(len(nuevos)))).to_numpy(),
        "prob_no_completar": prob.round(3),
        "alerta": np.where(prob >= umbral, "OFRECER APOYO", "seguimiento normal"),
    })
    resultado["factores_principales"] = ["; ".join(f) for f in factores(modelo, X)]
    return resultado.sort_values("prob_no_completar", ascending=False).reset_index(drop=True)
