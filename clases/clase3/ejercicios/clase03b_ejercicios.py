# -*- coding: utf-8 -*-
"""
Clase 3 — Práctico B: del archivo al DataFrame
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
Cada ejercicio tiene un encabezado con cinco rótulos:

    Qué se busca      el propósito del ejercicio
    Ya está escrito   el código que viene hecho; no hay que tocarlo
    Se pide           lo único que hay que escribir, numerado
    Se verifica       cómo saber que quedó bien, sin preguntarle a nadie
    En la bitácora    la pregunta que se responde por escrito

Los lugares donde hay que escribir están marcados así:

    # --- COMPLETAR 1 ---

La numeración de «Se pide» y la de los COMPLETAR es la misma.

Antes de empezar, ejecutar una sola vez el generador de archivos:

    py generar_archivos.py          (Windows)
    python3 generar_archivos.py     (Mac / Linux)

Crea la carpeta `datos/` con cuatro archivos. Tres están deliberadamente mal
formados. Para clasificar los mensajes que aparezcan, usar el catálogo del
anexo de errores de la clase 3.

A diferencia del práctico A, este archivo no corre entero hasta estar
completo: el ejercicio 5 se detiene si la lectura no está resuelta. Es
deliberado.
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

# --- intento ingenuo: registrar el error ---
try:
    malo = pd.read_csv(RUTA_EXCEL)
    print(malo.head())
except Exception as e:
    print(type(e).__name__, ":", e)

# --- COMPLETAR 1 -----------------------------------------------------------
# Leer el archivo declarando el separador de columnas, el separador decimal y
# la codificación. Guardarlo en una variable llamada `bueno`.


# --- COMPLETAR 2 -----------------------------------------------------------
# Imprimir los tipos de `bueno` y confirmar que el peso es numérico.


# --- COMPLETAR 3 -----------------------------------------------------------
# Leer el mismo archivo otra vez, ahora sin declarar el decimal, y comparar el
# tipo de peso_estimado_g en las dos lecturas.


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

ruta = Path("datos") / "caja_negra.csv"

# --- COMPLETAR 1 -----------------------------------------------------------
# Si la ruta no existe, cortar con un FileNotFoundError propio que informe la
# ruta absoluta donde se buscó y qué hay que ejecutar primero.


# --- COMPLETAR 2 -----------------------------------------------------------
# Redefinir `ruta` a partir de la ubicación del propio archivo, de manera que
# funcione desde cualquier directorio de trabajo.


df_base = pd.read_csv(ruta)
print(df_base.shape)


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
print("Media ingenua:", round(faltantes_ingenuo["peso_estimado_g"].mean(), 2))
print()

# --- COMPLETAR 1 -----------------------------------------------------------
# Para cada columna, imprimir sus valores únicos. Conviene pasarlos a texto
# antes de ordenarlos: si no, mezclar faltantes con texto da error.
for col in faltantes_ingenuo.columns:
    pass


# --- COMPLETAR 2 -----------------------------------------------------------
# Releer el archivo declarando los códigos de faltante que read_csv() no
# reconoce. Guardarlo en `faltantes_declarado`.


# --- COMPLETAR 3 -----------------------------------------------------------
# Imprimir las dos medias una debajo de la otra y los faltantes por columna en
# las dos lecturas.


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

# --- lectura ingenua ---
vecino_ingenuo = pd.read_csv(RUTA_VECINO, encoding="utf-8")
print(vecino_ingenuo.shape)
print(vecino_ingenuo.dtypes, "\n")
print(vecino_ingenuo.head())

# Comparar con el texto crudo del archivo:
print("\nPrimeras lineas del archivo tal cual:")
for linea in open(RUTA_VECINO, encoding="utf-8").read().splitlines()[:4]:
    print("   ", linea)

# --- COMPLETAR 1 -----------------------------------------------------------
# Releer el archivo declarando el separador de miles. Guardarlo en `vecino`.


# --- COMPLETAR 2 -----------------------------------------------------------
# Reemplazar los nombres de columna por versiones en minúscula, sin espacios
# al principio ni al final, y con guion bajo en lugar de espacio interno.


# --- COMPLETAR 3 -----------------------------------------------------------
# Convertir la columna de fecha a fecha real, declarando el formato dd/mm/aaaa
# en vez de dejar que pandas lo adivine.


# --- COMPLETAR 4 -----------------------------------------------------------
# Sacar los espacios sobrantes de sucursal y convertirla a categórica. Hacer
# lo mismo con el medio de pago.


# --- COMPLETAR 5 -----------------------------------------------------------
# Imprimir los tipos finales, las categorías de sucursal antes y después de
# limpiar, el rango de fechas y la media del monto en las dos lecturas.
