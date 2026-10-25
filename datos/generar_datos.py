"""Genera el conjunto SINTÉTICO de participantes de adiestramiento laboral (WIOA, Puerto Rico).

Por qué sintético: los registros reales de participantes son confidenciales y no pueden salir
del proveedor ni subirse a GitHub (ver propuesta del Módulo 5). Este script imita su estructura:
datos de admisión, asistencia de las semanas 1 a 3, desempeño en el módulo 1 y el resultado final.
No contiene datos de ninguna persona real.

Uso:  python datos/generar_datos.py        ->  escribe datos/participantes_sinteticos.csv
El resultado es siempre el mismo (semilla fija y generador local).
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 540
RUTA_SALIDA = Path(__file__).parent / "participantes_sinteticos.csv"

COHORTES = ["2022-1", "2022-2", "2023-1", "2023-2", "2024-1", "2024-2", "2025-1", "2025-2"]
REGIONES = ["Metro", "Norte", "Sur", "Este", "Oeste", "Centro"]
AREAS = ["Salud", "Manufactura", "Tecnologia", "Hospitalidad", "Construccion"]
ESCOLARIDAD = ["sin_diploma", "cuarto_ano", "algo_universidad", "grado_universitario"]


def generar(n_por_cohorte=190, semilla=SEMILLA):
    """Devuelve un DataFrame con n_por_cohorte participantes por cohorte."""
    rng = np.random.default_rng(semilla)  # generador LOCAL: misma salida en cada llamada
    filas = []
    for i, cohorte in enumerate(COHORTES):
        n = n_por_cohorte
        programa = rng.choice(["jovenes", "adultos"], size=n, p=[0.4, 0.6])
        edad = np.where(programa == "jovenes", rng.integers(16, 25, size=n), rng.integers(22, 61, size=n))
        genero = rng.choice(["F", "M"], size=n, p=[0.55, 0.45])
        region = rng.choice(REGIONES, size=n, p=[0.30, 0.17, 0.15, 0.13, 0.13, 0.12])
        area = rng.choice(AREAS, size=n)
        escolaridad = rng.choice(ESCOLARIDAD, size=n, p=[0.18, 0.47, 0.25, 0.10])
        empleado = rng.binomial(1, 0.25, size=n)
        meses_desempleo = np.where(empleado == 1, 0, rng.gamma(2.0, 4.0, size=n).round().astype(int))
        # Las barreras de transporte son más frecuentes fuera del área metropolitana
        p_transporte = np.select([region == "Metro", np.isin(region, ["Centro", "Oeste"])], [0.15, 0.45], 0.30)
        barrera_transporte = rng.binomial(1, p_transporte)
        barrera_cuido = rng.binomial(1, np.where((genero == "F") & (edad >= 20), 0.35, 0.12))
        ingreso_bajo = rng.binomial(1, 0.55, size=n)

        # Riesgo latente de no completar (lo que el modelo debe descubrir)
        riesgo = (
            -1.35
            + 0.85 * barrera_transporte
            + 0.70 * barrera_cuido
            + 0.35 * ingreso_bajo
            + 0.45 * (escolaridad == "sin_diploma")
            + 0.04 * meses_desempleo
            + 0.30 * (edad < 20)
            - 0.25 * empleado
            + 0.10 * i / len(COHORTES)          # leve deriva entre cohortes
            + rng.normal(0, 0.9, size=n)
        )
        # Asistencia de las semanas 1-3: baja a medida que sube el riesgo latente
        base = 1 / (1 + np.exp(0.9 * riesgo - 1.6))
        asis = [np.clip(base - 0.04 * s + rng.normal(0, 0.12, size=n), 0, 1).round(2) for s in range(3)]
        puntuacion_m1 = np.clip(72 - 7 * riesgo + rng.normal(0, 10, size=n), 0, 100).round(0)

        p_no_completa = 1 / (1 + np.exp(-(1.1 * riesgo - 0.35)))
        no_completo = rng.binomial(1, p_no_completa)

        # Columnas que solo se conocen DESPUÉS de la semana 3 (no pueden usarse para predecir)
        asistencia_total = np.where(no_completo == 1, rng.uniform(0.15, 0.65, size=n), rng.uniform(0.75, 1.0, size=n)).round(2)
        semanas_completadas = np.where(no_completo == 1, rng.integers(3, 10, size=n), 12)
        empleo_q2 = np.where(no_completo == 1, rng.binomial(1, 0.30, size=n), rng.binomial(1, 0.68, size=n))

        for k in range(n):
            filas.append({
                "id_participante": f"P{i:02d}{k:04d}",
                "cohorte": cohorte,
                "programa": programa[k],
                "edad": int(edad[k]),
                "genero": genero[k],
                "region": region[k],
                "area_adiestramiento": area[k],
                "escolaridad": escolaridad[k],
                "empleado_al_ingreso": int(empleado[k]),
                "meses_desempleo": int(meses_desempleo[k]),
                "barrera_transporte": int(barrera_transporte[k]),
                "barrera_cuido": int(barrera_cuido[k]),
                "ingreso_bajo": int(ingreso_bajo[k]),
                "asistencia_sem1": float(asis[0][k]),
                "asistencia_sem2": float(asis[1][k]),
                "asistencia_sem3": float(asis[2][k]),
                "puntuacion_modulo1": float(puntuacion_m1[k]),
                "asistencia_total": float(asistencia_total[k]),
                "semanas_completadas": int(semanas_completadas[k]),
                "empleo_q2": int(empleo_q2[k]),
                "no_completo": int(no_completo[k]),
            })
    return pd.DataFrame(filas)


if __name__ == "__main__":
    df = generar()
    df.to_csv(RUTA_SALIDA, index=False)
    print(f"Escrito {RUTA_SALIDA.name}: {len(df)} filas, {df.shape[1]} columnas, "
          f"no completó = {df['no_completo'].mean():.1%}")
