# =====================================================================
# leer_ticket.py — Mandar la foto de un ticket a Gemini y recibir una tabla
# Introducción a la Ciencia de Datos — UM, FCEE
#
# Antes de correrlo:
#   1. Sacar una clave gratis en https://aistudio.google.com  ("Get API key")
#   2. Guardarla en un archivo clave_gemini.txt, en la carpeta RUTA
#   3. Poner la foto del ticket en esa carpeta con el nombre ticket.jpg
#   4. Instalar el paquete requests:  pip install requests
# =====================================================================

import base64

import requests

# ---------------------------------------------------------------------
# 1. Datos de la solicitud
# ---------------------------------------------------------------------
RUTA = "clases/clase11/clase_ia/"   # carpeta de la clase (si se corre desde esa misma carpeta, poner "")
CLAVE = open(RUTA + "clave_gemini.txt").read().strip()   # la clave NO se sube a GitHub
FOTO = "ticket.jpg"
TIPO = "image/jpeg"            # si la foto es .png, poner "image/png"
MODELO = "gemini-3.5-flash-lite"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"

INSTRUCCION = """Transcribí los ítems de este ticket de compra.
Respondé solo con una tabla CSV, sin ningún otro texto, con dos columnas:
descripcion,monto
- monto con punto decimal y sin separador de miles (1.250,00 se escribe 1250.00)
- no incluyas SUBTOTAL, IVA, TOTAL, EFECTIVO, CAMBIO ni TARJETA
- si algo no se puede leer, dejalo vacío; no lo inventes"""

# ---------------------------------------------------------------------
# 2. Pasar la foto a base64 (texto), porque el JSON solo admite texto
# ---------------------------------------------------------------------
with open(RUTA + FOTO, "rb") as archivo:
    bytes_foto = archivo.read()
imagen_base64 = base64.b64encode(bytes_foto).decode("ascii")

print("La foto pesa", len(bytes_foto), "bytes")
print("En base64 son", len(imagen_base64), "caracteres y empieza con", imagen_base64[:4])

# ---------------------------------------------------------------------
# 3. Armar el cuerpo de la solicitud (un diccionario que se envía como JSON)
# ---------------------------------------------------------------------
cuerpo = {
    "contents": [{
        "parts": [
            {"text": INSTRUCCION},
            {"inline_data": {"mime_type": TIPO, "data": imagen_base64}},
        ]
    }],
    "generationConfig": {"temperature": 0},
}

# ---------------------------------------------------------------------
# 4. Enviar la solicitud: método POST, con la clave en un encabezado
# ---------------------------------------------------------------------
respuesta = requests.post(URL, headers={"x-goog-api-key": CLAVE}, json=cuerpo, timeout=120)

print("Código de estado:", respuesta.status_code)   # 200 = todo bien
if respuesta.status_code != 200:
    print(respuesta.text)                          # el mensaje de error del servidor
    raise SystemExit("La solicitud falló: revisar el código de estado")

# ---------------------------------------------------------------------
# 5. Leer la respuesta
# ---------------------------------------------------------------------
datos = respuesta.json()                                   # JSON -> diccionario
texto = datos["candidates"][0]["content"]["parts"][0]["text"]
print(texto)

uso = datos["usageMetadata"]
print("Tokens de entrada (imagen + instrucción):", uso["promptTokenCount"])
print("Tokens de salida (la respuesta):", uso["candidatesTokenCount"])

# ---------------------------------------------------------------------
# 6. Guardar la tabla y abrirla con pandas
# ---------------------------------------------------------------------
texto = texto.replace("```csv", "").replace("```", "").strip()   # por si la envuelve
with open(RUTA + "ticket_gemini.csv", "w", encoding="utf-8") as archivo:
    archivo.write(texto + "\n")

import pandas as pd

tabla = pd.read_csv(RUTA + "ticket_gemini.csv")
print(tabla)
print("Suma de los ítems:", tabla["monto"].sum())   # comparar con el TOTAL impreso
