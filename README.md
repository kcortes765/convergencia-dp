# Convergencia de resolución SPH

Página estática para revisar el proceso de convergencia/resolución usado en la tesis SPH-Chrono.

El contenido resume:

- cómo se compararon variables continuas al disminuir `dp`;
- cómo se usaron curvas temporales de desplazamiento, velocidad, rotación y gauges hidráulicos;
- por qué se adoptó `dp = 0.003 m` como resolución operativa;
- cómo se separó el análisis de convergencia del análisis posterior de estabilidad/frontera;
- qué se lanzó después en los lotes productivos piloto y batch2.

Abrir localmente:

```text
index.html
```

El repositorio contiene solo archivos livianos: HTML, CSS, figuras exportadas, CSV resumidos y el script generador. No incluye salidas crudas de DualSPHysics.
