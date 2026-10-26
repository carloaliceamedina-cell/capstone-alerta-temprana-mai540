"""Prepara las rutas de importación en un solo lugar (revisión del PR #1, hallazgo 2):
la raíz del proyecto (paquete src) y la carpeta datos (generador sintético)."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
for ruta in (RAIZ, RAIZ / "datos"):
    if str(ruta) not in sys.path:
        sys.path.insert(0, str(ruta))
