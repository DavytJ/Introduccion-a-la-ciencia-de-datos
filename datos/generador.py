"""
Generador de datos sintéticos del curso.

Todos los conjuntos son ficticios y reproducibles: misma semilla, mismos datos.
Ningún script del curso necesita descargar nada para funcionar.

Uso desde un script de la carpeta clases/:
    from datos.generador import ventas_mensuales
    df = ventas_mensuales()
"""

import numpy as np
import pandas as pd

SEMILLA = 2026


def _rng(offset=0):
    return np.random.default_rng(SEMILLA + offset)


# --------------------------------------------------------------------------
# 1. Encuesta a estudiantes (corte transversal, con escalas y no respuesta)
# --------------------------------------------------------------------------
def encuesta_estudiantes(n=420):
    """Encuesta con dos constructos latentes y no respuesta no aleatoria."""
    rng = _rng(1)
    # Dos factores latentes: conocimiento financiero y aversión al riesgo
    conocimiento = rng.normal(0, 1, n)
    aversion = rng.normal(0, 1, n)

    def item(carga_c, carga_a, ruido=0.7):
        bruto = carga_c * conocimiento + carga_a * aversion + rng.normal(0, ruido, n)
        return np.clip(np.round(bruto * 1.2 + 4), 1, 7).astype(int)

    df = pd.DataFrame({
        "id": np.arange(1, n + 1),
        "edad": rng.integers(18, 30, n),
        "semestre": rng.integers(1, 9, n),
        "carrera": rng.choice(["ADE", "Economia", "Contador", "NNII", "Marketing"], n),
        # ítems del constructo "conocimiento"
        "p1_interes_compuesto": item(0.9, 0.0),
        "p2_inflacion": item(0.8, 0.1),
        "p3_diversificacion": item(0.9, -0.1),
        # ítems del constructo "aversión al riesgo"
        "p4_prefiere_seguro": item(0.0, 0.9),
        "p5_evita_perdidas": item(-0.1, 0.8),
        "p6_ahorro_precaucion": item(0.1, 0.7),
        "ingreso_mensual": np.round(rng.lognormal(9.6, 0.5, n), -2),
    })

    # No respuesta NO aleatoria: los de ingreso alto responden menos
    prob_falta = 0.05 + 0.35 * (df["ingreso_mensual"] > df["ingreso_mensual"].quantile(0.7))
    df.loc[rng.random(n) < prob_falta, "ingreso_mensual"] = np.nan

    # Ponderadores de expansión: sobremuestreo de semestres avanzados
    df["ponderador"] = np.where(df["semestre"] >= 5, 0.7, 1.4)
    return df


# --------------------------------------------------------------------------
# 2. Población de referencia (para muestreo)
# --------------------------------------------------------------------------
def poblacion_empresas(n=5000):
    """Población completa: sirve para comparar estimaciones contra la verdad."""
    rng = _rng(2)
    sector = rng.choice(["Agro", "Industria", "Comercio", "Servicios", "Construccion"],
                        n, p=[0.15, 0.20, 0.30, 0.28, 0.07])
    base = {"Agro": 11.0, "Industria": 11.6, "Comercio": 10.8,
            "Servicios": 11.2, "Construccion": 11.4}
    facturacion = np.exp([base[s] for s in sector] + rng.normal(0, 0.8, n))
    return pd.DataFrame({
        "empresa_id": np.arange(1, n + 1),
        "sector": sector,
        "facturacion": np.round(facturacion, 0),
        "empleados": np.maximum(1, (facturacion / 40000 + rng.normal(0, 3, n)).astype(int)),
    })


# --------------------------------------------------------------------------
# 3. Serie temporal de ventas (tendencia + estacionalidad + ruido)
# --------------------------------------------------------------------------
def ventas_mensuales(anios=8):
    rng = _rng(3)
    n = anios * 12
    fechas = pd.date_range("2018-01-01", periods=n, freq="MS")
    t = np.arange(n)
    tendencia = 1000 + 6 * t
    estacional = 120 * np.sin(2 * np.pi * (t % 12) / 12) + 60 * np.cos(4 * np.pi * (t % 12) / 12)
    diciembre = np.where(fechas.month == 12, 250, 0)
    ruido = rng.normal(0, 55, n)
    ventas = tendencia + estacional + diciembre + ruido
    return pd.DataFrame({"fecha": fechas, "ventas": np.round(ventas, 1)}).set_index("fecha")


def dos_series_no_estacionarias(n=200):
    """Dos caminatas aleatorias independientes: sirven para regresión espuria."""
    rng = _rng(4)
    x = np.cumsum(rng.normal(0, 1, n)) + 50
    y = np.cumsum(rng.normal(0, 1, n)) + 50
    fechas = pd.date_range("2010-01-01", periods=n, freq="MS")
    return pd.DataFrame({"x": x, "y": y}, index=fechas)


