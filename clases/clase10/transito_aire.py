# =============================================================================
# ¿El tránsito ensucia el aire?  Una investigación paso a paso
# Tres Cruces, junio de 2024: conteo vehicular, NO2 y PM2.5
# =============================================================================
# Cada paso tiene un gráfico. Cada gráfico dice ALGO, pero no TODO:
# al final de cada paso anotamos qué vemos y qué todavía no sabemos.
# =============================================================================
#%%
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

CARPETA = Path.cwd() / "clases/clase10"     # carpeta con los tres archivos
ARCH_AUTO = "autoscope_06_2024_volumen.csv"
ARCH_NO2 = "no2_05_2024_08_2024.csv"
ARCH_PM = "pm_2_5_05_2024_08_2024.csv"
RADIO_KM = 1.5

pauta = {"Ã³": "o", "Ã±": "ni", "Ã¡": "á", "Ã©": "é", "Ã­": "í",
         "Ãº": "ú", "Ã“": "Ó", "Ã‘": "NI", "Ã": "í"}

def limpiar(s):
    for a, b in pauta.items():
        s = s.str.replace(a, b, regex=False)
    return s

def estetica(ax):
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)

# =============================================================================
# 0. Carga: todo a valores por hora, junio de 2024
# =============================================================================
def cargar_aire(archivo, col):
    d = pd.read_csv(CARPETA / archivo, encoding="latin1", parse_dates=["fecha"]).drop_duplicates()
    d["estacion"] = limpiar(d["estacion"])
    por_hora = (d.set_index("fecha").groupby("estacion")[col]
                 .resample("h").mean().unstack("estacion"))
    coords = d.groupby("estacion")[["latitud", "longitud"]].first()
    return por_hora, coords

no2, coords_no2 = cargar_aire(ARCH_NO2, "no2")
pm, coords_pm = cargar_aire(ARCH_PM, "pm2_5")
coords_todas = pd.concat([coords_no2, coords_pm]).groupby(level=0).first()

auto = pd.read_csv(CARPETA / ARCH_AUTO, encoding="latin1", parse_dates=["fecha"]).drop_duplicates()
auto["fecha_hora"] = pd.to_datetime(auto["fecha"].dt.strftime("%Y-%m-%d") + " " + auto["hora"])
puntos = auto.groupby(["latitud", "longitud"]).size().reset_index(name="registros")

# Puntos de conteo cercanos a la estación (distancia sobre la esfera, en km)
def dist_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = np.sin((lat2 - lat1) / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2)**2
    return 2 * 6371 * np.arcsin(np.sqrt(a))

puntos_todos = puntos.copy()

def serie_estacion(est):
    """Tránsito de los puntos cercanos a la estación, NO2 y PM2.5, por hora."""
    c = coords_todas.loc[est]
    d = dist_km(puntos["latitud"], puntos["longitud"], c["latitud"], c["longitud"])
    cerca = puntos[d < RADIO_KM]
    a = auto.merge(cerca[["latitud", "longitud"]], on=["latitud", "longitud"])
    tr = a.set_index("fecha_hora")["volume"].resample("h").sum(min_count=1)
    horas = pd.date_range("2024-06-01", "2024-06-30 23:00", freq="h")
    serie = pd.DataFrame({"transito": tr.reindex(horas)})
    serie["no2"] = no2[est].reindex(horas) if est in no2.columns else np.nan
    serie["pm25"] = pm[est].reindex(horas) if est in pm.columns else np.nan
    return serie, cerca

# =============================================================================
# PASO 1. ¿Dónde medimos?
# =============================================================================
fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(puntos["longitud"], puntos["latitud"], s=8, color="tab:blue", label="Conteo vehicular")
ax.scatter(coords_todas["longitud"], coords_todas["latitud"], s=250, marker="*", color="red",
           label="Estación de aire")
for est, c in coords_todas.iterrows():
    ax.annotate(est, (c["longitud"], c["latitud"]), xytext=(6, 6), textcoords="offset points")
ax.set_aspect(1 / np.cos(np.radians(-34.9)))
ax.set(title="Paso 1. Dónde se cuenta el tránsito y dónde se mide el aire",
       xlabel="Longitud", ylabel="Latitud")
ax.legend(fontsize=8)
estetica(ax)
plt.show()
# Qué vemos: tres estaciones de aire y muchos puntos de conteo, repartidos
#   de forma muy desigual.
# Qué no sabemos: en cuál estación conviene buscar la huella del tránsito.

