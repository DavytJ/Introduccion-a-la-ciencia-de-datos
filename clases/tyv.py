# =============================================================================
# Distancia entre detectores de conteo vehicular y estaciones de aire
# Ejemplo: medioambiente y aire (ozono, PM2.5, conteo vehicular) — Montevideo
# Versión Python (pandas + matplotlib)
# =============================================================================
# Instalación (una sola vez):  pip install pandas numpy matplotlib
# =============================================================================
#%%
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

BASE_DIR = Path.cwd()
SUBCARPETA = BASE_DIR / "clases/clase7"   # carpeta donde están los tres csv
SUBCARPETA2 = BASE_DIR / "clases/clase10"  # carpeta donde está el csv de conteo vehicular

# =============================================================================
# 1. Carga y preparación de los datos
# =============================================================================

## 1.1 Pauta de limpieza de caracteres mal codificados (Buscar -> Reemplazar)
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

def limpiar_texto(columna):
    for buscar, reemplazar in pauta_limpieza.items():
        columna = columna.str.replace(buscar, reemplazar, regex=False)
    return columna

## 1.2 Aire: ozono y PM2.5 (traen estación, longitud y latitud)
def cargar_aire(archivo, carpeta=SUBCARPETA):
    datos = pd.read_csv(carpeta / archivo, encoding="latin1", parse_dates=["fecha"])
    datos["estacion"] = limpiar_texto(datos["estacion"])
    return datos.drop_duplicates()

ozono_limpio = cargar_aire("o3_01_2024_04_2024.csv")
pm_limpio = cargar_aire("pm_2_5_01_2024_04_2024.csv")
no_limpio = cargar_aire("no2_01_2024_04_2024.csv", carpeta=SUBCARPETA2)

print(ozono_limpio.head())
print(pm_limpio.head())
print(no_limpio.head())

## 1.3 Conteo vehicular (Centro de Gestión de Movilidad, abril de 2024)
auto = pd.read_csv(SUBCARPETA / "autoscope_04_2024_volumen.csv",
                   encoding="latin1", parse_dates=["fecha"])
for col in ["dsc_avenida", "dsc_int_anterior", "dsc_int_siguiente"]:
    auto[col] = limpiar_texto(auto[col])
auto = auto.drop_duplicates()

# fecha y hora vienen separadas y hora es texto: las unimos en un solo sello
auto["fecha_hora"] = pd.to_datetime(auto["fecha"].dt.strftime("%Y-%m-%d")
                                    + " " + auto["hora"])
auto.info()
print(auto.head())

# =============================================================================
# 2. Coordenadas de las estaciones, tomadas de los archivos de aire
# =============================================================================
estaciones_coord = (
    pd.concat([
        ozono_limpio[["estacion", "latitud", "longitud"]].assign(contaminante="O3"),
        pm_limpio[["estacion", "latitud", "longitud"]].assign(contaminante="PM2.5"),
    ])
    .drop_duplicates()
    .rename(columns={"latitud": "lat_est", "longitud": "lon_est"})
)
print(estaciones_coord)    # qué estación mide qué contaminante

# Control: cada estación debe tener una sola coordenada
print(estaciones_coord.groupby("estacion")[["lat_est", "lon_est"]].nunique())

# Para las distancias, una fila por estación (sin repetir por contaminante)
estaciones_coord = (estaciones_coord
                    .drop_duplicates(subset=["estacion", "lat_est", "lon_est"])
                    [["estacion", "lat_est", "lon_est"]]
                    .reset_index(drop=True))

# =============================================================================
# 3. Ubicaciones únicas de los detectores
# =============================================================================
# Un mismo cod_detector aparece en más de una ubicación (en las primeras filas,
# el 206 carril 2 está en otro punto que el 206 carril 1). La unidad de
# ubicación es entonces la combinación detector–carril.
ubic = (
    auto[["cod_detector", "id_carril", "dsc_avenida", "dsc_int_anterior",
          "dsc_int_siguiente", "latitud", "longitud"]]
    .drop_duplicates(subset=["cod_detector", "id_carril", "latitud", "longitud"])
    .reset_index(drop=True)
)
print("Combinaciones detector–carril–ubicación:", len(ubic))
print("Detector–carril con más de una ubicación:",
      ubic.duplicated(subset=["cod_detector", "id_carril"]).sum())
print("Puntos distintos en el mapa:",
      len(ubic[["latitud", "longitud"]].drop_duplicates()))

# =============================================================================
# 4. Distancia (haversine)
# =============================================================================
R_TIERRA_KM = 6371.0

def distancia_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    return 2 * R_TIERRA_KM * np.arcsin(np.sqrt(a))

# how="cross": cada detector con cada estación
dist = ubic.merge(estaciones_coord, how="cross")
dist["dist_km"] = distancia_km(dist["latitud"], dist["longitud"],
                               dist["lat_est"], dist["lon_est"])

# =============================================================================
# 5. Tablas de distancias
# =============================================================================
# Detector × estación
tabla_dist = dist.pivot_table(index=["cod_detector", "id_carril", "dsc_avenida"],
                              columns="estacion", values="dist_km").round(2)
print(tabla_dist)

# Estación más cercana a cada detector
mas_cercana = dist.loc[dist.groupby(["cod_detector", "id_carril", "latitud", "longitud"])
                           ["dist_km"].idxmin()]
print(mas_cercana["estacion"].value_counts())   # cuántos detectores tiene cerca cada estación
print(mas_cercana.groupby("estacion")["dist_km"].describe().round(2))

# =============================================================================
# 6. Control visual: detectores y estaciones en el plano
# =============================================================================
# Sirve también para detectar coordenadas mal cargadas (signo cambiado,
# latitud y longitud invertidas).
fig, ax = plt.subplots(figsize=(8, 7))
sc = ax.scatter(mas_cercana["longitud"], mas_cercana["latitud"],
                c=mas_cercana["dist_km"], cmap="viridis", s=20)
ax.scatter(estaciones_coord["lon_est"], estaciones_coord["lat_est"],
           marker="*", s=300, color="red")
for _, e in estaciones_coord.iterrows():
    ax.annotate(e["estacion"], (e["lon_est"], e["lat_est"]),
                xytext=(6, 6), textcoords="offset points", fontsize=9)
fig.colorbar(sc, ax=ax, label="Distancia a la estación más cercana (km)")
ax.set(title="Detectores de conteo vehicular y estaciones de aire",
       xlabel="Longitud", ylabel="Latitud")
