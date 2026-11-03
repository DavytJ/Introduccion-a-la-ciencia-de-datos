# %%
# opción 1
import os
# es el equivalente a getwd() de R:
os.getcwd()
# definir un directorio de trabajo en una subcarpeta:
os.chdir("clases/clase4")

# Subir un nivel en el árbol de carpetas (equivalente a 'cd ..'):
os.chdir("..")

# opción 2
from pathlib import Path
# listado de subdirectorios
p = Path('.')
