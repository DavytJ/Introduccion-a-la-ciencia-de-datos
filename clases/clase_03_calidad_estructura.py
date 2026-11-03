"""
CLASE 03 — ¿Cómo es esto? Estructura y calidad del dato
Unidad 2: exploración y calidad (4 h)

OBJETIVO
  Pasar de un archivo crudo a una tabla en la que se pueda confiar.

IDEA CENTRAL
  La limpieza no es trabajo previo al análisis: es una cadena de decisiones
  que hay que justificar y documentar.
"""
import numpy as np
import pandas as pd
from _comun import SALIDAS, titulo
from datos.generador import transacciones_sucias

pd.set_option("display.width", 120)
df = transacciones_sucias()

titulo("1. Primer contacto: nunca empezar por el análisis")
print(df.head(3), "\n")
print(df.dtypes, "\n")
print(f"Filas: {len(df)}   Columnas: {df.shape[1]}")

titulo("2. Diagnóstico automático de calidad")
def diagnostico(d):
    return pd.DataFrame({
        "tipo": d.dtypes.astype(str),
        "faltantes": d.isna().sum(),
        "pct_faltantes": (d.isna().mean() * 100).round(1),
        "unicos": d.nunique(),
    })
print(diagnostico(df))

titulo("3. Duplicados: ¿exactos o de negocio?")
print(f"Filas duplicadas exactas: {df.duplicated().sum()}")
print(f"Duplicados por id_operacion: {df.duplicated(subset='id_operacion').sum()}")
print(">> El id debería ser único. Si no lo es, la llave está mal o hay reproceso.")
df = df.drop_duplicates()

titulo("4. Categorías que son la misma cosa escrita distinto")
print("Antes:", sorted(df['moneda'].unique()), sorted(df['canal'].unique()))
df["moneda"] = (df["moneda"].str.strip().str.upper()
                .replace({"$U": "UYU"}))
df["canal"] = df["canal"].str.strip().str.lower()
print("Después:", sorted(df['moneda'].unique()), sorted(df['canal'].unique()))

titulo("5. Valores imposibles según la regla de negocio")
negativos = (df["monto"] < 0).sum()
print(f"Montos negativos: {negativos}")
print(">> Decisión: ¿son devoluciones mal cargadas o error de signo?")
print(">> Lo que NO se puede hacer es borrarlos sin dejar constancia.")
df["monto_valido"] = df["monto"].where(df["monto"] > 0)

titulo("6. Reglas de validación que corren solas")
def validar(d):
    reglas = {
        "id único": d["id_operacion"].is_unique,
        "sin fechas futuras": (d["fecha"] <= pd.Timestamp("2026-01-01")).all(),
        "montos positivos": (d["monto_valido"].dropna() > 0).all(),
        "monedas conocidas": set(d["moneda"]) <= {"UYU", "USD"},
    }
    for nombre, ok in reglas.items():
        print(f"  [{'OK ' if ok else 'FALLA'}] {nombre}")
    return all(reglas.values())

validar(df)

titulo("7. Formato largo y formato ancho")
resumen = (df.assign(mes=df["fecha"].dt.to_period("M"))
             .groupby(["mes", "canal"], observed=True)["monto_valido"].sum()
             .reset_index())
print("LARGO (una fila por combinación):\n", resumen.head(4), "\n")
ancho = resumen.pivot(index="mes", columns="canal", values="monto_valido")
print("ANCHO (una columna por categoría):\n", ancho.head(4).round(0))

df.to_csv(SALIDAS / "clase03_transacciones_limpias.csv", index=False)

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. Escribí las reglas de validación de TU conjunto de datos (mínimo cinco).
2. Documentá cada decisión de limpieza en un archivo decisiones.md:
   qué encontraste, qué hiciste, qué alternativa descartaste y por qué.
3. ¿Cuántas filas perdiste en total? Si es más del 5 %, justificalo.
"""
