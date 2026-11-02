# %% [markdown]
# ## 7. Data-to-Text: estadística y contexto en una crónica trazable
# La función solicitada recibe el DataFrame estadístico y las entidades del NLP.
# Valida identidad, edición y magnitudes; los números salen del DataFrame.
# Solo usa paráfrasis documentales para afirmaciones de contexto histórico.
# Si faltan entidades, lo declara en vez de rellenar una biografía de memoria.
# Es generación por plantilla auditable: no depende de una API ni de un LLM.
# %%
from tareas.tarea01_ingesta_limpieza import BASE, SALIDA, cargar_datos, limpiar_maraton, formatear_tiempo, normalizar_texto
from tareas.tarea02_podios_historicos import extraer_podios
from tareas.tarea04_manuel_plaza_1928 import analizar_1928
from tareas.tarea05_integracion_documental import preparar_corpus
from tareas.tarea06_nlp_cronicas import procesar_corpus
import numpy as np
import pandas as pd


def generar_cronica_historica(df_stats, entidades_nlp):
    """Integra cifras y entidades documentadas del caso Plaza sin inventar hechos."""
    requeridas = {"Atleta", "Año", "Ciudad", "Medalla", "Tiempo segundos", "Diferencia oro segundos"}
    if not isinstance(df_stats, pd.DataFrame) or not requeridas.issubset(df_stats.columns):
        raise ValueError(f"df_stats debe contener {sorted(requeridas)}")
    seleccion = df_stats.loc[df_stats["Atleta"].map(normalizar_texto).str.contains(r"manuel.*plaza", regex=True)
                             & df_stats["Año"].eq(1928)]
    if len(seleccion) != 1:
        raise ValueError("Se requiere una única observación de Manuel Plaza en 1928")
    fila = seleccion.iloc[0]
    tiempo, diferencia = float(fila["Tiempo segundos"]), float(fila["Diferencia oro segundos"])
    if not np.isfinite([tiempo, diferencia]).all() or tiempo <= 0 or diferencia < 0 or diferencia >= tiempo:
        raise ValueError("Tiempo o diferencia inválidos")
    if fila["Medalla"] != "Plata" or normalizar_texto(fila["Ciudad"]) != "amsterdam":
        raise ValueError("Los metadatos no corresponden al caso de estudio")
    columnas_ent = {"entidad", "etiqueta", "tipo_documento", "fuente_url", "oracion"}
    if not isinstance(entidades_nlp, pd.DataFrame) or not columnas_ent.issubset(entidades_nlp.columns):
        raise ValueError("Se requieren entidades NLP con tipo documental y procedencia")
    documentadas = entidades_nlp.loc[entidades_nlp["tipo_documento"].eq("parafrasis_documental")
                                    & entidades_nlp["fuente_url"].notna()].copy()
    entidad_norm = documentadas["entidad"].map(normalizar_texto)
    def presente(nombre, etiqueta):
        return bool((entidad_norm.eq(normalizar_texto(nombre)) & documentadas["etiqueta"].eq(etiqueta)).any())
    # Requerimos que cada contexto provenga de un documento que nombra al atleta.
    ids_atleta = set(documentadas.loc[entidad_norm.isin(["manuel plaza", "manuel plaza reyes"]), "doc_id"]) if "doc_id" in documentadas else set()
    if ids_atleta:
        documentadas = documentadas.loc[documentadas["doc_id"].isin(ids_atleta)]
        entidad_norm = documentadas["entidad"].map(normalizar_texto)
    else:
        documentadas = documentadas.iloc[0:0]
        entidad_norm = documentadas["entidad"].map(normalizar_texto)
    cronica = (
        f"En Ámsterdam {int(fila['Año'])}, Manuel Plaza Reyes, representante de Chile, "
        f"obtuvo la medalla de {fila['Medalla'].lower()} de la maratón con "
        f"{formatear_tiempo(tiempo)} ({tiempo:g} segundos). El oro se resolvió en "
        f"{formatear_tiempo(tiempo - diferencia)}: la separación exacta fue de {diferencia:g} segundos."
    )
    contextos = []
    if presente("suplementero", "OCUPACION") and presente("Santiago", "LOC"):
        contextos.append("Las fuentes documentales lo sitúan trabajando como suplementero en Santiago")
    if presente("Parque Cousiño", "LOC"):
        contextos.append("vinculan su preparación con el antiguo Parque Cousiño")
    if contextos:
        cronica += "\n\n" + "; también ".join(contextos) + ". "
        cronica += "Ese contexto permite leer la distancia al oro junto a una trayectoria de trabajo y entrenamiento que la tabla de resultados no registra."
    else:
        cronica += "\n\nNo hay entidades documentales suficientes para reconstruir el contexto social; no se completan esos vacíos con la simulación."
    cronica += (
        "\n\nEl tiempo mide el resultado, pero no explica por sí solo sus causas. "
        "Las entidades fueron reconocidas con reglas y requieren revisión histórica. "
        "Los fragmentos simulados son material didáctico, no testimonios de 1928. "
        "El centenario 1928–2028 es un horizonte de memoria, no una observación futura del dataset."
    )
    urls = sorted(set(documentadas["fuente_url"].dropna()))
    if urls:
        cronica += "\n\nContexto documental: " + "; ".join(urls)
    return cronica

# %% [markdown]
# ### Crónica generada
# La salida siguiente se exporta como texto. Modificar una marca validada cambia
# la narración; quitar el contexto documentado produce una declaración de ausencia.
# De este modo se separa lo medido, lo documentado y lo simulado.
# %%
if __name__ == "__main__":
    tablas = cargar_datos()
    maraton, _, _, _ = limpiar_maraton(tablas)
    podios = extraer_podios(maraton, tablas["medals"], BASE / "datos_documentales/suplemento_tokio2020.csv")
    podio_1928, df_stats = analizar_1928(podios)
    corpus, _ = preparar_corpus()
    resultados_nlp = procesar_corpus(corpus)
    entidades_nlp = resultados_nlp["entidades"]
    cronica = generar_cronica_historica(df_stats, entidades_nlp)
    print(cronica)
    (SALIDA / "cronica_historica.txt").write_text(cronica, encoding="utf-8")

# %% [markdown]
# **Conclusión.** La síntesis une 26 segundos de diferencia con lugares y oficio,
# conservando el respaldo documental. No convierte una correlación en causa ni
# una recreación literaria en archivo histórico. La plantilla tiene un alcance
# deliberado: el caso de Manuel Plaza en 1928, con datos previamente validados.
