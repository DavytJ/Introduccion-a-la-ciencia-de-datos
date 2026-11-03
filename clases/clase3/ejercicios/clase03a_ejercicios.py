# -*- coding: utf-8 -*-
"""
Clase 3 — Práctico A: del diccionario al archivo
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
Cada ejercicio tiene un encabezado con cinco rótulos:

    Qué se busca      el propósito del ejercicio
    Ya está escrito   el código que viene hecho; no hay que tocarlo
    Se pide           lo único que hay que escribir, numerado
    Se verifica       cómo saber que quedó bien, sin preguntarle a nadie
    En la bitácora    la pregunta que se responde por escrito

Los lugares donde hay que escribir están marcados así:

    # --- COMPLETAR 1 ---

La numeración de «Se pide» y la de los COMPLETAR es la misma. El archivo corre
de arriba abajo aunque no esté completo: los `print` van a mostrar el estado
sin resolver, que también sirve para ver qué falta.

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

# --- COMPLETAR 1 -----------------------------------------------------------
# Convertir textura en categórica nominal: conjunto cerrado de valores, sin
# orden entre ellos. Resuelto cuando df["textura"].dtype dice 'category'.


# --- COMPLETAR 2 -----------------------------------------------------------
# Convertir rigidez en categórica ordenada. El orden hay que declararlo: no es
# el alfabético. Resuelto cuando df["rigidez"] > "blando" no da error.


# --- COMPLETAR 3 -----------------------------------------------------------
# Convertir certeza_observador en categórica ordenada de 1 a 5, incluyendo el
# 1, que no aparece en los datos pero sí en la escala.


print(df.dtypes)


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

    # --- COMPLETAR 1 -------------------------------------------------------
    # Contar los pesos que no son estrictamente positivos y, si hay alguno,
    # agregar a `problemas` un texto que diga cuántos son.


    # --- COMPLETAR 2 -------------------------------------------------------
    # Contar los valores de certeza fuera del rango 1-5. Atención: después del
    # ejercicio 1 la columna es categórica, no numérica; hay que convertirla
    # antes de comparar.


    # --- COMPLETAR 3 -------------------------------------------------------
    # Contar los conteos de aristas negativos.


    # --- COMPLETAR 4 -------------------------------------------------------
    # Contar los objeto_id repetidos.


    return problemas


print("df       ->", validar(df))
print("df_roto  ->", validar(df_roto))


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

diccionario = pd.DataFrame([
    {
        "variable": "peso_estimado_g",
        "tipo": "numérica continua",
        "unidad": "gramos",
        "instrumento": "estimación táctil del observador, 15 s, sin ver el objeto",
        "rango_valido": "> 0",
        "faltante": "vacío",
    },

    # --- COMPLETAR 1 -------------------------------------------------------
    # Cinco diccionarios más, uno por variable, con las mismas seis claves.

])

diccionario.to_csv(CARPETA / "diccionario_variables.csv",
                   index=False, encoding="utf-8")
print(diccionario)


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
df.to_csv(CARPETA / "caja_negra_mio.csv")          # falta un argumento

# --- vuelta ---
df_leido = pd.read_csv(CARPETA / "caja_negra_mio.csv")

print("columnas originales:", list(df.columns))
print("columnas releídas  :", list(df_leido.columns))
print()
print("rigidez original :", df["rigidez"].dtype)
print("rigidez releída  :", df_leido["rigidez"].dtype)

# --- COMPLETAR 1 -----------------------------------------------------------
# Volver a escribir el CSV, esta vez sin que el índice se guarde como columna.


# --- COMPLETAR 2 -----------------------------------------------------------
# Leerlo de nuevo y devolverle a rigidez su tipo ordenado. El orden no está en
# el archivo: hay que volver a declararlo acá.


# --- COMPLETAR 3 -----------------------------------------------------------
# Escribir y releer el mismo DataFrame en parquet, y comprobar si el tipo
# ordenado sobrevivió sin reconstruirlo.
