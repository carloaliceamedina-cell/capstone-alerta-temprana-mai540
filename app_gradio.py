"""Demostración web de la alerta temprana (Gradio). Adaptado del ejemplo de despliegue del curso.

Uso local:   pip install -r requirements-demo.txt
             python app_gradio.py          y abre la dirección que aparece (http://127.0.0.1:7860)
En Colab:    demo_colab.ipynb lo ejecuta con un enlace público temporal.
"""
import pandas as pd

from src.alerta import entrenar, generar_alertas
from src.datos import cargar_datos

# El modelo se entrena al iniciar, con los datos sintéticos del repositorio (unos segundos).
MODELO = entrenar(cargar_datos())

AREAS = ["Salud", "Manufactura", "Tecnologia", "Hospitalidad", "Construccion"]
ESCOLARIDAD = ["sin_diploma", "cuarto_ano", "algo_universidad", "grado_universitario"]

LIMITACIONES = (
    "**Para qué sirve:** priorizar a quién ofrecer apoyo (transporte, cuido, tutoría) en la semana 3 de un "
    "programa de adiestramiento. **No** decide elegibilidad, permanencia ni expulsión.\n\n"
    "**Limitaciones:** se entrenó con datos **sintéticos**; detecta a 6 de cada 10 participantes que abandonan, "
    "y menos en el grupo de 40 años o más (0.54). Si cambia la forma de registrar la asistencia, sus aciertos caen "
    "sin avisar. Un \"seguimiento normal\" no significa \"sin riesgo\": la coordinación mantiene su contacto habitual."
)


def evaluar(asist1, asist2, asist3, puntuacion, meses_desempleo, empleado, transporte, cuido, ingreso_bajo,
            programa, area, escolaridad):
    """Recibe los datos de un participante en la semana 3 y devuelve la alerta explicada."""
    caso = pd.DataFrame([{
        "id_participante": "demo",
        "asistencia_sem1": asist1 / 100, "asistencia_sem2": asist2 / 100, "asistencia_sem3": asist3 / 100,
        "puntuacion_modulo1": float(puntuacion), "meses_desempleo": int(meses_desempleo),
        "empleado_al_ingreso": int(empleado), "barrera_transporte": int(transporte),
        "barrera_cuido": int(cuido), "ingreso_bajo": int(ingreso_bajo),
        "programa": programa, "area_adiestramiento": area, "escolaridad": escolaridad,
    }])
    fila = generar_alertas(MODELO, caso).iloc[0]
    factores = fila["factores_principales"] or "ninguno por encima del participante promedio"
    return (f"Probabilidad de no completar: {fila['prob_no_completar']:.0%}\n"
            f"Alerta: {fila['alerta']}\n"
            f"Factores que más suben el riesgo: {factores}")


def construir_demo():
    import gradio as gr  # se importa aquí para que las pruebas sin Gradio puedan usar evaluar()

    return gr.Interface(
        fn=evaluar,
        inputs=[
            gr.Slider(0, 100, value=85, step=1, label="Asistencia semana 1 (%)"),
            gr.Slider(0, 100, value=80, step=1, label="Asistencia semana 2 (%)"),
            gr.Slider(0, 100, value=75, step=1, label="Asistencia semana 3 (%)"),
            gr.Slider(0, 100, value=72, step=1, label="Puntuación del módulo 1"),
            gr.Number(value=6, precision=0, label="Meses sin empleo antes de entrar"),
            gr.Checkbox(value=False, label="Estaba empleado al ingresar"),
            gr.Checkbox(value=False, label="Barrera de transporte"),
            gr.Checkbox(value=False, label="Barrera de cuido"),
            gr.Checkbox(value=True, label="Ingreso bajo"),
            gr.Dropdown(["jovenes", "adultos"], value="adultos", label="Programa"),
            gr.Dropdown(AREAS, value="Salud", label="Área de adiestramiento"),
            gr.Dropdown(ESCOLARIDAD, value="cuarto_ano", label="Escolaridad"),
        ],
        outputs=gr.Textbox(label="Resultado", lines=4),
        title="Alerta temprana de no completación · Adiestramiento laboral (WIOA, PR)",
        description=LIMITACIONES,
    )


if __name__ == "__main__":
    construir_demo().launch()
