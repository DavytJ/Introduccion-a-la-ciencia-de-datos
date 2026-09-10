# =============================================================================
# Carga y transformación
# Ejemplo: medioambiente y aire (ozono, PM2.5, conteo vehicular) — Montevideo
# Versión Python (pandas + matplotlib) — equivalente de carga_y_transformacion.R
# =============================================================================
# Instalación (una sola vez):  pip install pandas numpy matplotlib
# Para el mapa además:         pip install geopandas folium
# =============================================================================
import runpy
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Equivalente de here::here(): sube carpetas hasta encontrar un marcador
def raiz_proyecto(marcadores=(".git", "_quarto.yml", ".here")) -> Path:
    actual = Path.cwd().resolve()
    for carpeta in [actual, *actual.parents]:
        if any((carpeta / m).exists() for m in marcadores):
            return carpeta
    return actual


RAIZ = raiz_proyecto()
CLASE = RAIZ / "clases/clase7"


# =============================================================================
# 1. Carga de datos: ejemplo medioambiente y aire
# =============================================================================
# read_csv de R detecta fechas automáticamente; pandas necesita parse_dates.

## Ozono — datos minutales de concentración de O3 en aire ambiente
ozono = pd.read_csv(CLASE / "o3_01_2024_04_2024.csv",
                    encoding="latin1", parse_dates=["fecha"])

## Material particulado menor de 2,5 micras, estaciones automáticas
pm = pd.read_csv(CLASE / "pm_2_5_01_2024_04_2024.csv",
                 encoding="latin1", parse_dates=["fecha"])

## Conteo vehicular en las principales avenidas de Montevideo
# El sistema del Centro de Gestión de Movilidad (CGM) usa analíticas de video
# para medir volúmenes vehiculares. Los detectores miden el total de vehículos
# y su clasificación por largo, por sentido de circulación, y pueden
# discriminarse por carril dentro de cada sentido.
auto = pd.read_csv(CLASE / "autoscope_04_2024_volumen.csv",
                   encoding="latin1", parse_dates=["fecha"])


# =============================================================================
# 2. Data profiling: id, nulos y duplicados
# =============================================================================

## 2.1 Información básica del dataset  (equivale a str())
ozono.info()
print(ozono.head())

## 2.2 Identificador
# Los datos se toman por estación (que tiene una ubicación geográfica, es decir,
# es una característica de la estación) y por fecha.
# El identificador podría ser la fecha: sirve para unir con otros datos.
# También podría ser la combinación de fecha y estación.

# 1- Tenemos problemas con los valores de las estaciones
print(ozono.iloc[0:10, 2])          # filas 1-10, tercera columna (índice 2)

print(ozono["estacion"].unique())

# Creamos el diccionario de traducción (Busca -> Reemplaza)
pauta_limpieza = {
    "Ã³": "o",
    "Ã±": "ni",
    "Ã¡": "á",
    "Ã©": "é",
    "Ã­": "í",
    "Ãº": "ú",
    "Ã“": "Ó",
    "Ã‘": "NI",
    "Ã":  "í",   # a veces la 'í' sola se rompe así; dejarla al final del dict
}

# Aplicamos la limpieza a la columna. El dict conserva el orden de inserción,
# así que las reglas se aplican en el mismo orden que el vector de R.
ozono_limpio = ozono.copy()
for buscar, reemplazar in pauta_limpieza.items():
    ozono_limpio["estacion"] = ozono_limpio["estacion"].str.replace(
        buscar, reemplazar, regex=False)

## 2.3 Valores faltantes  (equivale a colSums(is.na()))
print(ozono.isna().sum())

# La única variable con valores faltantes es la medición, por lo tanto se pueden
# eliminar, ya que no eliminamos identificador (podría discutirse si hay que
# eliminar fechas sin registro).

# Quito los NaN de todo el dataset:
ozono_sinna = ozono_limpio.dropna()

# Quito los NaN de columnas específicas:
ozono_sinna = ozono_limpio.dropna(subset=["o3"]).copy()

