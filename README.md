# Convergencia de resolución SPH

Página estática para revisar el proceso de convergencia/resolución usado en la tesis SPH-Chrono.

El contenido resume:

- cómo se comparan variables continuas al disminuir `dp`;
- cuál fue el escenario físico fijo usado para correr la convergencia;
- cómo se usan máximos y curvas temporales de desplazamiento, velocidad del bloque y altura/cota de agua;
- cuáles son las diferencias absolutas y porcentuales entre `dp = 0.003 m` y `dp = 0.002 m`;
- por qué se adoptó `dp = 0.003 m` como resolución operativa;
- cómo se distinguen la banda de comparación de resolución y el umbral de movimiento `D_max > 5% d_eq`;
- cómo se usa después la resolución seleccionada en lotes productivos.

Abrir localmente:

```text
index.html
```

Regenerar las figuras adicionales de escenario y diferencias absolutas:

```powershell
python scripts\build_context_figures.py
```

El repositorio contiene solo archivos livianos: HTML, CSS, figuras exportadas, CSV resumidos y el script generador. No incluye salidas crudas de DualSPHysics.
