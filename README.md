# Ciencia de Datos y Big Data

Descripción General y Contexto del Proyecto

Los Juegos Olímpicos modernos representan uno de los eventos longitudinales con mayor
riqueza de datos estructurados y desestructurados del mundo, abarcando más de un siglo de
historia (desde Atenas 1896 hasta la actualidad).

Este proyecto se divide en dos grandes etapas:

1. Macroanálisis Global e Histórico del Maratón: Exploración, limpieza y análisis de la prueba  reina del atletismo (Maratón Masculino) a lo largo de todas las ediciones olímpicas, identificando los podios históricos (Top 3) y la evolución de los registros temporales.

2. Microanálisis de Contexto y NLP (Caso Manuel Plaza): Profundización en la gesta del atleta chileno Manuel Plaza en los Juegos Olímpicos de Ámsterdam 1928, cruzando los datos cuantitativos con técnicas de Procesamiento de Lenguaje Natural y fuentes documentales históricas.

Dataset: https://www.kaggle.com/datasets/piterfm/olympic-games-medals-19862018

SECCIÓN I: Macroanálisis y Evolución Histórica del Maratón Olímpico

Utilizando el dataset histórico de los Juegos Olímpicos de Kaggle (ej. Olympic Summer & Winter Games), cargue la información en un entorno de Python (pandas, numpy, matplotlib/seaborn) y desarrolle las siguientes tareas analíticas:

1. Ingesta, Limpieza y Filtrado de la Prueba

● Carga de datos: Cargue el dataset consolidado de atletas y resultados históricos.

● Filtrado específico: Aislar exclusivamente los registros correspondientes a la competencia
de Maratón Masculino (Marathon Men) a lo largo de toda la historia olímpica registrada.

● Limpieza de Tiempos: Escriba un script en Python para unificar el formato de los tiempos
de llegada (convertir marcas a segundos totales o formato timedelta de pandas) para
permitir comparaciones cronológicas precisas, eliminando valores nulos o descalificados
sin marca.

2. Extracción de los Tres Primeros Lugares Históricos

● Genere una tabla resumen o DataFrame en Python que contenga el podio histórico (Top 3: Oro, Plata y Bronce) de la maratón para cada una de las ediciones de los Juegos Olímpicos (desde Atenas 1896 hasta la edición más reciente disponible).

● La tabla final debe mostrar claramente las columnas: Año, Ciudad, Puesto (Medalla),Atleta, País/Equipo y Tiempo.

3. Visualización y Análisis de la Brecha Temporal

● Construya una visualización gráfica (por ejemplo, un gráfico de línea o dispersión con
matplotlib o seaborn) que muestre la evolución del tiempo del ganador de la medalla de
oro en la maratón a lo largo de los años.

● Analice e identifique en un párrafo breve: ¿Cómo ha evolucionado la marca ganadora a lo
largo de un siglo? ¿Se aprecian saltos drásticos en ciertas décadas (por ejemplo, debido a
cambios en pistas, nutrición o tecnología deportiva)?

SECCIÓN II: Profundización Histórica y Caso de Estudio – Manuel Plaza en Ámsterdam 1928

Haciendo un zoom-in desde la macroestructura global hacia la historia humana, la evaluación se focaliza en el hito del deportista chileno Manuel Plaza Reyes y su histórica medalla de plata en los Juegos Olímpicos de Ámsterdam 1928.


4. Aislamiento y Contexto Cuantitativo del Podio de 1928

● A través de código en Python, filtre específicamente los registros de la maratón de
Ámsterdam 1928 extraídos en la Sección I.

● Presente los datos exactos del podio de esa edición:
○ 🥇 Boughera El Ouafi (Francia) - 02:32:57
○ 🥇 Manuel Plaza Reyes (Chile) - 02:33:23
○ 🥇 Martti Marttelin (Finlandia) - 02:35:02

● Calcule analíticamente la diferencia exacta en segundos con la que Manuel Plaza quedó del oro olímpico.

5. Simulación de Integración con Fuentes Documentales
    
● Diseño de pipeline de búsqueda: Suponga que su script debe enriquecer este dato numérico conectándose a repositorios externos o motores de búsqueda de crónicas históricas.

● Escriba un bloque de código conceptual o función en Python que reciba los metadatos de Manuel Plaza (Atleta, Año, Ciudad) y simule la ingesta de un mini-corpus de texto con fragmentos de periódicos de 1928 que describan su origen socioeconómico (suplementero en Santiago) y su entrenamiento en el antiguo Parque Cousiño.

6. Procesamiento de Lenguaje Natural (NLP) sobre Crónicas Históricas

