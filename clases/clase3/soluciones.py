# -*- coding: utf-8 -*-
"""
Clase 3 — Práctico: crear un dataset y volver a cargarlo  —  SOLUCIONES
Del diccionario al archivo y del archivo al DataFrame: qué sobrevive al viaje
Joselina Davyt-Colo — Facultad de Ciencias Empresariales y Economía — Universidad de Montevideo

En la clase 2 construimos un DataFrame a partir de la dinámica de la caja
negra. Ese DataFrame vivía en memoria: al cerrar la sesión desapareció.

Un dataset recién existe como objeto compartible cuando se escribe en un
archivo. Y ese archivo es, él mismo, un instrumento de medición: tiene una
codificación, un separador, una convención decimal y una forma de representar
lo que falta. Si esas decisiones no se registran, el archivo deja de ser un
registro fiel del DGP y pasa a ser una fuente propia de error.

Este práctico recorre ese viaje de ida y vuelta. Cada ejercicio está
construido alrededor de algo que falla; el objetivo no es evitar el error sino
saber leerlo.

Antes de empezar, ejecutar una sola vez el generador de archivos:

    py generar_archivos.py          (Windows)
    python3 generar_archivos.py     (Mac / Linux)

Crea la carpeta `datos/` con cuatro archivos. Tres están deliberadamente mal
formados.
"""

# ===========================================================================
# EJERCICIO 1. DEL DICCIONARIO AL DATAFRAME: EL TIPO ES UNA DECISIÓN DE MEDICIÓN
# ===========================================================================
#
# Objetivo: Declarar explícitamente el tipo de cada variable y justificarlo.
#
# 1. Reconstruir el diccionario datos_caja de la clase 2 y pasarlo a
#    DataFrame.
# 2. Declarar textura como categórica nominal y rigidez como categórica
#    ordenada (blando < medio < rígido).
# 3. Declarar certeza_observador como categórica ordenada de 1 a 5.
# 4. Verificar con .dtypes que ninguna columna quedó como texto genérico.
# 5. Responder en la bitácora: en num_aristas, un objeto esférico tiene 0.
#    ¿Ese cero es una medición o es un «no aplica»? ¿Cambia la respuesta si el
#    observador no supo contar las aristas?

import pandas as pd
import numpy as np

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

df["textura"] = df["textura"].astype("category")

df["rigidez"] = pd.Categorical(
    df["rigidez"], categories=["blando", "medio", "rígido"], ordered=True
)

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
# Objetivo: Convertir supuestos implícitos sobre la medición en verificaciones ejecutables.
#
# 1. Escribir cuatro verificaciones que codifiquen restricciones del proceso
#    de medición: el peso es estrictamente positivo; la certeza está entre 1 y
#    5; num_aristas es un entero no negativo; objeto_id no tiene repetidos.
# 2. Envolverlas en una función validar(df) que devuelva la lista de problemas
#    encontrados en lugar de detenerse en el primero.
# 3. Probarla con el DataFrame correcto y después con df_roto, que tiene tres
#    errores introducidos a propósito.

df_roto = df.copy()
df_roto.loc[0, "peso_estimado_g"] = -12.0
df_roto.loc[3, "num_aristas"] = -1
df_roto.loc[7, "objeto_id"] = 1


def validar(datos):
    """Devuelve una lista de problemas. Lista vacía = dataset válido."""
    problemas = []

    n = (datos["peso_estimado_g"] <= 0).sum()
    if n:
        problemas.append(f"{n} peso(s) no positivo(s)")

    certeza = pd.to_numeric(datos["certeza_observador"], errors="coerce")
    n = (~certeza.between(1, 5)).sum()
    if n:
        problemas.append(f"{n} valor(es) de certeza fuera de 1-5")

    n = (datos["num_aristas"] < 0).sum()
    if n:
        problemas.append(f"{n} conteo(s) de aristas negativo(s)")

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
# Objetivo: Documentar el instrumento de medición junto con el dato.
#
# 1. Construir un segundo DataFrame, diccionario, con una fila por variable y
#    las columnas: variable, tipo, unidad, instrumento, rango_valido,
#    faltante.
# 2. En instrumento describir cómo se obtuvo el valor (por ejemplo:
#    «estimación táctil del observador, 15 segundos, sin ver el objeto»).
# 3. Guardarlo como datos/diccionario_variables.csv.
# 4. Responder en la bitácora: ¿qué columna del diccionario habría evitado el
#    problema del 0 en num_aristas del ejercicio 1?

