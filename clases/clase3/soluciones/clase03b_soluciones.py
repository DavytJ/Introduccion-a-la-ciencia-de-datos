# -*- coding: utf-8 -*-
"""
Clase 3 — Práctico B: del archivo al DataFrame  —  SOLUCIONES
El archivo como instrumento: separador, decimal, codificación y faltantes
Joselina Davyt-Colo — Facultad de Ciencias Empresariales y Economía — Universidad de Montevideo

El práctico A terminó con un archivo escrito por nosotros, con decisiones que
tomamos y documentamos. Este empieza donde empieza el trabajo real: con
archivos escritos por otros, sin documentación, cuyas decisiones hay que
reconstruir.

Un archivo es, él mismo, un instrumento de medición: tiene una codificación,
un separador, una convención decimal y una forma de representar lo que falta.
Si esas decisiones no se registran, el archivo deja de ser un registro fiel
del DGP y pasa a ser una fuente propia de error.

Cada ejercicio está construido alrededor de algo que falla. De los cuatro
archivos, uno falla con un mensaje de error y tres fallan en silencio: se leen
sin protestar y entregan datos corridos. El objetivo no es evitar el error
sino saber leerlo, y sobre todo detectarlo cuando no lo hay.

CÓMO SE LEE ESTE ARCHIVO
------------------------
Los encabezados son los mismos del archivo de ejercicios. El rótulo «Se
verifica» funciona acá como lista de corrección. Los comentarios numerados
—# 1., # 2.— marcan qué líneas resuelven cada COMPLETAR del enunciado.

Antes de empezar, ejecutar una sola vez el generador de archivos:

    py generar_archivos.py          (Windows)
    python3 generar_archivos.py     (Mac / Linux)

Crea la carpeta `datos/` con cuatro archivos. Tres están deliberadamente mal
formados. Para clasificar los mensajes que aparezcan, usar el catálogo del
anexo de errores de la clase 3.
"""

import pandas as pd
from pathlib import Path


# ===========================================================================
# EJERCICIO 5. EL CSV QUE ARMÓ EXCEL
# ===========================================================================
#
# Qué se busca
#   Diagnosticar y corregir las tres decisiones de formato que trae un archivo
#   exportado desde Excel en español: separador, decimal y codificación.
#
# Ya está escrito
#   El intento ingenuo, envuelto en try/except para que imprima el error sin
#   detener el script.
#
# Se pide
#   1. Leer el archivo con los tres argumentos correctos.
#   2. Verificar que peso_estimado_g quedó numérica y no texto.
#   3. Leerlo otra vez sin declarar el decimal y comparar los dos tipos.
#   Antes de escribir nada, abrir el archivo con un editor de texto —no con
#   Excel— y mirar cuál es el separador de columnas y cuál el decimal.
#
# Se verifica
#   Con los tres argumentos, peso_estimado_g es float64. Sin declarar el
#   decimal, la misma columna queda como texto y el archivo se lee igual, sin
#   ningún mensaje.
#
# En la bitácora
#   Copiar el mensaje de error completo del intento ingenuo e identificar a
#   qué causa del anexo corresponde. Después: omitir decimal=',' ¿habría hecho
#   fallar el código o lo habría dejado seguir con datos mal tipados?

RUTA_EXCEL = "datos/caja_negra_excel.csv"

try:
    pd.read_csv(RUTA_EXCEL)
except Exception as e:
    print(type(e).__name__, ":", e)
# UnicodeDecodeError: el byte 0xed de "rígido" no es UTF-8 válido

print()
# 1. los tres argumentos: separador, decimal y codificación
bueno = pd.read_csv(RUTA_EXCEL, sep=";", decimal=",", encoding="latin-1")
# 2.
print(bueno.dtypes)
print()

# 3. sin decimal="," el archivo se lee igual, pero mal tipado:
a_medias = pd.read_csv(RUTA_EXCEL, sep=";", encoding="latin-1")
print("con decimal=',' ->", bueno["peso_estimado_g"].dtype)
print("sin decimal     ->", a_medias["peso_estimado_g"].dtype)
print("media declarada correctamente:", round(bueno["peso_estimado_g"].mean(), 2))

# --- Discusión ------------------------------------------------------------
# El error de codificación es benigno porque es ruidoso: el programa se
# detiene y obliga a mirar. El error del separador decimal es el peligroso,
# porque no falla. El archivo se lee, la columna queda como texto, y el
# problema recién aparece varios pasos después, cuando un promedio devuelve un
# resultado imposible o una suma concatena cadenas. En datos uruguayos —INE,
# BCU, exportaciones de sistemas de gestión— la combinación `;` más coma
# decimal es la regla, no la excepción.


