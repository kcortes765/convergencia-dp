# Hydraulic characterization phase 2 - complete 6/6

Fecha export: 2026-05-26T21:17:45

## Estado
- Casos completados/exportados: 6/6
- Unblocked completos: 3/3
- With-block ref completos: 3/3
- Fallos numericos detectados: 0
- NTFY nativo activo durante la corrida; sin heartbeat.

## Uso metodologico
- Fase 2 densifica H_dam intermedios para transformar a variables hidraulicas locales.
- `unblocked` es el insumo transferible principal.
- `with_block_ref` es diagnostico de perturbacion/interaccion con bloque estable.

## Resumen por caso
- hydro2_unblocked_H01875: condition=unblocked, H=0.1875, hmax=0.0492 m, Uxmax=0.873 m/s, rho*hU2=11.45.
- hydro2_unblocked_H02050: condition=unblocked, H=0.2050, hmax=0.0542 m, Uxmax=0.829 m/s, rho*hU2=13.45.
- hydro2_unblocked_H02175: condition=unblocked, H=0.2175, hmax=0.0577 m, Uxmax=0.930 m/s, rho*hU2=15.33.
- hydro2_withblock_ref_H01875: condition=with_block_ref, H=0.1875, hmax=0.0665 m, Uxmax=0.822 m/s, rho*hU2=8.88, Dmax=1.23% d_eq.
- hydro2_withblock_ref_H02050: condition=with_block_ref, H=0.2050, hmax=0.0680 m, Uxmax=0.814 m/s, rho*hU2=9.00, Dmax=1.23% d_eq.
- hydro2_withblock_ref_H02175: condition=with_block_ref, H=0.2175, hmax=0.0713 m, Uxmax=0.871 m/s, rho*hU2=10.94, Dmax=1.23% d_eq.

## Comparacion with_block_ref / unblocked
- H=0.1875: h ratio=1.351, U ratio=0.941, momentum ratio=0.775, Dmax=1.23% d_eq.
- H=0.2050: h ratio=1.255, U ratio=0.982, momentum ratio=0.669, Dmax=1.23% d_eq.
- H=0.2175: h ratio=1.235, U ratio=0.936, momentum ratio=0.713, Dmax=1.23% d_eq.

## Archivos
- `hydraulic_phase1_all_summary.csv`: resumen de los 6 casos.
- `hydraulic_unblocked_summary.csv`: solo flujo incidente.
- `hydraulic_with_block_ref_summary.csv`: diagnostico con bloque.
- `hydraulic_comparison_summary.csv`: ratios por H.
- `selected_processed_csv/`: V05, hmax03, ChronoExchange si existe, Run.csv y RunPARTs.csv.

No incluye `.bi4`, `.ibi4`, VTK, `Part*`, `cases/` ni carpetas `_out`.