ax.set_aspect(1 / np.cos(np.radians(-34.9)))   # corrige la deformación a esta latitud
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
fig.tight_layout()
plt.show()

# =============================================================================
# 7. Series a paso de 10 minutos (solo abril: el conteo vehicular es de abril)
# =============================================================================
PASO = "10min"
INICIO_ABRIL = pd.Timestamp("2024-04-01 00:00:00")
FIN_ABRIL = pd.Timestamp("2024-04-30 23:50:00")
grilla = pd.date_range(INICIO_ABRIL, FIN_ABRIL, freq=PASO)
 
## 7.1 Tránsito: un "punto" es una ubicación; se suman los carriles de ese punto
auto["punto"] = auto.groupby(["latitud", "longitud"]).ngroup()
puntos = (auto.groupby("punto")
              .agg(latitud=("latitud", "first"), longitud=("longitud", "first"),
                   dsc_avenida=("dsc_avenida", "first"))
              .reset_index())
 
# sum(min_count=1): una caja sin ningún registro queda NaN, no 0
transito = (auto.set_index("fecha_hora")
                .groupby("punto")["volume"]
                .resample(PASO).sum(min_count=1)
                .unstack("punto")
                .reindex(grilla))
 
# Puntos con más de la mitad de las cajas en 0: probablemente detector apagado
prop_ceros = (transito == 0).sum() / transito.notna().sum()
print("Puntos descartados por exceso de ceros:", (prop_ceros >= 0.5).sum())
transito = transito.loc[:, prop_ceros < 0.5]
 
## 7.2 PM2.5: promedio por caja de 10 minutos, una columna por estación
pm_abril = pm_limpio[(pm_limpio["fecha"] >= INICIO_ABRIL)
                     & (pm_limpio["fecha"] < FIN_ABRIL + pd.Timedelta(PASO))]
pm_10 = (pm_abril.set_index("fecha")
                 .groupby("estacion")["pm2_5"]
                 .resample(PASO).mean()
                 .unstack("estacion")
                 .reindex(grilla))
print("Cajas con dato de PM2.5 por estación:")
print(pm_10.notna().sum())
 
## 7.3 Desvíos respecto del perfil típico (hora del día × semana/fin de semana)
# Saca el ciclo diario compartido, que infla la correlación cruda.
def desvio_perfil(df):
    clave = [df.index.dayofweek >= 5, df.index.hour]
    return df - df.groupby(clave).transform("mean")
 
tr_res = desvio_perfil(transito)
pm_res = desvio_perfil(pm_10)
 
# =============================================================================
# 8. Correlación de cada punto de tránsito con cada estación de PM2.5
# =============================================================================
MIN_PARES = 500      # ~3,5 días de cajas con dato en las dos series
 
filas = []
for est in pm_10.columns:
    for p in transito.columns:
        n = (pm_10[est].notna() & transito[p].notna()).sum()
        if n < MIN_PARES:
            continue
        filas.append({"estacion": est, "punto": p, "n": n,
                      "r_crudo":  pm_10[est].corr(transito[p]),
                      "r_desvio": pm_res[est].corr(tr_res[p])})
 
corr = pd.DataFrame(filas).dropna()
corr = corr.merge(puntos, on="punto").merge(estaciones_coord, on="estacion")
corr["dist_km"] = distancia_km(corr["latitud"], corr["longitud"],
                               corr["lat_est"], corr["lon_est"])
print(corr.groupby("estacion")[["r_crudo", "r_desvio", "dist_km"]].describe().round(2))
 
## 8.1 Recta por estación: r = a + b · distancia (descriptiva, sin p-valores)
pendientes = []
for est, d in corr.groupby("estacion"):
    for col in ["r_crudo", "r_desvio"]:
        b, a = np.polyfit(d["dist_km"], d[col], 1)
        pendientes.append({"estacion": est, "correlacion": col, "n_puntos": len(d),
                           "r_a_0_km": a, "cambio_r_por_km": b})
print(pd.DataFrame(pendientes).round(3))
 
## 8.2 Gráfico: correlación contra distancia
fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharex=True, sharey=True)
for ax, col, titulo in [(axes[0], "r_crudo", "Correlación cruda"),
                        (axes[1], "r_desvio", "Correlación de los desvíos")]:
    for est, d in corr.groupby("estacion"):
        puntos_graf = ax.scatter(d["dist_km"], d[col], s=15, alpha=0.6, label=est)
        b, a = np.polyfit(d["dist_km"], d[col], 1)
        x = np.linspace(d["dist_km"].min(), d["dist_km"].max(), 2)
        ax.plot(x, a + b * x, color=puntos_graf.get_facecolor()[0], linewidth=2)
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.set(title=titulo, xlabel="Distancia del punto de conteo a la estación (km)")
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
axes[0].set_ylabel("Correlación tránsito – PM2.5")
axes[1].legend(title="Estación de PM2.5")
fig.suptitle("¿La relación entre tránsito y PM2.5 depende de la distancia? Abril de 2024")
fig.tight_layout()
plt.show()

est = "Tres Cruces"
p = corr[corr["estacion"] == est].nsmallest(1, "dist_km")["punto"].iloc[0]
par = pd.DataFrame({"pm": pm_res[est], "tr": tr_res[p]}).dropna()

fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
axes[0].plot(par.index, par["tr"], linewidth=0.5)
axes[0].set_ylabel("Tránsito, desvío")
axes[1].plot(par.index, par["pm"], linewidth=0.5, color="tab:orange")
axes[1].set_ylabel("PM2.5, desvío")
fig.suptitle(f"Punto {p} y {est}, abril de 2024")
fig.tight_layout()
plt.show()

# Una r por día: ¿la asociación es estable o la arman unos pocos días?
r_dia = par.groupby(par.index.date).apply(lambda d: d["pm"].corr(d["tr"]))
print(r_dia.round(2))

# =============================================================================
# 9. Regresión en el tiempo: PM2.5 contra tránsito por anillos de distancia
# =============================================================================
# En lugar de resumir cada par en una r, usamos cada caja de 10 minutos como
# observación. Para cada estación s y cada momento t:
#
#   PM[s,t] = alfa[hora, tipo de día] + sum_k beta[s,k] * T[s,k,t] + error
#
# T[s,k,t] = tránsito medio por punto (vehículos cada 10 min, en decenas) de
# los puntos que están en el anillo k de distancia alrededor de la estación s.
# beta[s,k] dice cuánto sube el PM2.5 cuando sube el tránsito a esa distancia,
# con el tránsito de los otros anillos fijo. Si el efecto es local, beta debería
# ser mayor en los anillos cercanos.
# Los alfa (efectos fijos hora × tipo de día) cumplen el rol de los desvíos.
 