# =============================================================================
# PASO 2. ¿Qué estación elegimos? Lo que mide cada una y cuánto tránsito tiene cerca
# =============================================================================
estaciones = list(coords_todas.index)
series = {est: serie_estacion(est) for est in estaciones}

resumen = pd.DataFrame({
    est: {"puntos de conteo cerca": len(cerca_e),
          "horas con NO2": serie["no2"].notna().sum(),
          "horas con PM2.5": serie["pm25"].notna().sum()}
    for est, (serie, cerca_e) in series.items()}).T
print(resumen)

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), gridspec_kw={"width_ratios": [1, 2]})
axes[0].barh(resumen.index, resumen["puntos de conteo cerca"], color="tab:blue")
axes[0].set(title=f"Puntos de conteo a < {RADIO_KM} km", xlabel="Cantidad")
# Qué días de junio tiene dato cada estación (al menos 12 horas en el día)
for i, est in enumerate(estaciones):
    serie = series[est][0]
    for j, (col, color) in enumerate([("no2", "tab:orange"), ("pm25", "tab:green")]):
        dias = serie[col].resample("D").count()
        dias = dias[dias >= 12].index
        axes[1].scatter(dias, np.full(len(dias), i + 0.15 * (j - 0.5)), marker="s", s=25, color=color,
                        label=("NO2" if col == "no2" else "PM2.5") if i == 0 else None)
axes[1].set_yticks(range(len(estaciones)))
axes[1].set_yticklabels(estaciones)
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
axes[1].set(title="Días de junio con dato (al menos 12 horas)")
axes[1].legend(loc="upper right", fontsize=8)
for ax in axes:
    estetica(ax)
fig.suptitle("Paso 2. ¿Dónde tiene sentido buscar?")
fig.tight_layout()
plt.show()
# Qué vemos: el NO2 se mide solo en dos estaciones. Una tiene muchos puntos
#   de conteo cerca; la otra, muy pocos. Pero la que tiene más tránsito
#   medido tiene NO2 solo la primera mitad de junio.
# Decisión: empezamos por la estación con más tránsito medido alrededor,
#   aceptando que tiene menos días. Al final volvemos a mirar la otra.
ESTACION = resumen["puntos de conteo cerca"][resumen["horas con NO2"] > 0].idxmax()
df, cerca = series[ESTACION]
print("Estación elegida:", ESTACION)

# =============================================================================
# PASO 3. Mirar las series: una semana
# =============================================================================
semana = df["2024-06-04":"2024-06-10"]
fig, axes = plt.subplots(3, 1, figsize=(12, 7), sharex=True)
for ax, col, nombre, color in [(axes[0], "transito", "Vehículos por hora", "tab:blue"),
                               (axes[1], "no2", "NO2 (µg/m³)", "tab:orange"),
                               (axes[2], "pm25", "PM2.5 (µg/m³)", "tab:green")]:
    ax.plot(semana.index, semana[col], color=color)
    ax.set_ylabel(nombre)
    estetica(ax)
axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%a %d"))
axes[0].set_title(f"Paso 3. Una semana en {ESTACION}")
fig.tight_layout()
plt.show()
# Qué vemos: el tránsito sube de día y baja de noche. El NO2 también parece
#   tener un ritmo diario. El PM2.5 tiene picos que no se parecen a nada.
# Qué no sabemos: "parece" no alcanza. Necesitamos mirar muchos días juntos.

# =============================================================================
# PASO 4. El día típico: perfil horario, entre semana y fin de semana
# =============================================================================
tipo_dia = np.where(df.index.dayofweek >= 5, "fin de semana", "lunes a viernes")
perfil = df.groupby([tipo_dia, df.index.hour]).mean()

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
for ax, tipo in zip(axes, ["lunes a viernes", "fin de semana"]):
    p = perfil.loc[tipo]
    for col, nombre in [("transito", "Tránsito"), ("no2", "NO2"), ("pm25", "PM2.5")]:
        ax.plot(p.index, p[col] / p[col].mean(), marker="o", markersize=3, label=nombre)
    ax.set(title=tipo, xlabel="Hora del día", ylabel="Relativo a su media")
    estetica(ax)
axes[0].legend()
fig.suptitle("Paso 4. El día típico (cada serie dividida por su media)")
fig.tight_layout()
plt.show()
# Qué vemos: el NO2 tiene picos en las mismas horas que el tránsito, y
#   entre semana más marcados que el fin de semana. El PM2.5 no sigue ese ritmo.
# Ojo: el fin de semana se apoya en pocos días (el NO2 tiene ~12 días de dato).
# Qué no sabemos: dos cosas con ritmo diario se parecen aunque no tengan
#   nada que ver (la luz del sol y el tránsito también se parecen...).

