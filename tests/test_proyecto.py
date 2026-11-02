"""Controles de errores que alterarían las conclusiones del proyecto."""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tareas.tarea01_ingesta_limpieza import BASE, cargar_datos, limpiar_maraton, normalizar_tiempo, formatear_tiempo, mascara_maraton
from tareas.tarea02_podios_historicos import extraer_podios, COLUMNAS_PODIO
from tareas.tarea04_manuel_plaza_1928 import analizar_1928
from tareas.tarea05_integracion_documental import preparar_corpus, simular_ingesta_documental
from tareas.tarea06_nlp_cronicas import procesar_corpus, evaluar_entidades_control, crear_pipeline_nlp, analizar_lexico
from tareas.tarea07_cronica_historica import generar_cronica_historica
from tareas.tarea08_reflexion_critica import REFLEXION


@pytest.mark.parametrize("valor,esperado", [
    (9203000, 9203), ("9177000", 9177), ("02:33:23", 9203),
    ("02:33:23,4", 9203.4), ("2h 33m 23s", 9203),
    ("2-33:23", 9203), (pd.Timedelta(hours=2, minutes=33, seconds=23), 9203),
])
def test_tiempos_y_unidades(valor, esperado):
    assert normalizar_tiempo(valor) == pytest.approx(esperado)


@pytest.mark.parametrize("valor", [None, pd.NA, np.nan, "", "DNS", "DNF", "DSQ", "02:75:00", "02:30:60", "basura", "-20", "0"])
def test_no_inventar_marcas(valor):
    assert np.isnan(normalizar_tiempo(valor))


def test_unidad_explicita_y_fracciones():
    assert normalizar_tiempo(9203, unidad_numerica="s") == 9203
    with pytest.raises(ValueError):
        normalizar_tiempo(9203, unidad_numerica="adivinar")
    assert formatear_tiempo(10518.4) == "02:55:18.4"
    assert normalizar_tiempo(formatear_tiempo(10518.4)) == pytest.approx(10518.4)


def test_filtrar_athletics_y_genero():
    prueba = pd.DataFrame({"discipline_title": ["Athletics", "Athletics", "Marathon Swimming", "Athletics", "Athletics"],
                          "event_title": ["marathon men", "marathon women", "Marathon - 10 km men", "Men's Marathon", "20km walk men"]})
    assert mascara_maraton(prueba).tolist() == [True, False, False, True, False]


@pytest.fixture(scope="module")
def datos():
    tablas = cargar_datos()
    maraton, limpia, excluidas, auditoria = limpiar_maraton(tablas)
    podios = extraer_podios(maraton, tablas["medals"], BASE / "datos_documentales/suplemento_tokio2020.csv")
    return tablas, maraton, limpia, excluidas, auditoria, podios


def test_cobertura_y_balance_de_filas(datos):
    _, maraton, limpia, excluidas, auditoria, _ = datos
    assert len(maraton) == 2296
    assert len(limpia) == 1560
    assert len(excluidas) == 736
    assert len(limpia) + len(excluidas) == len(maraton)
    assert limpia["Tiempo segundos"].notna().all()
    assert limpia["Tiempo segundos"].gt(0).all()
    assert limpia["slug_game"].nunique() == 28
    assert auditoria["ultimo_anio_edicion"] == 2020
    assert maraton["slug_game"].nunique() == 29
    assert set(excluidas["Motivo exclusión"]) == {"Estado sin clasificación válida (DNF/DNS/DSQ/IRM)", "Marca ausente o formato inválido"}


