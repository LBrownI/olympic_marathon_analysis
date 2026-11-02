# %% [markdown]
# ## 4. Ámsterdam 1928: podio y diferencia exacta
# Filtramos el podio generado automáticamente. Conservamos los nombres originales
# y añadimos una presentación legible para los tres atletas del enunciado.
# El cálculo usa segundos numéricos sin redondear previamente. Oro, plata y
# bronce se presentan con sus medallas correctas.
# %%
from tareas.tarea01_ingesta_limpieza import BASE, SALIDA, cargar_datos, limpiar_maraton, mostrar_tabla
from tareas.tarea02_podios_historicos import extraer_podios
import pandas as pd


def analizar_1928(podios):
    podio = podios.loc[podios["slug_game"].eq("amsterdam-1928")].sort_values("Puesto").copy()
    if len(podio) != 3 or set(podio["Puesto"]) != {1, 2, 3}:
        raise ValueError("No hay un podio completo para Ámsterdam 1928")
    plaza = podio.loc[podio["Atleta"].str.contains("Manuel.*PLAZA", case=False, regex=True, na=False)]
    if len(plaza) != 1 or plaza.iloc[0]["Medalla"] != "Plata":
        raise ValueError("No se identifica de forma unívoca la plata de Manuel Plaza")
    if podio["Tiempo segundos"].isna().any():
        raise ValueError("Faltan marcas para calcular la diferencia")
    oro = float(podio.loc[podio["Puesto"].eq(1), "Tiempo segundos"].iloc[0])
    podio["Diferencia oro segundos"] = podio["Tiempo segundos"] - oro
    if podio["Diferencia oro segundos"].lt(0).any():
        raise ValueError("Hay marcas inconsistentes con el orden de 1928")
    nombres = {1: "Boughera El Ouafi", 2: "Manuel Plaza Reyes", 3: "Martti Marttelin"}
    paises = {1: "Francia", 2: "Chile", 3: "Finlandia"}
    podio["Atleta presentación"] = podio["Puesto"].map(nombres)
    podio["País presentación"] = podio["Puesto"].map(paises)
    estadisticas = podio.loc[podio["Puesto"].eq(2)].copy()
    return podio, estadisticas

# %% [markdown]
# ### Resultado cuantitativo
# 02:33:23 = 9203 s; 02:32:57 = 9177 s; por tanto, 9203 − 9177 = 26 s.
# La cercanía en tiempo no demuestra un error de recorrido ni que Plaza habría
# ganado bajo otras condiciones: esas hipótesis necesitan evidencia documental.
# %%
if __name__ == "__main__":
    tablas = cargar_datos()
    maraton, _, _, _ = limpiar_maraton(tablas)
    podios = extraer_podios(maraton, tablas["medals"], BASE / "datos_documentales/suplemento_tokio2020.csv")
    podio_1928, df_stats = analizar_1928(podios)
    columnas_1928 = ["Medalla", "Atleta presentación", "País presentación", "Tiempo", "Diferencia oro segundos"]
    mostrar_tabla(podio_1928[columnas_1928])
    print(f"\nManuel Plaza quedó a {df_stats.iloc[0]['Diferencia oro segundos']:g} segundos del oro.")
    podio_1928.to_csv(SALIDA / "podio_1928.csv", index=False)
    df_stats.to_csv(SALIDA / "estadisticas_plaza.csv", index=False)

# %% [markdown]
# **Conclusión.** Los datos confirman 26 segundos entre oro y plata, y 125 entre
# oro y bronce. La relevancia nacional de la plata se documenta además en el
# [registro del Comité Olímpico de Chile](https://www.coch.cl/wp-content/uploads/2018/01/medallistas-olimpicos5.pdf).
