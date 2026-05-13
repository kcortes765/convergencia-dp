# Convergencia de resolución SPH

Página estática para revisar el proceso de convergencia/resolución usado en la tesis SPH-Chrono.

El contenido resume:

- cómo se comparan variables continuas al disminuir `dp`;
- cómo se usan máximos y curvas temporales de desplazamiento, velocidad del bloque y altura/cota de agua;
- por qué se adoptó `dp = 0.003 m` como resolución operativa;
- cómo se distinguen la banda de comparación de resolución y el umbral de movimiento `D_max > 5% d_eq`;
- cómo se usa después la resolución seleccionada en lotes productivos.

Abrir localmente:

```text
index.html
```

El repositorio contiene solo archivos livianos: HTML, CSS, figuras exportadas, CSV resumidos y el script generador. No incluye salidas crudas de DualSPHysics.
