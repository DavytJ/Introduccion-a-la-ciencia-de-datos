# -*- coding: utf-8 -*-
"""
Clase 3 — Práctico A: del diccionario al archivo  —  SOLUCIONES
Construir un dataset: el tipo, la restricción y la documentación
Joselina Davyt-Colo — Facultad de Ciencias Empresariales y Economía — Universidad de Montevideo

En la clase 2 construimos un DataFrame a partir de la dinámica de la caja
negra. Ese DataFrame vivía en memoria: al cerrar la sesión desapareció.

Un dataset recién existe como objeto compartible cuando se escribe en un
archivo. Antes de escribirlo hay tres decisiones que nadie más va a poder
tomar después: de qué tipo es cada variable, qué valores admite el proceso que
la generó, y cómo se documenta el instrumento que la midió.

Este práctico cubre el tramo de ida: del diccionario de Python al archivo en
disco. El tramo de vuelta —leer archivos escritos por otros, sin
documentación— es el práctico B.

CÓMO SE LEE ESTE ARCHIVO
------------------------
Los encabezados son los mismos del archivo de ejercicios. El rótulo «Se
verifica» funciona acá como lista de corrección. Los comentarios numerados
—# 1., # 2.— marcan qué líneas resuelven cada COMPLETAR del enunciado.

No requiere ningún archivo previo: todo lo que se lee acá lo escribe este
mismo script. El ejercicio 4 usa parquet y necesita `pip install pyarrow`.
"""

import pandas as pd
import numpy as np
from pathlib import Path

CARPETA = Path("datos")
CARPETA.mkdir(exist_ok=True)


# ===========================================================================
# EJERCICIO 1. DEL DICCIONARIO AL DATAFRAME: EL TIPO ES UNA DECISIÓN DE MEDICIÓN
# ===========================================================================
#
# Qué se busca
#   Declarar explícitamente el tipo de cada variable, en vez de aceptar el que
#   pandas adivina.
#
# Ya está escrito
#   El diccionario datos_caja de la clase 2, convertido en DataFrame, y la
#   línea final de verificación.
#
# Se pide
#   1. textura como categórica nominal.
#   2. rigidez como categórica ordenada: blando < medio < rígido.
#   3. certeza_observador como categórica ordenada de 1 a 5.
#
# Se verifica
#   .dtypes no devuelve ninguna columna de texto genérico, y la comparación
#   df["rigidez"] > "blando" selecciona seis observaciones sin dar error.
#
# En la bitácora
#   En num_aristas, un objeto esférico tiene 0. ¿Ese cero es una medición o es
#   un «no aplica»? ¿Cambia la respuesta si el observador no supo contar las
#   aristas?

datos_caja = {
    "objeto_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "textura": ["suave", "rugoso", "poroso", "suave", "rugoso",
                "suave", "poroso", "rugoso", "suave", "poroso"],
    "rigidez": ["blando", "rígido", "medio", "blando", "rígido",
                "rígido", "blando", "medio", "medio", "blando"],
    "num_aristas": [0, 8, 0, 4, 12, 0, 0, 6, 4, 0],
    "peso_estimado_g": [45.0, 120.5, 15.0, 85.0, 210.0,
                        35.0, 18.5, 95.0, 70.0, 22.0],
    "certeza_observador": [5, 4, 3, 5, 4, 2, 4, 3, 4, 3],
}

df = pd.DataFrame(datos_caja)

# 1. textura: nominal, conjunto cerrado sin orden
df["textura"] = df["textura"].astype("category")

# 2. rigidez: el orden se declara, no se deduce del alfabeto
df["rigidez"] = pd.Categorical(
    df["rigidez"], categories=["blando", "medio", "rígido"], ordered=True
)

# 3. certeza: la escala incluye el 1, aunque no aparezca en los datos
df["certeza_observador"] = pd.Categorical(
    df["certeza_observador"], categories=[1, 2, 3, 4, 5], ordered=True
)

print(df.dtypes)

# El orden habilita comparaciones que en una nominal no tendrían sentido:
print("\nObservaciones con rigidez mayor a 'blando':")
print(df.loc[df["rigidez"] > "blando", ["objeto_id", "rigidez"]])