ANILLOS_KM = [0, 1, 2, 4, 8, np.inf]
ETIQ_ANILLOS = ["0-1 km", "1-2 km", "2-4 km", "4-8 km", "8+ km"]
LAGS_NW = 36          # 6 horas de cajas de 10 min para los errores estándar
 
## 9.1 Distancia de cada punto (con datos) a cada estación de PM2.5, y su anillo
dist_pt = (puntos[puntos["punto"].isin(transito.columns)]
           .merge(estaciones_coord[estaciones_coord["estacion"].isin(pm_10.columns)],
                  how="cross"))
dist_pt["dist_km"] = distancia_km(dist_pt["latitud"], dist_pt["longitud"],
                                  dist_pt["lat_est"], dist_pt["lon_est"])
dist_pt["anillo"] = pd.cut(dist_pt["dist_km"], ANILLOS_KM, labels=ETIQ_ANILLOS,
                           right=False)
print(dist_pt.pivot_table(index="estacion", columns="anillo", values="punto",
                          aggfunc="count", observed=False))   # puntos por anillo
 
## 9.2 Tabla de regresión de una estación: una fila por caja de 10 minutos
def tabla_estacion(est):
    d = dist_pt[dist_pt["estacion"] == est]
    tabla = pd.DataFrame({"pm": pm_10[est]})
    for anillo, g in d.groupby("anillo", observed=True):
        # promedio por punto: no depende de cuántos detectores reportan en esa caja
        tabla[f"T {anillo}"] = transito[g["punto"]].mean(axis=1) / 10
    tabla["franja"] = pd.cut(tabla.index.hour, bins=[-1, 5, 11, 17, 23],
                             labels=["madrugada", "mañana", "tarde", "noche"])
    tabla["fe"] = (np.where(tabla.index.dayofweek >= 5, "finde", "semana")
                   + "_" + tabla.index.hour.astype(str))
    return tabla
 
## 9.3 Mínimos cuadrados con errores estándar de Newey–West
# Los residuos están autocorrelacionados (lo vimos en la ACF): los errores
# estándar habituales serían demasiado chicos. Newey–West los corrige.
def ajustar(tabla, lags=LAGS_NW):
    cols_T = [c for c in tabla.columns if c.startswith("T ")]
    d = tabla.dropna(subset=["pm"] + cols_T)
    fe = pd.get_dummies(d["fe"], dtype=float)
    X = pd.concat([d[cols_T], fe], axis=1)
    X = X.loc[:, X.abs().sum() > 0]                  # saca columnas vacías
    Xv, y = X.to_numpy(), d["pm"].to_numpy()
    coef, *_ = np.linalg.lstsq(Xv, y, rcond=None)
    e = y - Xv @ coef
    # u_t = x_t e_t sobre la grilla completa (0 donde no hay dato), para que el
    # rezago l sea l cajas de 10 minutos y no l filas
    U = (pd.DataFrame(Xv * e[:, None], index=d.index)
           .reindex(grilla, fill_value=0).to_numpy())
    S = U.T @ U
    for l in range(1, lags + 1):
        G = U[l:].T @ U[:-l]
        S += (1 - l / (lags + 1)) * (G + G.T)
    XtX_inv = np.linalg.inv(Xv.T @ Xv)
    ee = np.sqrt(np.diag(XtX_inv @ S @ XtX_inv))
    res = pd.DataFrame({"coef": coef, "ee": ee}, index=X.columns).loc[cols_T]
    res["n"] = len(d)
    return res
 
## 9.4 Un modelo por estación, todo abril
resultados = []
for est in pm_10.columns:
    tabla = tabla_estacion(est)
    cols_T = [c for c in tabla.columns if c.startswith("T ")]
    # Colinealidad: correlación entre anillos una vez sacado el perfil hora × día
    print(f"\n{est}: correlación entre anillos, desvíos (colinealidad)")
    print(desvio_perfil(tabla[cols_T]).corr().round(2))
    r = ajustar(tabla)
    r["estacion"] = est
    resultados.append(r)
resultados = pd.concat(resultados).rename_axis("anillo").reset_index()
resultados["anillo"] = resultados["anillo"].str.replace("T ", "")
print(resultados.round(3))
 
## 9.5 Gráfico: efecto del tránsito según el anillo de distancia
fig, ax = plt.subplots(figsize=(9, 5))
desplaz = {est: i * 0.1 for i, est in enumerate(resultados["estacion"].unique())}
for est, d in resultados.groupby("estacion"):
    x = np.array([ETIQ_ANILLOS.index(a) for a in d["anillo"]]) + desplaz[est]
    ax.errorbar(x, d["coef"], yerr=2 * d["ee"], fmt="o-", capsize=3, label=est)
ax.axhline(0, color="grey", linewidth=0.8)
ax.set_xticks(range(len(ETIQ_ANILLOS)))
ax.set_xticklabels(ETIQ_ANILLOS)
ax.set(title="PM2.5 según el tránsito en cada anillo de distancia, abril de 2024",
       xlabel="Anillo de distancia a la estación",
       ylabel="µg/m³ por cada 10 vehículos más\npor punto en 10 min (± 2 e.e.)")
ax.legend(title="Estación de PM2.5")
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
fig.tight_layout()
plt.show()
 
## 9.6 ¿Cambia dentro del día? El mismo modelo, por franja horaria
por_franja = []
for est in pm_10.columns:
    tabla = tabla_estacion(est)
    for franja, t in tabla.groupby("franja", observed=True):
        r = ajustar(t)
        r["estacion"], r["franja"] = est, franja
        por_franja.append(r)
por_franja = pd.concat(por_franja).rename_axis("anillo").reset_index()
por_franja["anillo"] = por_franja["anillo"].str.replace("T ", "")
print(por_franja.pivot_table(index=["estacion", "anillo"], columns="franja",
                             values="coef", observed=True).round(3))
 
## 9.7 ¿Cambia entre semanas? El mismo modelo, semana por semana
por_semana = []
for est in pm_10.columns:
    tabla = tabla_estacion(est)
    for semana, t in tabla.groupby(tabla.index.isocalendar().week):
        if t["pm"].notna().sum() < 300:          # semanas con pocos datos
            continue
        r = ajustar(t)
        r["estacion"], r["semana"] = est, semana
        por_semana.append(r)
