---
title: "Ejercicios de repaso (segunda serie)"
subtitle: "Introducción a la Ciencia de Datos — Universidad de Montevideo"
lang: es
mainfont: DejaVu Serif
monofont: DejaVu Sans Mono
fontsize: 11pt
geometry: margin=2.3cm
header-includes:
  - \usepackage{enumitem}
  - \setlist{itemsep=2pt}
  - \pagestyle{plain}
  - \renewcommand{\arraystretch}{1.35}
---

Nombre: \hfill Fecha: \hspace{4cm}

Trabajo en papel, sin computadora. Los valores de las tablas están inventados, salvo
que el ejercicio diga que salen de la tabla de la clase 12.

**Cómo leer la letra.** Todos los ejercicios tienen dos partes: *Datos* (lo que se
tiene) y *Se pide* (lo que hay que hacer). Cada inciso empieza con un verbo, y cada
verbo pide siempre el mismo tipo de respuesta:

| Verbo      | La respuesta es                                                         |
|:-----------|:------------------------------------------------------------------------|
| Escribir   | un texto exacto que no es código: una ruta, un nombre, un valor         |
| Contar     | un número entero                                                        |
| Calcular   | un número, con la cuenta a la vista                                     |
| Completar  | las celdas vacías de una tabla o los huecos \_\_\_\_                     |
| Clasificar | una opción de la lista que da el inciso                                 |
| Decidir    | sí o no, y un renglón de justificación                                  |
| Programar  | código en Python, escrito en la hoja                                     |

**Solo el verbo Programar pide código.** Con cualquier otro verbo la respuesta no lleva
código. Cuando hay que programar, el ejercicio dice cómo se llama la tabla y qué
columnas tiene; se usan esos nombres.

**Para ir más lejos.** Algunos ejercicios terminan con incisos bajo ese título. Son
opcionales: se hacen después de terminar el resto.

**La tabla de la clase 12.** `transito_aire_junio2024.csv` tiene una fila por estación y
hora de junio de 2024, con las columnas `estacion`, `hora`, `transito` (vehículos por hora
cerca de la estación), `no2` y `pm25` (µg/m³). Las estaciones son Tres Cruces, Curva de
Maroñas y Museo Romántico.

**Python.** Se supone que ya se corrió:

```
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
```

\newpage

## Ejercicio 24 (faltantes y una variable nueva).

*Datos.* La tabla se llama `aire` y tiene estas filas (NA es una celda vacía; la columna
fila solo numera los renglones):

| fila | estacion        | hora             | transito | pm25 |
|:----:|:----------------|:-----------------|---------:|-----:|
| 1    | Tres Cruces     | 2024-06-03 08:00 | 31200    | 18,4 |
| 2    | Tres Cruces     | 2024-06-03 09:00 | NA       | 22,0 |
| 3    | Tres Cruces     | 2024-06-03 10:00 | 35800    | NA   |
| 4    | Museo Romántico | 2024-06-03 08:00 | 2900     | 9,5  |
| 5    | Museo Romántico | 2024-06-03 09:00 | 3400     | NA   |
| 6    | Museo Romántico | 2024-06-03 10:00 | 4100     | 31,0 |

Se crea la columna `transito_miles`, que es `transito` dividido 1000.

*Se pide.*

a) Contar los NA de cada columna de `aire`.
b) Completar la columna `transito_miles` para las seis filas.
c) Contar los NA de `transito_miles`.
d) Programar la línea que crea `transito_miles` en la tabla `aire`.
e) Programar la línea que muestra cuántos NA tiene cada columna de `aire`.

*Para ir más lejos.* Se crea otra columna con esta línea:

```
aire["pm25_alto"] = np.where(aire["pm25"] > 25, "alto", "bajo")
```

f) Completar la columna `pm25_alto` para las seis filas. (En Python, NA > 25 da
   `False`.)
g) Decidir si las filas 3 y 5 quedan bien clasificadas.

\newpage

## Ejercicio 25 (variables a partir de la hora).

*Datos.* La tabla se llama `datos`. Su columna `hora` es una fecha, y tiene estos seis
valores. El 1 de junio de 2024 fue sábado.

