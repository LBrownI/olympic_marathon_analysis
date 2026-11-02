# %% [markdown]
# ## 1. Ingesta, limpieza y selección de la maratón masculina
# Leemos los cuatro CSV como texto para conservar códigos y valores originales.
# El filtro exige Athletics y un nombre exacto de prueba: así excluimos natación
# en aguas abiertas, otras distancias y la maratón femenina. El año es el de la
# edición; Tokio 2020 se celebró en 2021. Ciudad significa sede de la edición,
# no necesariamente el lugar efectivo del circuito (Sapporo en Tokio 2020).
# %%
from pathlib import Path
from datetime import timedelta
import hashlib
import json
import re
import unicodedata
import numpy as np
import pandas as pd


def localizar_proyecto():
    """Localiza el proyecto desde su carpeta, U2, U1 o al ejecutar un módulo."""
    candidatos = [Path.cwd(), Path.cwd() / "U2", Path.cwd().parent / "U2",
                  Path.cwd() / "olympic_marathon_analysis",
                  Path.cwd() / "U2" / "olympic_marathon_analysis",
                  Path.cwd().parent / "U2" / "olympic_marathon_analysis"]
    if "__file__" in globals():
        candidatos.insert(0, Path(__file__).resolve().parent.parent)
    for candidato in candidatos:
        if (candidato / "SetDatos" / "olympic_results.csv").is_file():
            return candidato.resolve()
    raise FileNotFoundError("Abra el notebook desde olympic_marathon_analysis, junto a SetDatos/.")


BASE = localizar_proyecto()
SALIDA = BASE / "resultados"
SALIDA.mkdir(exist_ok=True)


def normalizar_texto(texto):
    texto = unicodedata.normalize("NFKD", str(texto).casefold())
    return " ".join("".join(c for c in texto if not unicodedata.combining(c)).split())


def mascara_maraton(df):
    return (
        df["discipline_title"].map(normalizar_texto).eq("athletics")
        & df["event_title"].map(normalizar_texto).isin(["marathon men", "men's marathon"])
    )


def cargar_datos(carpeta=None):
    carpeta = Path(carpeta) if carpeta else BASE / "SetDatos"
    tablas = {
        nombre: pd.read_csv(carpeta / f"olympic_{nombre}.csv", dtype="string")
        for nombre in ("athletes", "results", "hosts", "medals")
    }
    requeridas = {
        "results": {"discipline_title", "event_title", "slug_game", "athlete_url",
                    "athlete_full_name", "country_name", "country_3_letter_code",
                    "rank_position", "medal_type", "value_unit", "value_type"},
        "hosts": {"game_slug", "game_year", "game_name", "game_start_date", "game_season"},
        "athletes": {"athlete_url", "athlete_full_name", "athlete_year_birth"},
        "medals": {"discipline_title", "event_title", "slug_game", "medal_type",
                   "athlete_full_name", "country_3_letter_code"},
    }
    for nombre, columnas in requeridas.items():
        faltan = columnas - set(tablas[nombre])
        if faltan:
            raise ValueError(f"{nombre}: faltan columnas {sorted(faltan)}")
    return tablas

# %% [markdown]
# ### Normalización de las marcas
# En estos CSV, value_unit contiene el valor numérico en **milisegundos**;
# value_type=TIME identifica tiempos, pero no declara su escala. Se comprueba la
# escala con el podio de 1928: 9 203 000 / 1000 = 9203 s = 02:33:23.
# La función también acepta HH:MM:SS, fracciones y timedelta. La unidad numérica
# es explícita: nunca se infiere por la magnitud. No imputamos abandonos ni marcas
# faltantes. Conservamos esas filas en una tabla de exclusiones con su motivo.
# %%
def normalizar_tiempo(valor, unidad_numerica="ms"):
    """Devuelve segundos o NaN; numéricos en ms (dataset) o s, sin adivinar."""
    if unidad_numerica not in {"ms", "s"}:
        raise ValueError("unidad_numerica debe ser 'ms' o 's'")
    if valor is None or pd.isna(valor):
        return np.nan
    if isinstance(valor, (pd.Timedelta, timedelta)):
        segundos = valor.total_seconds()
    else:
        texto = str(valor).strip().upper().replace(",", ".")
        if texto in {"", "DNF", "DNS", "DSQ", "DQ", "DQB", "NM", "N/A", "NAN", "-"}:
            return np.nan
        if re.fullmatch(r"\d+(?:\.\d+)?", texto):
            segundos = float(texto) / (1000 if unidad_numerica == "ms" else 1)
        else:
            texto = re.sub(r"\s+", "", texto)
            texto = re.sub(r"H|M", ":", texto).removesuffix("S")
            texto = re.sub(r"^(\d+)-(\d{2}:)", r"\1:\2", texto)
            match = re.fullmatch(r"(\d{1,2}):(\d{2}):(\d{2}(?:\.\d+)?)", texto)
            if not match:
                return np.nan
            horas, minutos, seg = map(float, match.groups())
            if minutos >= 60 or seg >= 60:
                return np.nan
            segundos = horas * 3600 + minutos * 60 + seg
    return round(float(segundos), 6) if np.isfinite(segundos) and segundos > 0 else np.nan


def formatear_tiempo(segundos):
    """HH:MM:SS.mmm sin perder décimas históricas; vacío si no hay marca."""
    if pd.isna(segundos):
        return "Sin marca"
    milisegundos = round(float(segundos) * 1000)
    horas, resto = divmod(milisegundos, 3_600_000)
    minutos, resto = divmod(resto, 60_000)
    seg, fraccion = divmod(resto, 1000)
    sufijo = f".{fraccion:03d}".rstrip("0") if fraccion else ""
    return f"{horas:02d}:{minutos:02d}:{seg:02d}{sufijo}"


