"""Ensambla las ocho tareas, conservando explicaciones y código visible en celdas.

python generar_notebook.py --ejecutar
Usa el Python activo para el kernel; no requiere registrar uno en el sistema.
"""
import argparse
import ast
import hashlib
import os
from pathlib import Path
import re
import textwrap

import nbformat

BASE = Path(__file__).resolve().parent
DESTINO = BASE / "proyecto_maraton_olimpica_manuel_plaza.ipynb"


def adaptar_codigo(texto):
    """Quita imports locales redundantes y desenvuelve el bloque de ejecución."""
    arbol = ast.parse(texto)
    lineas = texto.splitlines(keepends=True)
    for nodo in reversed(arbol.body):
        if isinstance(nodo, ast.ImportFrom) and (nodo.module or "").startswith("tareas."):
            lineas[nodo.lineno - 1:nodo.end_lineno] = []
        elif isinstance(nodo, ast.If) and ast.unparse(nodo.test) == "__name__ == '__main__'":
            cuerpo = "".join(lineas[nodo.lineno:nodo.end_lineno])
            lineas[nodo.lineno - 1:nodo.end_lineno] = [textwrap.dedent(cuerpo)]
    return "".join(lineas).strip()


def extraer_partes(fuente):
    """Extrae funciones completas sin alterar sus cuerpos ni ejecutar el script."""
    partes = {"imports": [], "globales": [], "ejecucion": []}
    lineas = fuente.splitlines(keepends=True)
    for nodo in ast.parse(fuente).body:
        fragmento = ast.get_source_segment(fuente, nodo)
        if isinstance(nodo, (ast.Import, ast.ImportFrom)):
            if not (isinstance(nodo, ast.ImportFrom) and (nodo.module or "").startswith("tareas.")):
                partes["imports"].append(fragmento)
        elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            partes[nodo.name] = [fragmento]
        elif isinstance(nodo, ast.If) and ast.unparse(nodo.test) == "__name__ == '__main__'":
            partes["ejecucion"].append(textwrap.dedent("".join(lineas[nodo.lineno:nodo.end_lineno])).strip())
        else:
            partes["globales"].append(fragmento)
    return {clave: "\n\n".join(textos) for clave, textos in partes.items()}


def recuperar_portada():
    """Conserva la portada que el usuario editó, incluidos sus adjuntos y metadatos."""
    if DESTINO.exists():
        anterior = nbformat.read(DESTINO, as_version=4)
        primera = anterior.cells[0]
        if primera.cell_type == "markdown":
            import copy
            portada = copy.deepcopy(primera)
            # El índice pasa a una celda propia; no se duplica en regeneraciones.
            linea_indice = re.search(r"(?im)^.*[ÍI]NDICE DE CONTENIDOS.*$", portada.source)
            if linea_indice:
                portada.source = portada.source[:linea_indice.start()].rstrip().removesuffix("---").rstrip()
            portada.metadata["tipo_contenido"] = "portada_usuario"
            return portada
    return nbformat.v4.new_markdown_cell("# **INFORME SOLEMNE 2**\n\n## Maratón olímpica: evolución histórica y caso Manuel Plaza")


def recuperar_fuentes():
    if DESTINO.exists():
        anterior = nbformat.read(DESTINO, as_version=4)
        for celda in reversed(anterior.cells):
            if celda.cell_type == "markdown" and "Kaggle:" in celda.source and "Fuentes" in celda.source:
                texto = celda.source
                if '<a id="fuentes-limites"></a>' not in texto:
                    texto = '<a id="fuentes-limites"></a>\n' + texto
                if "[Volver al índice]" not in texto:
                    texto += "\n\n[Volver al índice](#indice-contenidos)"
                return texto
    raise FileNotFoundError("No se encontró la celda de fuentes del informe existente.")


