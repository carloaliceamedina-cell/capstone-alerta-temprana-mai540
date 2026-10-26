"""Decisiones del proyecto en un solo lugar: qué columnas se usan, cuáles están prohibidas y por qué."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DATOS = RAIZ / "datos" / "participantes_sinteticos.csv"
SEMILLA = 42

OBJETIVO = "no_completo"          # 1 = no completó el programa (clase positiva: la que queremos detectar)

# Costo del error (hallazgo V1.4 de la auditoría): no detectar a quien va a abandonar (falso negativo)
# cuesta más que ofrecer apoyo a quien lo habría completado igual (falso positivo). El primero pierde
# el adiestramiento y el programa pierde un resultado de desempeño WIOA; el segundo cuesta una llamada
# o un pase de transporte. Por eso la métrica prioritaria es la EXHAUSTIVIDAD de la clase 1, con una
# precisión mínima de 0.50 para que el número de alertas siga siendo manejable para la coordinación.

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