# --- Discusión ------------------------------------------------------------
# Declarar `rigidez` como ordenada no es cosmético: habilita `>` y
# `sort_values()` con el orden correcto, e impide que el promedio de una
# escala ordinal se calcule por descuido. Sobre `num_aristas`: el `0` de una
# esfera y el `0` de un observador que no supo contar son el mismo número y
# dos mediciones distintas. Si no se distinguen en el momento de crear el
# dataset, ya no se pueden distinguir después.


# ===========================================================================
# EJERCICIO 2. LAS RESTRICCIONES DEL DGP, ESCRITAS COMO CÓDIGO
# ===========================================================================
#
# Qué se busca
#   Convertir supuestos implícitos sobre la medición en verificaciones que la
#   máquina pueda correr sola.
#
# Ya está escrito
#   df_roto, una copia del dataset con tres errores introducidos a propósito,
#   el esqueleto de la función validar() y sus dos llamadas.
#
# Se pide
#   1. El peso es estrictamente positivo.
#   2. La certeza está entre 1 y 5.
#   3. num_aristas es un conteo no negativo.
#   4. objeto_id no tiene repetidos.
#   Cada verificación agrega un texto a la lista `problemas` en lugar de
#   detener la ejecución: la función tiene que llegar hasta el final y
#   devolver todos los problemas de una sola pasada.
#
# Se verifica
#   validar(df) devuelve una lista vacía y validar(df_roto) devuelve
#   exactamente tres problemas, uno por cada error introducido.

df_roto = df.copy()
df_roto.loc[0, "peso_estimado_g"] = -12.0
df_roto.loc[3, "num_aristas"] = -1
df_roto.loc[7, "objeto_id"] = 1


def validar(datos):
    """Devuelve una lista de problemas. Lista vacía = dataset válido."""
    problemas = []

    # 1.
    n = (datos["peso_estimado_g"] <= 0).sum()
    if n:
        problemas.append(f"{n} peso(s) no positivo(s)")

    # 2. la columna es categórica: hay que convertirla antes de comparar
    certeza = pd.to_numeric(datos["certeza_observador"], errors="coerce")
    n = (~certeza.between(1, 5)).sum()
    if n:
        problemas.append(f"{n} valor(es) de certeza fuera de 1-5")

    # 3.
    n = (datos["num_aristas"] < 0).sum()
    if n:
        problemas.append(f"{n} conteo(s) de aristas negativo(s)")

    # 4.
    n = datos["objeto_id"].duplicated().sum()
    if n:
        problemas.append(f"{n} objeto_id repetido(s)")

    return problemas


print("df       ->", validar(df))
print("df_roto  ->", validar(df_roto))

# --- Discusión ------------------------------------------------------------
# Un `assert` corta la ejecución en el primer error y oculta los demás.
# Devolver la lista completa permite ver el estado real del dataset de una
# sola pasada. Estas cuatro líneas son la primera versión del control de
# calidad que cada equipo va a necesitar sobre su propia estructura de datos:
# la restricción no la impone pandas, la impone el proceso que generó el dato.


# ===========================================================================
# EJERCICIO 3. EL DICCIONARIO DE VARIABLES
# ===========================================================================
#
# Qué se busca
#   Documentar el instrumento de medición junto con el dato, para que el
#   archivo le sirva a alguien que no estuvo en la clase.
#
# Ya está escrito
#   La primera fila, la de peso_estimado_g, como modelo de las demás, y la
#   escritura del archivo.
#
# Se pide
#   1. Agregar una fila por cada una de las cinco variables restantes:
#      objeto_id, textura, rigidez, num_aristas y certeza_observador. En
#      `instrumento` va cómo se obtuvo el valor, no qué significa: el
#      procedimiento, su duración y sus condiciones.
#
# Se verifica
#   datos/diccionario_variables.csv tiene seis filas y seis columnas, y
#   ninguna celda de la columna `faltante` quedó vacía.
#
# En la bitácora
#   ¿Qué columna del diccionario habría evitado el problema del 0 en
#   num_aristas del ejercicio 1?

