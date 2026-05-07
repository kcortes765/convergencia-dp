# Convergencia de `dp` y frontera práctica

Página estática para revisar el proceso de convergencia/resolución usado en la tesis SPH-chrono.

El contenido resume:

- cómo se evaluó la sensibilidad de resolución;
- por qué se adoptó `dp = 0.003 m` como malla operativa;
- cómo se acotó la frontera práctica en torno a `mu = 0.68050-0.68075`;
- por qué `dp = 0.002 m` se usa como evidencia suplementaria de sensibilidad, no como cierre de convergencia asintótica fuerte;
- qué se lanzó después en los lotes productivos piloto y batch2.

Abrir localmente:

```text
index.html
```

El repositorio contiene solo archivos livianos: HTML, CSS, figuras exportadas, CSV resumidos y el script generador. No incluye salidas crudas de DualSPHysics.