from pathlib import Path

CARPETA = Path("datos")
CARPETA.mkdir(exist_ok=True)

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
# Objetivo: Comprobar que el CSV no conserva los tipos declarados.
#
# 1. Guardar df como datos/caja_negra_mio.csv sin el argumento index=False.
# 2. Volver a leerlo y comparar .dtypes y .columns con los del DataFrame
#    original.
# 3. Identificar las dos pérdidas: una columna que apareció y un tipo que se
#    degradó.
# 4. Corregir la escritura y reconstruir el tipo ordenado en la lectura.
# 5. Repetir el mismo viaje con .to_parquet() / .read_parquet() y comparar el
#    resultado (requiere pip install pyarrow).

# --- ida y vuelta ingenuas ---
df.to_csv("datos/caja_negra_mio.csv")
df_leido = pd.read_csv("datos/caja_negra_mio.csv")

print("columnas releídas  :", list(df_leido.columns))   # aparece 'Unnamed: 0'
print("rigidez releída    :", df_leido["rigidez"].dtype)  # ya no es categórica
print()

# --- corrección ---
df.to_csv("datos/caja_negra_mio.csv", index=False, encoding="utf-8")

ORDEN_RIGIDEZ = ["blando", "medio", "rígido"]
df_ok = pd.read_csv("datos/caja_negra_mio.csv", encoding="utf-8")
df_ok["rigidez"] = pd.Categorical(df_ok["rigidez"],
                                  categories=ORDEN_RIGIDEZ, ordered=True)
df_ok["textura"] = df_ok["textura"].astype("category")

print("tras corregir      :", list(df_ok.columns))
print("rigidez            :", df_ok["rigidez"].dtype)
print()

# --- el mismo viaje en parquet ---
df.to_parquet("datos/caja_negra_mio.parquet")
df_pq = pd.read_parquet("datos/caja_negra_mio.parquet")

print("parquet, rigidez   :", df_pq["rigidez"].dtype)
print("parquet, ordenada  :", df_pq["rigidez"].cat.ordered)

# --- Discusión ------------------------------------------------------------
# El CSV guarda texto: no tiene dónde anotar que `rigidez` era ordenada ni que
# `blando` precede a `medio`. Esa información vive en el código que lee el
# archivo, no en el archivo. Parquet sí la conserva, pero no se abre con Excel
# ni se lee a ojo. La elección entre ambos no es técnica sino de destinatario:
# quién va a abrir ese archivo y con qué.


# ===========================================================================
# EJERCICIO 5. EL CSV QUE ARMÓ EXCEL
# ===========================================================================
#
# Objetivo: Diagnosticar y corregir separador, decimal y codificación.
#
# 1. Intentar leer datos/caja_negra_excel.csv con pd.read_csv() sin
#    argumentos. Copiar el mensaje de error completo en la bitácora.
# 2. Abrir el archivo con un editor de texto (no con Excel) y describir qué se
#    ve: ¿cuál es el separador de columnas? ¿y el decimal?
# 3. Leerlo correctamente usando sep, decimal y encoding.
# 4. Verificar que peso_estimado_g quedó numérica y no texto.
# 5. Responder: si se hubiera leído con sep=';' pero sin decimal=',', ¿el
#    código habría fallado o habría seguido adelante con datos mal tipados?

RUTA = "datos/caja_negra_excel.csv"

try:
    pd.read_csv(RUTA)