# ===========================================================================
# EJERCICIO 6. DÓNDE ESTÁ EL ARCHIVO
# ===========================================================================
#
# Qué se busca
#   Escribir rutas que funcionen en la máquina de otra persona.
#
# Ya está escrito
#   La impresión del directorio de trabajo y una ruta relativa que puede o no
#   existir según desde dónde se ejecute el script.
#
# Se pide
#   1. Verificar con .exists() que el archivo está donde se lo busca, antes de
#      intentar leerlo, y cortar con un mensaje que diga dónde se buscó y qué
#      hacer.
#   2. Construir la ruta a partir de la ubicación del propio archivo, para que
#      no dependa de la carpeta desde la que se ejecute.
#      En un script: Path(__file__).parent — en un notebook: Path.cwd()
#
# Se verifica
#   El script corre igual desde la carpeta del proyecto y desde cualquier
#   otra. Si se renombra el archivo a mano, el mensaje dice exactamente en qué
#   ruta lo buscó.
#
# En la bitácora
#   ¿Por qué una ruta como C:/Users/jodavyt/Documents/GitHub/.../caja_negra.csv
#   rompe el trabajo en equipo?

print("Directorio de trabajo:", Path.cwd())

# En un script .py:      BASE = Path(__file__).parent
# En un notebook .ipynb: BASE = Path.cwd()
# 2. la ruta se construye desde la ubicación del propio archivo
try:
    BASE = Path(__file__).parent
except NameError:
    BASE = Path.cwd()

ruta = BASE / "datos" / "caja_negra.csv"

# 1. cortar antes de leer, con un mensaje que diga dónde se buscó
if not ruta.exists():
    raise FileNotFoundError(
        f"No se encontró {ruta.name}.\n"
        f"Se buscó en: {ruta.resolve()}\n"
        f"Ejecutar primero generar_archivos.py"
    )

df_base = pd.read_csv(ruta, encoding="utf-8")
print("Cargado:", ruta.name, "->", df_base.shape)

# --- Discusión ------------------------------------------------------------
# Una ruta absoluta contiene el nombre de usuario de quien la escribió:
# `jodavyt`. En cualquier otra máquina el script falla en la primera línea. La
# ruta relativa construida desde la ubicación del propio archivo es la única
# que sobrevive al repositorio compartido. El chequeo con `.exists()` cambia
# un `FileNotFoundError` genérico por un mensaje que dice dónde se buscó y qué
# hacer.


# ===========================================================================
# EJERCICIO 7. EL -99 QUE SE LLEVA PUESTA LA MEDIA
# ===========================================================================
#
# Qué se busca
#   Detectar faltantes disfrazados de dato válido, que entran a los cálculos
#   sin producir ninguna señal.
#
# Ya está escrito
#   La lectura ingenua del archivo y su media, y el esqueleto del recorrido
#   por columnas.
#
# Se pide
#   1. Inspeccionar los valores únicos de cada columna y encontrar las cuatro
#      maneras distintas en que este archivo codifica un faltante.
#   2. Volver a leer declarando con na_values los códigos que read_csv() no
#      reconoce por su cuenta.
#   3. Comparar las dos medias y reportar .isna().sum() por columna en las dos
#      lecturas.
#
# Se verifica
#   Los cuatro códigos son -99, s/d, NA y la celda vacía. De esos, read_csv()
#   reconoce dos sin ayuda; los otros dos hay que declararlos. Las dos medias
#   difieren, y la diferencia la producen dos celdas.
#
# En la bitácora
#   La diferencia entre ambas medias, ¿es un problema de programación o un
#   problema de medición?

RUTA_FALTANTES = "datos/caja_negra_faltantes.csv"

faltantes_ingenuo = pd.read_csv(RUTA_FALTANTES)
print("Media ingenua :", round(faltantes_ingenuo["peso_estimado_g"].mean(), 2))
print()

# 1. inspección: convertimos a texto a mano para no mezclar tipos al ordenar
for col in faltantes_ingenuo.columns:
    valores = sorted({"<faltante>" if pd.isna(v) else str(v)
                      for v in faltantes_ingenuo[col]})
    print(f"{col:22s}", valores[:8])
print()

# read_csv() ya reconoce por su cuenta la celda vacía y el texto "NA":
print("Faltantes detectados sin declarar nada:")
print(faltantes_ingenuo.isna().sum(), "\n")

# 2. los que no reconoce son los códigos propios del relevamiento:
CODIGOS_FALTANTE = [-99, "-99", "s/d", "S/D"]
faltantes_declarado = pd.read_csv(RUTA_FALTANTES,
                                  na_values=CODIGOS_FALTANTE, encoding="utf-8")

# 3.
print("Media ingenua  :", round(faltantes_ingenuo["peso_estimado_g"].mean(), 2))
print("Media declarada:", round(faltantes_declarado["peso_estimado_g"].mean(), 2))
print()
print("Faltantes por columna tras declarar:")
print(faltantes_declarado.isna().sum())

