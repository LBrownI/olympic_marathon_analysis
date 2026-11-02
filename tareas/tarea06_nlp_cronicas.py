# %% [markdown]
# ## 6. NLP en español: limpieza, tokens, entidades y tono léxico
# Adaptamos la tokenización, stopwords y frecuencias de los notebooks de clase.
# Conservamos tildes y mayúsculas para NER; para frecuencias usamos minúsculas.
# spaCy proporciona tokenizador y stopwords españoles sin descargas adicionales.
# NER usa EntityRuler con reglas explícitas de dominio (PER, LOC, DATE, ORG).
# OCUPACION es una etiqueta propia para contexto social. No se presenta como
# un modelo estadístico entrenado ni como descubrimiento abierto de entidades.
# Este enfoque es auditable y limitado al vocabulario declarado; un archivo real
# requeriría un modelo español más revisión manual de OCR y entidades desconocidas.
# %%
from tareas.tarea01_ingesta_limpieza import SALIDA, normalizar_texto, mostrar_tabla
from tareas.tarea05_integracion_documental import preparar_corpus
from collections import Counter
import json
import re
import unicodedata
import pandas as pd
import spacy
import matplotlib.pyplot as plt


def limpiar_texto(texto):
    """Limpieza suave: Unicode, etiquetas y espacios; no destruye las entidades."""
    texto = unicodedata.normalize("NFC", texto)
    texto = re.sub(r"<[^>]+>", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def crear_pipeline_nlp():
    nlp = spacy.blank("es")
    nlp.add_pipe("sentencizer")
    ruler = nlp.add_pipe("entity_ruler", config={"phrase_matcher_attr": "LOWER"})
    catalogo = {
        "PER": ["Manuel Plaza Reyes", "Manuel Plaza", "Boughera El Ouafi", "Martti Marttelin", "Magdalena Llanos", "Alfonso Sánchez Rodríguez"],
        "LOC": ["Ámsterdam", "Amsterdam", "Santiago", "Parque Cousiño", "Sudamérica", "Chile", "Francia", "Finlandia"],
        "ORG": ["Vergara 240", "Comité Olímpico de Chile"],
        "OCUPACION": ["suplementero", "suplementeros"],
    }
    patrones = [{"label": etiqueta, "pattern": nombre} for etiqueta, nombres in catalogo.items() for nombre in nombres]
    patrones += [
        {"label": "DATE", "pattern": [{"TEXT": {"REGEX": r"^(?:18|19|20)\d{2}$"}}]},
        {"label": "DATE", "pattern": [{"TEXT": {"REGEX": r"^\d{1,2}$"}}, {"LOWER": "de"},
                                             {"LOWER": {"IN": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]}},
                                             {"LOWER": "de"}, {"TEXT": {"REGEX": r"^(?:18|19|20)\d{2}$"}}]},
    ]
    ruler.add_patterns(patrones)
    return nlp

# %% [markdown]
# ### Diccionario de tono y alcance de la interpretación
# Medimos tres campos semánticos separados: épica, sorpresa y precariedad.
# Un texto puede contener los tres. Contamos palabras y tasas por 100 tokens
# alfabéticos, sin convertir precariedad en una evaluación negativa del atleta.
# Una ventana de tres tokens en la misma oración detecta algunas negaciones;
# guardamos sus coincidencias para revisión. No cubre ironía ni todas las negaciones.
# No se usa un clasificador de sentimiento general entrenado en otro dominio.
# %%
LEXICO = {
    "epica": {"hazaña", "gesta", "gloria", "orgullo", "coraje", "heroico", "heroica", "proeza", "esfuerzo", "entusiasmo"},
    "sorpresa": {"asombro", "sorpresa", "inesperado", "inesperada", "sorprendente"},
    "precariedad": {"humilde", "escasez", "precariedad", "dificultades", "pobreza", "limitados"},
}
NEGACIONES = {"no", "nunca", "jamás", "jamas", "sin"}


def analizar_lexico(doc):
    conteos = dict.fromkeys(LEXICO, 0)
    evidencias = []
    for oracion in doc.sents:
        tokens = [t for t in oracion if t.is_alpha]
        for i, token in enumerate(tokens):
            for categoria, palabras in LEXICO.items():
                if token.lower_ in palabras:
                    anteriores = {t.lower_ for t in tokens[max(0, i - 3):i]}
                    negado = bool(anteriores & NEGACIONES)
                    conteos[categoria] += int(not negado)
                    evidencias.append({"categoria": categoria, "palabra": token.text,
                                       "negado": negado, "oracion": oracion.text})
    total = sum(t.is_alpha for t in doc)
    tasas = {f"{k}_por_100": round(v / total * 100, 3) if total else 0.0 for k, v in conteos.items()}
    maximo = max(conteos.values())
    tono = ", ".join(k for k, v in conteos.items() if v == maximo) if maximo else "sin evidencia léxica"
    return {"tokens_alfabeticos": total, **conteos, **tasas, "tono_predominante": tono}, evidencias