## 2.4 Duplicados
# Número total de filas repetidas en todo el dataset
print(ozono_sinna.duplicated().sum())

# Mostrar TODAS las filas involucradas en un duplicado (la primera y sus copias)
ozono_repetidas = ozono_sinna[ozono_sinna.duplicated(keep=False)]

## 2.5 Eliminar duplicados
# Conserva solo la primera aparición de cada fila única
dataset_sindup = ozono_sinna.drop_duplicates()

# Duplicados según una sola columna, conservando el resto del primer registro
dataset_sindup_columna = ozono_sinna.drop_duplicates(subset=["estacion"])


# =============================================================================
# 3. Tipos de datos y transformación de datos
# =============================================================================

## 3.1 Fechas
# El equivalente de POSIXct en pandas es datetime64[ns]: internamente un entero
# de 64 bits (nanosegundos desde el 1 de enero de 1970), lo que hace muy rápidas
# las operaciones aritméticas entre fechas.
print(ozono["fecha"].dtype)

# Si la columna no se hubiera parseado al leer:
# ozono["fecha"] = pd.to_datetime(ozono["fecha"])

## 3.2 Crear variables  (el accesor .dt cumple el rol de lubridate)
ozono_new = ozono_sinna.assign(
    anio=lambda d: d["fecha"].dt.year,
    mes=lambda d: d["fecha"].dt.month,
    hora=lambda d: d["fecha"].dt.hour,
)


# =============================================================================
# 4. Generación de información
# =============================================================================

## 4.1 Agregación mensual
ozono_mes = (
    ozono_new.groupby("mes")
    .agg(o3_medio_mes=("o3", "mean"), n_registros_mes=("o3", "size"))
    .reset_index()
)
print(ozono_mes)

## 4.2 Visualización
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(ozono_mes["mes"], ozono_mes["o3_medio_mes"],
        color="blue", linewidth=2)                        # línea
ax.scatter(ozono_mes["mes"], ozono_mes["o3_medio_mes"],
           color="red", s=60, zorder=3)                   # puntos
ax.set(title="Concentración de Ozono en el ambiente, por mes, 2024",
       xlabel="Fecha", ylabel="Valores")
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
plt.tight_layout()
plt.show()

# Partes básicas de un gráfico:
#   - dataset
#   - variable eje x
#   - variable eje y
#   - tipo de gráfico
#   - títulos: del gráfico y nombres de los ejes


# =============================================================================
# 5. Análisis profundo: agregación temporal minutal -> horario -> diario
# =============================================================================
# Pregunta central: al agregar, ¿qué estadístico representa el fenómeno?
#   - media: nivel típico
#   - máximo: episodios puntuales (sensible a errores del sensor)
#   - percentil 95: episodios altos pero robusto a picos aislados
#   - n: cuántos minutos respaldan el valor agregado (cobertura)


def p95(x):
    return x.quantile(0.95)


## 5.1 Horario
# pd.Grouper(freq=...) cumple el rol de floor_date() + group_by()
ozono_hora = (
    ozono_sinna
    .groupby(["estacion", pd.Grouper(key="fecha", freq="h")])["o3"]
    .agg(media="mean", maximo="max", p95=p95, n_min="size")   # n_min: máx 60
    .reset_index()
    .rename(columns={"fecha": "fecha_hora"})
)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(ozono_hora["fecha_hora"], ozono_hora["media"], color="blue", linewidth=1)
ax.scatter(ozono_hora["fecha_hora"], ozono_hora["media"], color="red", s=4, zorder=3)
ax.set(title="Concentración de Ozono en el ambiente, por hora, 2024",
       xlabel="Fecha", ylabel="Valores")
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
plt.tight_layout()
plt.show()


# =============================================================================
# 6. Teoría estadística
# =============================================================================
# Los paneles se construyen en un script aparte, que guarda las dos figuras.
# runpy.run_path es el equivalente de source() de R.
runpy.run_path(str(CLASE / "estadistica_basica.py"))

