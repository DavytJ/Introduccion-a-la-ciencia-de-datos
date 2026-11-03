"""
Genera los archivos de datos que consumen los ejercicios de la clase 3.

Ejecutar una sola vez antes del práctico:
    py generar_archivos.py        (Windows)
    python3 generar_archivos.py   (Mac / Linux)

Crea la carpeta datos/ con cuatro archivos. Tres de ellos están
deliberadamente mal formados: reproducen los problemas que aparecen al
recibir un archivo de una fuente externa.

Semilla fija: los archivos son idénticos en todas las máquinas.
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 42
DESTINO = Path(__file__).parent / "datos"
DESTINO.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Dataset base: el mismo de la clase 2 (dinámica de la caja negra)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 1. Archivo limpio, convención internacional (coma, punto decimal, UTF-8)
# ---------------------------------------------------------------------------
df.to_csv(DESTINO / "caja_negra.csv", index=False, encoding="utf-8")

# ---------------------------------------------------------------------------
# 2. Archivo "exportado desde Excel en español"
#    Punto y coma como separador, coma decimal, codificación latin-1.
#    Leerlo con read_csv() por defecto falla.
# ---------------------------------------------------------------------------
df.to_csv(
    DESTINO / "caja_negra_excel.csv",
    index=False,
    sep=";",
    decimal=",",
    encoding="latin-1",
)

# ---------------------------------------------------------------------------
# 3. Archivo con faltantes codificados de cuatro maneras distintas
#    -99 (sentinela numérico), "s/d", "NA" y celda vacía.
# ---------------------------------------------------------------------------
rng = np.random.default_rng(SEMILLA)
df_faltantes = df.copy()
for col in ["peso_estimado_g", "num_aristas", "certeza_observador", "textura"]:
    df_faltantes[col] = df_faltantes[col].astype(object)

df_faltantes.loc[[2, 6], "peso_estimado_g"] = -99          # sentinela numérico
df_faltantes.loc[[5], "textura"] = "s/d"                    # sin dato
df_faltantes.loc[[8], "num_aristas"] = "NA"                 # texto
df_faltantes.loc[[1], "certeza_observador"] = ""            # celda vacía
df_faltantes.to_csv(DESTINO / "caja_negra_faltantes.csv",
                    index=False, encoding="utf-8")

# ---------------------------------------------------------------------------
# 4. Archivo "del equipo vecino": registro transaccional sin documentar.
#    Nombres de columna con espacios y mayúsculas, fecha en formato dd/mm/aaaa,
#    monto con separador de miles, categoría con espacios sobrantes.
# ---------------------------------------------------------------------------
n = 40
fechas = pd.date_range("2026-03-02", periods=n, freq="D")
sucursales = rng.choice(["Centro", "Pocitos ", " Carrasco", "Centro "], size=n)
montos = np.round(rng.gamma(shape=2.0, scale=900.0, size=n), 0)

df_vecino = pd.DataFrame({
    "ID Transaccion": range(1001, 1001 + n),
    "Fecha Operacion": fechas.strftime("%d/%m/%Y"),
    "Sucursal ": sucursales,
    "Monto UYU": [f"{m:,.0f}".replace(",", ".") for m in montos],
    "Medio de Pago": rng.choice(["debito", "credito", "efectivo"], size=n),
})
df_vecino.to_csv(DESTINO / "equipo_vecino.csv", index=False, encoding="utf-8")

# ---------------------------------------------------------------------------
print("Archivos generados en:", DESTINO.resolve())
for archivo in sorted(DESTINO.glob("*.csv")):
    print("  -", archivo.name, f"({archivo.stat().st_size} bytes)")
