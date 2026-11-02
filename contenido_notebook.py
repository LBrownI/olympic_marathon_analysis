"""Texto editorial y organización del informe; el código procede de tareas/."""

INDICE = """<a id="indice-contenidos"></a>
## **ÍNDICE DE CONTENIDOS**

**ENTENDIMIENTO DEL PROYECTO**

1. [Contexto y justificación del análisis](#contexto-proyecto)
2. [Objetivos y criterios de éxito](#objetivos-proyecto)
3. [Alcance, fuentes y reproducción](#alcance-proyecto)
4. [Preparación del entorno de trabajo](#preparacion-entorno)

**MACROANÁLISIS Y EVOLUCIÓN HISTÓRICA DEL MARATÓN OLÍMPICO — SECCIÓN I**

1. [Ingesta, limpieza y filtrado de la prueba](#tarea-1)
2. [Extracción de los podios históricos](#tarea-2)
3. [Visualización y análisis de la evolución temporal](#tarea-3)

**PROFUNDIZACIÓN HISTÓRICA: MANUEL PLAZA EN ÁMSTERDAM 1928 — SECCIÓN II**

4. [Podio de 1928 y diferencia exacta respecto del oro](#tarea-4)
5. [Simulación de integración con fuentes documentales](#tarea-5)
6. [Procesamiento de lenguaje natural sobre las crónicas](#tarea-6)
7. [Síntesis automatizada: de los datos a la crónica](#tarea-7)

**PREGUNTA CONCEPTUAL Y DE CIERRE — SECCIÓN III**

8. [Reflexión crítica sobre Big Data e historia](#tarea-8)

**CIERRE DEL INFORME**

- [Conclusiones integradas](#conclusiones-integradas)
- [Fuentes documentales y límites del trabajo](#fuentes-limites)

---
"""

INTRODUCCION = """<a id="contexto-proyecto"></a>
## **Entendimiento del proyecto**

### 1. Contexto y justificación del análisis

Un tiempo de llegada permite ordenar una competencia, pero no explica la vida de
quien lo consiguió. Este proyecto aborda esa diferencia mediante dos escalas de
observación: primero examina la maratón masculina en las ediciones olímpicas
disponibles y luego se concentra en la plata de Manuel Plaza en Ámsterdam 1928.
La primera escala permite reconocer cambios en los registros ganadores; la segunda
vincula una diferencia deportiva concreta con lugares, oficios y relatos documentales.

La integración se organiza a partir de cuatro tablas de Kaggle: resultados,
medallas, sedes y fichas de atletas. Los resultados aportan clasificación y marcas;
las sedes permiten asignar año y ciudad; las medallas sirven para contrastar el
podio; las fichas añaden información biográfica cuando existe una correspondencia.
Después se incorpora un pequeño corpus para mostrar cómo el NLP puede organizar
contexto que no está representado en las columnas deportivas.

<a id="objetivos-proyecto"></a>
### 2. Objetivos de Data Science y criterios de éxito

| Objetivo | Evidencia con la que se comprueba |
|---|---|
| Seleccionar exclusivamente la maratón masculina de atletismo | Filtro por disciplina y nombre exacto de la prueba, con balance de filas |
| Comparar marcas registradas en formatos distintos | Conversión explícita a segundos y conservación de las fracciones históricas |
| Reconstruir el podio de cada edición disponible | Una medalla de cada tipo por edición y contraste entre results y medals |
| Explicar la evolución del oro | Gráfico, diferencias entre ediciones y análisis con límites de comparabilidad |
| Medir el resultado de Manuel Plaza | Podio de 1928 y cálculo reproducible de la brecha respecto del primer lugar |
| Relacionar estadística y contexto humano | Entidades, evidencias léxicas y una crónica con procedencia documental |

El criterio de calidad es que cada cifra pueda rastrearse hasta una transformación
de los CSV y cada afirmación de contexto tenga una fuente identificada. Las
recreaciones del ejercicio se reconocen como simulaciones durante todo el proceso.

<a id="alcance-proyecto"></a>
### 3. Alcance, fuentes y reproducción

La copia local contiene información de verano e invierno hasta 2022; la serie de
maratón masculina termina en **Tokio 2020**, celebrado en 2021. No se incorporan
resultados de París 2024. La columna Ciudad representa la sede de la edición;
en Tokio 2020, por ejemplo, no identifica el lugar efectivo del circuito de maratón.

Los cuatro CSV se encuentran en `SetDatos/`. La carpeta `datos_documentales/`
contiene las paráfrasis con procedencia y el suplemento de tres marcas de Tokio,
ausentes en el CSV original. El análisis guarda sus derivados en `resultados/`.
El notebook incluye el código de las ocho tareas: puede ejecutarse sin abrir los
archivos Python individuales, siempre que se conserven las dos carpetas de datos.

Para reproducirlo, seleccionar el entorno Python con las dependencias de
`requirements.txt` y ejecutar las celdas desde el principio. No se necesita conexión
durante el análisis ni descargar un modelo lingüístico. Los scripts separados
permiten reutilizar las funciones y el generador mantiene este informe sincronizado.

[Volver al índice](#indice-contenidos)
"""