# Densidad:  h_i = f_i / a_i


# =============================================================================
# 7. Diario
# =============================================================================
ozono_dia = (
    ozono_sinna
    .groupby(["estacion", pd.Grouper(key="fecha", freq="D")])["o3"]
    .agg(media="mean", maximo="max", p95=p95, n_min="size")   # n_min: máx 1440
    .reset_index()
    .rename(columns={"fecha": "dia"})
)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(ozono_dia["dia"], ozono_dia["media"], color="blue", linewidth=1)
ax.scatter(ozono_dia["dia"], ozono_dia["media"], color="red", s=4, zorder=3)
ax.set(title="Concentración de Ozono en el ambiente, por hora, 2024",
       xlabel="Fecha", ylabel="Valores")
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
plt.tight_layout()
plt.show()

# Las tres curvas cuentan historias distintas sobre el mismo día
estaciones = ozono_dia["estacion"].unique()
fig, axes = plt.subplots(len(estaciones), 1, figsize=(9, 3 * len(estaciones)),
                         sharex=True, squeeze=False)
for ax, est in zip(axes[:, 0], estaciones):
    d = ozono_dia[ozono_dia["estacion"] == est]
    for col in ("media", "p95", "maximo"):
        ax.plot(d["dia"], d[col], label=col)
    ax.set_title(est)
    ax.set_ylabel("O3 (µg/m³)")
    ax.grid(alpha=0.3)
axes[0, 0].legend()
fig.suptitle("Agregación diaria: media, p95 y máximo por estación")
plt.tight_layout()
plt.show()


# =============================================================================
# 8. El estadístico normativo: máximo diario de la media móvil de 8 horas
# =============================================================================
# Las guías OMS (2021) para O3 usan el máximo diario de la media móvil de 8 h.
# Una media móvil requiere una grilla horaria COMPLETA: si faltan horas, la
# ventana de 8 posiciones deja de ser una ventana de 8 horas.

grilla_horaria = pd.date_range(ozono_hora["fecha_hora"].min(),
                               ozono_hora["fecha_hora"].max(), freq="h")

# reindex sobre la grilla completa por estación = tidyr::complete()
ozono_8h = (
    ozono_hora
    .set_index("fecha_hora")
    .groupby("estacion")["media"]
    .apply(lambda s: s.reindex(grilla_horaria))     # inserta NaN en horas ausentes
    .rename_axis(["estacion", "fecha_hora"])
    .reset_index()
)
# rolling(8, min_periods=8): si falta alguna de las 8 horas, el resultado es NaN,
# igual que stats::filter con NA en la ventana.
ozono_8h["media_8h"] = (
    ozono_8h.groupby("estacion")["media"]
    .transform(lambda s: s.rolling(8, min_periods=8).mean())
)

max_8h_dia = (
    ozono_8h
    .assign(dia=lambda d: d["fecha_hora"].dt.floor("D"))
    .groupby(["estacion", "dia"])["media_8h"]
    .agg(max_8h="max", horas_validas="count")   # max ignora NaN; count no los cuenta
    .reset_index()
)

fig, ax = plt.subplots(figsize=(9, 5))
for est, d in max_8h_dia.groupby("estacion"):
    ax.plot(d["dia"], d["max_8h"], label=est)
