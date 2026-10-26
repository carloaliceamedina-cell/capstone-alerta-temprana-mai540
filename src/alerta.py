"""Alerta temprana: entrena el modelo elegido y explica cada alerta con los tres factores que más pesan."""
import numpy as np
import pandas as pd

from src.config import PREDICTORES, PREDICTORES_CAT
from src.datos import separar_X_y, validar_datos
from src.modelos import construir_modelos

# Cada factor que ve el coordinador agrupa una o más columnas transformadas.
# empleado_al_ingreso y meses_desempleo van juntas: están casi duplicadas (quien estaba empleado
# tiene 0 meses sin empleo) y por separado sus coeficientes se compensan y engañan.
FACTORES = {
    "situación de empleo al ingresar": ["num__meses_desempleo", "bin__empleado_al_ingreso"],
    "asistencia baja en la semana 1": ["num__asistencia_sem1"],
    "asistencia baja en la semana 2": ["num__asistencia_sem2"],
    "asistencia baja en la semana 3": ["num__asistencia_sem3"],
    "puntuación baja en el módulo 1": ["num__puntuacion_modulo1"],
    "barrera de transporte": ["bin__barrera_transporte"],
    "barrera de cuido": ["bin__barrera_cuido"],
    "ingreso bajo": ["bin__ingreso_bajo"],
}
ETIQUETAS_CAT = {"programa": "programa", "area_adiestramiento": "área de adiestramiento", "escolaridad": "escolaridad"}


def entrenar(df, nombre_modelo="Regresión logística (balanced)"):
    """Entrena el modelo final con todos los datos históricos (después de evaluarlo con CV) y guarda
    el participante promedio de entrenamiento, que es la referencia para explicar cada alerta."""
    validar_datos(df)
    X, y = separar_X_y(df)
    modelo = construir_modelos()[nombre_modelo].fit(X, y)
    modelo.referencia_ = _transformar(modelo, X).mean(axis=0)
    return modelo


def _transformar(modelo, X):
    Z = modelo.named_steps["prep"].transform(X)
    return Z.toarray() if hasattr(Z, "toarray") else np.asarray(Z)


def factores(modelo, X, n=3):
    """Contribución de cada factor al logit FRENTE AL PARTICIPANTE PROMEDIO de entrenamiento:
    coeficiente x (valor transformado - promedio). Devuelve, por fila, los n factores que más SUBEN
    el riesgo (solo contribuciones positivas)."""
    nombres = list(modelo.named_steps["prep"].get_feature_names_out())
    contrib = (_transformar(modelo, X) - modelo.referencia_) * modelo.named_steps["modelo"].coef_[0]
    grupos = {f: [nombres.index(c) for c in cols] for f, cols in FACTORES.items()}
    for cat in PREDICTORES_CAT:
        grupos[cat] = [j for j, c in enumerate(nombres) if c.startswith(f"cat__{cat}_")]
    salida = []
    for i, fila in enumerate(contrib):
        totales = {f: fila[idx].sum() for f, idx in grupos.items()}
        orden = sorted((f for f in totales if totales[f] > 0), key=totales.get, reverse=True)[:n]
        salida.append([f"{ETIQUETAS_CAT[f]}: {str(X.iloc[i][f]).replace('_', ' ')}" if f in ETIQUETAS_CAT else f
                       for f in orden])
    return salida


def generar_alertas(modelo, nuevos, umbral=0.5):
    """Recibe participantes en la semana 3 y devuelve probabilidad, alerta y factores principales."""
    validar_datos(nuevos, con_objetivo=False)
    X = nuevos[PREDICTORES].reset_index(drop=True)
    prob = modelo.predict_proba(X)[:, 1]
    resultado = pd.DataFrame({
        "id_participante": nuevos.get("id_participante", pd.Series(range(len(nuevos)))).to_numpy(),
        "prob_no_completar": prob.round(3),
        "alerta": np.where(prob >= umbral, "OFRECER APOYO", "seguimiento normal"),
    })
    resultado["factores_principales"] = ["; ".join(f) for f in factores(modelo, X)]
    return resultado.sort_values("prob_no_completar", ascending=False).reset_index(drop=True)
