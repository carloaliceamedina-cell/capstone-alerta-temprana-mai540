"""Verificación reproducida (Skill auditoria-modelos, V4.2): ¿la brecha del grupo 40+ es estable o es ruido?
Repite la CV estratificada de 5 pliegues con 5 semillas distintas. Solo lectura sobre el proyecto.
Uso (desde la raíz del repositorio): python auditorias/v2_despues/evidencia/verificacion_estabilidad_edad.py"""
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import recall_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.auditoria import con_grupo_edad  # noqa: E402
from src.datos import cargar_datos, separar_X_y  # noqa: E402
from src.modelos import construir_modelos  # noqa: E402

df = cargar_datos()
X, y = separar_X_y(df)
grupo = con_grupo_edad(df)["grupo_edad"]
res = {k: [] for k in ["global", "16-24", "25-39", "40+"]}
for semilla in range(5):
    cv = StratifiedKFold(5, shuffle=True, random_state=semilla)
    p = cross_val_predict(construir_modelos()["Regresión logística (balanced)"], X, y, cv=cv)
    res["global"].append(recall_score(y, p))
    for g in ["16-24", "25-39", "40+"]:
        res[g].append(recall_score(y[grupo == g], p[grupo == g]))
for g, v in res.items():
    print(f"{g:7s} exhaustividad por semilla = {np.round(v, 3).tolist()}  media = {np.mean(v):.3f}")
print("\nPromedio de asistencia y barreras por grupo de edad (para explicar la brecha):")
print(con_grupo_edad(df).groupby("grupo_edad")[["asistencia_sem1", "asistencia_sem3", "barrera_transporte",
                                                 "barrera_cuido", "meses_desempleo"]].mean().round(2).to_string())