ax.axhline(100, linestyle="--", color="black")   # guía OMS 2021: 100 µg/m³
ax.set(title="Máximo diario de la media móvil de 8 h", ylabel="O3 (µg/m³)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# =============================================================================
# 9. Mapa
# =============================================================================
runpy.run_path(str(CLASE / "mapa.py"))


# =============================================================================
# 10. Patrones de faltantes
# =============================================================================
# Tres tipos de faltante en una serie de sensor:
#   a) explícito: la fila existe, o3 es NaN
#   b) en rachas: muchos NaN consecutivos -> sensor caído o en mantenimiento
#   c) implícito: la fila no existe (el minuto no está en el archivo)
# Eliminar NaN sin mirar esto borra evidencia sobre el proceso de medición.

## 10.1 Faltantes explícitos por estación
resumen_na = (
    ozono_limpio.groupby("estacion")["o3"]
    .agg(n_filas="size",
         n_na=lambda s: s.isna().sum(),
         prop_na=lambda s: s.isna().mean())
    .reset_index()
)
print(resumen_na)

## 10.2 ¿Cuándo faltan? Proporción de NaN por día
na_dia = (
    ozono_limpio
    .assign(es_na=lambda d: d["o3"].isna())
    .groupby(["estacion", pd.Grouper(key="fecha", freq="D")])["es_na"]
    .mean()
    .rename("prop_na").reset_index()
    .rename(columns={"fecha": "dia"})
)

estaciones = na_dia["estacion"].unique()
fig, axes = plt.subplots(len(estaciones), 1, figsize=(9, 2.5 * len(estaciones)),
                         sharex=True, squeeze=False)
for ax, est in zip(axes[:, 0], estaciones):
    d = na_dia[na_dia["estacion"] == est]
    ax.bar(d["dia"], d["prop_na"], color="grey", width=1)
    ax.set_title(est)
    ax.set_ylabel("Proporción de NaN")
fig.suptitle("Proporción de minutos sin dato, por día y estación")
plt.tight_layout()
plt.show()


## 10.3 Rachas de NaN consecutivos (equivalente de rle())
def rachas_na(s: pd.Series) -> pd.DataFrame:
    es_na = s.isna().to_numpy()
    # cada cambio de valor abre una racha nueva
    id_racha = np.concatenate([[0], np.cumsum(es_na[1:] != es_na[:-1])])
    return (pd.DataFrame({"faltante": es_na, "id_racha": id_racha})
            .groupby("id_racha")
            .agg(faltante=("faltante", "first"), largo=("faltante", "size"))
            .reset_index(drop=True))


rachas = (
    ozono_limpio.sort_values(["estacion", "fecha"])
    .groupby("estacion")["o3"]
    .apply(rachas_na)
    .reset_index(level=0)
    .reset_index(drop=True)
)

tabla_rachas = (
    rachas[rachas["faltante"]]
    .assign(tipo=lambda d: pd.cut(
        d["largo"], bins=[0, 1, 10, 60, 1440, np.inf],
        labels=["1 min", "2-10 min", "11 min-1 h", "1 h-1 día", "> 1 día"]))
    .groupby(["estacion", "tipo"], observed=True).size()
    .rename("n_rachas").reset_index()
)
print(tabla_rachas)

## 10.4 Faltantes implícitos: minutos que no están en el archivo
implicitos = (
    ozono_limpio.groupby("estacion")["fecha"]
    .agg(primero="min", ultimo="max", presentes="nunique")
    .assign(
        esperados=lambda d: ((d["ultimo"] - d["primero"])
                             / pd.Timedelta(minutes=1)).astype(int) + 1,
        implicitos=lambda d: d["esperados"] - d["presentes"],
        prop_implicitos=lambda d: d["implicitos"] / d["esperados"],
    )
    .reset_index()
)
print(implicitos)

## 10.5 Cobertura contra la grilla del período pedido
INICIO = pd.Timestamp("2024-01-01 00:00:00")
FIN    = pd.Timestamp("2024-04-30 23:59:00")
ESPERADOS = int((FIN - INICIO) / pd.Timedelta(minutes=1)) + 1

cobertura = (
    ozono_limpio.groupby("estacion")
    .agg(presentes=("fecha", "nunique"),
         validos=("o3", "count"))          # count no cuenta los NaN
    .assign(
        esperados=ESPERADOS,
        sin_fila=lambda d: d["esperados"] - d["presentes"],
        fila_sin_medicion=lambda d: d["presentes"] - d["validos"],
        cobertura=lambda d: 100 * (d["validos"] / d["esperados"]).round(3),
    )
    .reset_index()
)
print(cobertura)
