# =====================================================================
# leer_ticket.R — Mandar la foto de un ticket a Gemini y recibir una tabla
# Introducción a la Ciencia de Datos — UM, FCEE
#
# Antes de correrlo:
#   1. Sacar una clave gratis en https://aistudio.google.com  ("Get API key")
#   2. Guardarla en un archivo clave_gemini.txt, en esta misma carpeta
#   3. Poner la foto del ticket en esta carpeta con el nombre ticket.jpg
#   4. Instalar los paquetes:  install.packages(c("httr2", "jsonlite"))
# =====================================================================

library(httr2)      # para enviar solicitudes HTTP
library(jsonlite)   # para base64 y JSON

# ---------------------------------------------------------------------
# 1. Datos de la solicitud
# ---------------------------------------------------------------------
ruta <- "clases/clase11/clase_ia/"
clave  <- readLines(here::here(paste0(ruta, "clave_gemini.txt")), warn = FALSE)[1]   # la clave NO se sube a GitHub
foto   <- "ticket.jpg"
tipo   <- "image/jpeg"          # si la foto es .png, poner "image/png"
modelo <- "gemini-3.5-flash-lite"
url    <- paste0("https://generativelanguage.googleapis.com/v1beta/models/",
                 modelo, ":generateContent")

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
# ---------------------------------------------------------------------
cuerpo <- list(
  contents = list(list(
    parts = list(
      list(text = instruccion),
      list(inline_data = list(mime_type = tipo, data = imagen_base64))
    )
  )),
  generationConfig = list(temperature = 0)
)

# ---------------------------------------------------------------------
# 4. Enviar la solicitud: método POST, con la clave en un encabezado
# ---------------------------------------------------------------------
respuesta <- request(url) |>
  req_headers(`x-goog-api-key` = clave) |>
  req_body_json(cuerpo) |>                 # también fija el método POST
  req_timeout(120) |>
  req_error(is_error = function(r) FALSE) |>   # no cortar: queremos ver el código
  req_perform()

cat("Código de estado:", resp_status(respuesta), "\n")   # 200 = todo bien
if (resp_status(respuesta) != 200) {
  cat(resp_body_string(respuesta), "\n")   # el mensaje de error del servidor
  stop("La solicitud falló: revisar el código de estado")
}

# ---------------------------------------------------------------------
# 5. Leer la respuesta
# ---------------------------------------------------------------------
datos <- resp_body_json(respuesta)                        # JSON -> lista
texto <- datos$candidates[[1]]$content$parts[[1]]$text
cat(texto, "\n")

cat("Tokens de entrada (imagen + instrucción):", datos$usageMetadata$promptTokenCount, "\n")
cat("Tokens de salida (la respuesta):", datos$usageMetadata$candidatesTokenCount, "\n")

# ---------------------------------------------------------------------
# 6. Guardar la tabla y abrirla
# ---------------------------------------------------------------------
texto <- gsub("```csv|```", "", texto)       # por si la envuelve
writeLines(trimws(texto), here::here(paste0(ruta, "ticket_gemini.csv"))) 

tabla <- read.csv(here::here(paste0(ruta, "ticket_gemini.csv")))
print(tabla)
cat("Suma de los ítems:", sum(tabla$monto, na.rm = TRUE), "\n")   # comparar con el TOTAL impreso
