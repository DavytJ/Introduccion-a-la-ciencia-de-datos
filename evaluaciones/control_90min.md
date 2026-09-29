---
title: "Control — Introducción a la Ciencia de Datos"
subtitle: 'Universidad de Montevideo — FCEE · Duración: 90 minutos'
lang: es
output: pdf_document
---

**Nombre:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ **Horario:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ **Fecha:** \_\_\_\_\_\_\_\_\_\_

Cada pregunta tiene cuatro opciones. Marcar **cada opción** como verdadera (V) o falsa (F): pueden ser verdaderas una, varias, todas o ninguna.
Utilizar lapicera o similar, no usar lápiz.

---

**1.** Ana editó `bitacora.md` en VS Code, guardó con Ctrl+S y cerró la computadora sin hacer nada más:

a) El cambio está guardado en su máquina
b) El cambio ya quedó en el historial
c) El equipo lo puede ver en GitHub
d) Para que quede registrado falta confirmar y sincronizar

**2.** Al sincronizar, la interfaz avisa que hay un conflicto en `decisiones.md`:

a) El repositorio se rompió y hay que clonarlo de nuevo
b) Otra persona modificó las mismas líneas del mismo archivo
c) Hay que elegir qué versión queda y volver a confirmar
d) Conviene conversarlo en el equipo y anotar la decisión

**3.** El Proceso Generador de Datos (DGP):

a) Es el archivo `.csv` que recibimos
b) Es el mecanismo que produce los eventos que intentamos registrar
c) Es la "caja negra" de Breiman
d) El modelo lo conoce automáticamente al ajustarse

**4.** Las variables de la dinámica de la caja negra:

a) Textura (`suave` / `rugoso` / `poroso`) es nominal
b) Rigidez (`blando` / `medio` / `rígido`) es ordinal
c) Cantidad de aristas es numérica continua
d) Peso estimado en gramos es numérica continua

**5.** ¿Qué es la vectorización?

a) Que una operación se aplica a todos los elementos a la vez, sin escribir un bucle
b) En R es el comportamiento por defecto: `c(1, 2, 3) * 10` da `10 20 30`
c) En Python, `[1, 2, 3] * 10` vectoriza igual que en R
d) En Python se obtiene con `np.array([1, 2, 3]) * 10`

**6.** Los errores del primer día:

a) `NameError` significa que el archivo no existe
b) `TypeError` significa que la operación no corresponde a ese tipo
c) `FileNotFoundError` es un error de ubicación
d) Un mensaje de error se lee de abajo hacia arriba

**7.** `c(1, "a", TRUE)` en R:

a) Da error por mezclar tipos
b) Devuelve un vector de texto: `"1" "a" "TRUE"`
c) La conversión es silenciosa
d) Tiene longitud 3

**8.** Instalar y cargar:

a) `pip install pandas` se ejecuta en la terminal, una sola vez
b) `import pandas as pd` se escribe al principio de cada script
c) `install.packages("ggplot2")` se corre cada vez que se abre RStudio
d) `library(ggplot2)` carga el paquete en la sesión

**9.** Aparece `No module named 'pandas'` (Python) o `there is no package called 'ggplot2'` (R):

a) Hay un error de sintaxis en el script
b) El paquete no está instalado en ese entorno
c) Se resuelve con `pip install` / `install.packages()`
d) Se resuelve reescribiendo la línea `import` / `library()`

**10.** Rutas:

a) `"data/raw/datos.csv"` es una ruta relativa
b) `"C:/Users/jodavyt/..."` es absoluta y falla en otra máquina
c) La ruta absoluta es más reproducible
d) Para el lenguaje, una ruta es texto

**11.** El identificador:

a) Es una columna con tantos valores únicos como filas
b) Siempre es la primera columna
c) Sirve para unir tablas
d) Puede ser compuesto, por ejemplo fecha + estación

**12.** El flujo de análisis:

a) Va de ingesta → perfilado → limpieza → exploración → transformación → entrega
b) El perfilado se hace después de limpiar
c) El perfilado incluye nulos, cardinalidad y valores fuera de rango
d) En la ingesta no se modifican los datos originales

**13.** Codificación:

a) `encoding="latin1"` es una instrucción de lectura
b) Ver `"Ã³"` en lugar de `"ó"` indica un desajuste de codificación
c) Cambiar la codificación modifica el archivo
d) `str.replace` / `str_replace_all` con un diccionario limpia los nombres de estaciónx

**14.** Niveles de medición:

a) Los niveles de Stevens son nominal, ordinal, intervalo y razón
b) La temperatura en °C es de razón
c) El ingreso en pesos es de razón
d) Satisfacción de 1 a 5 es ordinal

**15.** El instrumento:

a) Validez: mide lo que dice medir
b) Confiabilidad: da resultados consistentes al repetir
c) Validez y confiabilidad son sinónimos
d) Operacionalizar es traducir un concepto en variables medibles

**16.** Faltantes en una encuesta:

a) Faltante estructural: la pregunta no aplicaba
b) No respuesta: aplicaba y no se contestó
c) Los dos se tratan igual
d) El libro de códigos documenta cada variable y sus valores

**17.** Fechas:

a) `read_csv` de readr detecta fechas automáticamente
b) pandas necesita `parse_dates=["fecha"]`
c) `POSIXct` guarda la fecha como texto
d) El accesor `.dt` cumple el rol de lubridate

**18.** Agregación:

a) `group_by()` + `summarise()` equivale a `groupby()` + `agg()`
b) `n()` en R y `"size"` en pandas cuentan filas
c) `floor_date()` + `group_by()` equivale a `pd.Grouper(freq=...)`
d) `mean()` en R ignora los `NA` por defecto

**19.** Faltantes en una serie de sensor:

a) Explícito: la fila existe y la medición es `NA`
b) Implícito: la fila no existe
c) En rachas: muchos `NA` seguidos, sensor caído
d) Eliminar los `NA` sin mirar no pierde información

**20.** Partes de un gráfico:

a) Dataset, variable x, variable y, tipo de gráfico y títulos
b) `"Valores"` es un buen rótulo para el eje y
c) El rótulo del eje debe incluir la unidad
d) `ylim(0, 40)` es una decisión de lectura, no de datos

**21.** ¿Qué tipo de gráfico para qué pregunta?

a) Una variable a lo largo del tiempo: línea
b) Comparar un valor entre categorías (estaciones): barras
c) La relación entre dos variables numéricas: dispersión
d) La distribución de una variable: línea

**22.** Ejes y escalas, en el gráfico de ozono mensual:

a) Un eje x con `1, 2, 3, 4` se lee mejor con `Ene, Feb, Mar, Abr`
b) Empezar el eje y en 25 en lugar de 0 exagera las diferencias entre meses
c) `ax.set_xticks([1, 2, 3, 4], ["Ene", "Feb", "Mar", "Abr"])` cambia las etiquetas del eje
d) Cambiar los límites del eje cambia los datos

**23.** Para graficar una serie en el tiempo con matplotlib:

a) La columna fecha tiene que ser `datetime` (`parse_dates` al leer, o `pd.to_datetime()`), no texto
b) Si la fecha queda como texto, matplotlib la trata como categorías y el eje no respeta las distancias entre fechas
c) `ax.plot(df["fecha"], df["o3"])` acepta directamente una columna `datetime`
d) Hay que convertir la fecha a número a mano antes de graficar

**24.** `inner_join()` / `merge(how="inner")`:

a) Conserva solo las filas cuya clave existe en ambos lados
b) Para O3 y PM2.5 la clave fue estación + fecha
c) Las filas que quedan fuera se borran del disco
d) Lo que queda fuera se puede graficar, pero no comparar

**25.** Paneles y apilado:

a) `facet_wrap(~ estacion)` da un panel por estación
b) `bind_rows()` equivale a `pd.concat()`
c) `pd.merge()` apila tablas
d) En `patchwork`, `/` apila gráficos

**26.** Grilla de tiempo regular:

a) Observaciones a intervalos iguales
b) Un paso corto conserva la variabilidad
c) Remuestrear a paso horario es siempre mejor
d) `df.resample("10min").mean()` remuestrea con índice datetime

**27.** Rezago y autocorrelación:

a) `x.shift(1)` / `lag(x)` desplaza la serie un paso
b) En el gráfico de rezago, puntos sobre la diagonal indican autocorrelación positiva
c) La autocorrelación es la correlación con otra serie
d) La ACF calcula la autocorrelación para varios rezagos k

**28.** Breiman (2001), *Statistical Modeling: The Two Cultures*:

a) Una cultura supone un modelo estocástico del mecanismo que genera los datos
b) La otra trata al mecanismo como caja negra y evalúa por capacidad predictiva
c) La caja negra de la clase 2 es la de este artículo
d) Los comentaristas (Cox, Efron, Hoadley, Parzen) son coautores del artículo

**29.** Hernán, Hsu y Healy (2019), *A Second Chance to Get Causal Inference Right*:

a) Clasifican las tareas de la ciencia de datos en descripción, predicción e inferencia causal
b) La inferencia causal requiere supuestos y conocimiento del dominio que los datos por sí solos no dan
c) Predecir bien alcanza para saber qué pasa si se interviene
d) Sostienen que la ciencia de datos debe reconocer la inferencia causal como tarea distinta

**30.** Bueno de Mesquita y Fowler (2021), *Thinking Clearly with Data*:

a) Correlación no implica causalidad: hay que pensar en confusores y causalidad inversa
b) Sin variación en la variable explicativa no hay correlación que estimar
c) Seleccionar los casos según la variable de resultado sesga la conclusión
d) Una correlación fuerte alcanza para afirmar un efecto causal

**31.** Un compañero clona el repositorio del equipo y corre el script. 
Primero aparece No module named 'pandas'; después, un FileNotFoundError, porque el script lee "C:/Users/lucia/datos/ventas.csv":

a) El primer error indica que pandas no está instalado en ese entorno y se resuelve con pip install pandas.
b) El primer error se resuelve reescribiendo la línea import pandas as pd
c) El segundo error ocurre porque esa ruta absoluta no existe en otra máquina; una ruta relativa lo evita
d) Para que funcione en todas las máquinas, conviene subir el CSV crudo al repositorio


**32.** Un equipo quiere saber si las ventas de la cafetería aumentan los días de lluvia. Tiene el registro del sistema de caja y una encuesta de satisfacción de 1 a 5:

a) Las ventas registradas son preferencia revelada; la satisfacción declarada en la encuesta es preferencia declarada
b) La satisfacción de 1 a 5 es una variable de razón 
c) Si la correlación entre lluvia y ventas es fuerte, alcanza para afirmar que la lluvia causa el aumento 
d) Estudiar solo los días de mayores ventas para ver qué tienen en común sesga la conclusión

**33.** Un equipo abre el CSV minutal de ozono: los nombres de estación aparecen como "EstaciÃ³n" y la columna fecha quedó como texto. Quieren graficar la serie:

a) "EstaciÃ³n" indica un error de tipo: hay que convertir la columna a número 
b) Indicar la codificación al leer es una instrucción de lectura: no modifica el archivo 
c) Para graficar en el tiempo, la fecha tiene que ser datetime; si queda como texto, matplotlib la trata como categorías 
d) Con datos minutales, graficar todo sin agregar produce siempre el gráfico más legible