| fila | hora             | h\hspace{1.6cm} | franja\hspace{1.6cm} | tipo_dia\hspace{1.6cm} |
|:----:|:-----------------|:-:|:------:|:--------:|
| 1    | 2024-06-01 03:00 |   |        |          |
| 2    | 2024-06-02 12:00 |   |        |          |
| 3    | 2024-06-03 05:00 |   |        |          |
| 4    | 2024-06-03 06:00 |   |        |          |
| 5    | 2024-06-05 17:00 |   |        |          |
| 6    | 2024-06-07 18:00 |   |        |          |

Las franjas son: madrugada de 0 a 5, mañana de 6 a 11, tarde de 12 a 17 y noche de 18
a 23. El tipo de día es «fin de semana» o «lunes a viernes».
En Python, `datos["hora"].dt.hour` da la hora del día, y `datos["hora"].dt.dayofweek`
da el día de la semana con lunes = 0, …, sábado = 5, domingo = 6.

*Se pide.*

a) Completar la columna `h` (hora del día).
b) Completar la columna `franja`.
c) Completar la columna `tipo_dia`.
d) Contar las filas de cada franja.
e) Programar la línea que crea la columna `h`.
f) Programar la línea que crea la columna `tipo_dia`, usando `np.where`.

*Para ir más lejos.* En clase la franja se creó con
`pd.cut(datos["h"], bins=[-1, 5, 11, 17, 23], labels=[...])`. Cada intervalo de `pd.cut`
no incluye su extremo izquierdo e incluye el derecho: el primero es «más de −1, hasta 5».

g) Si se escribe `bins=[0, 5, 11, 17, 23]`, completar la franja que les toca a h = 0 y
   a h = 5.
h) Decidir si con `bins=[0, 5, 11, 17, 23]` la madrugada queda completa.

\newpage

## Ejercicio 26 (promedios por grupo).

*Datos.* La tabla se llama `tc` y tiene ocho horas de Tres Cruces. El tránsito está en
miles de vehículos por hora:

| franja    | transito | pm25 |
|:----------|---------:|-----:|
| madrugada | 10       | 18   |
| madrugada | 12       | 22   |
| mañana    | 28       | 16   |
| mañana    | 30       | NA   |
| tarde     | 38       | 15   |
| tarde     | 40       | 19   |
| noche     | 24       | 30   |
| noche     | 22       | 34   |

*Se pide.*

a) Completar la tabla por franja. La media no cuenta los NA; n es la cantidad de
   valores de `pm25` con dato.

| franja    | media de transito | media de pm25 | n\hspace{1cm} |
|:----------|:-----------------:|:-------------:|:-:|
| madrugada |                   |               |   |
| mañana    |                   |               |   |
| tarde     |                   |               |   |
| noche     |                   |               |   |

b) Escribir la franja con más tránsito y la franja con más PM2.5.
c) Decidir si, en esta tabla, el PM2.5 de una franja sigue al tránsito de esa misma
   franja.
d) Programar la línea que calcula la media de `transito` y de `pm25` para cada franja
   y la guarda como `por_franja`.

*Para ir más lejos.*

e) Calcular la media de `pm25` de las siete filas con dato, y el promedio de las cuatro
   medias del inciso a).
f) Decidir si el promedio de las cuatro medias es la media de `pm25` de la tabla.

\newpage

## Ejercicio 27 (tránsito relativo).

*Datos.* La columna `transito` suma los vehículos de los puntos de conteo que están a
menos de 1,5 km de cada estación. La estación A tiene 2 puntos de conteo cerca; la
estación B tiene 40. Tres horas de un mismo día:

| estacion | hora  | transito | transito_rel\hspace{1.6cm} |
|:--------:|:-----:|---------:|:------------:|
| A        | 08:00 | 200      |              |
| A        | 13:00 | 400      |              |
| A        | 20:00 | 300      |              |
| B        | 08:00 | 6000     |              |
| B        | 13:00 | 9000     |              |
| B        | 20:00 | 9000     |              |

El tránsito relativo es el tránsito de la hora dividido el tránsito medio de su
estación: 1 es lo habitual de la estación, 2 es el doble.

*Se pide.*

a) Calcular el tránsito medio de cada estación.
b) Completar la columna `transito_rel`, con dos decimales.
c) Calcular cuántas veces es el tránsito medio de B respecto del de A.
d) Decidir si eso quiere decir que cerca de B pasan esas veces más vehículos que
   cerca de A.