● Utilizando un corpus de texto histórico provisto o simulado sobre la participación de

Manuel Plaza:

○ Aplique un pipeline de NLP básico usando librerías como spaCy o NLTK: limpieza de
texto, tokenización y eliminación de stopwords.

○ Ejecute Extracción de Entidades Nombradas (NER) para identificar automáticamente
las locaciones geográficas clave (ej. Ámsterdam, Santiago, Parque Cousiño), fechas y
actores involucrados.

○ Realice un análisis léxico o de polaridad/sentimiento para evaluar si las crónicas de la
época describían el logro de Sudamérica con un tono épico, de sorpresa o de
precariedad.


7. Síntesis Automatizada de Datos y Texto (Data-to-Text)
● Diseñe una función en Python llamada generar_cronica_historica(df_stats, entidades_nlp) que reciba:

1. Los datos duros del dataset (Tiempo: 2h 33m 23s, Medalla de Plata, diferencia de 26 segundos).

2. Las entidades y el contexto sociohistórico extraído por NLP.

● La función debe estructurar y retornar un reporte narrativo integrado que fusione la
estadística fría del maratón olímpico con la narrativa humana del hito de 1928.

SECCIÓN III: Pregunta Conceptual y de Cierre

8. Reflexión Crítica sobre Big Data e Historia: En un ensayo breve (máximo 15
líneas), responda analíticamente: ¿Qué valor agregado real aporta combinar un dataset tabular masivo de Kaggle (como los podios históricos del maratón) con técnicas de Procesamiento de Lenguaje Natural (NLP) y búsqueda documental, en comparación con realizar únicamente un análisis estadístico cuantitativo tradicional? Fundamente utilizando el caso de Manuel Plaza y la magnitud temporal transcurrida (1928 - 2028).

Aquí se detalla los criterios a evaluar del desarrollo del código en Python (análisis de datos masivos y NLP) como la profundidad en el análisis histórico del caso Manuel Plaza.

Criterios de evaluacion por Sección

1. Ingesta, Limpieza y Filtrado de Datos (Sec. I)
- Código limpio y robusto en Pandas.
- Filtra correctamente la prueba de Maratón Masculino en todo el dataset y normaliza sin errores los formatos de tiempo y nulos.

2. Extracción de Podios Históricos (Sec. I)
- Genera de forma automatizada y correcta el DataFrame con el Top 3 (Oro, Plata, Bronce) de cada edición olímpica histórica con todas las columnas solicitadas.

3. Visualización y Brecha Temporal (Sec. I)
- Gráfico profesional y estético (Matplotlib/Seaborn) que muestra claramente la evolución del oro.
- El análisis crítico posterior es profundo y coherente con los datos.

4. Aislamiento del Podio 1928 y Manuel Plaza (Sec. II)
- Extrae con precisión milimétrica los datos del podio de Ámsterdam 1928.
- Calcula correctamente la diferencia en segundos y contextualiza el
logro.

5. Simulación de Integración Documental (Sec. II)
- Propone un pipeline o función conceptual clara y coherente para simular la ingesta y estructuración de textos históricos vinculados al origen del atleta.

6. Procesamiento de Lenguaje Natural - NLP (Sec. II)
- Aplica correctamente un pipeline de NLP (tokenización, stopwords, NER efectivo extrayendo locaciones/actores) y realiza un análisis léxico/sentimiento adecuado.

7. Síntesis Automatizada Data-to-Text (Sec. II)
- Diseña una función robusta y funcional que combina magistralmente los datos estructurados cuantitativos con las entidades del NLP en un reporte narrativo fluido.

8. Reflexión Crítica y Cierre (Sec. III) 
- Ensayo analítico sobresaliente que argumenta con solidez el valor agregado del cruce Big Data + NLP frente al análisis tradicional, usando la escala temporal 1928-2028.


Los cuatro CSV se encuentran en `SetDatos/`. La carpeta `datos_documentales/`
contiene las paráfrasis con procedencia y el suplemento de tres marcas de Tokio,
ausentes en el CSV original. El análisis guarda sus derivados en `resultados/`.
El notebook incluye el código de las ocho tareas: puede ejecutarse sin abrir los
archivos Python individuales, siempre que se conserven las dos carpetas de datos.

Para reproducirlo, seleccionar el entorno Python con las dependencias de
`requirements.txt` y ejecutar las celdas desde el principio. No se necesita conexión
durante el análisis ni descargar un modelo lingüístico. Los scripts separados
permiten reutilizar las funciones y el generador mantiene este informe sincronizado.