def construir_notebook():
    from contenido_notebook import INDICE, INTRODUCCION, ENTORNO_ANTES, ENTORNO_DESPUES, SECCIONES, CONCLUSIONES
    portada, fuentes = recuperar_portada(), recuperar_fuentes()
    n = nbformat.v4.new_notebook()
    n.metadata.update({"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"},
                       "organizacion": "Informe con índice, explicación previa e interpretación de resultados"})
    md = nbformat.v4.new_markdown_cell
    n.cells = [portada, md(INDICE), md(INTRODUCCION), md(ENTORNO_ANTES),
               nbformat.v4.new_code_cell("""import os
import tempfile
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "u2-matplotlib"))
if "get_ipython" in globals():
    get_ipython().run_line_magic("matplotlib", "inline")
import pandas as pd
pd.set_option("display.max_columns", 12)
pd.set_option("display.max_rows", 100)"""), md(ENTORNO_DESPUES)]
    titulos_seccion = {
        1: "SECCIÓN I · Macroanálisis y evolución histórica del maratón olímpico",
        4: "SECCIÓN II · Profundización histórica: Manuel Plaza en Ámsterdam 1928",
        8: "SECCIÓN III · Pregunta conceptual y de cierre",
    }
    for seccion in SECCIONES:
        numero = seccion["numero"]
        archivos = list((BASE / "tareas").glob(f"tarea{numero:02d}_*.py"))
        if len(archivos) != 1:
            raise ValueError(f"Se esperaba un único script para la tarea {numero}")
        archivo = archivos[0]
        fuente = archivo.read_text(encoding="utf-8")
        partes = extraer_partes(fuente)
        usadas = [p for b in seccion["bloques"] for p in b["partes"]]
        if len(usadas) != len(set(usadas)):
            raise ValueError(f"Partes duplicadas en tarea {numero}")
        faltantes = {p for p, codigo in partes.items() if codigo} - set(usadas)
        if faltantes:
            raise ValueError(f"Código sin incluir en tarea {numero}: {sorted(faltantes)}")
        if numero in titulos_seccion:
            n.cells.append(md(f"# **{titulos_seccion[numero]}**"))
        n.cells.append(md(f'<a id="tarea-{numero}"></a>\n## **{numero}. {seccion["titulo"]}**\n\n{seccion["introduccion"]}'))
        for b in seccion["bloques"]:
            n.cells.append(md(f'### {b["titulo"]}\n\n{b["antes"]}'))
            codigo = "\n\n".join(partes[p] for p in b["partes"] if partes[p])
            ast.parse(codigo)
            celda = nbformat.v4.new_code_cell(codigo)
            celda.metadata.update({"archivo_origen": f"tareas/{archivo.name}",
                                   "sha256_fuente": hashlib.sha256(fuente.encode()).hexdigest(),
                                   "partes_origen": b["partes"]})
            n.cells.append(celda)
            if b["despues"]:
                n.cells.append(md(b["despues"]))
        n.cells.append(md("[Volver al índice](#indice-contenidos)"))
    n.cells += [md(CONCLUSIONES), md(fuentes)]
    nbformat.validate(n)
    nbformat.write(n, DESTINO)
    return n


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ejecutar", action="store_true")
    args = parser.parse_args()
    n = construir_notebook()
    if args.ejecutar:
        os.environ.setdefault("JUPYTER_RUNTIME_DIR", str(Path(os.environ.get("TMPDIR", "/tmp")) / "u2-jupyter-runtime"))
        os.environ.setdefault("IPYTHONDIR", str(Path(os.environ.get("TMPDIR", "/tmp")) / "u2-ipython"))
        from nbclient import NotebookClient
        from jupyter_client import AsyncKernelManager
        import sys
        # El kernelspec estándar puede apuntar a un Python distinto del activo.
        km = AsyncKernelManager(kernel_name="python3")
        km.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
        client = NotebookClient(n, km=km, timeout=120, startup_timeout=45,
                                on_cell_start=lambda cell, cell_index, **kwargs: print(f"Celda {cell_index + 1}/{len(n.cells)}", flush=True),
                                resources={"metadata": {"path": str(BASE)}})
        client.execute(cleanup_kc=True)
        nbformat.write(n, DESTINO)
    print(f"Notebook {'ejecutado' if args.ejecutar else 'generado'}: {DESTINO}")


if __name__ == "__main__":
    main()