def mostrar_tabla(tabla):
    """Tabla HTML en Jupyter; texto legible al ejecutar los archivos Python."""
    try:
        from IPython import get_ipython
        from IPython.display import display
        if get_ipython() is not None:
            display(tabla)
            return
    except ImportError:
        pass
    print(tabla.to_string(index=False))


def limpiar_maraton(tablas):
    originales = tablas["results"].loc[mascara_maraton(tablas["results"])].copy()
    df = originales.drop_duplicates().copy()
    hosts = tablas["hosts"].rename(columns={"game_slug": "slug_game"})
    df = df.merge(hosts, on="slug_game", how="left", validate="many_to_one", indicator=True)
    if not df["_merge"].eq("both").all() or not df["game_season"].eq("Summer").all():
        raise ValueError("Hay resultados sin sede o fuera de Juegos de Verano")
    df = df.drop(columns="_merge")
    # Solo identificadores no nulos: pandas puede unir nulos entre sí.
    atletas = tablas["athletes"].dropna(subset=["athlete_url"])
    atletas = atletas.loc[atletas["athlete_url"].isin(df["athlete_url"].dropna())]
    # Se aceptan duplicados exactos; los identificadores contradictorios fallan.
    atletas = atletas.drop_duplicates()
    if atletas["athlete_url"].duplicated().any():
        raise ValueError("Identificadores de atletas con fichas contradictorias")
    atletas = atletas.rename(columns={"athlete_full_name": "nombre_ficha"})
    df = df.merge(atletas[["athlete_url", "nombre_ficha", "athlete_year_birth"]],
                  on="athlete_url", how="left", validate="many_to_one")
    df["athlete_full_name"] = df["athlete_full_name"].fillna(df["nombre_ficha"])
    df["Año"] = pd.to_numeric(df["game_year"], errors="raise").astype(int)
    df["Año celebración"] = pd.to_datetime(df["game_start_date"], utc=True).dt.year
    df["Ciudad"] = df["game_name"].str.replace(r"\s+\d{4}$", "", regex=True)
    df["Tiempo original"] = df["value_unit"]
    df["Tiempo segundos"] = df["value_unit"].map(normalizar_tiempo)
    df["Tiempo"] = df["Tiempo segundos"].map(formatear_tiempo)
    df["Tiempo timedelta"] = pd.to_timedelta(df["Tiempo segundos"], unit="s")
    rango = pd.to_numeric(df["rank_position"], errors="coerce")
    estado_invalido = rango.isna() | df["value_type"].eq("IRM").fillna(False)
    df["Motivo exclusión"] = np.select(
        [estado_invalido.to_numpy(dtype=bool), df["Tiempo segundos"].isna()],
        ["Estado sin clasificación válida (DNF/DNS/DSQ/IRM)", "Marca ausente o formato inválido"],
        default="",
    )
    validos = df.loc[df["Motivo exclusión"].eq("")].copy()
    excluidos = df.loc[df["Motivo exclusión"].ne("")].copy()
    auditoria = {
        "filas_fuentes": {k: len(v) for k, v in tablas.items()},
        "registros_maraton_originales": len(originales),
        "duplicados_exactos_eliminados": len(originales) - len(df),
        "ediciones_maraton": int(df["slug_game"].nunique()),
        "primer_anio": int(df["Año"].min()), "ultimo_anio_edicion": int(df["Año"].max()),
        "marcas_validas_originales": len(validos), "registros_excluidos": len(excluidos),
        "motivos": excluidos["Motivo exclusión"].value_counts().to_dict(),
        "sin_ficha_atleta": int(df["nombre_ficha"].isna().sum()),
        "urls_atletas_duplicadas_fuente_global": int(tablas["athletes"]["athlete_url"].duplicated().sum()),
        "unidad_numerica": "milisegundos", "division_a_segundos": 1000,
    }
    if len(validos) + len(excluidos) != len(df):
        raise AssertionError("La auditoría no conserva el total de filas")
    return df, validos, excluidos, auditoria

# %% [markdown]
# ### Resultado y control de cobertura
# Mostramos tamaños reales y algunos ejemplos de conversión. Los CSV originales
# quedan intactos; resultados/ contiene las tablas derivadas y la auditoría.
# %%
if __name__ == "__main__":
    tablas = cargar_datos()
    maraton, maraton_limpia, exclusiones, auditoria = limpiar_maraton(tablas)
    maraton_limpia.to_csv(SALIDA / "maraton_limpia.csv", index=False)
    exclusiones.to_csv(SALIDA / "registros_excluidos.csv", index=False)
    (SALIDA / "auditoria_ingesta.json").write_text(json.dumps(auditoria, indent=2, ensure_ascii=False), encoding="utf-8")
    hashes_fuentes = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in (BASE / "SetDatos").glob("*.csv")}
    (SALIDA / "sha256_datasets.json").write_text(json.dumps(hashes_fuentes, indent=2), encoding="utf-8")
    print(json.dumps(auditoria, indent=2, ensure_ascii=False))
    mostrar_tabla(maraton_limpia[["Año", "athlete_full_name", "Tiempo original", "Tiempo segundos", "Tiempo"]].head())

# %% [markdown]
# **Conclusión.** La cobertura histórica se determina a partir de los archivos,
# no de la fecha actual. Tokio 2020 es la última edición de verano disponible;
# París 2024 no está en esta copia. Una marca faltante no significa que el atleta
# no haya terminado: hay que distinguir calidad del dato y estado deportivo.
