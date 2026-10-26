"""Alerta temprana de no completación — línea de comandos.

    python main.py evaluar                         compara modelos con validación cruzada y elige uno
    python main.py alertar datos/ejemplo_semana3.csv   genera alertas para participantes nuevos
    python main.py auditar                         matriz de confusión, validación temporal y brechas por subgrupo
    python main.py degradacion                     cómo cae el modelo si cambian los datos (sin tocar el código)
"""
import argparse
import sys

import pandas as pd

from src.alerta import entrenar, generar_alertas
from src.auditoria import (exhaustividad_por_subgrupo, matriz_confusion, predicciones_fuera_de_pliegue,
                           validacion_temporal)
from src.config import RAIZ
from src.degradacion import simular
from src.datos import cargar_datos, separar_X_y, validar_datos
from src.modelos import construir_modelos
from src.validacion import elegir_modelo, evaluar_cv


def cmd_evaluar(_args):
    df = cargar_datos()
    validar_datos(df)
    X, y = separar_X_y(df)
    print(f"Datos: {len(df)} participantes, {df['cohorte'].nunique()} cohortes, "
          f"no completó = {y.mean():.1%}\n")
    tabla = evaluar_cv(construir_modelos(), X, y)
    vista = pd.DataFrame({
        "Modelo": tabla["modelo"],
        "Exhaustividad": [f"{m:.3f} ± {s:.3f}" for m, s in zip(tabla["exhaustividad_media"], tabla["exhaustividad_desv"])],
        "Precisión": [f"{m:.3f} ± {s:.3f}" for m, s in zip(tabla["precision_media"], tabla["precision_desv"])],
        "F1": [f"{m:.3f} ± {s:.3f}" for m, s in zip(tabla["f1_media"], tabla["f1_desv"])],
        "Exact. balanceada": [f"{m:.3f} ± {s:.3f}" for m, s in zip(tabla["exactitud_balanceada_media"], tabla["exactitud_balanceada_desv"])],
    })
    print("Validación cruzada estratificada, 5 pliegues (media ± desviación estándar):")
    print(vista.to_string(index=False))
    elegido = elegir_modelo(tabla)
    print(f"\nModelo elegido: {elegido}")
    print("Criterio: mayor exhaustividad media con precisión media >= 0.50; "
          "si la diferencia es menor que una desviación, gana el más interpretable.")
    (RAIZ / "resultados").mkdir(exist_ok=True)
    tabla.to_csv(RAIZ / "resultados" / "tabla_cv.csv", index=False)
    return 0


def cmd_alertar(args):
    modelo = entrenar(cargar_datos())
    nuevos = pd.read_csv(args.archivo)
    alertas = generar_alertas(modelo, nuevos)
    print(alertas.to_string(index=False))
    n = (alertas["alerta"] == "OFRECER APOYO").sum()
    print(f"\n{n} de {len(alertas)} participantes con alerta. La alerta prioriza apoyo; "
          "no decide elegibilidad ni expulsión.")
    return 0


def cmd_auditar(_args):
    df = cargar_datos()
    validar_datos(df)
    nombre = "Regresión logística (balanced)"
    pred = predicciones_fuera_de_pliegue(df, nombre)
    m = matriz_confusion(df["no_completo"], pred)
    print(f"Modelo: {nombre} · predicciones fuera de pliegue (CV estratificada, 5 pliegues)\n")
    print("Matriz de confusión (1 = no completó):")
    print(f"                 predijo 0   predijo 1\n  real 0 (completó)   {m['VN']:5d}       {m['FP']:5d}\n"
          f"  real 1 (no compl.)  {m['FN']:5d}       {m['VP']:5d}")
    print(f"  exhaustividad = {m['exhaustividad']:.3f} · precisión = {m['precision']:.3f}\n")
    t = validacion_temporal(df, nombre)
    print(f"Validación temporal: entrena con {t['entrenamiento']}, prueba con {t['prueba']}")
    print(f"  exhaustividad = {t['exhaustividad']:.3f} · precisión = {t['precision']:.3f}\n")
    tabla, global_ = exhaustividad_por_subgrupo(df, pred)
    print(f"Exhaustividad por subgrupo (global = {global_:.3f}; brecha si > 0.05 por debajo o cociente < 0.80, "
          "con >= 30 positivos):")
    print(tabla.to_string(index=False))
    (RAIZ / "resultados").mkdir(exist_ok=True)
    tabla.to_csv(RAIZ / "resultados" / "subgrupos.csv", index=False)
    n = int(tabla["brecha"].sum())
    print(f"\n{n} subgrupo(s) con brecha. Ver README, sección Limitaciones.")
    return 0


def cmd_degradacion(_args):
    df = cargar_datos()
    validar_datos(df)
    tabla = simular(df)
    print("Modelo entrenado con las cohortes 2022-1 a 2024-2 y evaluado con las cohortes 2025.")
    print("El código y el modelo son idénticos en los tres escenarios; solo cambian los datos.\n")
    print(tabla.to_string(index=False))
    print("\nLínea base de referencia (regla de asistencia < 75 %): exhaustividad 0.514 en CV.")
    print("Si la exhaustividad medida al cerrar una cohorte cae por debajo de esa línea base, hay que revisar y reentrenar.")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Alerta temprana de no completación (adiestramiento laboral)")
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("evaluar", help="compara modelos con validación cruzada")
    a = sub.add_parser("alertar", help="genera alertas para un CSV de participantes en la semana 3")
    a.add_argument("archivo")
    sub.add_parser("auditar", help="matriz de confusión, validación temporal y exhaustividad por subgrupo")
    sub.add_parser("degradacion", help="simula cambios en los datos y mide cuánto cae el modelo")
    args = p.parse_args(argv)
    comandos = {"evaluar": cmd_evaluar, "alertar": cmd_alertar, "auditar": cmd_auditar, "degradacion": cmd_degradacion}
    return comandos[args.comando](args)


if __name__ == "__main__":
    sys.exit(main())