ENTORNO_ANTES = """<a id="preparacion-entorno"></a>
## **Preparación del entorno de trabajo**

La primera celda configura la presentación del informe. `Path` permite construir
rutas sin escribir separadores específicos del sistema operativo; `tempfile`
localiza una carpeta temporal en la que Matplotlib puede guardar su configuración.
Esto evita depender de permisos de escritura en la carpeta personal del usuario.

La instrucción `run_line_magic("matplotlib", "inline")` hace que las figuras
aparezcan dentro del notebook. Su ejecución se condiciona a la presencia de IPython,
por lo que no se presupone que este mecanismo exista en una consola Python común.
Finalmente, las opciones de pandas permiten mostrar hasta 12 columnas y 100 filas:
ese límite basta para examinar los 87 medallistas sin truncar el listado de filas.
Esta celda prepara la visualización; todavía no carga ni transforma los datos.
"""

ENTORNO_DESPUES = """La ausencia de una tabla en esta salida es esperada: se han configurado
opciones, no ejecutado consultas sobre los CSV. En las siguientes celdas, pandas
se utilizará para tablas y uniones, NumPy para operaciones numéricas, Matplotlib
para figuras y spaCy para el procesamiento de texto en español. Las versiones de
la ejecución verificada se registran en `resultados/verificacion_ejecucion.json`.
"""

# Cada bloque indica partes del script original, explicación previa y lectura posterior.
def bloque(titulo, partes, antes, despues=""):
    return {"titulo": titulo, "partes": partes, "antes": antes, "despues": despues}


