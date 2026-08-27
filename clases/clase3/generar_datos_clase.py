# -*- coding: utf-8 -*-
"""
Generador de los archivos de ejemplo de la clase «Cargar datos».
Joselina Davyt-Colo — Facultad de Ciencias Empresariales y Economía — Universidad de Montevideo

Se ejecuta una sola vez, antes de seguir el documento de la clase:

    py generar_datos_clase.py          (Windows)
    python3 generar_datos_clase.py     (Mac / Linux)

Crea la carpeta `datos_clase/` junto a este archivo, con los mismos datos
—ventas mensuales de una cadena de locales— guardados en seis formatos
distintos. La comparación entre esos seis archivos es el contenido de la clase.

Requisitos: pandas y openpyxl vienen con Anaconda. El archivo de SPSS necesita
pyreadstat, que no viene incluido; si no está, ese formato se saltea y el resto
se genera igual.
"""

import json
import sqlite3
from pathlib import Path

import pandas as pd

# La carpeta se construye desde la ubicación de este archivo, no desde el
# directorio de trabajo: así el script funciona desde cualquier lado.
BASE = Path(__file__).parent
CARPETA = BASE / "datos_clase"
CARPETA.mkdir(exist_ok=True)

base = pd.DataFrame({
    "id_local":   [101, 102, 103, 104, 105, 106],
    "sucursal":   ["Centro", "Centro", "Pocitos", "Cordón", "Pocitos", "Cordón"],
    "mes":        ["2025-01", "2025-02", "2025-01", "2025-02", "2025-03", "2025-03"],
    "ventas_uyu": [128500.50, 143200.00, 98750.25, 110430.75, 152980.00, 121045.40],
    "empleados":  [12, 12, 8, 9, 8, 9],
})


# --- 1. CSV con las convenciones locales -----------------------------------
# Punto y coma como separador, coma decimal, codificación latin-1: es lo que
# exporta Excel en español y lo que publican varios organismos.
base.to_csv(CARPETA / "ventas_local.csv",
            sep=";", decimal=",", index=False, encoding="latin-1")


# --- 2. Excel con dos hojas y filas de título -------------------------------
# La tabla no empieza en A1: arriba hay un título y una fecha, como en
# cualquier reporte real.
with pd.ExcelWriter(CARPETA / "ventas.xlsx", engine="openpyxl") as w:
    base.to_excel(w, sheet_name="ventas", index=False, startrow=3)
    pd.DataFrame({"sucursal": ["Centro", "Pocitos", "Cordón"],
                  "barrio":   ["Ciudad Vieja", "Pocitos", "Cordón"],
                  "m2":       [220, 180, 150]}).to_excel(
        w, sheet_name="locales", index=False)
    w.book["ventas"]["A1"] = "Reporte de ventas — uso interno"
    w.book["ventas"]["A2"] = "Generado el 12/03/2025"


# --- 3. Stata, con etiquetas de variable ------------------------------------
base.to_stata(CARPETA / "ventas.dta", write_index=False, version=118,
              variable_labels={"ventas_uyu": "Ventas mensuales en pesos uruguayos",
                               "empleados":  "Personal ocupado en el local"})


# --- 4. SPSS, con etiquetas de variable y de valor --------------------------
try:
    import pyreadstat

    datos_sav = base.copy()
    datos_sav["sucursal_cod"] = datos_sav["sucursal"].map(
        {"Centro": 1, "Pocitos": 2, "Cordón": 3})
    datos_sav = datos_sav.drop(columns=["sucursal"])

    pyreadstat.write_sav(
        datos_sav, str(CARPETA / "ventas.sav"),
        column_labels={"ventas_uyu": "Ventas mensuales en pesos",
                       "sucursal_cod": "Sucursal"},
        variable_value_labels={"sucursal_cod": {1: "Centro",
                                                2: "Pocitos",
                                                3: "Cordón"}})
except ImportError:
    print("pyreadstat no está instalado: se saltea ventas.sav")
    print("Para generarlo:  pip install pyreadstat")


# --- 5. Base de datos SQLite con dos tablas ---------------------------------
con = sqlite3.connect(CARPETA / "comercio.db")
base.to_sql("ventas", con, index=False, if_exists="replace")
pd.DataFrame({"sucursal": ["Centro", "Pocitos", "Cordón"],
              "region":   ["Sur", "Sur", "Centro"]}).to_sql(
    "locales", con, index=False, if_exists="replace")
con.close()


# --- 6. Respuesta anidada, del tipo que devuelve una API --------------------
respuesta = {
    "meta": {"fuente": "sistema interno", "actualizado": "2025-03-31"},
    "resultados": [
        {"local": {"id": 101, "sucursal": "Centro"},
         "periodo": "2025-01", "ventas": 128500.50},
        {"local": {"id": 103, "sucursal": "Pocitos"},
         "periodo": "2025-01", "ventas": 98750.25},
    ],
}
(CARPETA / "respuesta_api.json").write_text(
    json.dumps(respuesta, ensure_ascii=False, indent=2), encoding="utf-8")


print(f"Archivos creados en {CARPETA}:")
for archivo in sorted(CARPETA.iterdir()):
    print("  ", archivo.name)
