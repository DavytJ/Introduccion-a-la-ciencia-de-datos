# =====================================================================
# leer_ticket_groq.R — Mandar la foto de un ticket a Groq y recibir una tabla
# Introducción a la Ciencia de Datos — UM, FCEE
# Es igual a leer_ticket.R; cambian la dirección, la clave y la forma del mensaje.
#
# Antes de correrlo:
#   1. Sacar una clave en https://console.groq.com  ("API Keys")
#   2. Guardarla en un archivo clave_groq.txt, en esta misma carpeta
#   3. Poner la foto del ticket en esta carpeta con el nombre ticket.jpg
#   4. Instalar los paquetes:  install.packages(c("httr2", "jsonlite"))
# =====================================================================

library(httr2)      # para enviar solicitudes HTTP
library(jsonlite)   # para base64 y JSON

# ---------------------------------------------------------------------
# 1. Datos de la solicitud
# ---------------------------------------------------------------------
ruta <- "clases/clase11/clase_ia/"
clave  <- readLines(here::here(paste0(ruta, "clave_groq.txt")), warn = FALSE)[1]   # la clave NO se sube a GitHub
foto   <- "ticket.jpg"
tipo   <- "image/jpeg"          # si la foto es .png, poner "image/png"
modelo <- "qwen/qwen3.8-27b"   # el único modelo de Groq que recibe imágenes (los gpt-oss son solo texto)
url    <- "https://api.groq.com/openai/v1/chat/completions"

instruccion <- "Transcribí los ítems de este ticket de compra.
Respondé solo con una tabla CSV, sin ningún otro texto, con dos columnas:
descripcion,monto
- monto con punto decimal y sin separador de miles (1.250,00 se escribe 1250.00)
- no incluyas SUBTOTAL, IVA, TOTAL, EFECTIVO, CAMBIO ni TARJETA
- si algo no se puede leer, dejalo vacío; no lo inventes"

# ---------------------------------------------------------------------
# 2. Pasar la foto a base64 (texto), porque el JSON solo admite texto
# ---------------------------------------------------------------------
bytes_foto     <- readBin(here::here(paste0(ruta, foto)), what = "raw", n = file.size(here::here(paste0(ruta, foto))))
imagen_base64  <- gsub("[\r\n]", "", base64_enc(bytes_foto))   # sin saltos de línea

cat("La foto pesa", length(bytes_foto), "bytes\n")
cat("En base64 son", nchar(imagen_base64), "caracteres y empieza con",
    substr(imagen_base64, 1, 4), "\n")

# ---------------------------------------------------------------------
# 3. Armar el cuerpo de la solicitud (una lista que se envía como JSON)
#    En Groq la imagen va como una dirección "data:" que contiene el base64
# ---------------------------------------------------------------------
cuerpo <- list(
  model = modelo,
  temperature = 0,
  max_tokens = 800,     # Groq gratis permite 1000 tokens de salida por minuto; sin esto reserva 2048 y rechaza con 429
  messages = list(list(
    role = "user",
    content = list(
      list(type = "text", text = instruccion),
      list(type = "image_url",
           image_url = list(url = paste0("data:", tipo, ";base64,", imagen_base64)))
    )
  ))
)

# ---------------------------------------------------------------------
# 4. Enviar la solicitud: método POST, con la clave en un encabezado
# ---------------------------------------------------------------------
respuesta <- request(url) |>
  req_headers(Authorization = paste("Bearer", clave)) |>
  req_body_json(cuerpo) |>                 # también fija el método POST
  req_timeout(120) |>
  req_retry(max_tries = 5, backoff = function(intento) 10 * intento) |>   # si da 429 o 503, espera y reintenta
  req_error(is_error = function(r) FALSE) |>   # no cortar: queremos ver el código
  req_perform()

cat("Código de estado:", resp_status(respuesta), "\n")   # 200 = todo bien
if (resp_status(respuesta) != 200) {
  cat(resp_body_string(respuesta), "\n")   # el mensaje de error del servidor
  stop("La solicitud falló: revisar el código de estado")
}

# ---------------------------------------------------------------------
# 5. Leer la respuesta (en Groq el texto está en choices[[1]]$message$content)
# ---------------------------------------------------------------------
datos <- resp_body_json(respuesta)                        # JSON -> lista
texto <- datos$choices[[1]]$message$content
cat(texto, "\n")

cat("Tokens de entrada (imagen + instrucción):", datos$usage$prompt_tokens, "\n")
cat("Tokens de salida (la respuesta):", datos$usage$completion_tokens, "\n")

# ---------------------------------------------------------------------
# 6. Guardar la tabla y abrirla
# ---------------------------------------------------------------------
texto <- gsub("```csv|```", "", texto)       # por si la envuelve
writeLines(trimws(texto), "ticket.csv")

tabla <- read.csv("ticket.csv")
print(tabla)
cat("Suma de los ítems:", sum(tabla$monto, na.rm = TRUE), "\n")   # comparar con el TOTAL impreso

# ---------------------------------------------------------------------
# 6. Guardar la tabla y abrirla
# ---------------------------------------------------------------------
texto <- gsub("```csv|```", "", texto)       # por si la envuelve
writeLines(trimws(texto), here::here(paste0(ruta, "ticket_groq_qwen.csv"))) 

tabla <- read.csv(here::here(paste0(ruta, "ticket_groq_qwen.csv")))
print(tabla)
cat("Suma de los ítems:", sum(tabla$monto, na.rm = TRUE), "\n")   # comparar con el TOTAL impreso

