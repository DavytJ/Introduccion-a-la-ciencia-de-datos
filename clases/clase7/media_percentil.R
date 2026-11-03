# =============================================================================
# Figura didáctica: media y percentil 95 con datos simulados
# Genera media_p95.png y media_p95.pdf
# Versión R (ggplot2 + patchwork)
# =============================================================================
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(patchwork)
})

set.seed(2024)

# --- Datos simulados: un día de mediciones minutales (n = 1440) ----------------
# Distribución gamma: asimétrica a la derecha, como una concentración.
k <- 4; theta <- 8                       # forma y escala
n <- 1440
x <- rgamma(n, shape = k, scale = theta)

mu      <- k * theta                                 # media poblacional  E[X]
q95_pob <- qgamma(0.95, shape = k, scale = theta)    # p95 poblacional   F^{-1}(0.95)

media <- mean(x)                                     # media muestral
p95   <- unname(quantile(x, 0.95))                   # p95 muestral (type = 7)

# --- Panel C: los mismos datos con 10 picos espurios ---------------------------
x_con_picos <- c(x, rep(500, 10))
media_c <- mean(x_con_picos)
p95_c   <- unname(quantile(x_con_picos, 0.95))

datos <- tibble(x = x)
azul <- "#1f77b4"; rojo <- "#d62728"; gris <- "#7f7f7f"

tema <- theme_minimal(base_size = 11) +
  theme(legend.position = c(0.98, 0.98), legend.justification = c(1, 1),
        legend.background = element_rect(fill = "white", colour = gris, linewidth = 0.3),
        legend.text = element_text(size = 8), legend.title = element_blank(),
        legend.key.height = unit(0.4, "cm"),
        plot.title = element_text(size = 11))

# =============================================================================
# A. Distribución, media y p95
# =============================================================================
grid <- tibble(x = seq(0, 165, length.out = 400),
               f = dgamma(x, shape = k, scale = theta))
lineasA <- tibble(valor = c(media, p95), que = c("media", "p95"))

pA <- ggplot(datos, aes(x)) +
  geom_histogram(aes(y = after_stat(density)), bins = 50, fill = gris, alpha = 0.45) +
  geom_area(data = filter(grid, x >= p95), aes(x, f), fill = rojo, alpha = 0.25) +
  geom_line(data = grid, aes(x, f), colour = "black") +
  geom_vline(data = lineasA, aes(xintercept = valor, colour = que), linewidth = 1) +
  scale_colour_manual(values = c(media = azul, p95 = rojo),
                      labels = c(media = sprintf("media = %.1f", media),
                                 p95 = sprintf("p95 = %.1f", p95))) +
  annotate("text", x = 47, y = 0.0245, label = "densidad poblacional f(x)",
           hjust = 0, size = 3, colour = "black") +
  annotate("text", x = 80, y = 0.0035, label = "5 % superior", hjust = 0, size = 3, colour = rojo) +
  annotate("text", x = 82, y = 0.0300, label = sprintf("datos simulados (n = %d)", n),
           hjust = 0, size = 3, colour = gris) +
  annotate("label", x = 163, y = c(0.0165, 0.0125, 0.0105, 0.0080), hjust = 1, size = 3,
           parse = TRUE, label.size = 0,
           label = c("bar(x) == frac(1, n) * sum(x[i], i == 1, n)",
                     "sum(x[i] - bar(x), i == 1, n) == 0",
                     "'(punto de equilibrio)'",
                     sprintf("'poblacional: ' * mu == E*'[X]' ~ '=' ~ %.0f", mu))) +
  annotate("rect", xmin = 108, xmax = 165, ymin = 0.0065, ymax = 0.0185,
           fill = NA, colour = gris, linewidth = 0.3) +
  coord_cartesian(xlim = c(0, 165)) +
  labs(title = "A. ¿Dónde están la media y el p95?", x = "O3 (µg/m³)", y = "densidad") +
  tema + theme(legend.position = c(0.98, 0.80))