def procesar_corpus(corpus):
    nlp = crear_pipeline_nlp()
    entidades, resumenes, frecuencias, coincidencias, tokenizados = [], [], [], [], []
    textos = [limpiar_texto(d["texto"]) for d in corpus]
    for documento, texto, doc in zip(corpus, textos, nlp.pipe(textos)):
        # Las negaciones se conservan para no perder contexto crítico.
        filtrados = [t.lower_ for t in doc if t.is_alpha and (not t.is_stop or t.lower_ in NEGACIONES)]
        tokenizados.append({"doc_id": documento["doc_id"], "tipo_documento": documento["tipo_documento"],
                            "texto_limpio": texto, "tokens_filtrados": filtrados})
        for palabra, n in Counter(filtrados).items():
            frecuencias.append({"doc_id": documento["doc_id"], "tipo_documento": documento["tipo_documento"], "palabra": palabra, "frecuencia": n})
        for ent in doc.ents:
            entidades.append({"doc_id": documento["doc_id"], "tipo_documento": documento["tipo_documento"],
                               "entidad": ent.text, "etiqueta": ent.label_, "inicio": ent.start_char,
                               "fin": ent.end_char, "oracion": ent.sent.text, "fuente_url": documento["fuente_url"],
                               "metodo": "spaCy EntityRuler: reglas de dominio"})
        resumen, evidencia = analizar_lexico(doc)
        resumenes.append({"doc_id": documento["doc_id"], "tipo_documento": documento["tipo_documento"],
                          "tokens_filtrados": len(filtrados), **resumen})
        coincidencias.extend({"doc_id": documento["doc_id"], **e} for e in evidencia)
    return {"entidades": pd.DataFrame(entidades), "tonos": pd.DataFrame(resumenes),
            "frecuencias": pd.DataFrame(frecuencias), "evidencias_lexicas": pd.DataFrame(coincidencias),
            "tokens": tokenizados}


def evaluar_entidades_control(entidades):
    """Control manual de presencia; no es F1 ni evaluación fuera de muestra."""
    esperadas = [
        ("SIM_01", "Manuel Plaza Reyes", "PER"), ("SIM_01", "Santiago", "LOC"),
        ("SIM_01", "Parque Cousiño", "LOC"), ("SIM_01", "1928", "DATE"),
        ("SIM_02", "Ámsterdam", "LOC"), ("SIM_02", "5 de agosto de 1928", "DATE"),
        ("SIM_02", "Boughera El Ouafi", "PER"), ("SIM_02", "Martti Marttelin", "PER"),
    ]
    detectadas = set(entidades[["doc_id", "entidad", "etiqueta"]].itertuples(index=False, name=None))
    return pd.DataFrame([{"doc_id": d, "entidad_esperada": e, "etiqueta": t,
                          "detectada": (d, e, t) in detectadas} for d, e, t in esperadas])


def graficar_nlp(resultados):
    tonos = resultados["tonos"]
    grupos = tonos.groupby("tipo_documento")[["epica", "sorpresa", "precariedad", "tokens_alfabeticos"]].sum()
    tasas = grupos[list(LEXICO)].div(grupos["tokens_alfabeticos"], axis=0) * 100
    frec = resultados["frecuencias"].groupby("palabra")["frecuencia"].sum().nlargest(12).sort_values()
    with plt.rc_context({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False}):
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), layout="constrained")
        tasas.rename(index={"simulado": "Simulación", "parafrasis_documental": "Paráfrasis documentales"}).plot.bar(
            ax=axes[0], color=["#1c5968", "#d8a14a", "#aa6250"], rot=0)
        axes[0].set_title("Campos léxicos por tipo de texto", fontweight="bold")
        axes[0].set_ylabel("Coincidencias por 100 tokens alfabéticos")
        axes[0].set_xlabel("")
        axes[0].legend(title="Campo semántico", frameon=False)
        frec.plot.barh(ax=axes[1], color="#388579")
        axes[1].set_title("12 palabras frecuentes · corpus combinado", fontweight="bold")
        axes[1].set_xlabel("Frecuencia tras filtrar stopwords")
        axes[1].set_ylabel("")
        fig.suptitle("NLP exploratorio · 3 recreaciones y 2 paráfrasis, sin representatividad histórica", fontsize=13)
        fig.savefig(SALIDA / "analisis_nlp.png", dpi=180, bbox_inches="tight")
    return fig

# %% [markdown]
# ### Resultados, evidencias y control manual
# Las posiciones inicio/fin apuntan al texto limpio guardado, de modo que cada
# entidad puede revisarse. El pequeño control comprueba ocho entidades conocidas
# del corpus simulado; como también participaron en el diseño de reglas, no mide
# generalización. Se mantienen separados los resultados de simulación y paráfrasis.
# %%
if __name__ == "__main__":
    corpus, _ = preparar_corpus()
    resultados_nlp = procesar_corpus(corpus)
    entidades_nlp = resultados_nlp["entidades"]
    control_ner = evaluar_entidades_control(entidades_nlp)
    for nombre, tabla in resultados_nlp.items():
        if isinstance(tabla, pd.DataFrame):
            tabla.to_csv(SALIDA / f"nlp_{nombre}.csv", index=False)
    (SALIDA / "nlp_tokens.json").write_text(json.dumps(resultados_nlp["tokens"], ensure_ascii=False, indent=2), encoding="utf-8")
    control_ner.to_csv(SALIDA / "nlp_control_entidades.csv", index=False)
    mostrar_tabla(entidades_nlp[["doc_id", "entidad", "etiqueta"]])
    print("TONO LÉXICO")
    mostrar_tabla(resultados_nlp["tonos"])
    print("CONTROL NER")
    mostrar_tabla(control_ner)
    figura_nlp = graficar_nlp(resultados_nlp)
    plt.show()
    plt.close(figura_nlp)

# %% [markdown]
# **Conclusión.** Las recreaciones contienen épica, sorpresa y precariedad porque
# se diseñaron para ilustrar esas categorías. El predominio léxico resultante no
# prueba el tono de la prensa de 1928. Las paráfrasis reflejan además decisiones
# de redacción actuales: para estudiar recepción histórica se necesitarían textos
# originales, muestreo de medios, validación manual y revisión de lenguaje racista
# o nacionalista, sin reproducirlo como una valoración propia del análisis.
