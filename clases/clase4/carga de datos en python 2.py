# %%
from pathlib import Path
import pandas as pd

# 1. Definir la ruta raíz del proyecto o del directorio de trabajo actual
BASE_DIR = Path.cwd()

# 2. Construir la ruta relativa de forma segura utilizando el operador /
# Estructura esperada: tu_proyecto/data/raw/datos.csv
archivo = "cantidad_de_residuos_en_la_estacion_de_transferencia_2023.csv"
ruta_csv = BASE_DIR / "clases" / "clase4" / archivo

ruta_csv = BASE_DIR / "clases" / "clase4" / "cantidad_de_residuos_en_la_estacion_de_transferencia_2023.csv"

# 3. Verificar que el archivo realmente existe antes de cargarlo
if not ruta_csv.exists():
    raise FileNotFoundError(f"No se encontró el archivo en: {ruta_csv}")

# 4. Cargar el archivo CSV
df = pd.read_csv(ruta_csv)

# 5. Inspección inicial de los datos
print(f"--- Archivo cargado exitosamente desde: {ruta_csv.name} ---")
print(df.info())
print("\nPrimeras 5 filas:")
print(df.head())

## 51. Dimensiones y estructura de los datos (Equivalente a str(df))
df.info()
# Nota: df.shape te da exactamente las dimensiones (filas, columnas) -> (1222, 41)
df.shape

# 2. Filas únicas: detectando la columna que contiene el ID (Equivalente a length(unique(...)))
df["matricula_letra"].nunique()

# 5.3 Datos faltantes

df.isnull().sum()  # Conteo de NA por columna
(df == "").sum()   # Falsos nulos (cadenas vacías)

## 5.4 Duplicados
df.duplicated().sum() # Cantidad de filas exactamente iguales