# Hydraulic characterization phase 1 - complete 8/8

Fecha export: 2026-05-25T21:19:44

## Estado
- Casos completados/exportados: 8/8
- Unblocked completos: 4/4
- With-block ref completos: 4/4
- Fallos numericos detectados en esta fase: 0
- Este export reemplaza al parcial 7/8 como paquete principal para analisis en laptop.

## Uso metodologico
- `unblocked` es el insumo principal transferible para caracterizar el flujo incidente local.
- `with_block_ref` es diagnostico de perturbacion e interaccion bloque-flujo, no reemplaza el flujo incidente.
- La rotacion/desplazamiento del bloque en with_block_ref se usa como diagnostico de estabilidad del caso de referencia.

## Resumen por caso
- hydro_unblocked_H0175: condition=unblocked, H=0.175, hmax=0.0493 m, Uxmax=0.801 m/s, rho*hU2=9.59.
- hydro_unblocked_H0200: condition=unblocked, H=0.200, hmax=0.0540 m, Uxmax=0.818 m/s, rho*hU2=13.08.
- hydro_unblocked_H0210: condition=unblocked, H=0.210, hmax=0.0536 m, Uxmax=0.864 m/s, rho*hU2=14.01.
- hydro_unblocked_H0225: condition=unblocked, H=0.225, hmax=0.0592 m, Uxmax=0.896 m/s, rho*hU2=16.75.
- hydro_withblock_ref_H0175: condition=with_block_ref, H=0.175, hmax=0.0663 m, Uxmax=0.778 m/s, rho*hU2=7.59, Dmax=1.23% d_eq.
- hydro_withblock_ref_H0200: condition=with_block_ref, H=0.200, hmax=0.0682 m, Uxmax=0.759 m/s, rho*hU2=8.01, Dmax=1.23% d_eq.
- hydro_withblock_ref_H0210: condition=with_block_ref, H=0.210, hmax=0.0692 m, Uxmax=0.868 m/s, rho*hU2=7.98, Dmax=1.23% d_eq.
- hydro_withblock_ref_H0225: condition=with_block_ref, H=0.225, hmax=0.0714 m, Uxmax=0.821 m/s, rho*hU2=10.24, Dmax=1.26% d_eq.

## Comparacion with_block_ref / unblocked
- H=0.175: h ratio=1.345, U ratio=0.972, momentum ratio=0.791, Dmax=1.23% d_eq.
- H=0.200: h ratio=1.264, U ratio=0.927, momentum ratio=0.612, Dmax=1.23% d_eq.
- H=0.210: h ratio=1.290, U ratio=1.004, momentum ratio=0.570, Dmax=1.23% d_eq.
- H=0.225: h ratio=1.206, U ratio=0.916, momentum ratio=0.611, Dmax=1.26% d_eq.

## Archivos
- `hydraulic_phase1_all_summary.csv`: resumen 8 casos.
- `hydraulic_unblocked_summary.csv`: solo flujo incidente.
- `hydraulic_with_block_ref_summary.csv`: solo diagnostico con bloque.
- `hydraulic_comparison_summary.csv`: ratios por H entre with_block_ref y unblocked.
- `selected_processed_csv/`: V05, hmax03, ChronoExchange si existe, Run.csv y RunPARTs.csv por caso.
- `hydraulic_characterization_status.json`: estado final de la reanudacion.

No incluye `.bi4`, `.ibi4`, VTK, `Part*`, `cases/` ni carpetas `_out`.
