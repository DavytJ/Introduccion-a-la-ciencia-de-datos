# %%
from pathlib import Path
import pandas as pd

# 1. Carpeta donde estamos trabajando
BASE_DIR = Path.cwd()

# 2. Nombre del archivo
archivo = "cantidad_de_residuos_en_la_estacion_de_transferencia_2023.csv"

# El CSV está dentro de la misma carpeta clase4
ruta_csv = BASE_DIR / archivo

# 3. Comprobar que existe
if not ruta_csv.exists():
    raise FileNotFoundError(f"No se encontró el archivo en: {ruta_csv}")

# 4. Cargar CSV
df = pd.read_csv(ruta_csv)

# 5. Inspección inicial
print(f"Archivo cargado exitosamente: {ruta_csv.name}")

print("\nInformación:")
df.info()

print("\nPrimeras 5 filas:")
print(df.head())


# 5.1 Dimensiones
print("\nFilas y columnas:")
print(df.shape)

# 5.2 Cantidad de matrículas únicas
print("\nMatrículas únicas:")
print(df["matricula_letra"].nunique())

# 5.3 Datos faltantes
print("\nDatos faltantes por columna:")
print(df.isnull().sum())

print("\nCadenas vacías por columna:")
print((df == "").sum())

# 5.4 Duplicados
print("\nFilas duplicadas:")
print(df.duplicated().sum())
# %%