e) Programar la línea que crea `transito_rel` en la tabla `datos`, usando
   `groupby("estacion")` y `transform("mean")`.

*Para ir más lejos.*

f) Escribir la estación en la que la hora 13:00 está más por encima de lo habitual.

\newpage

## Ejercicio 28 (correlación).

*Datos.* Coeficientes de correlación calculados con la tabla de la clase 12:

| n.º | Estación          | Variables        | r     |
|:---:|:------------------|:-----------------|------:|
| 1   | Tres Cruces       | tránsito y NO2   | 0,59  |
| 2   | Curva de Maroñas  | tránsito y NO2   | 0,15  |
| 3   | Tres Cruces       | NO2 y PM2.5      | 0,40  |
| 4   | Curva de Maroñas  | NO2 y PM2.5      | 0,55  |
| 5   | Tres Cruces       | tránsito y PM2.5 | −0,02 |

En este curso, la intensidad se clasifica así: débil si el valor absoluto de r es menor
que 0,3; moderada entre 0,3 y 0,7; fuerte si es mayor que 0,7.
La tabla `tc` tiene las horas de Tres Cruces con dato de NO2.

*Se pide.*

a) Clasificar cada coeficiente por su signo (positiva o negativa) y por su intensidad
   (débil, moderada o fuerte).
b) Decidir si el coeficiente 1 alcanza para afirmar que el tránsito causa el NO2.
c) Decidir si los coeficientes 1 y 2 permiten afirmar que el tránsito contamina más
   en Tres Cruces que en Curva de Maroñas.
d) Programar la línea que calcula la correlación entre `transito` y `no2` en la tabla
   `tc`.

*Para ir más lejos.* Cinco pares de valores:

| x | 1 | 2 | 3 | 4 | 5 |
|:-:|:-:|:-:|:-:|:-:|:-:|
| y | 2 | 4 | 5 | 4 | 5 |

La fórmula es
$r = \dfrac{\sum (x - \bar{x})(y - \bar{y})}{\sqrt{\sum (x - \bar{x})^2 \, \sum (y - \bar{y})^2}}$.
Dato: $\sqrt{60} \approx 7{,}75$.

e) Calcular las medias de x y de y.
f) Calcular r.
g) Clasificar r por su signo y su intensidad.

\newpage

## Ejercicio 29 (la recta).

*Datos.* Con las 291 horas de Tres Cruces que tienen NO2 se ajustó la recta

$$\text{no2} = 18{,}3 + 0{,}79 \cdot \text{transito\_miles}$$

con R² = 0,35. El tránsito de esas horas va de 4,7 a 48,8 miles de vehículos por hora.
La tabla se llama `tc`.

*Se pide.*

a) Calcular el NO2 que da la recta para 0, 10 y 30 mil vehículos por hora.
b) Calcular el residuo de una hora con 30 mil vehículos y un NO2 medido de 50 µg/m³.
   (Residuo = valor medido − valor que da la recta.)
c) Clasificar esa hora: queda por encima o por debajo de la recta.
d) Clasificar cada uno de los números 18,3, 0,79 y 0,35 con una de estas opciones:
   (i) el NO2 que la recta le asigna a una hora sin tránsito; (ii) cuánto sube el NO2
   por cada mil vehículos más por hora; (iii) la parte de la variación del NO2 que
   explica la recta.
e) Programar las líneas que ajustan la recta, la guardan como `modelo` y muestran los
   coeficientes y el R².

*Para ir más lejos.*

f) Calcular cuántos miles de vehículos por hora hacen falta para que la recta dé
   50 µg/m³.
g) Decidir si conviene usar la recta para una hora con 80 mil vehículos.

\newpage

## Ejercicio 30 (una variable categórica en el modelo).

*Datos.* El modelo `no2 ~ transito_miles + pm25 + franja`, ajustado con la tabla `tc`,
da estos coeficientes:

| Coeficiente        | Valor |
|:-------------------|------:|
| Intercept          | 9,08  |
| transito_miles     | 0,65  |
| pm25               | 0,45  |
| franja[T.mañana]   | 2,80  |
| franja[T.tarde]    | 5,41  |
| franja[T.noche]    | 6,21  |

*Se pide.*

a) Escribir la franja de referencia: la que no tiene coeficiente propio.
b) Calcular el NO2 que da el modelo para una hora de la noche con 20 mil vehículos y
   PM2.5 = 30.
