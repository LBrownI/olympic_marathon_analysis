# %% [markdown]
# ## 8. Reflexión crítica: Big Data, NLP e historia (máximo 15 líneas)
# El ensayo usa doce líneas explícitas. Distingue la perspectiva histórica del
# volumen real de estos archivos y trata 2028 como centenario, no como datos
# observados ni como un hecho que ya ocurrió.
# %%
from tareas.tarea01_ingesta_limpieza import SALIDA

REFLEXION = """El análisis tabular sitúa a Manuel Plaza en una serie histórica y mide sus 26 segundos de distancia al oro.
Esa precisión permite comparar ediciones, pero no reconstruye por sí sola las condiciones sociales del atleta.
El NLP organiza personas, lugares y vocabulario para vincular resultados con documentos y testimonios.
En este caso, Santiago, el oficio de suplementero y el Parque Cousiño aportan una escala humana al podio.
La lectura documental permite además contrastar relatos y preguntar qué memorias materiales se conservan.
Entre 1928 y el centenario de 2028 transcurren cien años: digitalizar facilita acceso, no elimina vacíos históricos.
Integrar tablas y textos aporta variedad y trazabilidad, dos retos de Big Data más relevantes aquí que el volumen.
Los CSV locales son manejables en memoria; llamarlos Big Data no demuestra procesamiento distribuido.
Las entidades y los conteos léxicos orientan la lectura, pero no prueban causas ni representan toda la prensa.
Un corpus simulado sirve para verificar un método; nunca acredita cómo se narró realmente el triunfo.
Las fuentes retrospectivas también seleccionan recuerdos y deben distinguirse de documentos contemporáneos.
El valor agregado es una explicación verificable y contextual, con incertidumbres visibles y sin sustituir al historiador."""

if __name__ == "__main__":
    if len(REFLEXION.splitlines()) > 15:
        raise AssertionError("La reflexión excede las 15 líneas")
    print(REFLEXION)
    (SALIDA / "reflexion_critica.txt").write_text(REFLEXION + "\n", encoding="utf-8")