por_semana = pd.concat(por_semana).rename_axis("anillo").reset_index()
por_semana["anillo"] = por_semana["anillo"].str.replace("T ", "")
print(por_semana.pivot_table(index=["estacion", "anillo"], columns="semana",
                             values="coef").round(3))

# =============================================================================
# 10. ¿Por dónde pasan más vehículos? Volumen y cobertura por punto
# =============================================================================
# Antes de sumar tránsito "cercano" hay que saber cuánto pesa cada punto y si
# tiene datos todo el mes. Usamos todos los puntos (sin el filtro de ceros de 7.1).
 
## 10.1 Serie de 10 minutos de todos los puntos
transito_todos = (auto.set_index("fecha_hora")
                      .groupby("punto")["volume"]
                      .resample(PASO).sum(min_count=1)
                      .unstack("punto")
                      .reindex(grilla))
 
## 10.2 Resumen por punto
# veh_hora: promedio de vehículos por hora en las cajas con dato
#           (no depende de cuántas cajas faltan, a diferencia del total del mes)
# cobertura: proporción de cajas de 10 min de abril con dato
descr = (auto.groupby("punto")
             .agg(dsc_avenida=("dsc_avenida", "first"),
                  dsc_int_anterior=("dsc_int_anterior", "first"),
                  dsc_int_siguiente=("dsc_int_siguiente", "first"),
                  n_detectores=("cod_detector", "nunique"),
                  n_carriles=("id_carril", "nunique"),
                  latitud=("latitud", "first"),
                  longitud=("longitud", "first")))
 
volumen = pd.DataFrame({
    "veh_hora":   transito_todos.mean() * 6,
    "total_mes":  transito_todos.sum(),
    "cobertura":  transito_todos.notna().mean(),
    "prop_ceros": (transito_todos == 0).sum() / transito_todos.notna().sum(),
})
volumen = descr.join(volumen).reset_index()
 
# Estación de PM2.5 más cercana y su distancia
d_pm = volumen[["punto", "latitud", "longitud"]].merge(
    estaciones_coord[estaciones_coord["estacion"].isin(pm_10.columns)], how="cross")
d_pm["dist_km"] = distancia_km(d_pm["latitud"], d_pm["longitud"],
                               d_pm["lat_est"], d_pm["lon_est"])
cercana = (d_pm.loc[d_pm.groupby("punto")["dist_km"].idxmin(),
                    ["punto", "estacion", "dist_km"]]
               .rename(columns={"estacion": "estacion_pm_cercana"}))
volumen = volumen.merge(cercana, on="punto").sort_values("veh_hora", ascending=False)
 
pd.set_option("display.width", 200)
print(volumen[["punto", "dsc_avenida", "dsc_int_anterior", "n_carriles",
               "veh_hora", "cobertura", "prop_ceros",
               "estacion_pm_cercana", "dist_km"]].head(20).round(2))
 
## 10.3 ¿Qué tan concentrado está el tránsito?
v = volumen["veh_hora"].dropna().sort_values(ascending=False)
acum = v.cumsum() / v.sum()
for frac in [0.1, 0.2, 0.5]:
    k = int(np.ceil(frac * len(v)))
    print(f"El {frac:.0%} de puntos con más tránsito ({k} puntos) "
          f"lleva el {acum.iloc[k - 1]:.0%} de los vehículos")
 
## 10.4 Volumen cerca de cada estación de PM2.5 (puntos a menos de 2 km)
print(volumen[volumen["dist_km"] < 2]
      .groupby("estacion_pm_cercana")
      .agg(n_puntos=("punto", "size"),
           veh_hora_total=("veh_hora", "sum"),
           cobertura_media=("cobertura", "mean"))
      .round(2))
 
## 10.5 Mapa: tamaño = vehículos por hora, color = cobertura
ESCALA = volumen["veh_hora"].max() / 400          # el punto más cargado mide 400
fig, ax = plt.subplots(figsize=(9, 8))
sc = ax.scatter(volumen["longitud"], volumen["latitud"],
                s=volumen["veh_hora"] / ESCALA, c=volumen["cobertura"],
                cmap="viridis", vmin=0, vmax=1, alpha=0.7, edgecolor="k", linewidth=0.3)
ax.scatter(estaciones_coord["lon_est"], estaciones_coord["lat_est"],
           marker="*", s=300, color="red")
for _, e in estaciones_coord.iterrows():
    ax.annotate(e["estacion"], (e["lon_est"], e["lat_est"]),
                xytext=(6, 6), textcoords="offset points", fontsize=9)
fig.colorbar(sc, ax=ax, label="Cobertura (proporción de cajas con dato)")
manijas, etiquetas = sc.legend_elements(prop="sizes", num=4, alpha=0.6,
                                        func=lambda s: s * ESCALA)
ax.legend(manijas, etiquetas, title="Vehículos por hora", loc="lower left")
ax.set(title="Volumen de tránsito por punto de conteo, abril de 2024",
       xlabel="Longitud", ylabel="Latitud")
ax.set_aspect(1 / np.cos(np.radians(-34.9)))
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
fig.tight_layout()
plt.show()

# =============================================================================
# 11. Tránsito total (ciudad y cercano) a paso horario y correlación cruzada
# =============================================================================
# Pregunta: ¿el PM2.5 responde al tránsito con algún rezago? ¿cambia si el
# tránsito es el cercano a la estación o el de toda la ciudad?
# Todo en desvíos respecto del perfil hora × tipo de día, como en la clase 10.
 
COBERTURA_MIN = 0.8     # un punto entra si tiene dato en el 80 % de las horas
MIN_PRESENTES = 0.8     # una hora vale si reporta el 80 % de los puntos elegidos
RADIO_CERCA_KM = 2      # "cercano" = a menos de 2 km de la estación
 
## 11.1 Paso horario
grilla_h = pd.date_range(INICIO_ABRIL, FIN_ABRIL.floor("h"), freq="h")
 
# Tránsito: la hora vale solo si están sus 6 cajas de 10 min (hora completa)
tr_h = transito_todos.resample("h").sum(min_count=6).reindex(grilla_h)
 
# PM2.5: promedio de la hora si hay al menos 4 de las 6 cajas
pm_h = (pm_10.resample("h").mean()
             .where(pm_10.resample("h").count() >= 4)
             .reindex(grilla_h))
 
