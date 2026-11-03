# =============================================================================
# ¿El tránsito se ve en el NO2? ¿Y en el PM2.5?  Comparación rápida, abril 2024
# =============================================================================
# Para cada estación: tránsito de los puntos de conteo cercanos, NO2 y PM2.5,
# todo por hora. Dos gráficos por estación:
#   izquierda: perfil horario promedio (cada serie dividida por su media)
#   derecha:  correlación de los desvíos (sin el perfil hora x tipo de día)
#             entre el contaminante y el tránsito de k horas antes
# =============================================================================
#%%
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path.cwd()
CARPETA_AIRE = BASE / "clases/clase7"      # PM2.5 y conteo vehicular
CARPETA_NO2 = BASE / "clases/clase10"      # NO2
ARCH_PM = "pm_2_5_01_2024_04_2024.csv"
ARCH_NO2 = "no2_01_2024_04_2024.csv"       # <- poner el nombre real del archivo
ARCH_AUTO = "autoscope_04_2024_volumen.csv"
RADIO_KM = 1.5                             # "cerca" de la estación

pauta = {"Ã³": "o", "Ã±": "ni", "Ã¡": "á", "Ã©": "é", "Ã­": "í",
         "Ãº": "ú", "Ã“": "Ó", "Ã‘": "NI", "Ã": "í"}

def limpiar(s):
    for a, b in pauta.items():
        s = s.str.replace(a, b, regex=False)
    return s

# =============================================================================
# 1. Carga: todo a promedios (o sumas) por hora
# =============================================================================
def cargar_aire(carpeta, archivo, col):
    d = pd.read_csv(carpeta / archivo, encoding="latin1", parse_dates=["fecha"]).drop_duplicates()
    d["estacion"] = limpiar(d["estacion"])
    por_hora = (d.set_index("fecha").groupby("estacion")[col]
                 .resample("h").mean().unstack("estacion"))
    coords = d.groupby("estacion")[["latitud", "longitud"]].first()
    return por_hora, coords

no2, coords = cargar_aire(CARPETA_NO2, ARCH_NO2, "no2")
pm, _ = cargar_aire(CARPETA_AIRE, ARCH_PM, "pm2_5")
print("Estaciones con NO2:", list(no2.columns))

auto = pd.read_csv(CARPETA_AIRE / ARCH_AUTO, encoding="latin1", parse_dates=["fecha"]).drop_duplicates()
auto["fecha_hora"] = pd.to_datetime(auto["fecha"].dt.strftime("%Y-%m-%d") + " " + auto["hora"])
auto["punto"] = auto.groupby(["latitud", "longitud"]).ngroup()     # punto = ubicación
puntos = auto.groupby("punto")[["latitud", "longitud"]].first()
transito = (auto.set_index("fecha_hora").groupby("punto")["volume"]
                .resample("h").sum(min_count=1).unstack("punto"))   # vehículos por hora

# =============================================================================
# 2. Herramientas
# =============================================================================
def dist_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = (np.sin((lat2 - lat1) / 2)**2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2)**2)
    return 2 * 6371 * np.arcsin(np.sqrt(a))

def desvio(s):
    # resta el promedio de su hora del día y tipo de día (semana / fin de semana)
    clave = [s.index.dayofweek >= 5, s.index.hour]
    return s - s.groupby(clave).transform("mean")

REZAGOS = range(-6, 13)   # k > 0: tránsito de k horas antes

# =============================================================================
# 3. Por estación: perfil horario y correlación con rezagos
# =============================================================================
ests = [e for e in no2.columns if e in coords.index]
fig, axes = plt.subplots(len(ests), 2, figsize=(12, 3.8 * len(ests)), squeeze=False)
resumen = []

for fila, est in zip(axes, ests):
    d = dist_km(puntos["latitud"], puntos["longitud"],
                coords.loc[est, "latitud"], coords.loc[est, "longitud"])
    cerca = d[d < RADIO_KM].index
    if len(cerca) == 0:
        fila[0].set_title(f"{est}: sin puntos de conteo a menos de {RADIO_KM} km")
        continue

    df = pd.DataFrame({"Tránsito cercano": transito[cerca].mean(axis=1)})
    df["NO2"] = no2[est].reindex(df.index)
    df["PM2.5"] = pm[est].reindex(df.index) if est in pm.columns else np.nan

    # Izquierda: perfil horario, cada serie dividida por su media
    perfil = df.groupby(df.index.hour).mean()
    (perfil / perfil.mean()).plot(ax=fila[0], marker="o", markersize=3)
    fila[0].set(title=f"{est}: perfil horario ({len(cerca)} puntos a < {RADIO_KM} km)",
                xlabel="Hora del día", ylabel="Relativo a su media")

    # Derecha: correlación de desvíos con el tránsito de k horas antes
    res = df.apply(desvio)
    for var in ["NO2", "PM2.5"]:
        c = pd.Series({k: res[var].corr(res["Tránsito cercano"].shift(k)) for k in REZAGOS})
        fila[1].plot(c.index, c.values, marker="o", markersize=3, label=var)
        resumen.append({"estacion": est, "contaminante": var, "puntos_cerca": len(cerca),
                        "r_rezago_0": c.loc[0], "r_max": c.max(), "rezago_max_h": c.idxmax()})
    fila[1].axhline(0, color="grey", linewidth=0.8)
    fila[1].axvline(0, color="grey", linewidth=0.8, linestyle="--")
    fila[1].set(title="Desvíos: contaminante vs tránsito de k horas antes",
                xlabel="Rezago k (horas)", ylabel="Correlación")
    fila[1].legend()

for ax in axes.flat:
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
fig.tight_layout()
plt.show()

print(pd.DataFrame(resumen).round(2))
# Lectura: si el NO2 da una r clara en rezago 0-1 y el PM2.5 no, el tránsito
# se ve en el NO2 y conviene trabajar con él. Recordar que valores de ~0,1
# pueden salir por azar (lo vimos con la prueba de desplazamiento).