# --------------------------------------------------------------------------
# 4. Panel de sucursales (unidad x tiempo, desbalanceado, con atrito)
# --------------------------------------------------------------------------
def panel_sucursales(n_suc=60, meses=36):
    rng = _rng(5)
    fechas = pd.date_range("2022-01-01", periods=meses, freq="MS")
    filas = []
    for s in range(1, n_suc + 1):
        efecto_suc = rng.normal(0, 300)          # heterogeneidad no observada
        tamanio = rng.choice(["chica", "mediana", "grande"], p=[0.4, 0.4, 0.2])
        # atrito: las sucursales con efecto bajo cierran antes
        prob_cierre = 0.03 if efecto_suc < -200 else 0.005
        vivo = True
        for i, f in enumerate(fechas):
            if not vivo:
                break
            promo = rng.random() < 0.25
            ventas = (2000 + efecto_suc + 15 * i + 400 * promo + rng.normal(0, 150))
            filas.append({"sucursal": s, "fecha": f, "tamanio": tamanio,
                          "promocion": int(promo), "ventas": round(ventas, 1)})
            if rng.random() < prob_cierre and i > 5:
                vivo = False
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------
# 5. Clientes con tiempo hasta la baja (datos censurados)
# --------------------------------------------------------------------------
def clientes_supervivencia(n=800, horizonte=24):
    """duracion = meses observados; evento = 1 si se dio de baja, 0 si sigue activo."""
    rng = _rng(6)
    plan = rng.choice(["basico", "premium"], n, p=[0.6, 0.4])
    canal = rng.choice(["web", "sucursal"], n, p=[0.55, 0.45])
    # el plan premium retiene más: tasa de riesgo menor
    tasa = np.where(plan == "premium", 0.030, 0.065) * np.where(canal == "web", 1.25, 1.0)
    tiempo_real = rng.exponential(1 / tasa)
    # censura administrativa: solo observamos hasta el horizonte
    alta = rng.integers(0, 12, n)              # mes de alta escalonado
    seguimiento = horizonte - alta
    duracion = np.minimum(tiempo_real, seguimiento)
    evento = (tiempo_real <= seguimiento).astype(int)
    return pd.DataFrame({
        "cliente_id": np.arange(1, n + 1),
        "cohorte_alta": alta,
        "plan": plan,
        "canal": canal,
        "duracion": np.round(duracion, 2),
        "evento": evento,
    })


# --------------------------------------------------------------------------
# 6. Experimento A/B
# --------------------------------------------------------------------------
def experimento_ab(n=4000, efecto=0.012):
    rng = _rng(7)
    grupo = rng.choice(["control", "tratamiento"], n)
    p_base = 0.085
    p = np.where(grupo == "tratamiento", p_base + efecto, p_base)
    return pd.DataFrame({
        "usuario_id": np.arange(1, n + 1),
        "grupo": grupo,
        "convirtio": rng.binomial(1, p),
        "ticket": np.round(rng.lognormal(6.2, 0.6, n), 0),
    })


# --------------------------------------------------------------------------
# 7. Panel para diferencias en diferencias
# --------------------------------------------------------------------------
def did_locales(n_locales=80, meses=24, mes_intervencion=12, efecto=180):
    rng = _rng(8)
    fechas = pd.date_range("2023-01-01", periods=meses, freq="MS")
    tratado = rng.random(n_locales) < 0.5
    filas = []
    for i in range(n_locales):
        nivel = rng.normal(3000, 400) + (250 if tratado[i] else 0)
        for j, f in enumerate(fechas):
            post = j >= mes_intervencion
            y = nivel + 12 * j + rng.normal(0, 120)
            if tratado[i] and post:
                y += efecto
            filas.append({"local": i + 1, "fecha": f, "tratado": int(tratado[i]),
                          "post": int(post), "ventas": round(y, 1)})
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------
# 8. Rendimientos sectoriales (para PCA)
# --------------------------------------------------------------------------
def rendimientos_sectoriales(n=180):
    rng = _rng(9)
    factor_pais = rng.normal(0, 1, n)
    factor_commodities = rng.normal(0, 1, n)
    sectores = {
        "agro":        (0.5, 0.9), "ganaderia": (0.4, 0.85), "forestal": (0.45, 0.7),
        "industria":   (0.8, 0.3), "comercio":  (0.9, 0.1),  "servicios": (0.85, 0.05),
        "construccion": (0.75, 0.2), "transporte": (0.7, 0.35),
    }
    fechas = pd.date_range("2011-01-01", periods=n, freq="MS")
    datos = {k: cp * factor_pais + cc * factor_commodities + rng.normal(0, 0.5, n)
             for k, (cp, cc) in sectores.items()}
    return pd.DataFrame(datos, index=fechas).round(4)


# --------------------------------------------------------------------------
# 9. Datos sucios (para la clase de calidad)
# --------------------------------------------------------------------------
def transacciones_sucias(n=1500):
    rng = _rng(10)
    df = pd.DataFrame({
        "id_operacion": np.arange(1, n + 1),
        "fecha": rng.choice(pd.date_range("2025-01-01", "2025-12-31"), n),
        "cliente": rng.integers(1, 300, n),
        "monto": np.round(rng.lognormal(7, 1.1, n), 2),
        "moneda": rng.choice(["UYU", "uyu", "$U", "USD", "usd"], n, p=[.5, .15, .1, .2, .05]),
        "canal": rng.choice(["Web", "web", " WEB", "Sucursal", "sucursal"], n),
    })
    # duplicados exactos y montos imposibles
    df = pd.concat([df, df.sample(40, random_state=1)], ignore_index=True)
    df.loc[df.sample(25, random_state=2).index, "monto"] *= -1
    df.loc[df.sample(15, random_state=3).index, "monto"] = np.nan
    return df.sample(frac=1, random_state=4).reset_index(drop=True)