## 11.2 Puntos con buena cobertura horaria y sin exceso de ceros
cob_h = tr_h.notna().mean()
buenos = volumen.loc[(volumen["prop_ceros"] < 0.5)
                     & (volumen["punto"].map(cob_h) >= COBERTURA_MIN), "punto"].tolist()
print("Puntos con buena cobertura:", len(buenos), "de", tr_h.shape[1])
 
## 11.3 Desvíos y tránsito total
# Sumar desvíos (no niveles): si un punto falta en una hora, aporta desvío 0,
# que equivale a suponer que esa hora tuvo su tránsito habitual. Así la suma
# no cae artificialmente cuando un detector deja de reportar. Como es una suma,
# las avenidas cargadas pesan más que las calles chicas.
tr_h_res = desvio_perfil(tr_h[buenos])
pm_h_res = desvio_perfil(pm_h)
 
def suma_desvios(cols):
    d = tr_h_res[cols]
    presentes = d.notna().mean(axis=1)
    return d.sum(axis=1).where(presentes >= MIN_PRESENTES)
 
tr_ciudad = suma_desvios(buenos)
 
tr_cerca = {}
for est in pm_h.columns:
    cerca = d_pm.loc[(d_pm["estacion"] == est) & (d_pm["dist_km"] < RADIO_CERCA_KM)
                     & d_pm["punto"].isin(buenos), "punto"].tolist()
    print(f"{est}: {len(cerca)} puntos cercanos con buena cobertura")
    if cerca:
        tr_cerca[est] = suma_desvios(cerca)
 
print("Horas con dato, tránsito ciudad:", tr_ciudad.notna().sum(), "de", len(grilla_h))
print("Horas con dato, PM2.5 por estación:")
print(pm_h_res.notna().sum())
 
## 11.4 Correlación cruzada: PM2.5 ahora contra tránsito de hace k horas
# k > 0: tránsito del pasado. Un pico en k = 3 diría "el PM2.5 responde al
# tránsito de 3 horas antes". Una meseta ancha que no baja con k indica
# días enteros que se mueven juntos (el factor común), no un rezago.
REZAGOS_H = range(-24, 49)
 
def ccf(pm, tr, rezagos):
    return pd.Series({k: pm.corr(tr.shift(k)) for k in rezagos})
 
def graficar_ccf(series_pm, rezagos, titulo):
    ests = series_pm.columns
    fig, axes = plt.subplots(len(ests), 1, figsize=(11, 3.2 * len(ests)),
                             sharex=True, sharey=True, squeeze=False)
    for ax, est in zip(axes[:, 0], ests):
        c = ccf(series_pm[est], tr_ciudad_graf, rezagos)
        ax.plot(c.index, c.values, label="Tránsito de toda la ciudad")
        if est in tr_cerca_graf:
            c = ccf(series_pm[est], tr_cerca_graf[est], rezagos)
            ax.plot(c.index, c.values, label=f"Tránsito a menos de {RADIO_CERCA_KM} km")
        ax.axhline(0, color="grey", linewidth=0.8)
        ax.axvline(0, color="grey", linewidth=0.8, linestyle="--")
        ax.set_title(est)
        ax.set_ylabel("Correlación")
        ax.grid(alpha=0.3)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    axes[0, 0].legend()
    axes[-1, 0].set_xlabel("Rezago del tránsito respecto del PM2.5 (horas; > 0 es tránsito del pasado)")
    fig.suptitle(titulo)
    fig.tight_layout()
    plt.show()
 
tr_ciudad_graf, tr_cerca_graf = tr_ciudad, tr_cerca
graficar_ccf(pm_h_res, REZAGOS_H,
             "PM2.5 contra tránsito rezagado, desvíos del perfil hora × tipo de día")
 
## 11.5 Solo dentro del día: además se resta la media de cada día
# Saca lo que afecta al día entero (lluvia, feriados, eventos). Lo que queda es
# la pregunta de dentro del día: en las horas en que el tránsito está por encima
# de lo habitual PARA ESE DÍA, ¿el PM2.5 también? Rezagos cortos: con la media
# diaria sacada, los rezagos de más de medio día pierden sentido.
def sin_media_dia(x):
    return x - x.groupby(x.index.date).transform("mean")
 
tr_ciudad_graf = sin_media_dia(tr_ciudad)
tr_cerca_graf = {est: sin_media_dia(s) for est, s in tr_cerca.items()}
graficar_ccf(pm_h_res.apply(sin_media_dia), range(-12, 13),
             "PM2.5 contra tránsito rezagado, solo variación dentro del día")
 
## 11.6 Escala diaria: ¿el tránsito de un día se ve en el PM2.5 del día siguiente?
# Con un mes hay unos 25 días útiles: esto es exploratorio. Además no separa
# "el día después de mucho tránsito" de "el día de la semana que es".
def media_diaria(x, min_horas=18):
    return x.resample("D").mean().where(x.resample("D").count() >= min_horas)
 
pm_dia = pm_h_res.apply(media_diaria)
filas = []
for est in pm_dia.columns:
    fuentes = {"ciudad": media_diaria(tr_ciudad)}
    if est in tr_cerca:
        fuentes["cercano"] = media_diaria(tr_cerca[est])
    for fuente, tr_d in fuentes.items():
        for k in [0, 1, 2]:
            par = pd.concat([pm_dia[est], tr_d.shift(k)], axis=1).dropna()
            filas.append({"estacion": est, "transito": fuente, "rezago_dias": k,
                          "n_dias": len(par),
                          "r": par.iloc[:, 0].corr(par.iloc[:, 1])})
print(pd.DataFrame(filas).round(2))

## 11.7 Sacar lo lento con una media móvil centrada de 24 horas
# La 11.5 restaba la media del día calendario: eso corta a medianoche, y un
# rezago de 11 h termina comparando horas centradas respecto de días distintos.
# Una media móvil centrada de 24 h saca igual los movimientos de varios días
# (lluvia, feriados, las caídas del 7, 14 y 21 de abril), pero es continua y no
# tiene cortes, así que los rezagos de hasta un día vuelven a tener sentido.
def sin_lento(x, ventana=24):
    return x - x.rolling(ventana, center=True, min_periods=18).mean()
 
pm_lento = pm_h_res.apply(sin_lento)
tr_ciudad_lento = sin_lento(tr_ciudad)
tr_cerca_lento = {est: sin_lento(s) for est, s in tr_cerca.items()}
 