# --- Discusión ------------------------------------------------------------
# De los cuatro códigos, `read_csv()` reconoce dos por su cuenta —la celda
# vacía y el texto `NA`, que están en su lista por defecto— y no reconoce los
# otros dos. El peligroso es el `-99`: es un número perfectamente válido, así
# que entra al promedio sin producir ninguna señal. La media pasa de 85,3 a
# 48,5 gramos, un sesgo del 43 % producido por dos celdas.
#
# Ninguna inspección del archivo revela que `-99` significa «no sé»; eso solo
# está en el diccionario de variables del práctico A, ejercicio 3. Es un
# problema de medición, no de programación: el error se cometió cuando alguien
# decidió codificar la ausencia como un número y no lo documentó. Es también
# la versión pequeña del argumento de Meng (2018): lo que decide la calidad de
# una estimación no es el tamaño de la muestra sino el mecanismo que determinó
# qué falta.


# ===========================================================================
# EJERCICIO 8. LECTURA A CIEGAS DEL ARCHIVO DEL EQUIPO VECINO
# ===========================================================================
#
# Qué se busca
#   Inspeccionar un archivo desconocido y reconstruir el proceso que lo
#   generó, sin documentación de por medio.
#
# Ya está escrito
#   La lectura ingenua, la inspección mínima —forma, tipos, primeras filas— y
#   la impresión de las primeras líneas del archivo crudo, para poder comparar
#   lo que dice el archivo con lo que quedó en el DataFrame.
#
# Se pide
#   1. Releer declarando el separador de miles del monto.
#   2. Normalizar los nombres de columna: minúsculas, sin espacios.
#   3. Convertir la fecha, que viene como dd/mm/aaaa.
#   4. Limpiar los espacios sobrantes de sucursal y pasarla a categórica.
#   5. Verificar el resultado con .dtypes, .describe() y el listado de
#      categorías de sucursal.
#
# Se verifica
#   El archivo dice 1.295 y la lectura ingenua carga 1,295; el 980, que no
#   lleva separador, se carga bien. Después de corregir, la fecha es
#   datetime64 y sucursal tiene tres categorías, no cuatro. Ninguno de los
#   cuatro problemas produce un mensaje de error en ningún momento.
#
# En la bitácora
#   Tres afirmaciones sobre el proceso que generó ese archivo, y una pregunta
#   que habría que hacerle al equipo que lo produjo.

RUTA_VECINO = "datos/equipo_vecino.csv"

# --- 1. lectura ingenua: no falla, pero corrompe ---
vecino_ingenuo = pd.read_csv(RUTA_VECINO, encoding="utf-8")
print("Monto leido ingenuamente:", vecino_ingenuo["Monto UYU"].head(4).tolist())
print("Media ingenua           :", round(vecino_ingenuo["Monto UYU"].mean(), 2))
print()

# --- 2. lectura correcta ---
# 1. el separador de miles se declara en la lectura
vecino = pd.read_csv(RUTA_VECINO, encoding="utf-8", thousands=".")

# 2.
vecino.columns = (vecino.columns
                  .str.strip()
                  .str.lower()
                  .str.replace(" ", "_", regex=False))

# 3. el formato se declara: dd/mm/aaaa no se adivina
vecino["fecha_operacion"] = pd.to_datetime(
    vecino["fecha_operacion"], format="%d/%m/%Y"
)

# 4.
vecino["sucursal"] = vecino["sucursal"].str.strip().astype("category")
vecino["medio_de_pago"] = vecino["medio_de_pago"].astype("category")

# 5.
print(vecino.dtypes, "\n")
print("Sucursales sin limpiar:", sorted(vecino_ingenuo["Sucursal "].unique()))
print("Sucursales limpias    :", list(vecino["sucursal"].cat.categories))
print()
print("Rango de fechas:", vecino["fecha_operacion"].min().date(),
      "a", vecino["fecha_operacion"].max().date())
print("Media correcta :", round(vecino["monto_uyu"].mean(), 2))

# --- Discusión ------------------------------------------------------------
# El monto es el caso grave: el archivo dice `1.295` y pandas carga `1,295`,
# porque interpreta el punto de miles como punto decimal. Pero `980`, que no
# lleva separador, se carga bien. La columna queda mezclando valores correctos
# y valores mil veces menores, y la media pasa de 1.471,50 a 169,28 sin un
# solo mensaje de error. `thousands="."` lo resuelve en la lectura.
#
# `sucursal` produce cuatro categorías donde hay tres, porque `Centro` y
# `Centro ` son cadenas distintas; cualquier agrupamiento por sucursal queda
# mal. La fecha como texto ordena `10/03` antes que `02/04`. Ninguno de los
# cuatro problemas genera una excepción: el archivo se lee sin protestar. Por
# eso la inspección inicial —forma, tipos, primeras filas, faltantes— tiene
# que ser un reflejo previo a cualquier análisis, y por eso conviene mirar el
# archivo crudo y no solo el DataFrame.