# =============================================================================
# PASO 5. La correlación "cruda"
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
for ax, col, nombre in [(axes[0], "no2", "NO2"), (axes[1], "pm25", "PM2.5")]:
    d = df[["transito", col]].dropna()
    r = d["transito"].corr(d[col])
    ax.scatter(d["transito"], d[col], s=8, alpha=0.4)
    ax.set(title=f"{nombre}: r = {r:.2f}", xlabel="Vehículos por hora", ylabel=f"{nombre} (µg/m³)")
    estetica(ax)
fig.suptitle("Paso 5. Tránsito contra contaminante, hora a hora")
fig.tight_layout()
plt.show()
# Qué vemos: el NO2 sube con el tránsito; el PM2.5 no.
# Qué no sabemos: parte de esa r viene solo de que los dos tienen ciclo diario
#   (paso 3). ¿Cuánto queda si sacamos el ciclo?

# =============================================================================
# PASO 6. Sacar el ciclo diario: desvíos respecto de lo habitual
# =============================================================================
# A cada hora le restamos el promedio de esa hora (y ese tipo de día).
# Lo que queda responde a: ¿esta hora estuvo por encima o por debajo de lo habitual?
def desvio(s):
    clave = [s.index.dayofweek >= 5, s.index.hour]
    return s - s.groupby(clave).transform("mean")

res = df.apply(desvio)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
for ax, col, nombre in [(axes[0], "no2", "NO2"), (axes[1], "pm25", "PM2.5")]:
    d = res[["transito", col]].dropna()
    r = d["transito"].corr(d[col])
    ax.scatter(d["transito"], d[col], s=8, alpha=0.4)
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.axvline(0, color="grey", linewidth=0.8)
    ax.set(title=f"{nombre}: r = {r:.2f}", xlabel="Tránsito: diferencia con lo habitual",
           ylabel=f"{nombre}: diferencia con lo habitual")
    estetica(ax)
fig.suptitle("Paso 6. Sin el ciclo diario")
fig.tight_layout()
plt.show()
# Qué vemos: la r del NO2 baja bastante: mucho de lo del paso 4 era el ciclo.
#   Pero no llega a cero. La del PM2.5 sigue en cero.
# Qué no sabemos: el aire tarda en reaccionar. ¿Y si el NO2 responde al
#   tránsito de un rato antes?

# =============================================================================
# PASO 7. ¿Con qué demora? Correlación con el tránsito de k horas antes
# =============================================================================
REZAGOS = range(-3, 9)
fig, ax = plt.subplots(figsize=(9, 4.5))
for col, nombre in [("no2", "NO2"), ("pm25", "PM2.5")]:
    c = [res[col].corr(res["transito"].shift(k)) for k in REZAGOS]
    ax.plot(list(REZAGOS), c, marker="o", label=nombre)
ax.axhline(0, color="grey", linewidth=0.8)
ax.axvline(0, color="grey", linewidth=0.8, linestyle="--")
ax.set(title="Paso 7. Contaminante ahora vs tránsito de k horas antes (desvíos)",
       xlabel="k (horas; k > 0 es tránsito del pasado)", ylabel="Correlación")
ax.legend()
estetica(ax)
plt.show()
# Qué vemos: el NO2 correlaciona más con el tránsito de ~1 hora antes, y el
#   efecto se apaga en pocas horas. Tiene sentido: sale del escape y dura poco.
# Qué no sabemos: buscamos el mejor rezago entre varios. ¿Un número así
#   podría salir por casualidad?

# =============================================================================
# PASO 8. ¿Casualidad? Corremos el tránsito días enteros
# =============================================================================
# Si movemos toda la serie de tránsito varios días, rompemos cualquier
# relación real con el aire, pero cada serie conserva su forma.
# Si la correlación real queda por encima de todas las corridas, no es casualidad.
REZAGOS_BUSQUEDA = range(0, 4)

def r_max(col, tr):
    return np.nanmax([res[col].corr(tr.shift(k)) for k in REZAGOS_BUSQUEDA])

dias = len(res) // 24
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharex=True)
for ax, col, nombre in [(axes[0], "no2", "NO2"), (axes[1], "pm25", "PM2.5")]:
    obs = r_max(col, res["transito"])
    azar = [r_max(col, pd.Series(np.roll(res["transito"].to_numpy(), 24 * d), index=res.index))
            for d in range(3, dias - 2)]
    ax.hist(azar, bins=10, color="lightgrey", edgecolor="grey", label="Tránsito corrido al azar")
    ax.axvline(obs, color="red", linewidth=2, label=f"Real: r = {obs:.2f}")
    ax.set(title=nombre, xlabel="Mejor correlación (rezagos 0 a 3 h)")
    ax.legend(fontsize=8)
    estetica(ax)
    print(f"{nombre}: corridas con r igual o mayor que la real: {np.mean(np.array(azar) >= obs):.0%}")
