# Hydraulic characterization phase 1 - partial 7/8 export

Fecha export: 2026-05-25T17:56:36

## Estado
- Casos exportados: 7/8
- Unblocked completos: 4/4
- With-block ref completos: 3/4
- Pendiente/no incluido: hydro_withblock_ref_H0225
- La corrida del caso faltante puede seguir viva en la WS; este paquete es parcial para analisis inmediato en laptop.

## Archivos principales
- hydraulic_phase1_partial_summary.csv
- hydraulic_unblocked_summary.csv
- hydraulic_with_block_ref_summary.csv
- hydraulic_comparison_summary_partial.csv
- selected_processed_csv/: V05, hmax03, ChronoExchange si existe, Run.csv y RunPARTs.csv por caso.

## Uso metodologico
- `unblocked` es el input transferible principal para mapear H_dam a h/u/momentum local.
- `with_block_ref` es diagnostico de perturbacion/interaccion.
- No cerrar Fase 1 definitiva hasta incluir H=0.225 with_block_ref.
