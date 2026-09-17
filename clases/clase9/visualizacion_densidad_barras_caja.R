# densidad
ggplot(ozono_new, aes(o3)) +
  geom_density()

# barras
ozono_new %>%
  ggplot(aes(o3)) +
  geom_bar() +
  scale_fill_hue(c = 40) +
  theme(legend.position="none") +
  theme_bw()

# caja
ozono_new %>%
  ggplot(aes(o3)) +
  geom_boxplot() +
  scale_fill_hue(c = 40) +
  theme(legend.position="none") +
  theme_bw()
