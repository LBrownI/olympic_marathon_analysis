# %% [markdown]
# ## 3. Evolución del oro y brechas entre ediciones
# Dibujamos minutos en el eje vertical con etiquetas HH:MM:SS. Distinguimos las
# primeras ediciones, cuya distancia no fue uniforme, y resaltamos 1928.
# La estandarización en 42,195 km data de 1921 (World Athletics): por ello se
# informa además la variación desde 1924. No estimamos efectos causales de
# zapatillas, nutrición o entrenamiento con una serie que no mide esas variables.
# %%
from tareas.tarea01_ingesta_limpieza import BASE, SALIDA, cargar_datos, limpiar_maraton, formatear_tiempo
from tareas.tarea02_podios_historicos import extraer_podios
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator


def analizar_evolucion(podios):
    oros = podios.loc[podios["Puesto"].eq(1)].sort_values("Año").copy()
    if oros["Tiempo segundos"].isna().any():
        raise ValueError("Hay oros sin marca: complete o declare su exclusión antes de comparar")
    oros["Cambio segundos"] = oros["Tiempo segundos"].diff()
    oros["Edición anterior"] = oros["Año"].shift().astype("Int64")
    primero, ultimo = oros.iloc[0], oros.iloc[-1]
    comparable = oros.loc[oros["Año"].ge(1924)].iloc[0]
    salto = oros.loc[oros["Cambio segundos"].idxmin()]
    retroceso = oros.loc[oros["Cambio segundos"].idxmax()]
    mejor = oros.loc[oros["Tiempo segundos"].idxmin()]
    mejora = primero["Tiempo segundos"] - ultimo["Tiempo segundos"]
    mejora_comparable = comparable["Tiempo segundos"] - ultimo["Tiempo segundos"]
    texto = (
        f"Entre {int(primero['Año'])} y {int(ultimo['Año'])}, el oro pasa de "
        f"{primero['Tiempo']} a {ultimo['Tiempo']}: {mejora / 60:.2f} minutos menos "
        f"({100 * mejora / primero['Tiempo segundos']:.1f}%). "
        f"Desde 1924, después de la estandarización, la reducción es de "
        f"{mejora_comparable / 60:.2f} minutos "
        f"({100 * mejora_comparable / comparable['Tiempo segundos']:.1f}%). "
        f"El descenso más pronunciado entre ediciones consecutivas observadas ocurre en "
        f"{int(salto['Edición anterior'])}–{int(salto['Año'])} "
        f"({abs(salto['Cambio segundos']) / 60:.2f} min); el mayor aumento, en "
        f"{int(retroceso['Edición anterior'])}–{int(retroceso['Año'])} "
        f"({retroceso['Cambio segundos'] / 60:.2f} min). "
        f"La marca de oro más rápida de esta copia es {mejor['Tiempo']} en {int(mejor['Año'])}. "
        "La trayectoria mejora a largo plazo, pero no de forma monótona: las oscilaciones "
        "impiden interpretar cada década como un progreso uniforme. Las distancias previas "
        "a 1921 limitan la comparación inicial; recorrido, clima y altitud también son "
        "factores plausibles, pero no están medidos aquí. No se puede atribuir un salto "
        "a nutrición o tecnología sin evidencia adicional y controles de contexto. "
        "Son tiempos de campeones olímpicos, no una serie de récords mundiales ni del corredor promedio."
    )
    return oros, texto


