"""Decisiones del proyecto en un solo lugar: qué columnas se usan, cuáles están prohibidas y por qué."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DATOS = RAIZ / "datos" / "participantes_sinteticos.csv"
SEMILLA = 42

OBJETIVO = "no_completo"          # 1 = no completó el programa (clase positiva: la que queremos detectar)

# Predictores: solo información disponible al cierre de la SEMANA 3 del programa.
PREDICTORES_NUM = [
    "meses_desempleo",
    "asistencia_sem1", "asistencia_sem2", "asistencia_sem3",
    "puntuacion_modulo1",
]
PREDICTORES_BIN = ["empleado_al_ingreso", "barrera_transporte", "barrera_cuido", "ingreso_bajo"]
PREDICTORES_CAT = ["programa", "area_adiestramiento", "escolaridad"]
PREDICTORES = PREDICTORES_NUM + PREDICTORES_BIN + PREDICTORES_CAT

# PROHIBIDAS por fuga de información: se registran después de la semana 3 o al salir del programa.
COLUMNAS_FUTURO = ["asistencia_total", "semanas_completadas", "empleo_q2"]

# Variables sensibles: se usan para AUDITAR la herramienta, nunca para decidir sobre personas.
COLUMNAS_SENSIBLES = ["edad", "genero", "region"]

# Identificadores que no aportan información para predecir
IDENTIFICADORES = ["id_participante", "cohorte"]
