# =====================================================================
# leer_ticket_groq.py — Mandar la foto de un ticket a Groq y recibir una tabla
# Introducción a la Ciencia de Datos — UM, FCEE
# Es igual a leer_ticket.py; cambian la dirección, la clave y la forma del mensaje.
#
# Antes de correrlo:
#   1. Sacar una clave en https://console.groq.com  ("API Keys")
#   2. Guardarla en un archivo clave_groq.txt, en la carpeta RUTA
#   3. Poner la foto del ticket en esa carpeta con el nombre ticket.jpg
#   4. Instalar el paquete requests:  pip install requests
# =====================================================================

import base64
import time

import requests

# ---------------------------------------------------------------------
# 1. Datos de la solicitud
# ---------------------------------------------------------------------
RUTA = "clases/clase11/clase_ia/"   # carpeta de la clase (si se corre desde esa misma carpeta, poner "")
CLAVE = open(RUTA + "clave_groq.txt").read().strip()   # la clave NO se sube a GitHub
FOTO = "ticket.jpg"
TIPO = "image/jpeg"            # si la foto es .png, poner "image/png"
MODELO = "qwen/qwen3.8-27b"    # el único modelo de Groq que recibe imágenes (los gpt-oss son solo texto)
URL = "https://api.groq.com/openai/v1/chat/completions"

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
#    En Groq la imagen va como una dirección "data:" que contiene el base64
# ---------------------------------------------------------------------
cuerpo = {
    "model": MODELO,
    "temperature": 0,
    "max_tokens": 800,     # Groq gratis permite 1000 tokens de salida por minuto; sin esto reserva 2048 y rechaza con 429
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": INSTRUCCION},
            {"type": "image_url",
             "image_url": {"url": f"data:{TIPO};base64,{imagen_base64}"}},
        ],
    }],
}

# ---------------------------------------------------------------------
# 4. Enviar la solicitud: método POST, con la clave en un encabezado
# ---------------------------------------------------------------------
for intento in range(1, 6):                    # hasta 5 intentos
    respuesta = requests.post(URL, headers={"Authorization": "Bearer " + CLAVE},
                              json=cuerpo, timeout=120)
    if respuesta.status_code not in (429, 503) or intento == 5:   # 429 = cuota, 503 = servidor saturado
        break
    print("Código", respuesta.status_code, "- espero", 10 * intento, "segundos y reintento")
    time.sleep(10 * intento)

print("Código de estado:", respuesta.status_code)   # 200 = todo bien
if respuesta.status_code != 200:
    print(respuesta.text)                          # el mensaje de error del servidor
    raise SystemExit("La solicitud falló: revisar el código de estado")

# ---------------------------------------------------------------------
# 5. Leer la respuesta (en Groq el texto está en choices[0].message.content)
# ---------------------------------------------------------------------
datos = respuesta.json()                                   # JSON -> diccionario
texto = datos["choices"][0]["message"]["content"]
print(texto)

uso = datos["usage"]
print("Tokens de entrada (imagen + instrucción):", uso["prompt_tokens"])
print("Tokens de salida (la respuesta):", uso["completion_tokens"])

# ---------------------------------------------------------------------
# 6. Guardar la tabla y abrirla con pandas
# ---------------------------------------------------------------------
texto = texto.replace("```csv", "").replace("```", "").strip()   # por si la envuelve
with open(RUTA + "ticket_groq_qwen.csv", "w", encoding="utf-8") as archivo:
    archivo.write(texto + "\n")

import pandas as pd

tabla = pd.read_csv(RUTA + "ticket_groq_qwen.csv")
print(tabla)
print("Suma de los ítems:", tabla["monto"].sum())   # comparar con el TOTAL impreso