def graficar_evolucion(podios):
    oros, _ = analizar_evolucion(podios)
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False}):
        fig, (ax, ax2) = plt.subplots(2, 1, figsize=(13, 8.8), sharex=True,
                                      gridspec_kw={"height_ratios": [3, 1.2]}, layout="constrained")
        fig.suptitle("Maratón olímpica masculina · evolución del tiempo ganador", fontsize=19, fontweight="bold")
        ax.set_title("29 ediciones disponibles · Atenas 1896–Tokio 2020 (celebrado en 2021)", loc="left", color="#596776")
        ax.axvspan(1894, 1921, color="#e7c77b", alpha=.25, label="Distancias no uniformes antes de 1921")
        ax.plot(oros["Año"], oros["Tiempo segundos"] / 60, color="#1c5968", lw=2, marker="o", ms=5)
        plaza = oros.loc[oros["Año"].eq(1928)].iloc[0]
        ax.scatter([1928], [plaza["Tiempo segundos"] / 60], s=110, color="#cb6632", zorder=4)
        ax.annotate(f"Ámsterdam 1928\nOro {plaza['Tiempo']}", (1928, plaza["Tiempo segundos"] / 60),
                    xytext=(1940, 172), arrowprops={"arrowstyle": "->", "color": "#cb6632"}, color="#963e18")
        for anio, desplazamiento in [(1904, (8, 5)), (2008, (-100, 45)), (2020, (-25, 16))]:
            fila = oros.loc[oros["Año"].eq(anio)]
            if not fila.empty:
                fila = fila.iloc[0]
                ax.annotate(f"{anio} · {fila['Tiempo']}", (anio, fila["Tiempo segundos"] / 60),
                            xytext=desplazamiento, textcoords="offset points", fontsize=9,
                            bbox={"facecolor": "white", "edgecolor": "none", "alpha": .85, "pad": 2})
        documental = oros.loc[oros["Complemento documental"]]
        ax.scatter(documental["Año"], documental["Tiempo segundos"] / 60, marker="D", s=80,
                   color="#9566a7", label="Marca completada con World Athletics", zorder=5)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: formatear_tiempo(x * 60)))
        ax.set_ylabel("Tiempo de llegada (menor = más rápido)")
        ax.grid(axis="y", alpha=.18)
        ax.legend(loc="upper right", frameon=False, fontsize=9)
        cambios = oros.dropna(subset=["Cambio segundos"])
        colores = np.where(cambios["Cambio segundos"].lt(0), "#388579", "#c88052")
        ax2.bar(cambios["Año"], cambios["Cambio segundos"] / 60, width=2.3, color=colores)
        ax2.axhline(0, color="#66737d", lw=.8)
        ax2.set_ylabel("Cambio (min)\nvs. edición anterior")
        ax2.set_xlabel("Año nominal de la edición · los intervalos siguen los años reales de la serie")
        ax2.xaxis.set_major_locator(MultipleLocator(8))
        ax2.grid(axis="y", alpha=.18)
        ax2.set_xlim(1893, 2024)
        fig.savefig(SALIDA / "evolucion_oro.png", dpi=180, bbox_inches="tight")
    return fig

# %% [markdown]
# ### Lectura del gráfico
# Los cambios negativos indican un oro más rápido que en la edición anterior
# disponible; no son cambios anuales. Las guerras generan intervalos sin Juegos,
# no observaciones faltantes para interpolar. El texto siguiente se calcula con
# los resultados, para que cada conclusión numérica tenga respaldo reproducible.
# %%
if __name__ == "__main__":
    tablas = cargar_datos()
    maraton, _, _, _ = limpiar_maraton(tablas)
    podios = extraer_podios(maraton, tablas["medals"], BASE / "datos_documentales/suplemento_tokio2020.csv")
    oros, conclusion_evolucion = analizar_evolucion(podios)
    oros[["Año", "Tiempo", "Cambio segundos", "Edición anterior"]].to_csv(SALIDA / "evolucion_oro.csv", index=False)
    figura_evolucion = graficar_evolucion(podios)
    plt.show()
    plt.close(figura_evolucion)
    print(conclusion_evolucion)
    (SALIDA / "conclusion_evolucion.txt").write_text(conclusion_evolucion, encoding="utf-8")

# %% [markdown]
# **Fuente de contexto:** [World Athletics, Marathon](https://worldathletics.org/disciplines/race-walks/marathon).
# La asociación temporal no identifica una causa. Aislar una mejora tecnológica
# requeriría variables de equipamiento y condiciones, además de un diseño comparativo.
