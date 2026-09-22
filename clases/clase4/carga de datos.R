# Lectura de datos en csv

ingenua <- read.csv("datos_clase/ventas_local.csv")
ingenua

# Para hacerlos explícitos (misma idea que en 7.3):
# ozono_completo <- ozono_limpio %>%
#   complete(estacion, fecha = seq(min(fecha), max(fecha), by = "min"))


# -----------------------------------------------------------------------------
# 10. Outliers
# -----------------------------------------------------------------------------
# "Eliminar outliers" es una decisión de modelado, no una limpieza neutra.
# Tres reglas con lógicas distintas:
#   - física: valores imposibles (concentración negativa)
#   - IQR:    fuera de [Q1 - 1.5·IQR, Q3 + 1.5·IQR]  (regla del boxplot)
#   - percentil: fuera de [p0.5, p99.5]  (recorta siempre el 1 %, haya o no error)

## 10.1 Boxplot por estación
ggplot(ozono_sinna, aes(x = estacion, y = o3)) +
  geom_boxplot(outlier.alpha = 0.2) +
  coord_flip() +
  theme_minimal() +
  labs(title = "Distribución de O3 minutal por estación", x = NULL, y = "O3 (µg/m³)")

## 10.2 Marcar según cada regla (por estación: las distribuciones difieren)
ozono_out <- ozono_sinna %>%
  group_by(estacion) %>%
  mutate(
    q1  = quantile(o3, 0.25),
    q3  = quantile(o3, 0.75),
    iqr = q3 - q1,
    out_fisico     = o3 < 0,
    out_iqr        = o3 < q1 - 1.5 * iqr | o3 > q3 + 1.5 * iqr,
    out_percentil  = o3 < quantile(o3, 0.005) | o3 > quantile(o3, 0.995)
  ) %>%
  ungroup()

ozono_out %>%
  group_by(estacion) %>%
  summarise(across(starts_with("out_"), ~ round(mean(.x), 4)), .groups = "drop")

## 10.3 ¿Qué cambia si los eliminamos?
# La media se mueve; el p95 casi no. Esa diferencia es el argumento a favor de
# estadísticos robustos cuando el objetivo es describir episodios.
ozono_out %>%
  group_by(estacion) %>%
  summarise(
    media_todo    = mean(o3),
    media_sin_iqr = mean(o3[!out_iqr]),
    p95_todo      = quantile(o3, 0.95),
    p95_sin_iqr   = quantile(o3[!out_iqr], 0.95),
    .groups = "drop"
  ) %>%
  mutate(across(where(is.numeric), ~ round(.x, 1)))

## 10.4 Ver los outliers en el tiempo: ¿aislados o agrupados?
# Picos aislados de 1 minuto sugieren error de sensor; picos agrupados en una
# tarde sugieren un episodio real. Mismo valor, decisión opuesta.
ozono_out %>%
  filter(out_iqr) %>%
  ggplot(aes(x = fecha, y = o3)) +
  geom_point(alpha = 0.4, size = 0.8) +
  facet_wrap(~ estacion, ncol = 1) +
  theme_minimal() +
  labs(title = "Observaciones marcadas como outlier (regla IQR)",
       x = NULL, y = "O3 (µg/m³)")