def test_podios_y_suplemento_no_silencioso(datos):
    tablas, maraton, _, _, _, podios = datos
    assert len(podios) == 87
    assert podios.groupby("Año")["Puesto"].apply(set).map(lambda s: s == {1, 2, 3}).all()
    assert len(podios[COLUMNAS_PODIO].columns) == 6
    assert podios["Tiempo segundos"].notna().all()
    agregados = podios.loc[podios["Complemento documental"]]
    assert len(agregados) == 3
    assert agregados["Tiempo original"].isna().all()
    assert agregados["slug_game"].eq("tokyo-2020").all()
    assert agregados["Año celebración"].eq(2021).all()
    assert agregados["Fuente tiempo"].str.startswith("https://worldathletics.org/").all()
    assert agregados["Tiempo segundos"].tolist() == [7718, 7798, 7800]
    assert agregados["Tiempo timedelta"].dt.total_seconds().tolist() == [7718, 7798, 7800]
    sin_suplemento = extraer_podios(maraton, tablas["medals"])
    assert len(sin_suplemento) == 87
    assert sin_suplemento["Tiempo segundos"].isna().sum() == 3


def test_rechaza_suplemento_contradictorio(datos, tmp_path):
    tablas, maraton, *_ = datos
    sup = pd.read_csv(BASE / "datos_documentales/suplemento_tokio2020.csv")
    sup = sup.iloc[:1].copy()
    sup.loc[:, "slug_game"] = "rio-2016"
    destino = tmp_path / "conflicto.csv"
    sup.to_csv(destino, index=False)
    with pytest.raises(ValueError, match="contradice"):
        extraer_podios(maraton, tablas["medals"], destino)


def test_resultado_exacto_1928(datos):
    podio, stats = analizar_1928(datos[-1])
    assert podio["Tiempo"].tolist() == ["02:32:57", "02:33:23", "02:35:02"]
    assert podio["Diferencia oro segundos"].tolist() == [0, 26, 125]
    assert stats.iloc[0]["Tiempo segundos"] == 9203
    assert stats.iloc[0]["Diferencia oro segundos"] == 26


@pytest.fixture(scope="module")
def nlp_resultados():
    corpus, _ = preparar_corpus()
    return corpus, procesar_corpus(corpus)


def test_procedencia_entidades_y_offsets(nlp_resultados):
    corpus, resultado = nlp_resultados
    assert sum(d["tipo_documento"] == "simulado" for d in corpus) == 3
    assert sum(d["tipo_documento"] == "parafrasis_documental" for d in corpus) == 2
    assert all(d["fuente_url"] is None for d in corpus if d["tipo_documento"] == "simulado")
    textos = {d["doc_id"]: d["texto_limpio"] for d in resultado["tokens"]}
    for fila in resultado["entidades"].itertuples(index=False):
        assert textos[fila.doc_id][fila.inicio:fila.fin] == fila.entidad
    assert evaluar_entidades_control(resultado["entidades"])["detectada"].all()
    assert set(resultado["entidades"]["etiqueta"]) >= {"PER", "LOC", "DATE", "OCUPACION"}
    with pytest.raises(ValueError):
        simular_ingesta_documental("Otro atleta", 1932, "Los Angeles")


def test_negacion_lexica_no_cruza_oraciones():
    nlp = crear_pipeline_nlp()
    resumen, evidencias = analizar_lexico(nlp("No fue una hazaña. Sorpresa y gloria."))
    assert resumen["epica"] == 1
    assert resumen["sorpresa"] == 1
    assert evidencias[0]["negado"] is True


def test_cronica_no_toma_simulacion_como_prueba(datos, nlp_resultados):
    _, stats = analizar_1928(datos[-1])
    entidades = nlp_resultados[1]["entidades"]
    texto = generar_cronica_historica(stats, entidades)
    assert all(s in texto for s in ["26 segundos", "02:33:23", "suplementero", "Parque Cousiño", "https://vergara240.udp.cl/"])
    sin_fuentes = entidades.loc[entidades["tipo_documento"].eq("simulado")]
    incompleto = generar_cronica_historica(stats, sin_fuentes)
    assert "No hay entidades documentales suficientes" in incompleto
    assert "suplementero" not in incompleto
    erroneo = stats.copy()
    erroneo["Diferencia oro segundos"] = -26
    with pytest.raises(ValueError):
        generar_cronica_historica(erroneo, entidades)
    assert len(REFLEXION.splitlines()) <= 15