# =============================================================================
# B. Definición del p95 vía la función de distribución empírica
# =============================================================================
pB <- ggplot(datos, aes(x)) +
  stat_function(fun = pgamma, args = list(shape = k, scale = theta),
                aes(linetype = "pob"), colour = gris, n = 400) +
  stat_ecdf(aes(linetype = "emp"), colour = "black", geom = "step") +
  geom_hline(yintercept = 0.95, colour = rojo, linetype = "dashed", linewidth = 0.4) +
  geom_vline(xintercept = media, colour = azul, linewidth = 1, alpha = 0.6) +
  geom_vline(xintercept = p95, colour = rojo, linewidth = 1) +
  annotate("point", x = p95, y = 0.95, colour = rojo, size = 2) +
  annotate("text", x = 118, y = 0.975, label = "0.95", colour = rojo, size = 3, hjust = 1) +
  scale_linetype_manual(values = c(emp = "solid", pob = "dotted"),
                        labels = c(emp = expression(F[n](x)~"empírica"), pob = expression(F(x)~"poblacional"))) +
  annotate("label", x = 1, y = c(0.93, 0.82, 0.74, 0.685, 0.60), hjust = 0, size = 3,
           parse = TRUE, label.size = 0,
           label = c("F[n](x) == frac(1, n) * sum(bold('1') * group('{', x[i] <= x, '}'), i == 1, n)",
                     "p[95] == min * group('{', x * ':' ~ F[n](x) >= 0.95, '}')",
                     "'con datos ordenados ' * x[(1)] <= group('', cdots <= x[(n)], '') * ':'",
                     sprintf("p[95] == x[(group(lceil, 0.95 * n, rceil))] ~ '=' ~ x[(%d)]", ceiling(0.95 * n)),
                     sprintf("'poblacional: ' * F^{-1} * (0.95) == %.1f", q95_pob))) +
  annotate("rect", xmin = 0, xmax = 84, ymin = 0.57, ymax = 0.99,
           fill = NA, colour = gris, linewidth = 0.3) +
  scale_y_continuous(limits = c(0, 1.02)) +
  labs(title = "B. El p95 como inversa de la distribución",
       x = "O3 (µg/m³)", y = "proporción de observaciones ≤ x") +
  tema + theme(legend.position = c(0.98, 0.35))

# =============================================================================
# C. Robustez: 10 picos espurios
# =============================================================================
cortes <- seq(0, 510, length.out = 81)
conteo <- function(v) {
  h <- hist(v, breaks = cortes, plot = FALSE)
  tibble(centro = h$mids, n = h$counts) %>% filter(n > 0)
}
hist_orig  <- conteo(x)
hist_picos <- conteo(x_con_picos)
ancho <- diff(cortes)[1]

lineasC <- tibble(
  valor = c(media, media_c, p95, p95_c),
  que   = factor(c("media antes", "media después", "p95 antes", "p95 después"),
                 levels = c("media antes", "media después", "p95 antes", "p95 después"))
)

pC <- ggplot() +
  geom_col(data = hist_orig, aes(centro, n, fill = "orig"), width = ancho, alpha = 0.45) +
  geom_col(data = hist_picos, aes(centro, n, colour = "picos"), width = ancho,
           fill = NA, linewidth = 0.3) +
  geom_vline(data = lineasC, aes(xintercept = valor, colour = que, linetype = que), linewidth = 1) +
  scale_fill_manual(values = c(orig = gris), labels = c(orig = "datos originales")) +
  scale_colour_manual(
    values = c(picos = "black", "media antes" = azul, "media después" = azul,
               "p95 antes" = rojo, "p95 después" = rojo),
    labels = c(picos = "+ 10 picos de 500 µg/m³",
               "media antes"   = sprintf("media antes = %.1f", media),
               "media después" = sprintf("media después = %.1f", media_c),
               "p95 antes"     = sprintf("p95 antes = %.1f", p95),
               "p95 después"   = sprintf("p95 después = %.1f", p95_c))) +
  scale_linetype_manual(
    values = c(picos = "solid", "media antes" = "dashed", "media después" = "solid",
               "p95 antes" = "dashed", "p95 después" = "solid"),
    guide = "none") +
  annotate("label", x = 300, y = 3.5, size = 3, label.size = 0.3, colour = "black",
           label = paste0(
             sprintf("la media se mueve %+.1f\nel p95 se mueve %+.1f\n\n", media_c - media, p95_c - p95),
             "en la media cada dato pesa por su valor:\n",
             "10 picos de 5000 la moverían 10 veces más\n\n",
             "en el p95 cada dato pesa por su rango:\n",
             sprintf("10 de %d es %.1f %% < 5 %%, el valor de los\npicos no importa",
                     length(x_con_picos), 100 * 10 / length(x_con_picos)))) +
  scale_y_log10() +
  guides(colour = guide_legend(override.aes = list(
    linetype = c("solid", "dashed", "solid", "dashed", "solid"),
    fill = NA))) +
  labs(title = "C. 10 picos espurios entre 1450 datos",
       x = "O3 (µg/m³)", y = "frecuencia (escala log)") +
  tema + theme(legend.spacing.y = unit(0.05, "cm"))

# =============================================================================
figura <- (pA | pB | pC) +
  plot_annotation(title = "Media y percentil 95: dos formas de resumir la misma distribución",
                  theme = theme(plot.title = element_text(hjust = 0.5, size = 13)))

ggsave("media_p95.png", figura, width = 15, height = 5, dpi = 200, bg = "white")
ggsave("media_p95.pdf", figura, width = 15, height = 5, device = cairo_pdf)

cat(sprintf("media=%.2f  p95=%.2f  |  con picos: media=%.2f  p95=%.2f\n",
            media, p95, media_c, p95_c))
pA
pB
pC
