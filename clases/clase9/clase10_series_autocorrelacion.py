# =============================================================================
# Clase 10 — Series de tiempo: grilla temporal y autocorrelación
# Ozono (O3) y PM2.5 en Curva de Maroñas, ene–abr 2024
# Fuente: Catálogo de Datos Abiertos (catalogodatos.gub.uy), Intendencia de Montevideo
# Continúa la clase 9 (unión de fuentes)
# =============================================================================
# Lo nuevo de hoy:
#   1. una serie de tiempo es una columna cuyo índice es el tiempo, a paso fijo
#   2. resample: agregar por intervalos de tiempo y completar la grilla
#   3. shift: la serie corrida k pasos hacia atrás
#   4. autocorrelación: la serie correlacionada consigo misma a distintos rezagos
# =============================================================================
#%%
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

SUBCARPETA = Path.cwd() / "clases/clase7"
ESTACION = "Curva de Maronias"
PASO = "10min"          # ajustar con el diagnóstico de la sección 2
POR_HORA = 6            # cuántos pasos entran en una hora: 60 / 10

pauta_limpieza = {
    "Ã³": "o", "Ã±": "ni", "Ã¡": "á", "Ã©": "é", "Ã­": "í",
    "Ãº": "ú", "Ã“": "Ó", "Ã‘": "NI", "Ã": "í",
}


# =============================================================================
# 1. Carga (igual que la clase 8) y una serie por contaminante
# =============================================================================
def cargar(archivo):
    datos = pd.read_csv(SUBCARPETA / archivo, encoding="latin1", parse_dates=["fecha"])
    for buscar, reemplazar in pauta_limpieza.items():
        datos["estacion"] = datos["estacion"].str.replace(buscar, reemplazar, regex=False)
    return datos


ozono_limpio = cargar("o3_01_2024_04_2024.csv")
pm_limpio = cargar("pm_2_5_01_2024_04_2024.csv")

# Una estación, indexada por fecha: esto ya es una serie de tiempo
o3_s = ozono_limpio[ozono_limpio["estacion"] == ESTACION].set_index("fecha")["o3"].sort_index()
pm_s = pm_limpio[pm_limpio["estacion"] == ESTACION].set_index("fecha")["pm2_5"].sort_index()

print(o3_s.head())
print(pm_s.head())


# =============================================================================
# 2. Diagnóstico: ¿cada cuánto mide cada sensor?
# =============================================================================
# diff() entre sellos consecutivos: el valor más frecuente es el paso de muestreo.
print("Intervalo entre mediciones, O3:")
print(o3_s.index.to_series().diff().value_counts().head())
print("Intervalo entre mediciones, PM2.5:")
print(pm_s.index.to_series().diff().value_counts().head())
print("Segundos en los sellos de PM2.5:", pm_s.index.second.unique())

# Con esto se elige PASO: el intervalo más chico que garantice al menos una
# medición por caja en la serie más rala.


# =============================================================================
# 3. resample: agregar por intervalos fijos y completar la grilla
# =============================================================================
# Corta el tiempo en cajas de PASO alineadas al reloj y promedia lo que cae en
# cada una. Las dos series quedan en las mismas cajas aunque sus sellos
# originales no coincidan. Caja vacía = NaN. Esto es la unión de la clase 9,
# con el tiempo como clave y la grilla completa.
serie = pd.DataFrame({
    "o3":   o3_s.resample(PASO).mean(),
    "pm25": pm_s.resample(PASO).mean(),
    "n_o3": o3_s.resample(PASO).count(),
    "n_pm": pm_s.resample(PASO).count(),
})

print(serie.head())
print("Cajas totales:", len(serie))
print("Cajas sin dato:")
print(serie[["o3", "pm25"]].isna().sum())
print("Mediciones por caja (típico):")
print(serie[["n_o3", "n_pm"]].median())

print("Primer dato válido O3:", serie["o3"].first_valid_index())

falta = serie["o3"].isna()
bloque = (falta != falta.shift()).cumsum()
huecos = (serie[falta].groupby(bloque[falta])
          .apply(lambda g: pd.Series({"desde": g.index[0],
                                      "hasta": g.index[-1],
                                      "horas": len(g) / POR_HORA})))