except Exception as e:
    print(type(e).__name__, ":", e)
# UnicodeDecodeError: el byte 0xed de "rígido" no es UTF-8 válido

print()
bueno = pd.read_csv(RUTA, sep=";", decimal=",", encoding="latin-1")
print(bueno.dtypes)
print()

# Sin decimal="," el archivo se lee igual, pero mal tipado:
a_medias = pd.read_csv(RUTA, sep=";", encoding="latin-1")
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
# Objetivo: Usar rutas que funcionen en la máquina de otra persona.
#
# 1. Imprimir el directorio de trabajo actual con Path.cwd().
# 2. Verificar con .exists() que el archivo está donde se lo busca, antes de
#    intentar leerlo, y emitir un mensaje claro si no está.
# 3. Reescribir la ruta de manera que el script funcione sin importar desde
#    qué carpeta se ejecute.
# 4. Responder: ¿por qué una ruta como
#    C:/Users/jodavyt/Documents/GitHub/.../caja_negra.csv rompe el trabajo en
#    equipo?

from pathlib import Path

print("Directorio de trabajo:", Path.cwd())

# En un script .py:      BASE = Path(__file__).parent
# En un notebook .ipynb: BASE = Path.cwd()
try:
    BASE = Path(__file__).parent
except NameError:
    BASE = Path.cwd()

ruta = BASE / "datos" / "caja_negra.csv"

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
# Objetivo: Detectar faltantes disfrazados de dato válido.
#
# 1. Leer datos/caja_negra_faltantes.csv sin argumentos especiales y calcular
#    la media de peso_estimado_g.
# 2. Inspeccionar los valores únicos de cada columna y encontrar las cuatro
#    maneras distintas en que ese archivo codifica un faltante: -99, s/d, NA y
#    celda vacía.
# 3. Determinar cuáles de esas cuatro reconoce read_csv() por sí solo y cuáles
#    no.
# 4. Volver a leer declarándolas con na_values y recalcular la media.
# 5. Reportar .isna().sum() por columna.
# 6. Responder: la diferencia entre ambas medias, ¿es un problema de
#    programación o un problema de medición?

RUTA = "datos/caja_negra_faltantes.csv"

ingenuo = pd.read_csv(RUTA)
print("Media ingenua :", round(ingenuo["peso_estimado_g"].mean(), 2))
print()

# Inspección: convertimos a texto a mano para no mezclar tipos al ordenar
for col in ingenuo.columns:
    valores = sorted({"<faltante>" if pd.isna(v) else str(v) for v in ingenuo[col]})
    print(f"{col:22s}", valores[:8])
print()

# read_csv() ya reconoce por su cuenta la celda vacía y el texto "NA":
print("Faltantes detectados sin declarar nada:")
print(ingenuo.isna().sum(), "\n")

# Los que no reconoce son los códigos propios del relevamiento:
CODIGOS_FALTANTE = [-99, "-99", "s/d", "S/D"]
declarado = pd.read_csv(RUTA, na_values=CODIGOS_FALTANTE, encoding="utf-8")

print("Media ingenua  :", round(ingenuo["peso_estimado_g"].mean(), 2))
print("Media declarada:", round(declarado["peso_estimado_g"].mean(), 2))
print()
print("Faltantes por columna tras declarar:")
print(declarado.isna().sum())

# --- Discusión ------------------------------------------------------------
# De los cuatro códigos, `read_csv()` reconoce dos por su cuenta —la celda
# vacía y el texto `NA`, que están en su lista por defecto— y no reconoce los
# otros dos. El peligroso es el `-99`: es un número perfectamente válido, así
# que entra al promedio sin producir ninguna señal. La media pasa de 85,3 a
# 48,5 gramos, un sesgo del 43 % producido por dos celdas.
# 
# Ninguna inspección del archivo revela que `-99` significa «no sé»; eso solo
# está en el diccionario de variables del ejercicio 3. Es un problema de
# medición, no de programación: el error se cometió cuando alguien decidió
# codificar la ausencia como un número y no lo documentó. Es también la
# versión pequeña del argumento de Meng (2018): lo que decide la calidad de
# una estimación no es el tamaño de la muestra sino el mecanismo que determinó
# qué falta.


