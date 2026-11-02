# %% [markdown]
# ## 2. Podios históricos: una fila por medallista y edición
# Se seleccionan medallas adjudicadas, sin ordenar por tiempo para reinventar el
# resultado oficial (una descalificación puede alterar el podio). Contrastamos
# results con medals por edición, medalla y país. El suplemento local verificado
# en World Athletics completa solo las tres marcas ausentes de Tokio 2020;
# conserva Tiempo original nulo e identifica la procedencia de cada marca.
# %%
from tareas.tarea01_ingesta_limpieza import BASE, SALIDA, cargar_datos, limpiar_maraton, mascara_maraton, normalizar_tiempo, formatear_tiempo, mostrar_tabla
import numpy as np
import pandas as pd

MEDALLAS = {"GOLD": "Oro", "SILVER": "Plata", "BRONZE": "Bronce"}
PUESTOS = {"GOLD": 1, "SILVER": 2, "BRONZE": 3}
COLUMNAS_PODIO = ["Año", "Ciudad", "Puesto (Medalla)", "Atleta", "País/Equipo", "Tiempo"]


def extraer_podios(maraton, tabla_medallas, suplemento=None):
    df = maraton.loc[maraton["medal_type"].isin(MEDALLAS)].copy()
    clave = ["slug_game", "medal_type", "country_3_letter_code"]
    contraste = tabla_medallas.loc[mascara_maraton(tabla_medallas), clave].drop_duplicates()
    control = df.merge(contraste, on=clave, how="outer", indicator=True, validate="one_to_one")
    if not control["_merge"].eq("both").all():
        raise ValueError("Los podios de results y medals no coinciden")
    df["Fuente tiempo"] = "SetDatos/olympic_results.csv (ms)"
    df["Complemento documental"] = False
    if suplemento is not None:
        sup = pd.read_csv(suplemento, dtype="string")
        if sup.duplicated(clave).any():
            raise ValueError("Suplemento con claves duplicadas")
        correspondencia = sup.merge(df[clave], on=clave, how="left", indicator=True, validate="one_to_one")
        if not correspondencia["_merge"].eq("both").all():
            raise ValueError("El suplemento contiene medallistas ajenos al dataset")
        sup = sup.rename(columns={"tiempo": "tiempo_documental", "athlete_full_name": "nombre_documental"})
        df = df.merge(sup[clave + ["nombre_documental", "tiempo_documental", "fuente_url"]],
                      on=clave, how="left", validate="one_to_one")
        documentado = df["tiempo_documental"].notna()
        if not df.loc[documentado, "athlete_full_name"].eq(df.loc[documentado, "nombre_documental"]).all():
            raise ValueError("El nombre documental no coincide con el medallista")
        nuevos = df["tiempo_documental"].map(normalizar_tiempo)
        conflicto = documentado & df["Tiempo segundos"].notna() & ~np.isclose(df["Tiempo segundos"], nuevos, equal_nan=True)
        if conflicto.any():
            raise ValueError("El suplemento contradice una marca original")
        completar = df["Tiempo segundos"].isna() & nuevos.notna()
        df.loc[completar, "Tiempo segundos"] = nuevos.loc[completar]
        df.loc[completar, "Fuente tiempo"] = df.loc[completar, "fuente_url"]
        df.loc[completar, "Complemento documental"] = True
    df["Tiempo"] = df["Tiempo segundos"].map(formatear_tiempo)
    df["Tiempo timedelta"] = pd.to_timedelta(df["Tiempo segundos"], unit="s")
    df["Puesto"] = df["medal_type"].map(PUESTOS)
    df["Medalla"] = df["medal_type"].map(MEDALLAS)
    rango = pd.to_numeric(df["rank_position"], errors="coerce")
    if not rango.eq(df["Puesto"]).all():
        raise ValueError("Posiciones y medallas incompatibles")
    df["Puesto (Medalla)"] = df["Puesto"].astype(str) + " (" + df["Medalla"] + ")"
    df = df.rename(columns={"athlete_full_name": "Atleta", "country_name": "País/Equipo"})
    df = df.sort_values(["Año", "Puesto"]).reset_index(drop=True)
    cobertura = df.groupby("slug_game")["medal_type"].agg(set)
    if not cobertura.map(lambda x: x == set(MEDALLAS)).all() or len(df) != 3 * maraton["slug_game"].nunique():
        raise ValueError("Se esperaba exactamente un oro, una plata y un bronce por edición")
    return df

# %% [markdown]
# ### Tabla completa y trazabilidad
# Exportamos una tabla con las seis columnas solicitadas y otra con segundos,
# posición, país original y fuente. Sin suplemento, los 87 medallistas se
# conservan, pero las tres marcas de Tokio figuran como Sin marca.
# %%
if __name__ == "__main__":
    tablas = cargar_datos()
    maraton, _, _, _ = limpiar_maraton(tablas)
    podios = extraer_podios(maraton, tablas["medals"], BASE / "datos_documentales/suplemento_tokio2020.csv")
    podios[COLUMNAS_PODIO].to_csv(SALIDA / "podios_historicos.csv", index=False)
    podios.to_csv(SALIDA / "podios_trazabilidad.csv", index=False)
    mostrar_tabla(podios[COLUMNAS_PODIO])
    print(f"\n{len(podios)} medallistas; {podios['Año'].nunique()} ediciones; "
          f"{podios['Complemento documental'].sum()} tiempos documentales; "
          f"{podios['Tiempo segundos'].isna().sum()} tiempos ausentes.")

# %% [markdown]
# **Conclusión.** Los podios cubren Atenas 1896–Tokio 2020. El año de edición se
# mantiene como 2020 para enlazar los CSV; Año celebración conserva 2021. Los
# nombres y países siguen el registro de Kaggle: no se reasignan nacionalidades
# históricas con criterios actuales. El suplemento no amplía la serie a 2024.
