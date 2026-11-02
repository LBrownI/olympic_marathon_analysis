"""Ejecute desde cualquier carpeta: python /ruta/a/U2/ejecutar_proyecto.py."""
import os
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parent


def main():
    entorno = os.environ.copy()
    entorno.setdefault("MPLBACKEND", "Agg")
    entorno.setdefault("MPLCONFIGDIR", str(Path(os.environ.get("TMPDIR", "/tmp")) / "u2-matplotlib"))
    for archivo in sorted((BASE / "tareas").glob("tarea*.py")):
        print(f"\n{'=' * 60}\n{archivo.stem}\n{'=' * 60}", flush=True)
        subprocess.run([sys.executable, "-m", f"tareas.{archivo.stem}"], cwd=BASE, env=entorno, check=True)
    print(f"\nProyecto completado. Resultados en {BASE / 'resultados'}")


if __name__ == "__main__":
    main()