SECCIONES = [
    {
        "numero": 1,
        "titulo": "Ingesta, limpieza y filtrado de la prueba",
        "introduccion": "La preparación define qué observaciones se pueden comparar. Primero se establece una ruta reproducible y se inspecciona la estructura de las cuatro fuentes; después se selecciona la prueba y se normalizan las marcas. Los registros descartados se conservan con una explicación para distinguir problemas deportivos de problemas de información.",
        "bloques": [
            bloque("1.1. Bibliotecas y localización de los archivos", ["imports", "localizar_proyecto", "globales"], """Se importan las herramientas generales y se define `localizar_proyecto()`. La
función busca la carpeta que contiene `SetDatos/olympic_results.csv`; encontrar ese
archivo permite fijar `BASE` sin introducir una ruta personal en cada lectura.
`SALIDA` se construye a partir de esa base y `mkdir(exist_ok=True)` permite volver
a ejecutar el informe aunque `resultados/` ya exista.

Esta separación de rutas tiene una finalidad práctica: los originales se leen
desde una carpeta y los productos del análisis se escriben en otra. En esta celda
solo se definen herramientas y ubicaciones; la lectura de los CSV se realizará
cuando se llame a `cargar_datos()`.
"""),
            bloque("1.2. Normalización de etiquetas y filtro de la maratón masculina", ["normalizar_texto", "mascara_maraton"], """Los textos que identifican una misma prueba pueden variar en mayúsculas,
tildes o espacios. `normalizar_texto()` homogeneiza esas diferencias para comparar
etiquetas, sin reemplazar los nombres originales que se presentarán en las tablas.

`mascara_maraton()` combina dos condiciones con `&`: la disciplina debe ser
Athletics y el evento debe coincidir exactamente con `marathon men` o `men's
marathon`. Usar únicamente una búsqueda de la palabra marathon incluiría pruebas
de natación en aguas abiertas y otras categorías. La función devuelve una máscara
booleana que luego se aplica con `.loc[...]`.
"""),
            bloque("1.3. Lectura de las cuatro fuentes y validación del esquema", ["cargar_datos"], """`pd.read_csv(..., dtype="string")` carga los archivos conservando las etiquetas,
los identificadores y las marcas originales como texto. La conversión a números
se reserva para las variables que realmente lo requieren, como año y tiempo.
Cada tabla se guarda en un diccionario con una clave que identifica su función.

Antes de continuar se comprueba que existan las columnas requeridas. Si una copia
del dataset cambia de esquema, se produce un error explícito en lugar de obtener
silenciosamente una tabla parcial. Esta comprobación valida la estructura; no
garantiza todavía que cada fila esté completa o que los identificadores sean únicos.
"""),
            bloque("1.4. Conversión de marcas a segundos y formato de presentación", ["normalizar_tiempo", "formatear_tiempo", "mostrar_tabla"], """La comparación temporal exige una unidad común. En esta copia, los valores
numéricos de `value_unit` están expresados en **milisegundos**, por lo que se dividen
por 1000. Por ejemplo, la marca de Plaza se interpreta como
**9 203 000 ms ÷ 1000 = 9203 s = 02:33:23**. `value_type=TIME` identifica el tipo
de resultado, pero no basta por sí solo para declarar su escala.

`normalizar_tiempo()` también acepta cadenas HH:MM:SS, fracciones de segundo y
objetos timedelta. La expresión regular valida la forma de la cadena y se revisa
que minutos y segundos sean menores que 60. Valores como DNF, DNS o DSQ, marcas
vacías y formatos no interpretables devuelven `NaN`: no se convierten en cero.
La unidad numérica se recibe como parámetro, evitando inferirla por la magnitud.

`formatear_tiempo()` vuelve a una representación legible sin perder décimas
históricas. La última función, `mostrar_tabla()`, elige una tabla HTML en Jupyter
o una representación de texto al ejecutar los scripts desde consola.
"""),
            bloque("1.5. Integración de tablas y auditoría de las exclusiones", ["limpiar_maraton"], """La limpieza comienza con el filtro de la prueba y la eliminación de filas
exactamente repetidas. Después se añade la información de sedes mediante
`merge(..., validate="many_to_one")`: varios resultados pueden pertenecer a una
misma edición, pero cada clave de edición debe corresponder a una sola sede.
El indicador de la unión permite detectar resultados sin correspondencia.

El cruce con atletas utiliza URL no nulas y limita las fichas a quienes participan
en la prueba. Así se evitan uniones entre nulos y multiplicaciones de filas por
identificadores repetidos. La falta de una ficha biográfica no elimina un resultado
deportivo que tenga nombre, clasificación y tiempo válidos.

Luego se distinguen el año nominal, el año de celebración, la ciudad y las marcas
originales y normalizadas. `np.select()` asigna un motivo de exclusión: estado sin
clasificación válida o marca ausente/no interpretable. La función devuelve la
tabla filtrada completa, los registros utilizables, los excluidos y un resumen
de auditoría. El balance entre esas salidas impide perder filas sin explicación.
"""),
            bloque("1.6. Ejecución de la ingesta y revisión de los resultados", ["ejecucion"], """Ahora se llaman las funciones anteriores. `cargar_datos()` entrega las cuatro
fuentes y `limpiar_maraton()` devuelve los objetos que usarán las tareas siguientes.
Las tablas limpia y excluida se exportan por separado; la auditoría JSON conserva
los tamaños, la cobertura y los motivos de descarte.

También se calcula una huella SHA-256 de cada CSV. Esa huella permite comprobar
si dos ejecuciones usaron exactamente los mismos bytes, aunque no certifica la
veracidad histórica de su contenido. La salida muestra el resumen y cinco ejemplos
de conversión para revisar visualmente la relación entre marca original y segundos.
""", """**Interpretación de la auditoría.** Los 162 804 resultados globales se reducen a
2296 registros de maratón masculina distribuidos en 29 ediciones. Se conservan
1560 registros con marca y clasificación válidas; 736 quedan en la tabla de
exclusiones: 641 por estado deportivo y 95 por ausencia o formato de marca.

No hay duplicados exactos entre los resultados seleccionados. Además, 367
registros no encuentran ficha en athletes; se mantienen porque una biografía
ausente no invalida el resultado. La cobertura de marcas originales llega a 28
ediciones: la ausencia de tiempos de Tokio exige una decisión documental explícita
en la tarea siguiente. Estos vacíos no deben interpretarse como abandonos.
"""),
        ],
    },
    {
        "numero": 2,
        "titulo": "Extracción de los podios históricos",
        "introduccion": "El podio se reconstruye a partir de las medallas adjudicadas y se verifica contra una segunda tabla del mismo conjunto. Este paso distingue el orden oficial de una simple ordenación por tiempo y conserva las ediciones con información incompleta.",
        "bloques": [
            bloque("2.1. Selección de medallas, contraste y suplemento documental", ["imports", "globales", "extraer_podios"], """Los diccionarios `MEDALLAS` y `PUESTOS` traducen las etiquetas GOLD, SILVER y
BRONZE a una presentación legible. `extraer_podios()` selecciona esas etiquetas
en la tabla completa de maratón: se parte de la medalla adjudicada para conservar
la clasificación oficial, sin recalcularla ordenando tiempos.

La unión con medals usa edición, medalla y código de país; `validate="one_to_one"`
comprueba que cada clave represente un solo medallista en esta prueba. Para
Tokio se permite incorporar un suplemento local, verificado en
[World Athletics](https://worldathletics.org/news/report/tokyo-olympic-games-men-marathon-report).
Antes de completar una marca se contrastan clave y nombre; si el suplemento
contradice una marca original existente, la función detiene el proceso.

`Tiempo original` conserva la ausencia del CSV y `Complemento documental` identifica
las filas completadas. Finalmente se revisa que cada edición tenga exactamente
un oro, una plata y un bronce, y se ordena por año y posición.
"""),
            bloque("2.2. Presentación del podio histórico y exportación", ["ejecucion"], """La llamada utiliza el archivo `suplemento_tokio2020.csv` junto con los resultados
y las medallas. Después se exportan dos vistas del mismo objeto: una tabla de
entrega con Año, Ciudad, Puesto (Medalla), Atleta, País/Equipo y Tiempo, y otra
tabla de trazabilidad con segundos y procedencia de cada marca.

El listado completo permite revisar las ediciones en orden cronológico. El
resumen impreso al final verifica tres aspectos concretos: número de medallistas,
número de ediciones y cantidad de tiempos incorporados documentalmente.
""", """**Interpretación del podio histórico.** Se obtienen **87 medallistas en 29
ediciones**, es decir, tres posiciones por edición. Las tres marcas de Tokio
proceden del suplemento y no quedan tiempos de podio ausentes en la tabla final.
Sin ese archivo se conservarían los 87 medallistas, con tres tiempos sin marca.

La serie termina en el año nominal 2020, mientras Año celebración registra 2021.
Los nombres y países siguen los registros de la fuente; no se reasignan
nacionalidades históricas según fronteras actuales. Completar tres tiempos no
equivale a actualizar la cobertura del dataset a ediciones posteriores.
"""),
        ],
    },
    {
        "numero": 3,
        "titulo": "Visualización y análisis de la evolución temporal",
        "introduccion": "La serie del oro resume cómo cambia el tiempo ganador entre ediciones. Se estudian tanto la tendencia de largo plazo como las variaciones puntuales, manteniendo separados el cambio observado y las posibles explicaciones de ese cambio.",
        "bloques": [
            bloque("3.1. Cálculo de variaciones y construcción del análisis", ["imports", "analizar_evolucion"], """`analizar_evolucion()` conserva el primer puesto y ordena las observaciones por
año. `.diff()` calcula la diferencia de segundos frente a la edición anterior
disponible; `.shift()` conserva el año con el que se está comparando. Un cambio
negativo significa una marca ganadora más rápida, no una mejora anual promedio.

La función identifica los extremos, el mayor descenso, el mayor aumento y la
marca de oro más rápida de la copia. Calcula también la reducción relativa entre
la primera y la última observación, usando el tiempo inicial como denominador.
Se añade una comparación desde 1924 porque
[World Athletics](https://worldathletics.org/disciplines/race-walks/marathon)
sitúa la estandarización de la distancia en 1921. Los valores se incorporan a un
párrafo calculado para que sus cifras respondan a los datos utilizados.
"""),
            bloque("3.2. Diseño y lectura de la visualización", ["graficar_evolucion"], """La figura tiene dos paneles que comparten el eje de años. El superior presenta
el tiempo del oro: internamente se dibuja en minutos y `FuncFormatter` convierte
las etiquetas a HH:MM:SS. El área sombreada distingue las primeras ediciones,
cuando la distancia no era uniforme; el punto de 1928 facilita conectar el
macroanálisis con el caso de estudio.

El panel inferior representa las diferencias calculadas: las barras verdes
indican descensos y las anaranjadas aumentos del tiempo ganador. El diamante de
Tokio identifica la marca complementada con fuente documental. Las anotaciones
seleccionan puntos para facilitar la lectura, sin alterar el conjunto de observaciones.
La función guarda una imagen PNG y devuelve la figura para mostrarla en el informe.
"""),
            bloque("3.3. Gráfico final, tabla de diferencias y conclusión cuantitativa", ["ejecucion"], """Se calculan la serie y el texto interpretativo, se exporta la tabla de cambios
y se muestra la figura. `plt.close()` libera la figura después de visualizarla;
no elimina la imagen ya mostrada ni el archivo guardado. El párrafo impreso a
continuación recoge los extremos y porcentajes calculados por la función.

Al leer el eje temporal, los intervalos sin Juegos no deben completarse mediante
interpolación: las barras comparan ediciones celebradas y no periodos anuales
de duración constante. Tampoco se eliminan automáticamente los tiempos extremos,
porque un resultado poco habitual puede ser históricamente válido.
""", """**Interpretación histórica del gráfico.** El oro pasa de **02:58:50 en 1896 a
02:08:38 en Tokio 2020**: 50,20 minutos menos, una reducción aproximada del 28,1 %.
Desde 1924, la reducción es de 32,74 minutos (20,3 %). La diferencia entre ambos
porcentajes muestra por qué no conviene ignorar la falta de uniformidad inicial.

Los mayores cambios consecutivos se concentran alrededor de 1904: el tiempo
aumenta 29,13 minutos desde 1900 y disminuye 33,58 minutos hasta 1908. La marca
de oro más rápida de esta copia corresponde a 2008, con 02:06:32. También existen
retrocesos posteriores, por lo que la evolución no es monótona. Recorrido, clima,
altitud, preparación o equipamiento son posibles factores de contexto, pero esta
serie no mide sus efectos y no permite atribuirles causalmente una variación.
"""),
        ],
    },
    {
        "numero": 4,
        "titulo": "Podio de 1928 y diferencia exacta respecto del oro",
        "introduccion": "El análisis cambia de escala: a partir del mismo podio histórico se selecciona Ámsterdam 1928. La finalidad es comprobar la clasificación y expresar con precisión la diferencia que después se integrará a la narración.",
        "bloques": [
            bloque("4.1. Identificación del caso de estudio y cálculo de la brecha", ["imports", "analizar_1928"], """`analizar_1928()` filtra por la clave `amsterdam-1928` y ordena las tres filas
por puesto. Antes de restar tiempos comprueba que el podio esté completo, que se
identifique un único Manuel Plaza y que su medalla sea de plata. Si faltara una
marca, el cálculo se detendría para evitar una diferencia incompleta.

El tiempo del ganador se resta del tiempo de cada medallista y se guarda en
`Diferencia oro segundos`. Los nombres y países de presentación se añaden en
columnas independientes; de ese modo la tabla mantiene también las etiquetas
originales. Se devuelve el podio completo y `df_stats`, que contiene la fila de
Plaza para la función narrativa de la tarea 7.
"""),
            bloque("4.2. Presentación e interpretación del podio de Ámsterdam", ["ejecucion"], """La tabla siguiente muestra las tres medallas, los nombres legibles, el país,
el tiempo y la diferencia frente al oro. La operación de interés se verifica
directamente en segundos: **9203 − 9177 = 26**. No es necesario redondear ni
aproximar una resta de cadenas de texto.

Se exportan tanto el podio como la observación estadística de Plaza. Al utilizar
objetos provenientes de la misma serie histórica, se evita transcribir manualmente
una segunda versión de los números que podría divergir de los resultados del análisis.
""", """**Interpretación del caso.** Boughera El Ouafi registra **02:32:57**, Manuel
Plaza **02:33:23** y Martti Marttelin **02:35:02**. Por tanto, la plata queda a
**26 segundos** del oro y el bronce a 125 segundos. Esta precisión cuantifica la
proximidad del resultado, pero no demuestra un extravío ni permite afirmar qué
habría ocurrido bajo otras condiciones.

La plata figura también en el
[registro del Comité Olímpico de Chile](https://www.coch.cl/wp-content/uploads/2018/01/medallistas-olimpicos5.pdf).
La tarea siguiente incorpora contexto documental para ampliar la interpretación
sin utilizar la brecha temporal como explicación de la biografía del atleta.
"""),
        ],
    },
    {
        "numero": 5,
        "titulo": "Simulación de integración con fuentes documentales",
        "introduccion": "Una tabla de resultados no describe por sí sola el trabajo cotidiano ni los espacios de entrenamiento de Plaza. Se diseña una integración documental que conserva la procedencia de los textos y distingue lo simulado de las paráfrasis de fuentes consultadas.",
        "bloques": [
            bloque("5.1. Metadatos, consultas y respuesta simulada", ["imports", "simular_ingesta_documental"], """`simular_ingesta_documental(atleta, anio, ciudad)` recibe los metadatos del caso
y construye consultas con el nombre, el año, la ciudad y términos de contexto.
`urlencode()` convierte esas consultas a una URL de búsqueda válida, pero la
función no envía solicitudes ni afirma haber recuperado noticias por internet.
La validación restringe esta caché didáctica a Manuel Plaza en Ámsterdam 1928.

La respuesta contiene tres recreaciones que permiten ensayar el procesamiento
de texto. Cada una incluye identificador, tipo documental, autor y texto; no se
le atribuye un periódico histórico ni una fecha de publicación ficticia. Los
campos semánticos se introducen deliberadamente para demostrar el análisis
léxico, lo que debe considerarse al interpretar sus conteos.
"""),
            bloque("5.2. Incorporación de paráfrasis y trazabilidad del corpus", ["preparar_corpus"], """`preparar_corpus()` combina las recreaciones con dos paráfrasis guardadas en
`corpus_documental.json`. Una procede del reportaje de Magdalena Llanos en
[Vergara 240 / UDP](https://vergara240.udp.cl/en-busca-de-la-medalla-olimpica-perdida/)
y otra del registro institucional de medallistas. Los documentos conservan URL,
fecha de consulta y tipo; una paráfrasis es una redacción propia, no una cita literal.

La función comprueba identificadores y huellas de texto para evitar duplicados.
Además, exige una URL para cada paráfrasis documental. En un pipeline conectado,
estos controles acompañarían la descarga, la limpieza de HTML u OCR y la revisión
manual. Aquí la copia local permite ejecutar siempre el mismo corpus.
"""),
            bloque("5.3. Revisión de las consultas y de los textos utilizados", ["ejecucion"], """Se muestran el plan de búsqueda y cada documento con su identificador y tipo.
Esta revisión hace visible qué material entrará al NLP, antes de reducirlo a
tokens o entidades. El corpus utilizado se guarda en JSON y el plan en CSV para
conservar la relación entre el diseño de integración y la entrada real del análisis.

La clasificación documental no se descarta después de la lectura: se trasladará
a las tablas de entidades y tono. Así será posible comparar tipos de texto y
evitar que una recreación termine respaldando una afirmación histórica.
""", """**Interpretación del corpus.** La entrada contiene **cinco documentos**:
tres simulaciones y dos paráfrasis documentales. Son suficientes para demostrar
el método, pero no constituyen una muestra representativa de periódicos de 1928.
El reportaje de UDP es retrospectivo: su información contextual debe distinguirse
de un testimonio publicado durante la competencia. La búsqueda documental añade
contexto y preguntas de investigación; no elimina por sí sola los vacíos del archivo.
"""),
        ],
    },
    {
        "numero": 6,
        "titulo": "Procesamiento de lenguaje natural sobre las crónicas",
        "introduccion": "El NLP organiza el contenido del mini-corpus en palabras, entidades y evidencias léxicas. Se conservan dos recorridos: el reconocimiento de entidades utiliza el texto con mayúsculas y tildes; las frecuencias utilizan tokens en minúsculas y stopwords filtradas. El análisis describe estos documentos y no generaliza a toda la prensa histórica.",
        "bloques": [
            bloque("6.1. Limpieza del texto sin destruir nombres propios", ["imports", "limpiar_texto"], """`limpiar_texto()` normaliza Unicode a NFC, retira etiquetas HTML y reúne
espacios repetidos. La limpieza es deliberadamente suave: conserva letras con
tilde, números, mayúsculas y puntuación útil para reconocer nombres, fechas y
límites de oración. Eliminar esos rasgos antes del NER podría fragmentar o
desfigurar entidades como Ámsterdam y Parque Cousiño.

`Counter` se utilizará después para frecuencias y spaCy para tokenización y
stopwords en español. No se eliminan palabras todavía: esta función produce una
versión limpia del texto que seguirá disponible para revisar los resultados.
"""),
            bloque("6.2. Tokenizador español y reconocimiento de entidades", ["crear_pipeline_nlp"], """`spacy.blank("es")` crea un procesador de español sin un modelo estadístico
preentrenado. `sentencizer` divide oraciones y `EntityRuler` aplica un catálogo de
patrones de dominio. La comparación LOWER tolera cambios de mayúsculas; no
equivale a corregir errores de OCR ni a reconocer cualquier nombre desconocido.

Las etiquetas PER, LOC, DATE y ORG representan personas, lugares, fechas y
organizaciones. OCUPACION es una etiqueta propia que permite conservar el oficio
de suplementero como contexto. Se añaden patrones para años y fechas completas;
si coinciden, spaCy resuelve los solapamientos de las entidades.

Se trata de NER mediante reglas explícitas. Su ventaja aquí es la reproducibilidad
y la posibilidad de auditar cada patrón; su límite es la dependencia del vocabulario
declarado. La presencia de una entidad señala una mención, no verifica que toda
la oración que la rodea sea históricamente cierta.
"""),
            bloque("6.3. Campos semánticos, tasas y tratamiento de negaciones", ["globales", "analizar_lexico"], """`LEXICO` define tres campos: épica, sorpresa y precariedad. La función recorre
los tokens alfabéticos de cada oración y cuenta coincidencias exactas, por lo que
no incorpora automáticamente sinónimos, flexiones o sentidos implícitos. Un texto
puede contener varios campos; el tono predominante admite empates.

Para comparar longitudes se calcula **tasa = coincidencias ÷ tokens alfabéticos × 100**.
El denominador corresponde al texto previo al filtrado de stopwords. Además,
la ventana de tres tokens anteriores busca negaciones dentro de la misma oración;
las coincidencias negadas se guardan como evidencia, pero no incrementan el campo.

Este procedimiento es un análisis léxico exploratorio, no un clasificador validado
de sentimiento. Una alusión a dificultades económicas tampoco expresa por sí
misma una valoración negativa del atleta. Guardar la oración permite revisar
posibles falsos positivos y negaciones que la regla no interprete correctamente.
"""),
            bloque("6.4. Aplicación del pipeline y construcción de tablas de salida", ["procesar_corpus"], """`procesar_corpus()` aplica el mismo pipeline a cada documento con `nlp.pipe()`.
Para las frecuencias conserva tokens alfabéticos en minúsculas y elimina las
stopwords españolas. Se mantienen excepciones para las negaciones, porque su
eliminación podría borrar diferencias de sentido relevantes para la interpretación.

Las entidades se guardan con identificador documental, etiqueta, posición de
inicio y fin, oración, tipo de documento y URL. Las posiciones se refieren al
texto limpio guardado, lo que permite recuperar el fragmento exacto de la mención.
Por separado se producen frecuencias, resúmenes de tono, evidencias léxicas y tokens.
Esta estructura conserva la relación entre un resultado agregado y su documento
de origen, en lugar de mezclar todos los textos en una única cadena sin procedencia.
"""),
            bloque("6.5. Control de ocho entidades conocidas", ["evaluar_entidades_control"], """Se define un pequeño control manual con ocho menciones esperadas en los
documentos simulados: personas, lugares y fechas. La comprobación usa la tupla
documento–entidad–etiqueta, de modo que encontrar Santiago en otro documento
no acredita haberlo detectado en el texto solicitado.

El resultado booleano indica si cada mención fue recuperada. Dado que el corpus
y el catálogo se diseñaron conjuntamente, este control verifica funcionamiento
en ejemplos conocidos; no mide precisión, F1 ni desempeño fuera de muestra.
Una evaluación de generalización requeriría textos y anotaciones independientes.
"""),
            bloque("6.6. Visualización de frecuencias y campos léxicos", ["graficar_nlp"], """El panel izquierdo agrupa por tipo documental y suma conteos y tokens antes
de calcular las tasas. Esta operación pondera correctamente por longitud: no
promedia tasas de documentos breves y largos como si tuvieran igual denominador.
Se mantienen separadas las simulaciones y las paráfrasis documentales.

El panel derecho muestra las doce palabras filtradas más frecuentes del corpus
combinado. Ese ranking permite reconocer temas y nombres recurrentes; por sí
solo no identifica emociones ni importancia histórica. La figura declara la
composición reducida del corpus para que su alcance quede visible junto al gráfico.
"""),
            bloque("6.7. Resultados del NLP y lectura crítica de las evidencias", ["ejecucion"], """Se prepara el corpus, se ejecuta el pipeline y se muestran tres salidas:
entidades reconocidas, tono léxico por documento y control manual. Después se
presenta el gráfico. Las tablas se exportan a CSV y los tokens a JSON para que
puedan revisarse sin volver a procesar los textos.

La lectura debe comparar primero documentos del mismo tipo y revisar las
oraciones que justifican los conteos. Una tasa igual a cero significa que el
diccionario no encontró palabras de ese campo; no demuestra que el texto carezca
de todo significado emocional o social.
""", """**Interpretación de los resultados del NLP.** El control recupera las **ocho
entidades esperadas**, incluidas Ámsterdam, Santiago, Parque Cousiño, las personas
del podio y la fecha completa. Esto confirma el comportamiento previsto de las
reglas en el corpus construido, sin acreditar generalización.

En las tres recreaciones aparecen 8 coincidencias de épica, 2 de sorpresa y 4 de
precariedad. SIM_01 concentra vocabulario de precariedad y SIM_02 y SIM_03 de
épica; esa diferencia responde en parte al diseño didáctico de los fragmentos.
La paráfrasis de UDP aporta una coincidencia de precariedad; la del registro
institucional no presenta coincidencias en estos campos. Esa ausencia refleja
también el carácter informativo y el vocabulario de la paráfrasis.

Los conteos permiten describir esta entrada y orientar una lectura, pero no
demuestran cómo narró el logro la prensa de 1928. Para esa pregunta se necesitan
originales, un muestreo definido, revisión del OCR y validación humana del lenguaje.
"""),
        ],
    },
    {
        "numero": 7,
        "titulo": "Síntesis automatizada: de los datos a la crónica",
        "introduccion": "La síntesis reúne los valores calculados con el contexto organizado por NLP. Se implementa una plantilla verificable: las cifras dependen del DataFrame y las afirmaciones sociales dependen de entidades procedentes de paráfrasis documentales identificadas.",
        "bloques": [
            bloque("7.1. Diseño y validaciones de generar_cronica_historica", ["imports", "generar_cronica_historica"], """La función recibe `df_stats` y `entidades_nlp`. Primero comprueba columnas,
identidad del atleta, edición, ciudad, medalla y magnitudes numéricas. El tiempo
de Plaza y su diferencia frente al ganador se extraen de la fila seleccionada;
el tiempo del oro se expresa como tiempo de Plaza menos diferencia. No se escribe
26 como una constante para fabricar la brecha.

Para el contexto se conservan solo entidades con tipo `parafrasis_documental`,
URL y un documento que mencione al atleta. Si esas evidencias permiten identificar
el oficio y los lugares, la plantilla añade las frases contextuales. Si no existen,
declara que el contexto es insuficiente. Este filtro evita usar la simulación como
respaldo documental, aunque el texto simulado contenga las mismas palabras.

La generación es determinista y no llama a un modelo de lenguaje. Esa decisión
permite inspeccionar cómo cada entrada afecta a la salida; la presencia de una
entidad sigue requiriendo revisión de la oración y de su fuente para validar
relaciones históricas más complejas.
"""),
            bloque("7.2. Crónica integrada y revisión de su procedencia", ["ejecucion"], """Se obtiene de nuevo la observación estadística de Plaza y se procesan las
entidades del mismo corpus. La función construye la crónica, la muestra y la
guarda en `cronica_historica.txt`. El primer párrafo debe coincidir con los números
de la tarea 4; los párrafos contextuales deben corresponder a la evidencia que
se mantuvo después de filtrar por tipo documental.

Esta ejecución permite revisar la integración completa: el resultado no consiste
solo en mencionar estadísticas y lugares en un mismo texto, sino en conservar
la diferencia entre cálculo, contexto documentado y simulación didáctica.
""", """**Interpretación de la crónica.** La salida conserva **02:33:23**, la plata y
los **26 segundos** de separación. Añade el oficio y los lugares que aparecen en
las paráfrasis documentales y presenta las URL del contexto. La narración permite
relacionar el resultado con una trayectoria humana sin convertir una diferencia
temporal en una explicación causal del desenlace.

La utilidad del procedimiento reside en que sus límites también son reproducibles:
si se retiran las entidades documentadas, la función comunica la ausencia de
contexto en vez de sustituirlas por información simulada.
"""),
        ],
    },
    {
        "numero": 8,
        "titulo": "Reflexión crítica sobre Big Data e historia",
        "introduccion": "El cierre responde a la pregunta conceptual del enunciado con un ensayo de doce líneas. Se valora qué añade combinar tablas y textos, sin equiparar automáticamente un archivo histórico extenso en el tiempo con una infraestructura de Big Data.",
        "bloques": [
            bloque("8.1. Ensayo de cierre: el horizonte 1928–2028", ["imports", "globales", "ejecucion"], """`REFLEXION` contiene el ensayo breve. La comprobación de `splitlines()` exige
que no exceda quince líneas explícitas de texto, conforme a la pauta; la cantidad
de líneas que se vean en pantalla puede variar según el ancho del visor. Luego se
muestra el contenido y se exporta a `reflexion_critica.txt`.

El argumento parte de los 26 segundos para mostrar qué mide la tabla y qué
contexto aporta el corpus. También distingue tres límites: la escala local del
dataset, la ausencia de representatividad de los textos y la diferencia entre
organizar evidencia e interpretar históricamente. El año 2028 se usa como horizonte
del centenario, no como una edición observada ni como información futura del dataset.
"""),
        ],
    },
]