tr_ciudad_graf, tr_cerca_graf = tr_ciudad_lento, tr_cerca_lento
graficar_ccf(pm_lento, range(-24, 25),
             "PM2.5 contra tránsito rezagado, sin movimientos de más de un día")
 
## 11.8 Prueba de desplazamiento circular: ¿qué correlación sale por azar?
# Se corre toda la serie de tránsito una cantidad de días enteros (lo que sale
# por el final entra por el principio) y se recalcula la correlación máxima.
# Eso rompe cualquier relación real con el PM2.5, pero cada serie conserva su
# autocorrelación y su perfil diario. Si la correlación observada queda por
# encima de casi todas las desplazadas, no es fácil explicarla por azar.
# Se compara el MÁXIMO observado con los MÁXIMOS desplazados: así la búsqueda
# del mejor rezago también se hace en el azar, y la comparación es justa.
REZAGOS_BUSQUEDA = range(0, 25)          # tránsito de 0 a 24 h antes
n_dias = len(grilla_h) // 24
DESPLAZ_H = [24 * d for d in range(3, n_dias - 2)]   # evita corrimientos de 0-2 días
# Con un mes hay pocos corrimientos posibles (~25), así que el p tiene poca
# resolución (~0,04). Con pasos de 1 hora habría más, pero se desalinearían
# días de semana con fines de semana.
 
def max_ccf(pm, tr):
    c = ccf(pm, tr, REZAGOS_BUSQUEDA)
    return c.max(), c.idxmax()
 
def desplazar(tr, horas):
    return pd.Series(np.roll(tr.to_numpy(), horas), index=tr.index)
 
versiones = {
    "perfil (11.4)":    (pm_h_res, tr_ciudad, tr_cerca),
    "sin lento (11.7)": (pm_lento, tr_ciudad_lento, tr_cerca_lento),
}
 
filas, nulos_graf = [], {}
for version, (pm_v, tr_c, tr_cer) in versiones.items():
    for est in pm_v.columns:
        fuentes = {"ciudad": tr_c}
        if est in tr_cer:
            fuentes["cercano"] = tr_cer[est]
        for fuente, tr in fuentes.items():
            r_obs, k_obs = max_ccf(pm_v[est], tr)
            nulos = np.array([max_ccf(pm_v[est], desplazar(tr, h))[0] for h in DESPLAZ_H])
            p = (np.sum(nulos >= r_obs) + 1) / (len(nulos) + 1)
            filas.append({"version": version, "estacion": est, "transito": fuente,
                          "r_max": r_obs, "rezago_h": k_obs,
                          "r_max_azar_mediana": np.median(nulos),
                          "r_max_azar_p95": np.quantile(nulos, 0.95),
                          "p": p, "n_desplaz": len(nulos)})
            if fuente == "ciudad":
                nulos_graf[(version, est)] = (nulos, r_obs, k_obs)
 
prueba = pd.DataFrame(filas)
print(prueba.round(3))
 
# Gráfico: distribución de los máximos por azar y el observado (tránsito ciudad)
ests = list(pm_h_res.columns)
fig, axes = plt.subplots(len(ests), len(versiones), figsize=(11, 3 * len(ests)),
                         sharex=True, squeeze=False)
for j, version in enumerate(versiones):
    for i, est in enumerate(ests):
        ax = axes[i, j]
        nulos, r_obs, k_obs = nulos_graf[(version, est)]
        ax.hist(nulos, bins=12, color="lightgrey", edgecolor="grey")
        ax.axvline(r_obs, color="red", linewidth=2,
                   label=f"observado: r = {r_obs:.2f} en {k_obs} h")
        ax.set_title(f"{est}, {version}", fontsize=10)
        ax.legend(fontsize=8)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
for ax in axes[-1, :]:
    ax.set_xlabel("Correlación máxima (rezagos 0 a 24 h)")
fig.suptitle("¿La correlación observada supera a la que sale por azar? Tránsito de toda la ciudad")
fig.tight_layout()
plt.show()

# =============================================================================
# 12. ¿Los picos de PM2.5 coinciden entre estaciones?
# =============================================================================
# Si un pico aparece a la vez en todas las estaciones, apunta a algo regional o
# meteorológico. Si aparece en una sola, apunta a una fuente cercana a ella
# (una fábrica, una quema, el puerto). No usa tránsito, así que tomamos todo el
# período de PM2.5 (enero a abril): más picos para comparar.
 
TOLERANCIA = pd.Timedelta("1h")   # dos picos "coinciden" si se superponen ± 1 h
PERCENTIL_PICO = 0.99             # umbral: el 1 % de excesos más altos de cada estación
MIN_EXCESO = 10                   # y además al menos 10 µg/m³ sobre su base
MAX_HUECO = pd.Timedelta("30min") # cajas en pico separadas por ≤ 30 min: mismo episodio
 
## 12.1 Serie de 10 minutos, enero a abril, una columna por estación
grilla_todo = pd.date_range("2024-01-01 00:00", "2024-04-30 23:50", freq=PASO)
pm_todo = (pm_limpio.set_index("fecha")
                    .groupby("estacion")["pm2_5"]
                    .resample(PASO).mean()
                    .unstack("estacion")
                    .reindex(grilla_todo))
print("Cobertura por estación, enero a abril:")
print(pm_todo.notna().mean().round(2))
 
## 12.2 Exceso sobre la base: mediana móvil centrada de 24 h
# La mediana no se deja arrastrar por los propios picos (la media sí).
base = pm_todo.rolling(144, center=True, min_periods=72).median()
exceso = pm_todo - base
umbral = exceso.quantile(PERCENTIL_PICO).clip(lower=MIN_EXCESO)
print("Umbral de pico por estación (µg/m³ sobre la base):")
print(umbral.round(1))
en_pico = exceso.gt(umbral)          # los NaN quedan como False
 
## 12.3 Episodios: tramos consecutivos en pico
def episodios(est):
    s = en_pico[est]
    bloque = (s != s.shift()).cumsum()
    tramos = [(g.index[0], g.index[-1]) for _, g in s[s].groupby(bloque[s])]
    unidos = []
    for ini, fin in tramos:
        if unidos and ini - unidos[-1][1] <= MAX_HUECO:
            unidos[-1] = (unidos[-1][0], fin)
        else:
            unidos.append((ini, fin))
    filas = []
    for ini, fin in unidos:
        tramo = exceso[est][ini:fin]
        filas.append({"estacion": est, "inicio": ini, "fin": fin + pd.Timedelta(PASO),
                      "duracion_h": ((fin - ini) + pd.Timedelta(PASO)) / pd.Timedelta("1h"),
                      "exceso_max": tramo.max(), "momento_max": tramo.idxmax()})
    return pd.DataFrame(filas)
 
