# -*- coding: utf-8 -*-
# Generador de los archivos de ejemplo de la clase «Cargar datos» — versión R
# Joselina Davyt-Colo — Facultad de Ciencias Empresariales y Economía — Universidad de Montevideo
#
# Se ejecuta una sola vez, antes de seguir el documento de la clase:
#
#     source("generar_datos_clase.R")        (desde R o RStudio)
#     Rscript generar_datos_clase.R          (desde la terminal)
#
# Crea la carpeta `datos_clase/` con los mismos datos —ventas mensuales de una
# cadena de locales— guardados en seis formatos distintos. La comparación entre
# esos seis archivos es el contenido de la clase.
#
# Paquetes: haven, openxlsx, DBI, RSQLite y jsonlite.
#     install.packages(c("haven", "openxlsx", "DBI", "RSQLite", "jsonlite"))

library(haven)
library(openxlsx)
library(DBI)
library(jsonlite)

CARPETA <- "datos_clase"
dir.create(CARPETA, showWarnings = FALSE)

base <- data.frame(
  id_local   = c(101L, 102L, 103L, 104L, 105L, 106L),
  sucursal   = c("Centro", "Centro", "Pocitos", "Cordón", "Pocitos", "Cordón"),
  mes        = c("2025-01", "2025-02", "2025-01", "2025-02", "2025-03", "2025-03"),
  ventas_uyu = c(128500.50, 143200.00, 98750.25, 110430.75, 152980.00, 121045.40),
  empleados  = c(12L, 12L, 8L, 9L, 8L, 9L)
)


# --- 1. CSV con las convenciones locales -----------------------------------
# Punto y coma como separador, coma decimal, codificación latin-1: es lo que
# exporta Excel en español y lo que publican varios organismos.
write.table(base, file.path(CARPETA, "ventas_local.csv"),
            sep = ";", dec = ",", row.names = FALSE, quote = FALSE,
            fileEncoding = "latin1")


# --- 2. Excel con dos hojas y filas de título -------------------------------
# La tabla no empieza en A1: arriba hay un título y una fecha, como en
# cualquier reporte real.
wb <- createWorkbook()
addWorksheet(wb, "ventas")
addWorksheet(wb, "locales")
writeData(wb, "ventas", "Reporte de ventas — uso interno", startRow = 1, startCol = 1)
writeData(wb, "ventas", "Generado el 12/03/2025", startRow = 2, startCol = 1)
writeData(wb, "ventas", base, startRow = 4)
writeData(wb, "locales", data.frame(
  sucursal = c("Centro", "Pocitos", "Cordón"),
  barrio   = c("Ciudad Vieja", "Pocitos", "Cordón"),
  m2       = c(220L, 180L, 150L)))
saveWorkbook(wb, file.path(CARPETA, "ventas.xlsx"), overwrite = TRUE)


# --- 3. Stata, con etiquetas de variable ------------------------------------
stata <- base
attr(stata$ventas_uyu, "label") <- "Ventas mensuales en pesos uruguayos"
attr(stata$empleados,  "label") <- "Personal ocupado en el local"
write_dta(stata, file.path(CARPETA, "ventas.dta"), version = 14)


# --- 4. SPSS, con etiquetas de variable y de valor --------------------------
# En SPSS la sucursal viaja como código numérico y la etiqueta dice qué
# significa cada número.
spss <- base
spss$sucursal_cod <- labelled(
  match(spss$sucursal, c("Centro", "Pocitos", "Cordón")),
  labels = c(Centro = 1, Pocitos = 2, "Cordón" = 3),
  label  = "Sucursal")
spss$sucursal <- NULL
attr(spss$ventas_uyu, "label") <- "Ventas mensuales en pesos"
write_sav(spss, file.path(CARPETA, "ventas.sav"))


# --- 5. Base de datos SQLite con dos tablas ---------------------------------
con <- dbConnect(RSQLite::SQLite(), file.path(CARPETA, "comercio.db"))
dbWriteTable(con, "ventas", base, overwrite = TRUE)
dbWriteTable(con, "locales", data.frame(
  sucursal = c("Centro", "Pocitos", "Cordón"),
  region   = c("Sur", "Sur", "Centro")), overwrite = TRUE)
dbDisconnect(con)


# --- 6. Respuesta anidada, del tipo que devuelve una API --------------------
respuesta <- list(
  meta = list(fuente = "sistema interno", actualizado = "2025-03-31"),
  resultados = list(
    list(local = list(id = 101L, sucursal = "Centro"),
         periodo = "2025-01", ventas = 128500.50),
    list(local = list(id = 103L, sucursal = "Pocitos"),
         periodo = "2025-01", ventas = 98750.25)
  )
)
write(toJSON(respuesta, auto_unbox = TRUE, pretty = TRUE),
      file.path(CARPETA, "respuesta_api.json"))


cat("Archivos creados en", normalizePath(CARPETA), ":\n")
cat(paste0("   ", list.files(CARPETA), collapse = "\n"), "\n")
