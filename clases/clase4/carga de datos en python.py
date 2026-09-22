# %%
import sqlite3
import pandas as pd
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ==============================================================================
# 1. GESTIÓN DE RUTAS Y ESTRUCTURA DEL PROYECTO (Equivalente a 'here' / Rproj)
# ==============================================================================
# Path.cwd() detecta la carpeta raíz del proyecto desde donde ejecutas el script
BASE_DIR = Path.cwd()
# Definimos las subcarpetas del proyecto de manera agnóstica al Sistema Operativo
DIR_DATOS = BASE_DIR / "datos"
DIR_REPORTES = BASE_DIR / "reportes"
DIR_BD = BASE_DIR / "base_datos"

# Creamos las carpetas si aún no existen
# de a una
DIR_DATOS.mkdir(parents=True, exist_ok=True)

# todas juntas
for carpeta in [DIR_DATOS, DIR_REPORTES, DIR_BD]:
    carpeta.mkdir(parents=True, exist_ok=True)
#parents=True: Crea cualquier carpeta contenedora intermedia que haga falta.
#exist_ok=True: Evita que el código lance un error si la carpeta ya existía previamente.

# ==============================================================================
# 2. DEFINICIÓN DE LOS DATOS (DataFrames de pandas)
# ==============================================================================
df_ventas = pd.DataFrame({
    'id_venta': [101, 102, 103, 104, 105],
    'sucursal': ['Centro', 'Pocitos', 'Cordón', 'Centro', 'Pocitos'],
    'monto': [1500, 2300, 890, 4100, 1750],
    'fecha': ['2025-03-10', '2025-03-11', '2025-03-11', '2025-03-12', '2025-03-12']
})

df_locales = pd.DataFrame({
    'sucursal': ["Centro", "Pocitos", "Cordón"],
    'barrio': ["Ciudad Vieja", "Pocitos", "Cordón"],
    'region': ["Sur", "Sur", "Centro"],
    'm2': [220, 180, 150]
})

# Opcional: Guardar respaldo en CSV en la carpeta de datos
df_ventas.to_csv(DIR_DATOS / "ventas.csv", index=False)

# ==============================================================================
# 3. GENERACIÓN DEL EXCEL CON FORMATO (Equivalente a openxlsx de R)
# ==============================================================================
wb = Workbook()

# --- Estilos Globales Reutilizables ---
font_titulo = Font(name="Segoe UI", size=14, bold=True, color="1F497D")
font_subtitulo = Font(name="Segoe UI", size=10, italic=True, color="595959")
font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
fill_header = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
border_thin = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

# --- Pestaña 1: "ventas" ---
ws_ventas = wb.active
ws_ventas.title = "ventas"

# Títulos iniciales
ws_ventas["A1"] = "Reporte de ventas — uso interno"
ws_ventas["A1"].font = font_titulo
ws_ventas["A2"] = "Generado el 12/03/2025"
ws_ventas["A2"].font = font_subtitulo

# Encabezados de la tabla (Fila 4)
for col_num, header in enumerate(df_ventas.columns, 1):
    cell = ws_ventas.cell(row=4, column=col_num, value=header)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = Alignment(horizontal="center")

# Datos de la tabla
for row_idx, row_data in enumerate(df_ventas.values, start=5):
    for col_idx, val in enumerate(row_data, start=1):
        cell = ws_ventas.cell(row=row_idx, column=col_idx, value=val)
        cell.border = border_thin
        if col_idx == 3:  # Columna Monto
            cell.number_format = "$#,##0"
            cell.alignment = Alignment(horizontal="right")
        elif col_idx == 4:  # Columna Fecha
            cell.alignment = Alignment(horizontal="center")

# Auto-ajustar anchos de columna
for col in ws_ventas.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws_ventas.column_dimensions[col_letter].width = max(max_len + 3, 12)

# --- Pestaña 2: "locales" ---
ws_locales = wb.create_sheet(title="locales")

# EPath.cwd()ncabezados
for col_num, header in enumerate(df_locales.columns, 1):
    cell = ws_locales.cell(row=1, column=col_num, value=header)
    cell.font = font_header
    cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    cell.alignment = Alignment(horizontal="center")

# Datos
for row_idx, row_data in enumerate(df_locales.values, start=2):
    for col_idx, val in enumerate(row_data, start=1):
        cell = ws_locales.cell(row=row_idx, column=col_idx, value=val)
        cell.border = border_thin
        if col_idx == 4:  # m2
            cell.number_format = "#,##0"

for col in ws_locales.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws_locales.column_dimensions[col_letter].width = max(max_len + 3, 12)

# Guardar el archivo Excel en la carpeta de reportes
wb.save(DIR_REPORTES / "ventas.xlsx")

# ==============================================================================
# 4. BASE DE DATOS SQLITE (Equivalente a RSQLite + DBI)
# ==============================================================================
path_db = DIR_BD / "comercio.db"

# Usamos 'with' para abrir y cerrar la conexión automáticamente de forma limpia
with sqlite3.connect(path_db) as con:
    # Escribir tablas (if_exists='replace' equivale a overwrite=TRUE)
    df_ventas.to_sql("ventas", con, if_exists="replace", index=False)
    df_locales.to_sql("locales", con, if_exists="replace", index=False)

    # Ejemplo de consulta SQL desde Python
    query = """
        SELECT v.id_venta, v.sucursal, l.barrio, v.monto, v.fecha
        FROM ventas v
        INNER JOIN locales l ON v.sucursal = l.sucursal
    """
    df_resultado = pd.read_sql_query(query, con)

print("¡Proceso completado exitosamente!")