# 1. una fila por variable, con las mismas seis claves
diccionario = pd.DataFrame([
    {"variable": "objeto_id", "tipo": "identificador",
     "unidad": "—", "instrumento": "asignado por la cátedra antes de la dinámica",
     "rango_valido": "entero único", "faltante": "no admite"},
    {"variable": "textura", "tipo": "categórica nominal",
     "unidad": "—", "instrumento": "percepción táctil, vocabulario cerrado de 3 opciones",
     "rango_valido": "suave | rugoso | poroso", "faltante": "s/d"},
    {"variable": "rigidez", "tipo": "categórica ordinal",
     "unidad": "—", "instrumento": "presión manual, escala de 3 niveles",
     "rango_valido": "blando < medio < rígido", "faltante": "s/d"},
    {"variable": "num_aristas", "tipo": "numérica discreta",
     "unidad": "conteo", "instrumento": "recorrido táctil del perímetro",
     "rango_valido": ">= 0", "faltante": "vacío (distinto de 0)"},
    {"variable": "peso_estimado_g", "tipo": "numérica continua",
     "unidad": "gramos", "instrumento": "estimación táctil del observador, 15 s",
     "rango_valido": "> 0", "faltante": "vacío"},
    {"variable": "certeza_observador", "tipo": "categórica ordinal",
     "unidad": "escala 1-5", "instrumento": "autorreporte posterior a la medición",
     "rango_valido": "1 <= x <= 5", "faltante": "vacío"},
])

diccionario.to_csv(CARPETA / "diccionario_variables.csv",
                   index=False, encoding="utf-8")
print(diccionario[["variable", "tipo", "rango_valido", "faltante"]])

# --- Discusión ------------------------------------------------------------
# La columna `faltante` es la que resuelve el problema del ejercicio 1: al
# declarar que en `num_aristas` el faltante se codifica como celda vacía y no
# como `0`, el cero recupera un significado único. El diccionario de variables
# es lo que convierte un archivo en un dataset reutilizable por alguien que no
# estuvo en la clase.


# ===========================================================================
# EJERCICIO 4. EL VIAJE DE IDA Y VUELTA: QUÉ SE PIERDE AL GUARDAR
# ===========================================================================
#
# Qué se busca
#   Comprobar que el CSV no conserva los tipos declarados en el ejercicio 1.
#
# Ya está escrito
#   Una escritura deliberadamente incompleta, su relectura, y las
#   comparaciones que muestran las dos pérdidas.
#
# Se pide
#   1. Reescribir el CSV sin la columna de índice.
#   2. Reconstruir rigidez como categórica ordenada después de leer.
#   3. Hacer el mismo viaje con .to_parquet() y .read_parquet(), y comparar.
#
# Se verifica
#   Antes de corregir: aparece una columna 'Unnamed: 0' que no estaba, y
#   rigidez volvió a ser texto. Después de corregir: las columnas releídas
#   coinciden con las originales y rigidez vuelve a ser 'category'. En
#   parquet, .cat.ordered devuelve True sin reconstruir nada.

# --- ida ---
df.to_csv(CARPETA / "caja_negra_mio.csv")
df_leido = pd.read_csv(CARPETA / "caja_negra_mio.csv")

print("columnas releídas  :", list(df_leido.columns))   # aparece 'Unnamed: 0'
print("rigidez releída    :", df_leido["rigidez"].dtype)  # ya no es categórica
print()

# --- corrección ---
# 1. sin la columna de índice
df.to_csv(CARPETA / "caja_negra_mio.csv", index=False, encoding="utf-8")

# 2. el orden no está en el archivo: se vuelve a declarar acá

ORDEN_RIGIDEZ = ["blando", "medio", "rígido"]
df_ok = pd.read_csv(CARPETA / "caja_negra_mio.csv", encoding="utf-8")
df_ok["rigidez"] = pd.Categorical(df_ok["rigidez"],
                                  categories=ORDEN_RIGIDEZ, ordered=True)
df_ok["textura"] = df_ok["textura"].astype("category")

print("tras corregir      :", list(df_ok.columns))
print("rigidez            :", df_ok["rigidez"].dtype)
print()

# --- el mismo viaje en parquet ---
# 3. parquet sí conserva el tipo ordenado
df.to_parquet(CARPETA / "caja_negra_mio.parquet")
df_pq = pd.read_parquet(CARPETA / "caja_negra_mio.parquet")

print("parquet, rigidez   :", df_pq["rigidez"].dtype)
print("parquet, ordenada  :", df_pq["rigidez"].cat.ordered)

# --- Discusión ------------------------------------------------------------
# El CSV guarda texto: no tiene dónde anotar que `rigidez` era ordenada ni que
# `blando` precede a `medio`. Esa información vive en el código que lee el
# archivo, no en el archivo. Parquet sí la conserva, pero no se abre con Excel
# ni se lee a ojo. La elección entre ambos no es técnica sino de destinatario:
# quién va a abrir ese archivo y con qué.
