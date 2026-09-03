library(here)
library(readr)

# 1. Definir la ruta del archivo con here
archivo <- "cantidad_de_residuos_en_la_estacion_de_transferencia_2023.csv"
ruta_csv <- here("clases", "clase4", archivo)

# 2. Cargar el archivo CSV
df <- read_csv(ruta_csv)

# 3. Profiling inicial: Dimensiones y estructura
cat("--- Archivo cargado:", basename(ruta_csv), "---\n")
cat("Dimensiones (filas, columnas):", dim(df), "\n")
str(df)

# 4. Primeras filas
head(df)

# 5. Detección de Columna ID (Comprobar valores únicos por columna)
# Si el resultado es igual a nrow(df), esa columna es un ID único
cat("\nValores únicos por columna (Buscar candidatos a ID):\n")
sapply(df, function(x) length(unique(x)))

# 6. Diagnóstico de datos faltantes y falsos nulos
cat("\nValores nulos (NA) por columna:\n")
colSums(is.na(df))

cat("\nFalsos nulos (Cadenas vacías '') por columna:\n")
colSums(df == "", na.rm = TRUE)

# 7. Diagnóstico de filas duplicadas
cat("\nTotal de filas exactamente duplicadas:\n")
sum(duplicated(df))