print(huecos.sort_values("horas", ascending=False).head(10))


# =============================================================================
# 4. Las dos series en el tiempo: período completo y una semana
# =============================================================================
semana = serie["2024-03-04":"2024-03-10"]

fig, axes = plt.subplots(2, 2, figsize=(13, 7), sharey="row")
for fila, (col, nombre) in enumerate([("o3", "O3"), ("pm25", "PM2.5")]):
    axes[fila, 0].plot(serie.index, serie[col], linewidth=0.4)
    axes[fila, 1].plot(semana.index, semana[col], linewidth=0.8)
    axes[fila, 0].set_ylabel(f"{nombre} (µg/m³)")
axes[0, 0].set_title(f"Enero a abril, paso {PASO}")
axes[0, 1].set_title("Una semana (4 a 10 de marzo)")
for ax in axes.flat:
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
fig.suptitle(f"Ozono y PM2.5, {ESTACION}")
fig.tight_layout()
plt.show()


# =============================================================================
# 5. Gráfico de rezago: la serie contra sí misma, k pasos antes
# =============================================================================
# shift(k) corre la serie k renglones hacia adelante: en cada fila queda el
# valor de hace k pasos. Como la grilla es completa, k pasos son k × PASO.
rezagos_horas = [1/6, 1, 12, 24]      # 10 min, 1 h, 12 h, 24 h

fig, axes = plt.subplots(1, 4, figsize=(14, 3.8), sharey=True)
for ax, h in zip(axes, rezagos_horas):
    k = int(h * POR_HORA)
    r = semana["o3"].corr(semana["o3"].shift(k))
    ax.scatter(semana["o3"].shift(k), semana["o3"], s=4, alpha=0.4)
    ax.set_title(f"rezago {h:g} h   r = {r:.2f}")
    ax.set_xlabel(f"O3 hace {h:g} h")
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
axes[0].set_ylabel("O3 ahora")
fig.suptitle("Ozono contra sí mismo a distintos rezagos, una semana")
fig.tight_layout()
plt.show()


# =============================================================================
# 6. Función de autocorrelación: el r de arriba para cada rezago
# =============================================================================
rezagos = range(0, 48 * POR_HORA + 1)
horas = [k / POR_HORA for k in rezagos]
acf_o3 = [serie["o3"].corr(serie["o3"].shift(k)) for k in rezagos]
acf_pm = [serie["pm25"].corr(serie["pm25"].shift(k)) for k in rezagos]

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(horas, acf_o3, label="O3")
ax.plot(horas, acf_pm, label="PM2.5")
ax.axhline(0, color="grey", linewidth=0.8)
ax.set(title="Autocorrelación, enero a abril", xlabel="Rezago (horas)",
       ylabel="Correlación con la serie rezagada", xticks=range(0, 49, 6))
ax.legend()
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
fig.tight_layout()
plt.show()

# Lectura: la curva arranca en 1 (rezago 0). Dónde cruza cero, dónde toca
# fondo y dónde vuelve a subir es el período de la serie. Un mínimo a 12 h y
# un máximo a 24 h es un ciclo diario, visto desde la serie sola.


# =============================================================================
# 7. Correlación cruzada: PM2.5 de hace k pasos contra O3 de ahora
# =============================================================================
rezagos_c = range(-24 * POR_HORA, 24 * POR_HORA + 1)
horas_c = [k / POR_HORA for k in rezagos_c]
ccf = [serie["o3"].corr(serie["pm25"].shift(k)) for k in rezagos_c]

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(horas_c, ccf)
ax.axhline(0, color="grey", linewidth=0.8)
ax.axvline(0, color="grey", linewidth=0.8, linestyle="--")
ax.set(title="Correlación entre O3 y PM2.5 según el rezago",
       xlabel="Rezago de PM2.5 respecto de O3 (horas; > 0 es PM del pasado)",
       ylabel="Correlación", xticks=range(-24, 25, 6))
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
fig.tight_layout()
plt.show()

# En rezago 0 es el r de la clase 9. El resto de la curva dice a qué distancia
# temporal la relación es más fuerte. Como las dos series tienen ciclo diario,
# la curva también lo tiene: parte de esa onda es el reloj de ambas.
