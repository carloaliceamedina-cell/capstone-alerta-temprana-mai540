"""Verificación reproducida (Skill auditoria-modelos, V1.2 y V4) sobre la versión auditada.
Solo lectura: importa el proyecto, no lo modifica. Uso: python auditorias/v1_antes/evidencia/verificacion_subgrupos_v1.py <copia del proyecto en el commit e654306>"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, sys.argv[1])
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from sklearn.model_selection import cross_val_predict
from src.datos import cargar_datos, separar_X_y
from src.modelos import construir_modelos
from src.validacion import particion

df = cargar_datos()
X, y = separar_X_y(df)
modelo = construir_modelos()["Regresión logística (balanced)"]
pred = cross_val_predict(modelo, X, y, cv=particion())
vn, fp, fn, vp = confusion_matrix(y, pred).ravel()
print(f"Matriz de confusión (CV, 5 pliegues): VN={vn} FP={fp} FN={fn} VP={vp}")
print(f"Exhaustividad global = {vp/(vp+fn):.3f} · Precisión global = {vp/(vp+fp):.3f}")

df = df.assign(pred=pred, grupo_edad=pd.cut(df["edad"], [0, 24, 39, 120], labels=["16-24", "25-39", "40+"]))
glob = recall_score(y, pred)
for col in ["genero", "grupo_edad", "region", "cohorte"]:
    print(f"\nSubgrupo: {col}")
    filas = []
    for g, d in df.groupby(col, observed=True):
        pos = (d["no_completo"] == 1).sum()
        filas.append((g, len(d), pos, recall_score(d["no_completo"], d["pred"])))
    mejor = max(f[3] for f in filas)
    for g, n, pos, r in filas:
        marca = "  <-- BRECHA" if pos >= 30 and (glob - r > 0.05 or r / mejor < 0.80) else ""
        print(f"  {str(g):8s} n={n:4d} positivos={pos:3d} exhaustividad={r:.3f} (global {glob:.3f}, cociente {r/mejor:.2f}){marca}")
