# =============================================================================
# ¿El tránsito ensucia el aire?  Cuatro gráficos para la clase
# =============================================================================
#%%
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

CARPETA = Path.cwd() / "clases/clase7"
ARCH_PM = "pm_2_5_01_2024_04_2024.csv"
ARCH_AUTO = "autoscope_04_2024_volumen.csv"
ESTACION = "Tres Cruces"      # la estación con más detectores cerca
RADIO_KM = 1.5

pauta = {"Ã³": "o", "Ã±": "ni", "Ã¡": "á", "Ã©": "é", "Ã­": "í",
         "Ãº": "ú", "Ã“": "Ó", "Ã‘": "NI", "Ã": "í"}

def limpiar(s):
    for a, b in pauta.items():
        s = s.str.replace(a, b, regex=False)
    return s

def dist_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = np.sin((lat2 - lat1) / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2)**2
    return 2 * 6371 * np.arcsin(np.sqrt(a))

def desvio(s):
    # resta el promedio de su hora del día y tipo de día (semana / fin de semana)
    clave = [s.index.dayofweek >= 5, s.index.hour]
    return s - s.groupby(clave).transform("mean")

# --- Carga ------------------------------------------------------------------
pm = pd.read_csv(CARPETA / ARCH_PM, encoding="latin1", parse_dates=["fecha"]).drop_duplicates()
pm["estacion"] = limpiar(pm["estacion"])
estaciones = pm.groupby("estacion")[["latitud", "longitud"]].first()

auto = pd.read_csv(CARPETA / ARCH_AUTO, encoding="latin1", parse_dates=["fecha"]).drop_duplicates()
auto["fecha_hora"] = pd.to_datetime(auto["fecha"].dt.strftime("%Y-%m-%d") + " " + auto["hora"])
puntos = auto.groupby(["latitud", "longitud"]).size().reset_index(name="n")

# =============================================================================
# 1. El mapa: dónde se cuenta el tránsito y dónde se mide el aire
# =============================================================================
fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(puntos["longitud"], puntos["latitud"], s=10, color="tab:blue", label="Conteo vehicular")
ax.scatter(estaciones["longitud"], estaciones["latitud"], s=250, marker="*", color="red",
           label="Estación de aire")
for est, e in estaciones.iterrows():
    ax.annotate(est, (e["longitud"], e["latitud"]), xytext=(6, 6), textcoords="offset points")
ax.set_aspect(1 / np.cos(np.radians(-34.9)))
ax.set(title="Tránsito y estaciones de aire, Montevideo", xlabel="Longitud", ylabel="Latitud")
ax.legend()
plt.show()

# =============================================================================
# 2. Tránsito cercano y PM2.5 por hora, abril: crudo vs sin el ciclo diario
# =============================================================================
e = estaciones.loc[ESTACION]
cerca = puntos[dist_km(puntos["latitud"], puntos["longitud"], e["latitud"], e["longitud"]) < RADIO_KM]
auto_cerca = auto.merge(cerca[["latitud", "longitud"]], on=["latitud", "longitud"])
transito = auto_cerca.set_index("fecha_hora")["volume"].resample("h").sum(min_count=1)

pm_hora = (pm[pm["estacion"] == ESTACION].set_index("fecha")["pm2_5"]
             .resample("h").mean())
df = pd.DataFrame({"transito": transito, "pm25": pm_hora.reindex(transito.index)}).dropna()
print(f"{ESTACION}: {len(cerca)} puntos de conteo a < {RADIO_KM} km, {len(df)} horas con dato")

res = df.apply(desvio)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, datos, titulo in [(axes[0], df, "Crudo"), (axes[1], res, "Sin el ciclo diario (desvíos)")]:
    r = datos["transito"].corr(datos["pm25"])
    ax.scatter(datos["transito"], datos["pm25"], s=6, alpha=0.4)
    ax.set(title=f"{titulo}:  r = {r:.2f}", xlabel="Vehículos por hora (cerca)",
           ylabel="PM2.5 (µg/m³)")
    ax.grid(alpha=0.3)
fig.suptitle(f"Tránsito y PM2.5, {ESTACION}, abril 2024")
fig.tight_layout()
plt.show()

# =============================================================================
# 3. ¿Hay un rezago? ¿O es azar?  Correlación máxima vs corrimientos al azar
# =============================================================================
REZAGOS = range(0, 25)   # tránsito de 0 a 24 horas antes

def r_max(tr):
    c = [res["pm25"].corr(tr.shift(k)) for k in REZAGOS]
    return np.nanmax(c), int(np.nanargmax(c))

obs, k_obs = r_max(res["transito"])
# Correr el tránsito días enteros rompe cualquier relación real con el PM2.5
azar = [r_max(pd.Series(np.roll(res["transito"].to_numpy(), 24 * d), index=res.index))[0]
        for d in range(3, len(res) // 24 - 2)]

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(azar, bins=12, color="lightgrey", edgecolor="grey", label="Tránsito corrido al azar")
ax.axvline(obs, color="red", linewidth=2, label=f"Observado: r = {obs:.2f} en {k_obs} h")
ax.set(title="¿La mejor correlación supera a la que sale por azar?",
       xlabel="Correlación máxima (rezagos 0 a 24 h)", ylabel="Cantidad de corrimientos")
ax.legend()
plt.show()
print(f"Corrimientos con r igual o mayor al observado: {np.mean(np.array(azar) >= obs):.0%}")

# =============================================================================
# 4. Dos episodios: uno de toda la ciudad y uno local
# =============================================================================
pm10 = (pm.set_index("fecha").groupby("estacion")["pm2_5"]
          .resample("10min").mean().unstack("estacion"))
episodios = [("2024-03-16 22:00", "16/03: suben y bajan todas juntas"),
             ("2024-04-24 21:50", "24/04: solo una estación")]

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), sharey=True)
for ax, (momento, titulo) in zip(axes, episodios):
    t = pd.Timestamp(momento)
    ventana = pm10[t - pd.Timedelta("12h"): t + pd.Timedelta("12h")]
    for est in ventana.columns:
        ax.plot(ventana.index, ventana[est], label=est)
    ax.set(title=titulo, ylabel="PM2.5 (µg/m³)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.grid(alpha=0.3)
axes[0].legend()
fig.tight_layout()
plt.show()