epis = pd.concat([episodios(est) for est in pm_todo.columns], ignore_index=True)
print("Episodios por estación:")
print(epis.groupby("estacion").agg(n=("inicio", "size"),
                                   duracion_mediana_h=("duracion_h", "median"),
                                   exceso_max_mediano=("exceso_max", "median")).round(2))
 
## 12.4 Coincidencia observada y coincidencia por azar
# Para cada episodio de la estación A y cada otra estación B: ¿B está en pico
# en algún momento entre [inicio - 1 h, fin + 1 h]? Solo se cuenta si B tiene
# dato en al menos la mitad de esa ventana.
# Por azar: se corre la serie de picos de B una cantidad de días enteros y se
# repite la cuenta. Eso da cuánta coincidencia saldría sin relación, dada la
# cantidad y duración de los picos de cada estación.
idx = {t: i for i, t in enumerate(grilla_todo)}
tol = int(TOLERANCIA / pd.Timedelta(PASO))
n_cajas = len(grilla_todo)
DESPLAZ_DIAS = range(3, n_cajas // 144 - 2)
 
def ventanas(est):
    e = epis[epis["estacion"] == est]
    i0 = np.clip([idx[t] - tol for t in e["inicio"]], 0, n_cajas - 1)
    i1 = np.clip([idx[t - pd.Timedelta(PASO)] + tol for t in e["fin"]], 0, n_cajas - 1)
    return e.index.to_numpy(), np.array(i0), np.array(i1)
 
def coincide(pico_b, dato_b, i0, i1):
    cp = np.concatenate([[0], np.cumsum(pico_b)])
    cd = np.concatenate([[0], np.cumsum(dato_b)])
    largo = i1 - i0 + 1
    hay_dato = (cd[i1 + 1] - cd[i0]) >= largo / 2
    hay_pico = (cp[i1 + 1] - cp[i0]) > 0
    return hay_pico, hay_dato
 
filas = []
for a in pm_todo.columns:
    ids, i0, i1 = ventanas(a)
    for b in pm_todo.columns:
        if a == b:
            continue
        pico_b = en_pico[b].to_numpy().astype(int)
        dato_b = pm_todo[b].notna().to_numpy().astype(int)
        hp, hd = coincide(pico_b, dato_b, i0, i1)
        epis.loc[ids, f"coincide_{b}"] = np.where(hd, hp, np.nan)
        azar = []
        for d in DESPLAZ_DIAS:
            hp_s, hd_s = coincide(np.roll(pico_b, d * 144), np.roll(dato_b, d * 144), i0, i1)
            azar.append(hp_s[hd_s].mean() if hd_s.any() else np.nan)
        azar = np.array(azar)
        obs = hp[hd].mean() if hd.any() else np.nan
        filas.append({"estacion_A": a, "estacion_B": b, "episodios_A_con_dato_B": hd.sum(),
                      "coinciden_obs": obs,
                      "coinciden_azar_media": np.nanmean(azar),
                      "coinciden_azar_p95": np.nanquantile(azar, 0.95),
                      "p": (np.sum(azar >= obs) + 1) / (np.sum(~np.isnan(azar)) + 1)})
coinc = pd.DataFrame(filas)
print("Proporción de episodios de A en que B también está en pico:")
print(coinc.round(3))
 
# ¿Cuántas otras estaciones acompañan cada episodio?
cols_c = [c for c in epis.columns if c.startswith("coincide_")]
epis["n_acompanan"] = epis[cols_c].sum(axis=1, min_count=1)
epis["n_comparables"] = epis[cols_c].notna().sum(axis=1)
epis["tipo"] = np.select(
    [epis["n_comparables"] == 0, epis["n_acompanan"] == 0,
     epis["n_acompanan"] == epis["n_comparables"]],
    ["sin comparación", "solo esta estación", "todas las estaciones"],
    default="algunas estaciones")
print(pd.crosstab(epis["estacion"], epis["tipo"]))
 
## 12.5 ¿A qué hora y qué día ocurren? (pistas sobre la fuente)
epis["hora_max"] = epis["momento_max"].dt.hour
epis["franja"] = pd.cut(epis["hora_max"], bins=[-1, 5, 11, 17, 23],
                        labels=["madrugada", "mañana", "tarde", "noche"])
epis["dia"] = np.where(epis["momento_max"].dt.dayofweek >= 5, "fin de semana", "semana")
print(pd.crosstab([epis["estacion"], epis["tipo"]], epis["franja"]))
print(pd.crosstab([epis["estacion"], epis["tipo"]], epis["dia"]))
 
## 12.6 Línea de tiempo de los episodios
colores = {"solo esta estación": "tab:blue", "algunas estaciones": "tab:orange",
           "todas las estaciones": "tab:red", "sin comparación": "lightgrey"}
ests = list(pm_todo.columns)
fig, ax = plt.subplots(figsize=(13, 1 + 0.8 * len(ests)))
for i, est in enumerate(ests):
    # franjas grises: períodos sin dato
    sin_dato = pm_todo[est].isna()
    bloque = (sin_dato != sin_dato.shift()).cumsum()
    for _, g in sin_dato[sin_dato].groupby(bloque[sin_dato]):
        ax.axvspan(g.index[0], g.index[-1], ymin=(i + 0.1) / len(ests),
                   ymax=(i + 0.9) / len(ests), color="whitesmoke", zorder=0)
    e = epis[epis["estacion"] == est]
    ax.scatter(e["momento_max"], np.full(len(e), i),
               s=10 + 3 * e["exceso_max"].clip(upper=100),
               c=e["tipo"].map(colores), alpha=0.8, edgecolor="k", linewidth=0.3)
ax.set_yticks(range(len(ests)))
ax.set_yticklabels(ests)
ax.set_ylim(-0.6, len(ests) - 0.4)
for tipo, color in colores.items():
    ax.scatter([], [], c=color, label=tipo, edgecolor="k", linewidth=0.3)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
ax.set(title="Episodios de PM2.5 por estación (tamaño = exceso sobre la base; gris = sin dato)")
ax.grid(axis="x", alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
fig.tight_layout()
plt.show()
 
## 12.7 Los 6 episodios más fuertes, con todas las estaciones alrededor
top = epis.nlargest(6, "exceso_max")
fig, axes = plt.subplots(3, 2, figsize=(13, 9), squeeze=False)
for ax, (_, e) in zip(axes.flat, top.iterrows()):
    ventana = pm_todo[e["momento_max"] - pd.Timedelta("12h"):
                      e["momento_max"] + pd.Timedelta("12h")]
    for est in ests:
        ax.plot(ventana.index, ventana[est], linewidth=1, label=est)
    ax.axvspan(e["inicio"], e["fin"], color="red", alpha=0.15)
    ax.set_title(f"{e['estacion']}, {e['momento_max']:%d/%m %H:%M} ({e['tipo']})",
                 fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.set_ylabel("PM2.5 (µg/m³)")
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
axes[0, 0].legend(fontsize=8)
fig.suptitle("Los seis episodios más fuertes: ± 12 h, todas las estaciones")
fig.tight_layout()
plt.show()

# =============================================================================
# 13. Diferencias en diferencias: ¿la parada de la refinería cambió el PM2.5
#     cerca de La Teja?
# =============================================================================
# La refinería dejó de producir el 4/9/2023 y a fines de abril de 2024 todavía
# no había vuelto a funcionar del todo. Entonces enero a abril de 2024 es
# "refinería apagada". Para el "antes" usamos los mismos meses de 2023
# (refinería funcionando): comparar las mismas fechas de dos años saca del
# medio el cambio de estación (verano -> otoño).
#
#   DiD = (tratada 2024 - tratada 2023) - (controles 2024 - controles 2023)
#
# Tratada: la estación más cercana a La Teja. Controles: las más lejanas.
# Si la refinería aportaba PM2.5 en la tratada, el DiD debería ser negativo.
# Supuesto clave: sin la parada, la tratada y los controles habrían cambiado
# lo mismo de 2023 a 2024. Lo que cambie distinto entre ellas (por ejemplo el
# régimen de vientos, que afecta más a la estación costera) queda mezclado.

VAR = "pm2_5"                       # cambiar a la columna de SO2 o NO2 si se usa otro archivo
TRATADA = "Museo Romántico"         # revisar los nombres con pm_limpio["estacion"].unique()
CONTROLES = ["Curva de Maronias", "Tres Cruces"]
ESTACIONES = [TRATADA] + CONTROLES

# pm_2023: mismo contaminante, enero a abril de 2023, cargado con cargar_aire
# pm_limpio: enero a abril de 2024 (ya cargado)

## 13.1 Promedio diario por estación, indexado por mes-día para comparar años
def diario(datos, anio):
    d = (datos[datos["fecha"].dt.year == anio]
         .set_index("fecha")
         .groupby("estacion")[VAR]
         .resample("D").mean()
         .unstack("estacion"))
    d = d[~((d.index.month == 2) & (d.index.day == 29))]   # 2024 es bisiesto
    d.index = d.index.strftime("%m-%d")
    return d

antes = diario(pm_2023, 2023)       # refinería funcionando
despues = diario(pm_limpio, 2024)   # refinería apagada

# Mismos días en los dos años, y con dato en las tres estaciones
comunes = antes.index.intersection(despues.index)
antes, despues = antes.loc[comunes, ESTACIONES], despues.loc[comunes, ESTACIONES]
ok = antes.notna().all(axis=1) & despues.notna().all(axis=1)
antes, despues = antes[ok], despues[ok]
print("Días comparables:", ok.sum(), "de", len(comunes))

## 13.2 Tabla 2 x 2: medias por estación y año
tabla = pd.DataFrame({"2023 (funcionando)": antes.mean(),
                      "2024 (apagada)": despues.mean()})
tabla["cambio"] = tabla["2024 (apagada)"] - tabla["2023 (funcionando)"]
print(tabla.round(2))

## 13.3 Estimación
cambio = despues - antes                              # cambio día a día, por estación
d_t = cambio[TRATADA] - cambio[CONTROLES].mean(axis=1)
did = d_t.mean()

# Incertidumbre aproximada: los días seguidos se parecen (autocorrelación),
# así que promediamos por semana y usamos la variación entre semanas.
semana = pd.to_datetime("2024-" + d_t.index).isocalendar().week.to_numpy()
d_sem = d_t.groupby(semana).mean()
ee = d_sem.std() / np.sqrt(len(d_sem))
print(f"DiD = {did:.2f} µg/m³  (± 2 e.e. aprox.: {did - 2*ee:.2f} a {did + 2*ee:.2f}, "
      f"{len(d_sem)} semanas)")

## 13.4 Placebo en el espacio: cada estación "tratada" por turno
# Si una estación de control da un DiD tan grande como la tratada, el efecto
# no es atribuible a la refinería.
placebos = {}
for est in ESTACIONES:
    otras = [e for e in ESTACIONES if e != est]
    placebos[est] = (cambio[est] - cambio[otras].mean(axis=1)).mean()
print(pd.Series(placebos, name="DiD como si fuera la tratada").round(2))

## 13.5 Gráficos
fechas = pd.to_datetime("2024-" + antes.index)
brecha_2023 = (antes[TRATADA] - antes[CONTROLES].mean(axis=1)).rolling(7, min_periods=4).mean()
brecha_2024 = (despues[TRATADA] - despues[CONTROLES].mean(axis=1)).rolling(7, min_periods=4).mean()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5),
                               gridspec_kw={"width_ratios": [3, 1]})
ax1.plot(fechas, brecha_2023.to_numpy(), label="2023 (refinería funcionando)")
ax1.plot(fechas, brecha_2024.to_numpy(), label="2024 (refinería apagada)")
ax1.axhline(0, color="grey", linewidth=0.8)
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
ax1.set(title=f"{TRATADA} menos el promedio de los controles (media móvil 7 días)",
        ylabel=f"{VAR}, diferencia (µg/m³)")
ax1.legend()

ax2.bar(range(len(placebos)), list(placebos.values()),
        color=["tab:red" if e == TRATADA else "lightgrey" for e in placebos])
ax2.set_xticks(range(len(placebos)))
ax2.set_xticklabels(list(placebos.keys()), rotation=20, ha="right")
ax2.axhline(0, color="grey", linewidth=0.8)
ax2.set(title="DiD con cada estación como tratada", ylabel="µg/m³")
for ax in (ax1, ax2):
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
fig.tight_layout()
plt.show()

