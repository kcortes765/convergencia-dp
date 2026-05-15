# Production Story Graphics

Figuras derivadas de exports livianos oficiales: piloto, batch2, batch3, batch4 y AL1.

## Regla visual aplicada
- El desplazamiento normalizado usa `Dmax (% d_eq)` y siempre muestra equivalente absoluto en mm cuando aparece como eje o escala principal.
- Umbral primario: `5% d_eq = 5.02 mm`.
- Colores de clase: azul = ESTABLE, vermillion = FALLO; se evita depender solo de rojo/verde.
- La rotacion se muestra como diagnostico acumulado; no define la clase.
- Las gauges hidraulicas explican contexto fisico, pero ChronoExchange sigue siendo la fuente primaria del movimiento del bloque.

## Dataset
- Casos oficiales incluidos: 42.
- Casos parciales documentados pero no usados como evidencia principal: 1.
- Rango H: 0.175 a 0.250 m.
- Rango mu: 0.300 a 0.860.
- Rango m*: 0.85 a 1.25.

## Figuras esenciales
- `01_response_map_h_mu_by_mass.png` / `01_response_map_h_mu_by_mass.svg`
  - Muestra: Mapa H-mu separado por masa relativa; color/forma indica clase y tamano indica Dmax.
  - Importa: Resume la frontera operacional aprendida por lotes dirigidos usando todos los casos oficiales hasta AL1.
  - Cautela: No interpolar visualmente: los puntos son simulaciones discretas, no una superficie continua validada.
- `02_margin_vs_mu_by_mass_and_h.png` / `02_margin_vs_mu_by_mass_and_h.svg`
  - Muestra: Margen continuo contra mu, con eje secundario en mm.
  - Importa: Evita reducir la fisica a una clase binaria; muestra cuan lejos queda cada punto del umbral.
  - Cautela: Las lineas unen puntos de la misma H solo como ayuda visual, no como interpolacion formal.
- `03_batch_story_margin_strip.png` / `03_batch_story_margin_strip.svg`
  - Muestra: Secuencia de lotes con margen continuo al umbral, en % y mm.
  - Importa: Cuenta visualmente como el experimento dirigido paso de extremos a puntos de frontera.
  - Cautela: No representa orden temporal exacto de cada simulacion, sino orden logico por lote.
- `06_rotation_diagnostic_vs_displacement.png` / `06_rotation_diagnostic_vs_displacement.svg`
  - Muestra: Rotacion acumulada maxima contra desplazamiento, con umbrales visuales.
  - Importa: Evita la confusion metodologica: rotar no equivale a fallar bajo displacement_only.
  - Cautela: La rotacion se integra de la velocidad angular y se reporta como diagnostico acumulado.

## Figuras de apoyo y suplementarias
- `04_local_hydraulics_vs_displacement.png` / `04_local_hydraulics_vs_displacement.svg` (apoyo)
  - Muestra: Relacion entre hmax/Umax locales y desplazamiento del bloque.
  - Importa: Ayuda a explicar fisicamente los fallos mas alla de H nominal.
  - Cautela: Las gauges son diagnosticas: no sustituyen ChronoExchange como evidencia primaria del movimiento.
- `05_forces_vs_displacement.png` / `05_forces_vs_displacement.svg` (suplementaria)
  - Muestra: Fuerza SPH y contacto contra Dmax, con eje superior en mm.
  - Importa: Muestra que las fuerzas son diagnosticas y deben leerse junto al desplazamiento.
  - Cautela: Contacto no se usa como criterio de falla por su variabilidad; se reporta solo como diagnostico.
- `07_computational_cost_by_batch.png` / `07_computational_cost_by_batch.svg` (apoyo)
  - Muestra: Tiempo y memoria de los lotes productivos oficiales.
  - Importa: Justifica por que el refinamiento y active learning se hacen en lotes pequenos.
  - Cautela: Los campos de costo faltan en algunos exports; esos puntos se omiten.
- `08_mass_effect_displacement_summary.png` / `08_mass_effect_displacement_summary.svg` (apoyo)
  - Muestra: Dmax contra m*, coloreado por mu y con borde por clase.
  - Importa: Resume el aprendizaje central de batch4/AL1: m* baja aumenta criticidad.
  - Cautela: No controla por H en un solo panel; usar junto al mapa H-mu por masa.

## Advertencias metodologicas
- Estas figuras describen la frontera operacional a `dp=0.003`, no una frontera universal independiente de resolucion.
- Los puntos unidos por lineas son guias visuales; la superficie formal debe venir de surrogate/GP y validacion posterior.
- AL2 esta en ejecucion y no se incluye hasta tener export oficial.