c) Calcular el NO2 que da el modelo para una hora de la madrugada con el mismo tránsito
   y el mismo PM2.5.
d) Calcular la diferencia entre b) y c).
e) Decidir si esa diferencia cambia cuando el tránsito es de 40 mil vehículos.
f) Programar la línea que crea en `tc` la columna `noche`: 1 si la franja es «noche»
   y 0 si no.
g) Programar las líneas que ajustan el modelo con `transito_miles`, `pm25` y `noche`,
   y muestran los coeficientes.

*Para ir más lejos.* En el modelo con interacción `no2 ~ transito_miles * franja`, el
coeficiente de `transito_miles` es 2,94 (la pendiente de la madrugada) y el de
`transito_miles:franja[T.mañana]` es −2,42.

h) Calcular la pendiente del tránsito en la mañana.
i) Decidir si, en la madrugada, mil vehículos más por hora suben el NO2 más que en la
   mañana.

\newpage

## Ejercicio 31 (rutas en la clase 12).

*Datos.* La carpeta `curso/` es el repositorio del curso. El archivo `.gitignore`
contiene la línea `*.csv`.

```
curso/
├── clases/
│   ├── clase10/
│   │   └── transito_aire_junio2024.csv
│   └── clase12/
│       ├── clase12_ejercicios.py
│       └── clase12_soluciones.py
└── .gitignore
```

En `clase12_ejercicios.py` está escrito:

```
RUTA = "clases/clase10/transito_aire_junio2024.csv"
```

*Se pide.*

a) Decidir si el programa encuentra el archivo cuando el directorio de trabajo es
   `curso/`.
b) Escribir en qué carpeta busca el archivo cuando el directorio de trabajo es
   `curso/clases/clase12/`.
c) Escribir la ruta relativa correcta para el caso del inciso b).
d) Programar la línea que lee el archivo, con la columna `hora` como fecha, y lo guarda
   como `aire`.
e) Programar las líneas que muestran el directorio de trabajo.

*Para ir más lejos.*

f) Decidir si un compañero que clona el repositorio recibe el archivo CSV.

\newpage

## Ejercicio 32 (perfilado de la tabla de la clase 12).

*Datos.* La tabla `aire` tiene tres estaciones, una fila por estación y hora, del 1 al
30 de junio de 2024. Museo Romántico no tiene ningún dato de NO2. Tres Cruces tiene
429 NA en `no2`.

*Se pide.*

a) Calcular cuántas filas tiene la tabla.
b) Escribir el identificador de la tabla: las columnas que, juntas, distinguen una fila
   de otra.
c) Escribir la unidad de observación: qué representa una fila.
d) Calcular el porcentaje de horas de Tres Cruces que tienen dato de NO2.
e) Decidir si se puede comparar el NO2 de las tres estaciones.
f) Programar la línea que cuenta cuántas filas tiene cada estación.

*Para ir más lejos.*

g) Un día de Tres Cruces tiene solo 6 horas con dato de NO2, todas entre las 10 y las
   15. Decidir si el promedio de esas 6 horas representa al día.

\newpage

## Ejercicio 33 (unir dos tablas por la hora).

*Datos.* Dos tablas de una misma estación y un mismo día:

Tabla `ozono`:

| hora  | o3 |
|:-----:|---:|
| 08:00 | 40 |
| 09:00 | 45 |
| 10:00 | 52 |
| 11:00 | 58 |

Tabla `pm`:

| hora  | pm25 |
|:-----:|-----:|
| 09:00 | 12   |
| 10:00 | 15   |
| 11:00 | 14   |
| 12:00 | 18   |

*Se pide.*

a) Escribir la columna que sirve de clave para unir las dos tablas.
b) Contar las filas de la unión interna (`how="inner"`: solo las horas que están en las
   dos tablas).
c) Contar las filas de la unión izquierda sobre `ozono` (`how="left"`) y los NA que
   quedan en `pm25`.
d) Programar la línea que hace la unión interna y la guarda como `juntas`.
e) Programar la línea que hace la unión izquierda sobre `ozono`.

*Para ir más lejos.* Por un error de carga, la tabla `pm` tiene dos filas con hora
10:00 (pm25 = 15 y pm25 = 16).

f) Contar las filas de la unión interna.
g) Decidir si la unión avisa del error.