fig.suptitle("Paso 8. ¿La relación supera a la casualidad?")
fig.tight_layout()
plt.show()
# Qué vemos: el NO2 queda por encima de todas las corridas; el PM2.5 queda
#   en el medio.
# Qué no sabemos: cuánto NO2 agrega el tránsito. Para eso, un modelo.

# =============================================================================
# PASO 9. Dos contaminantes, dos ritmos: el NO2 es rápido, el PM2.5 se acumula
# =============================================================================
# Miramos lo mismo que en el paso 7, pero con rezagos de hasta un día entero.
largos = range(0, 25)
fig, ax = plt.subplots(figsize=(10, 4.8))
for col, nombre in [("no2", "NO2"), ("pm25", "PM2.5")]:
    c = [res[col].corr(res["transito"].shift(k)) for k in largos]
    ax.plot(list(largos), c, marker="o", markersize=4, label=nombre)
ax.axhline(0, color="grey", linewidth=0.8)
ax.set(title="Paso 9. Contaminante ahora vs tránsito de k horas antes, hasta 24 horas",
       xlabel="k (horas; tránsito del pasado)", ylabel="Correlación")
ax.legend()
estetica(ax)
plt.show()
# Qué vemos: el NO2 responde enseguida al tránsito (1-2 horas) y se apaga.
#   El PM2.5 no responde en el momento: empieza a subir a las 5-6 horas y
#   llega a su máximo cerca de las 12-13. No sale del caño y se va: se junta.
# Por eso en el paso 4 el PM2.5 tenía su pico de noche, cuando el tránsito
#   ya había bajado: está mostrando el tránsito de todo el día.

# =============================================================================
# PASO 10. Un modelo
# =============================================================================
# La idea, en palabras:
#   lo que medimos = lo habitual de esa hora + lo que agrega el tránsito + lo que no sabemos
#
# En símbolos, para cada hora t:
#   y(t) = h(t) + a + b · x(t - k) + error
#     h(t)      lo habitual: el promedio de esa hora del día (y tipo de día)   -> pasos 4 y 6
#     x(t - k)  el desvío del tránsito de k horas antes                        -> pasos 6 y 9
#     a, b      la recta que mejor une el desvío del tránsito con el del
#               contaminante (mínimos cuadrados). b es lo que sube el
#               contaminante por cada vehículo por hora de más.
#     error     todo lo que el modelo no sabe (viento, lluvia, otras fuentes)
#
# El rezago k sale del paso 9: el NO2 responde en ~1 hora, el PM2.5 en ~13.
REZAGO = {"no2": 1, "pm25": 13}
CONTAMINANTES = [("no2", "NO2"), ("pm25", "PM2.5")]

def ajustar_modelo(col):
    d = pd.DataFrame({"medido": df[col],
                      "desvio": res[col],
                      "transito_desvio": res["transito"].shift(REZAGO[col])}).dropna()
    # 1. Lo habitual de cada hora: lo medido menos su desvío
    d["habitual"] = d["medido"] - d["desvio"]
    # 2. La recta entre los dos desvíos
    b, a = np.polyfit(d["transito_desvio"], d["desvio"], 1)
    # 3. La predicción: lo habitual más lo que agrega el tránsito
    d["modelo"] = d["habitual"] + a + b * d["transito_desvio"]
    return d, a, b

def r2(medido, predicho):
    # proporción de la variación de lo medido que el modelo reproduce
    return 1 - ((medido - predicho)**2).sum() / ((medido - medido.mean())**2).sum()

modelos = {col: ajustar_modelo(col) for col, _ in CONTAMINANTES}

tabla = pd.DataFrame([{
    "contaminante": nombre,
    "rezago k (h)": REZAGO[col],
    "b por cada 1000 veh/h": 1000 * modelos[col][2],
    "R² solo lo habitual": r2(modelos[col][0]["medido"], modelos[col][0]["habitual"]),
    "R² habitual + tránsito": r2(modelos[col][0]["medido"], modelos[col][0]["modelo"]),
    "horas usadas": len(modelos[col][0])} for col, nombre in CONTAMINANTES])
print(tabla.round(2).to_string(index=False))

