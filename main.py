"""Alerta temprana de no completación — línea de comandos.

    python main.py evaluar                         compara modelos con validación cruzada y elige uno
    python main.py alertar datos/ejemplo_semana3.csv   genera alertas para participantes nuevos
"""
import argparse
import sys

import pandas as pd

from src.alerta import entrenar, generar_alertas
from src.config import RAIZ
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


def main(argv=None):
    p = argparse.ArgumentParser(description="Alerta temprana de no completación (adiestramiento laboral)")
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("evaluar", help="compara modelos con validación cruzada")
    a = sub.add_parser("alertar", help="genera alertas para un CSV de participantes en la semana 3")
    a.add_argument("archivo")
    args = p.parse_args(argv)
    return {"evaluar": cmd_evaluar, "alertar": cmd_alertar}[args.comando](args)


if __name__ == "__main__":
    sys.exit(main())