CONCLUSIONES = """<a id="conclusiones-integradas"></a>
## **Conclusiones integradas**

El macroanálisis reconstruye 29 podios y hace visible una mejora de largo plazo
en los tiempos ganadores, junto con oscilaciones que impiden leer la serie como
un progreso uniforme. La normalización en segundos permite medir los cambios;
la distinción de distancias históricas y de procedencia limita interpretaciones
que no podrían justificarse únicamente con los valores del gráfico.

En el caso de Plaza, la diferencia de 26 segundos es un resultado exacto del
cálculo. El contexto documental amplía las preguntas que se pueden hacer sobre
ese resultado: las menciones a un oficio y a espacios de entrenamiento aportan
dimensiones que no aparecen en la clasificación deportiva. El NLP ayuda a
organizar esas menciones y a conservar su vínculo con cada documento.

La integración aporta valor cuando permite revisar de dónde salió una cifra,
qué texto sostiene un contexto y qué parte del ejercicio fue simulada. Las reglas
de entidades, el corpus pequeño y las paráfrasis tienen un alcance exploratorio;
una investigación histórica más amplia debería trabajar con originales y una
selección documental justificada. Los resultados aquí permiten demostrar un
proceso reproducible y reconocer qué evidencia adicional sería necesaria.

[Volver al índice](#indice-contenidos)
"""