# ===========================================================================
# EJERCICIO 8. LECTURA A CIEGAS DEL ARCHIVO DEL EQUIPO VECINO
# ===========================================================================
#
# Objetivo: Inspeccionar un archivo desconocido y reconstruir su DGP.
#
# 1. Cargar datos/equipo_vecino.csv, un registro transaccional sin
#    documentación.
# 2. Ejecutar la inspección mínima: .shape, .dtypes, .head(), .isna().sum(),
#    .describe(include='all').
# 3. Comparar la columna de monto en el archivo de texto con lo que quedó en
#    el DataFrame. El archivo dice 1.295; ¿qué valor cargó pandas? ¿Y para
#    980?
# 4. Corregir cuatro problemas: nombres de columna con espacios y mayúsculas;
#    la fecha leída como texto; el separador de miles del monto; los espacios
#    sobrantes en sucursal, que hacen que Centro y Centro  cuenten como
#    categorías distintas.
# 5. Escribir en la bitácora tres afirmaciones sobre el proceso que generó ese
#    archivo, y una pregunta que habría que hacerle al equipo que lo produjo.

RUTA = "datos/equipo_vecino.csv"

# --- 1. lectura ingenua: no falla, pero corrompe ---
ingenuo = pd.read_csv(RUTA, encoding="utf-8")
print("Monto leido ingenuamente:", ingenuo["Monto UYU"].head(4).tolist())
print("Media ingenua           :", round(ingenuo["Monto UYU"].mean(), 2))
print()

# --- 2. lectura correcta ---
vecino = pd.read_csv(RUTA, encoding="utf-8", thousands=".")

vecino.columns = (vecino.columns
                  .str.strip()
                  .str.lower()
                  .str.replace(" ", "_", regex=False))

vecino["fecha_operacion"] = pd.to_datetime(
    vecino["fecha_operacion"], format="%d/%m/%Y"
)

vecino["sucursal"] = vecino["sucursal"].str.strip().astype("category")
vecino["medio_de_pago"] = vecino["medio_de_pago"].astype("category")

print(vecino.dtypes, "\n")
print("Sucursales sin limpiar:", sorted(ingenuo["Sucursal "].unique()))
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


# ===========================================================================
# DESAFÍO POR EQUIPO
# ===========================================================================
# Desafío por equipo (entrega en la bitácora).
# 
# Aplicar el recorrido completo a la estructura de datos del propio equipo:
# construir un dataset mínimo de diez observaciones con la variable central de
# esa estructura, escribir su diccionario de variables, guardarlo en `datos/`,
# volver a cargarlo en una sesión nueva y verificar que nada se perdió en el
# viaje.
# 
# Cada estructura tiene un punto de quiebre distinto en este recorrido;
# identificarlo es parte de la consigna.
# 
#     Equipo                     -> Punto de quiebre esperado
#     Series macroeconómicas     -> La frecuencia y el índice temporal no sobreviven al CSV
#     Microdatos de encuesta     -> El ponderador y los códigos de no respuesta
#     Sistemas transaccionales   -> El identificador, los duplicados y la zona horaria
#     Datos experimentales       -> La asignación a tratamiento y el momento de medición
#     Datos espaciales           -> El sistema de coordenadas de referencia
#     Texto a red                -> La correspondencia entre nodos y aristas, y la codificación
#     Uso de IA                  -> La marca de tiempo, la sesión y la unidad de observación
# 

# -------------------------------------------------------------------------
# Criterio de corrección. Un ejercicio está resuelto cuando otra persona puede
# ejecutar el archivo en su máquina, sin editar ninguna ruta, y obtener
# exactamente el mismo resultado. No alcanza con que funcione en la
# computadora de quien lo escribió.