# --- 10a. La pieza nueva del modelo: la recta entre los desvíos -------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
for ax, (col, nombre) in zip(axes, CONTAMINANTES):
    d, a, b = modelos[col]
    ax.scatter(d["transito_desvio"], d["desvio"], s=8, alpha=0.4)
    x = np.linspace(d["transito_desvio"].min(), d["transito_desvio"].max(), 2)
    ax.plot(x, a + b * x, color="tab:red", linewidth=2, label=f"recta: b = {1000 * b:.1f} por 1000 veh/h")
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.axvline(0, color="grey", linewidth=0.8)
    ax.set(title=f"{nombre}: tránsito de {REZAGO[col]} h antes",
           xlabel="Tránsito: diferencia con lo habitual (veh/h)",
           ylabel=f"{nombre}: diferencia con lo habitual")
    ax.legend(fontsize=8)
    estetica(ax)
fig.suptitle("Paso 10a. Cuánto agrega el tránsito: la recta entre los desvíos")
fig.tight_layout()
plt.show()

# --- 10b. El modelo completo contra lo medido, una semana --------------------
horas = pd.date_range("2024-06-04", "2024-06-10 23:00", freq="h")   # grilla completa: los huecos cortan la línea
fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
for ax, (col, nombre) in zip(axes, CONTAMINANTES):
    d = modelos[col][0].reindex(horas)
    ax.plot(horas, d["medido"], color="black", linewidth=1, label="Medido")
    ax.plot(horas, d["habitual"], color="tab:grey", linestyle="--", label="Solo lo habitual de la hora")
    ax.plot(horas, d["modelo"], color="tab:red", label="Habitual + tránsito")
    ax.set(title=nombre, ylabel=f"{nombre} (µg/m³)")
    ax.legend(fontsize=8)
    estetica(ax)
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%a %d"))
fig.suptitle("Paso 10b. El modelo contra lo medido, una semana")
fig.tight_layout()
plt.show()
# Qué vemos: sin ninguna otra variable (ni viento, ni lluvia, ni temperatura),
#   lo habitual de la hora explica la mitad del NO2 y una quinta parte del
#   PM2.5. Sumar el tránsito, cada uno con su demora, mejora a los dos.
# Conclusión: el tránsito se ve en los dos contaminantes, con ritmos
#   distintos: el NO2 enseguida, el PM2.5 medio día después.
# ¿Dónde se equivoca el modelo? En los episodios y en las noches raras:
#   ahí está lo que no pusimos (el tiempo, otras fuentes).

# =============================================================================
# PASO 11. ¿Y en la otra estación? Lo mismo en todas las que miden NO2
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), sharey=True)
for est in [e for e in estaciones if series[e][0]["no2"].notna().any()]:
    serie, cerca_e = series[est]
    r_est = serie.apply(desvio)
    c = [r_est["no2"].corr(r_est["transito"].shift(k)) for k in REZAGOS]
    obs = np.nanmax([r_est["no2"].corr(r_est["transito"].shift(k)) for k in REZAGOS_BUSQUEDA])
    azar = [np.nanmax([r_est["no2"].corr(pd.Series(np.roll(r_est["transito"].to_numpy(), 24 * d),
                                                    index=r_est.index).shift(k))
                       for k in REZAGOS_BUSQUEDA])
            for d in range(3, len(r_est) // 24 - 2)]
    p = np.mean(np.array(azar) >= obs)
    axes[0].plot(list(REZAGOS), c, marker="o", label=f"{est} ({len(cerca_e)} puntos cerca)")
    axes[1].bar(est, obs, color="tab:red", alpha=0.7)
    axes[1].scatter([est] * len(azar), azar, color="grey", s=10, zorder=3)
    print(f"{est}: {len(cerca_e)} puntos cerca, mejor r = {obs:.2f}, corridas >= real: {p:.0%}")
axes[0].axhline(0, color="grey", linewidth=0.8)
axes[0].axvline(0, color="grey", linewidth=0.8, linestyle="--")
axes[0].set(title="NO2 vs tránsito de k horas antes (desvíos)", xlabel="k (horas)", ylabel="Correlación")
axes[0].legend(fontsize=8)
axes[1].set(title="Barra: r real (0 a 3 h).  Puntos: corridas al azar")
for ax in axes:
    estetica(ax)
fig.suptitle("Paso 11. La misma pregunta en las dos estaciones con NO2")
fig.tight_layout()
plt.show()
# Qué vemos: donde hay mucho tránsito medido cerca, la huella aparece; donde
#   hay pocos puntos de conteo, no se distingue del azar.
# Ojo: eso NO prueba que allí el tránsito no importe. No encontrar algo
#   también depende de qué tan bien lo medimos.