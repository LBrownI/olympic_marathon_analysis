# Proyecto de maratón olímpica y Manuel Plaza

La entrega principal es **[proyecto_maraton_olimpica_manuel_plaza.ipynb](proyecto_maraton_olimpica_manuel_plaza.ipynb)**.
Incluye las ocho tareas, código visible, tablas, gráficos, un **ÍNDICE DE
CONTENIDOS** con enlaces y explicaciones previas a cada celda. Los resultados
principales se acompañan de una interpretación posterior, siguiendo la estructura
de informe del notebook de Netflix de la Unidad 1. Se conserva el README original
como pauta de evaluación.

## Archivos de trabajo

| Tarea | Archivo Python | Producto principal |
|---|---|---|
| 1. Ingesta y limpieza | `tareas/tarea01_ingesta_limpieza.py` | Maratón filtrada y auditoría de exclusiones |
| 2. Podios | `tareas/tarea02_podios_historicos.py` | 87 medallistas, 29 ediciones, seis columnas solicitadas |
| 3. Evolución | `tareas/tarea03_evolucion_temporal.py` | Gráfico del oro, diferencias y análisis calculado |
| 4. Caso Plaza | `tareas/tarea04_manuel_plaza_1928.py` | Podio de 1928 y diferencia exacta de 26 segundos |
| 5. Documentos | `tareas/tarea05_integracion_documental.py` | Consultas conceptuales y corpus con procedencia |
| 6. NLP | `tareas/tarea06_nlp_cronicas.py` | Tokens, entidades, frecuencias, campos léxicos y gráfico |
| 7. Data-to-Text | `tareas/tarea07_cronica_historica.py` | `generar_cronica_historica(df_stats, entidades_nlp)` |
| 8. Reflexión | `tareas/tarea08_reflexion_critica.py` | Ensayo de 12 líneas |

`generar_notebook.py` ensambla las celdas desde los ocho scripts y el texto de
`contenido_notebook.py`, sin imports de módulos locales en el notebook final.
Separa las funciones en bloques de lectura y comprueba que no se omita ni duplique
ninguna parte del código fuente. Cada celda de las tareas guarda el archivo de
origen, las partes incluidas y el hash del script en sus metadatos. El generador
conserva la portada editada por los autores, incluidos la imagen adjunta y los
datos de presentación. El notebook puede ejecutarse con los datos aunque no se
lleve la carpeta `tareas/`. No requiere haber ejecutado antes los scripts.

## Preparación y ejecución

Se verificó con Python 3.12. Instalar las dependencias en un entorno virtual:

```bash
cd /ruta/a/U2/olympic_marathon_analysis
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Abrir el notebook en Jupyter o VS Code con ese intérprete y ejecutar todas las
celdas en orden. Si se necesita la interfaz web de Jupyter, se puede instalar
`jupyterlab` por separado; no es necesario para la ejecución automatizada.

Ejecutar los ocho archivos desde consola:

```bash
python ejecutar_proyecto.py
```

Ejecutar una tarea individual desde U2 (carga sus propias dependencias y datos):

```bash
python -m tareas.tarea04_manuel_plaza_1928
```

Regenerar y ejecutar el notebook después de editar los scripts:

```bash
python generar_notebook.py --ejecutar
python -m pytest -q tests
```

Cada ejecución actualiza los derivados en `resultados/`. No modifica `SetDatos/`,
el README ni los notebooks previos de clase. Para compartir el notebook
ejecutable, incluir `SetDatos/`, `datos_documentales/` y `requirements.txt`.

Los notebooks de clases anteriores, sus textos y los materiales de clima están
en `../archivos_clases/`. Esa carpeta no es necesaria para ejecutar ni entregar
el proyecto final.

## Decisiones de datos y fuentes

- **Cobertura:** 162 804 resultados olímpicos globales; 2296 registros de maratón
  masculina y 29 ediciones. La copia incluye verano hasta Tokio 2020 e invierno
  hasta 2022. No se agregan Juegos de París 2024.
- **Unidad:** las marcas numéricas del CSV se interpretan en milisegundos, con
  comprobación contra 1928. Se conservan décimas históricas; no se imputan marcas.
- **Limpieza:** 1560 registros con marca y clasificación válidas; 736 excluidos
  con motivo explícito. Una ausencia de marca no se interpreta como abandono.
  Cuatro URL de atletas están repetidas en la fuente global, fuera de los atletas
  de esta prueba; se restringe la ficha a los participantes antes de validar la unión.
- **Tokio:** faltan las marcas del podio en el CSV. El suplemento de
  `datos_documentales/suplemento_tokio2020.csv` completa únicamente esos tres
  tiempos, con [World Athletics](https://worldathletics.org/news/report/tokyo-olympic-games-men-marathon-report)
  como fuente, conservando el valor original nulo y una bandera documental.
  El bronce de Bashir Abdi es **02:10:00**; se usa la fuente deportiva primaria.
- **Comparabilidad:** [World Athletics](https://worldathletics.org/disciplines/race-walks/marathon)
  fecha la estandarización de 42,195 km en 1921. Se calcula también el cambio desde
  1924; no se atribuyen causalmente mejoras a equipamiento o nutrición.
- **Historia:** se consultó el [reportaje de Magdalena Llanos en UDP](https://vergara240.udp.cl/en-busca-de-la-medalla-olimpica-perdida/),
  incluido su contenido multimedia, y el [registro del Comité Olímpico de Chile](https://www.coch.cl/wp-content/uploads/2018/01/medallistas-olimpicos5.pdf).
  Las consultas se realizaron el **2 de noviembre de 2026**. No se adjudica una
  fecha de publicación no confirmada ni se presenta una hipótesis sobre el trofeo
  como hecho demostrado.
- **Corpus:** tres recreaciones didácticas y dos paráfrasis documentales propias,
  nunca recortes originales de 1928. Se guardan por separado sus tipos y fuentes.
- **NLP:** tokenizador y stopwords españoles de spaCy, NER con `EntityRuler` y
  diccionario de tres campos semánticos. No requiere descargar modelos. El control
  de ocho entidades conocidas comprueba funcionamiento, no generalización.
- **Sentimiento:** los conteos describen estos textos; no estiman la recepción de
  toda la prensa de 1928. El tono de una paráfrasis actual tampoco es el original.
- **Crónica:** solo las entidades con procedencia documental respaldan afirmaciones
  sociales. Si se retiran, la función declara que el contexto es insuficiente.

## Resultados y comprobaciones

Los derivados incluyen tablas CSV, dos gráficos PNG, auditoría JSON, hashes SHA-256
de los datasets, corpus y tokens JSON, crónica y reflexión TXT. Las pruebas cubren
unidades, marcas inválidas, balance de filas, selección de prueba, medallas,
suplementos contradictorios, 1928, entidades, negación léxica y procedencia narrativa.
El notebook se valida con `nbformat` y se ejecuta de principio a fin con `nbclient`.
