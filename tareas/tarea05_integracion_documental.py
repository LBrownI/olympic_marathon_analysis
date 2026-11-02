# %% [markdown]
# ## 5. Integración documental: metadatos → consulta → corpus trazable
# Simulamos la respuesta de un buscador; no inventamos periódicos ni citas reales.
# Cada documento identifica si es SIMULADO o una paráfrasis de una fuente leída.
# El pipeline conceptual es: validar metadatos → construir consultas → recuperar
# documentos → guardar URL/fecha/autor → limpiar HTML u OCR → detectar duplicados
# → revisión histórica. Aquí usamos una caché local reproducible, sin conexión.
# Un conector real debe preservar el texto original, su licencia y su procedencia.
# %%
from tareas.tarea01_ingesta_limpieza import BASE, SALIDA, normalizar_texto, mostrar_tabla
import hashlib
import json
from urllib.parse import urlencode
import pandas as pd


def simular_ingesta_documental(atleta, anio, ciudad):
    """Construye consultas y devuelve tres textos didácticos, nunca prensa real."""
    nombre = normalizar_texto(atleta)
    if nombre not in {"manuel plaza", "manuel plaza reyes"} or int(anio) != 1928 or normalizar_texto(ciudad) != "amsterdam":
        raise ValueError("La caché de demostración solo cubre Manuel Plaza, Ámsterdam 1928")
    consultas = [
        f'"{atleta}" "{anio}" "{ciudad}" maratón',
        f'"{atleta}" suplementero "Santiago" "Parque Cousiño"',
        f'"{atleta}" "1928" site:memoriachilena.gob.cl',
    ]
    textos = [
        f"Santiago, {anio}. {atleta}, suplementero de origen humilde, recorre la ciudad "
        "vendiendo diarios. En el Parque Cousiño entrena con esfuerzo, pese a la "
        "escasez de recursos y a la precariedad de su preparación.",
        f"Ámsterdam, 5 de agosto de {anio}. {atleta} obtiene la plata para Chile. "
        "Boughera El Ouafi representa a Francia y Martti Marttelin a Finlandia. "
        "La hazaña despierta asombro y sorpresa; Sudamérica celebra con orgullo "
        "el coraje del corredor.",
        f"El regreso de {atleta} a Santiago se narra como una gesta de esfuerzo y gloria. "
        "Su oficio de suplementero y las dificultades económicas conviven con "
        "el entusiasmo deportivo. El Parque Cousiño aparece como escenario de "
        "un entrenamiento sin recursos suficientes.",
    ]
    documentos = []
    for i, texto in enumerate(textos, 1):
        documentos.append({
            "doc_id": f"SIM_{i:02d}", "tipo_documento": "simulado",
            "titulo": f"Recreación didáctica {i} (NO es un periódico histórico)",
            "autor": "Elaboración propia para el ejercicio",
            "fuente_url": None, "fecha_publicacion": None, "anio_referido": int(anio),
            "es_cita_literal": False, "texto": texto,
        })
    plan = [{"consulta": q, "url_busqueda_conceptual": "https://www.google.com/search?" + urlencode({"q": q}),
             "estado": "simulación; consulta NO ejecutada por esta función"} for q in consultas]
    return documentos, plan


def preparar_corpus(atleta="Manuel Plaza Reyes", anio=1928, ciudad="Ámsterdam"):
    simulados, plan = simular_ingesta_documental(atleta, anio, ciudad)
    ruta = BASE / "datos_documentales/corpus_documental.json"
    documentales = json.loads(ruta.read_text(encoding="utf-8"))
    documentos = simulados + documentales
    ids, huellas = set(), set()
    for doc in documentos:
        if doc["tipo_documento"] not in {"simulado", "parafrasis_documental"}:
            raise ValueError("Tipo documental desconocido")
        if doc["tipo_documento"] == "parafrasis_documental" and not doc["fuente_url"]:
            raise ValueError("Falta URL para una paráfrasis documental")
        huella = hashlib.sha256(doc["texto"].encode("utf-8")).hexdigest()
        if doc["doc_id"] in ids or huella in huellas:
            raise ValueError("Documento o texto duplicado")
        ids.add(doc["doc_id"])
        huellas.add(huella)
        doc["sha256_texto"] = huella
    return documentos, pd.DataFrame(plan)

# %% [markdown]
# ### Inspección del corpus y de las consultas
# Mostramos los textos usados realmente. La URL de búsqueda es un diseño de
# integración, no la afirmación de que se consultó un archivo de prensa.
# Las paráfrasis se guardan con el proyecto para que su ejecución no dependa
# de cambios en las páginas. Ningún texto se fecha ficticiamente como publicado en 1928.
# %%
if __name__ == "__main__":
    corpus, plan_busqueda = preparar_corpus()
    (SALIDA / "corpus_utilizado.json").write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
    plan_busqueda.to_csv(SALIDA / "plan_busqueda.csv", index=False)
    mostrar_tabla(plan_busqueda[["consulta", "estado"]])
    for documento in corpus:
        print(f"\n[{documento['doc_id']} · {documento['tipo_documento']}]\n{documento['texto']}")

# %% [markdown]
# **Conclusión.** La integración agrega origen social y espacios de entrenamiento
# que no están en la tabla deportiva. El reportaje de UDP también permite discutir
# la conservación de la memoria material; el paradero del trofeo se presenta como
# desconocido al realizarse esa investigación, sin afirmar un hallazgo posterior.
# El reportaje es retrospectivo, no una crónica contemporánea de 1928.
#
# Fuentes: [Llanos, Vergara 240](https://vergara240.udp.cl/en-busca-de-la-medalla-olimpica-perdida/)
# y [Comité Olímpico de Chile](https://www.coch.cl/wp-content/uploads/2018/01/medallistas-olimpicos5.pdf).
