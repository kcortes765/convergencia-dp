from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "convergence_story_web"
FIG = OUT / "figures"
DATA = OUT / "data"
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "data" / "results"

D_EQ = 0.100421
REF_TIME = 0.5

GREEN = "#2f7d4f"
RED = "#b73b3b"
BLUE = "#2b6f9f"
AMBER = "#b98524"
GRAY = "#687385"
INK = "#17202a"

TEMPORAL_CASES = {
    0.006: "conv3_f05_full_dp0006",
    0.005: "conv3_f05_full_dp0005",
    0.004: "conv3_f05_full_dp0004",
    0.003: "conv3_f05_full_dp0003",
    0.002: "conv3_f05_full_dp0002",
}


def init() -> None:
    for path in [OUT, FIG, DATA]:
        path.mkdir(parents=True, exist_ok=True)
    for old in FIG.glob("*"):
        if old.suffix.lower() in {".png", ".svg"}:
            old.unlink()
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 220,
            "font.family": "DejaVu Sans",
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.18,
        }
    )


def save(name: str) -> None:
    for ext in ("png", "svg"):
        plt.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", facecolor="white")
    plt.close()


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, **kwargs)


def speed(df: pd.DataFrame, prefix: str) -> pd.Series:
    return np.sqrt(df[f"{prefix}.x [m/s]"] ** 2 + df[f"{prefix}.y [m/s]"] ** 2 + df[f"{prefix}.z [m/s]"] ** 2)


def load_chrono(case_dir: str) -> pd.DataFrame:
    df = read_csv(PROCESSED / case_dir / "ChronoExchange_mkbound_51.csv", sep=";")
    t0 = df["time [s]"].iloc[0]
    x0 = df["fcenter.x [m]"].iloc[0]
    y0 = df["fcenter.y [m]"].iloc[0]
    z0 = df["fcenter.z [m]"].iloc[0]
    df["t_rel"] = df["time [s]"] - t0 + REF_TIME
    df["disp_pct"] = (
        np.sqrt(
            (df["fcenter.x [m]"] - x0) ** 2
            + (df["fcenter.y [m]"] - y0) ** 2
            + (df["fcenter.z [m]"] - z0) ** 2
        )
        / D_EQ
        * 100
    )
    df["block_speed"] = np.sqrt(df["fvel.x [m/s]"] ** 2 + df["fvel.y [m/s]"] ** 2 + df["fvel.z [m/s]"] ** 2)
    omega = np.sqrt(
        df["fomega.x [rad/s]"] ** 2
        + df["fomega.y [rad/s]"] ** 2
        + df["fomega.z [rad/s]"] ** 2
    )
    dt = df["time [s]"].diff().fillna(0)
    df["rotation_deg"] = (omega * dt).cumsum() * 180 / np.pi
    return df


def load_gauge(case_dir: str, file_name: str) -> pd.DataFrame:
    df = read_csv(PROCESSED / case_dir / file_name, sep=";")
    if "zmax [m]" in df:
        df.loc[df["zmax [m]"] < -1e20, "zmax [m]"] = np.nan
    if {"velx [m/s]", "vely [m/s]", "velz [m/s]"}.issubset(df.columns):
        df["vel_mag"] = np.sqrt(df["velx [m/s]"] ** 2 + df["vely [m/s]"] ** 2 + df["velz [m/s]"] ** 2)
    return df


def load_frontier() -> pd.DataFrame:
    path = DATA / "master_convergence_frontier.csv"
    if path.exists():
        return read_csv(path)
    raise FileNotFoundError("No existe master_convergence_frontier.csv")


def load_productive() -> pd.DataFrame:
    frames = []
    pilot = DATA / "pilot_summary.csv"
    batch2 = DATA / "batch2_summary.csv"
    if pilot.exists():
        p = read_csv(pilot)
        p["lote"] = "piloto"
        frames.append(p)
    if batch2.exists():
        b = read_csv(batch2)
        b["lote"] = "batch2"
        frames.append(b)
    return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()


def cls_color(value: str) -> str:
    return RED if str(value).upper() == "FALLO" else GREEN


def label_class(value: str) -> str:
    return "F" if str(value).upper() == "FALLO" else "E"


def plot_00_method_flow() -> None:
    fig, ax = plt.subplots(figsize=(9.8, 2.4))
    ax.axis("off")
    boxes = [
        ("1", "Convergencia de\nvariables continuas", "desplazamiento, velocidad,\naltura de agua, rotación"),
        ("2", "Selección de\nresolución SPH", "balance entre similitud de\nrespuesta y costo"),
        ("3", "Aplicación posterior:\nestabilidad", "frontera estable/fallo\ncon dp adoptado"),
    ]
    xs = [0.16, 0.50, 0.84]
    for x, (num, title, body) in zip(xs, boxes):
        ax.text(
            x,
            0.62,
            f"{num}. {title}",
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=INK,
            bbox=dict(boxstyle="round,pad=0.55", fc="#ffffff", ec="#cfd8e3", lw=1.1),
        )
        ax.text(x, 0.23, body, ha="center", va="center", fontsize=8.5, color=GRAY)
    for x0, x1 in [(0.285, 0.375), (0.625, 0.715)]:
        ax.annotate("", xy=(x1, 0.62), xytext=(x0, 0.62), arrowprops=dict(arrowstyle="->", lw=1.2, color=BLUE))
    ax.set_title("Orden metodológico usado en la lectura final", fontsize=12, fontweight="bold", pad=8)
    save("00_orden_metodologico")


def plot_01_block_displacement_time() -> None:
    fig, ax = plt.subplots(figsize=(8.8, 4.5))
    for dp, case_dir in TEMPORAL_CASES.items():
        df = load_chrono(case_dir)
        ax.plot(df["t_rel"], df["disp_pct"], lw=1.5, label=f"dp={dp:.3f} m")
    ax.axhline(5, color=RED, ls="--", lw=1.1, label="umbral 5% d_eq")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Desplazamiento acumulado (% d_eq)")
    ax.set_title("Variable continua: desplazamiento del bloque en el tiempo")
    ax.legend(ncol=2, frameon=False)
    save("01_desplazamiento_tiempo_dp")


def plot_02_block_speed_rotation_time() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0), constrained_layout=True)
    for dp, case_dir in TEMPORAL_CASES.items():
        df = load_chrono(case_dir)
        axes[0].plot(df["t_rel"], df["block_speed"], lw=1.35, label=f"dp={dp:.3f}")
        axes[1].plot(df["t_rel"], df["rotation_deg"], lw=1.35, label=f"dp={dp:.3f}")
    axes[0].set_title("Velocidad del bloque")
    axes[0].set_xlabel("Tiempo (s)")
    axes[0].set_ylabel("Velocidad (m/s)")
    axes[1].set_title("Rotación acumulada observada")
    axes[1].set_xlabel("Tiempo (s)")
    axes[1].set_ylabel("Rotación (grados)")
    axes[0].legend(frameon=False, fontsize=7)
    fig.suptitle("Variables continuas del cuerpo rígido", fontsize=12, fontweight="bold")
    save("02_velocidad_rotacion_tiempo_dp")


def plot_03_hydraulic_gauges_time() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0), constrained_layout=True)
    for dp, case_dir in TEMPORAL_CASES.items():
        vel = load_gauge(case_dir, "GaugesVel_V05.csv")
        hmax = load_gauge(case_dir, "GaugesMaxZ_hmax03.csv")
        axes[0].plot(vel["time [s]"], vel["vel_mag"], lw=1.3, label=f"dp={dp:.3f}")
        axes[1].plot(hmax["time [s]"], hmax["zmax [m]"], lw=1.3, label=f"dp={dp:.3f}")
    axes[0].set_title("Velocidad del flujo en gauge V05")
    axes[0].set_xlabel("Tiempo (s)")
    axes[0].set_ylabel("|U| (m/s)")
    axes[1].set_title("Altura/cota máxima en gauge hmax03")
    axes[1].set_xlabel("Tiempo (s)")
    axes[1].set_ylabel("zmax (m)")
    axes[0].legend(frameon=False, fontsize=7)
    fig.suptitle("Variables hidráulicas usadas para revisar convergencia", fontsize=12, fontweight="bold")
    save("03_gauges_tiempo_dp")


def plot_04_classic_summary_vs_dp(summary: pd.DataFrame) -> None:
    df = summary.sort_values("dp")
    fig, axes = plt.subplots(2, 2, figsize=(9.8, 7.2), constrained_layout=True)
    specs = [
        ("max_displacement_m", "Desplazamiento máximo (m)"),
        ("max_velocity_ms", "Velocidad máx. bloque (m/s)"),
        ("max_flow_velocity_ms", "Velocidad máx. gauge (m/s)"),
        ("max_water_height_m", "Altura/cota máx. gauge (m)"),
    ]
    for ax, (col, title) in zip(axes.ravel(), specs):
        ax.plot(df["dp"], df[col], marker="o", color=BLUE, lw=1.5)
        ax.axvline(0.003, color=AMBER, ls=":", lw=1.2)
        ax.invert_xaxis()
        ax.set_xlabel("dp (m), menor hacia la derecha")
        ax.set_title(title)
    fig.suptitle("Resumen clásico: métricas continuas al refinar dp", fontsize=12, fontweight="bold")
    save("04_metricas_continuas_vs_dp")


def plot_05_cost_vs_dp(summary: pd.DataFrame) -> None:
    df = summary.sort_values("dp")
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.5), constrained_layout=True)
    specs = [
        ("n_particles", "Partículas"),
        ("mem_gpu_mb", "Memoria GPU (MB)"),
        ("tiempo_min", "Tiempo (min)"),
    ]
    for ax, (col, title) in zip(axes, specs):
        ax.plot(df["dp"], df[col], marker="o", color=AMBER, lw=1.5)
        ax.axvline(0.003, color=BLUE, ls=":", lw=1.2)
        ax.invert_xaxis()
        ax.set_xlabel("dp (m)")
        ax.set_title(title)
    fig.suptitle("Costo computacional del refinamiento", fontsize=12, fontweight="bold")
    save("05_costo_vs_dp")


def plot_06_frontier_after_resolution(frontier: pd.DataFrame) -> None:
    df = frontier[
        (frontier["dp"].round(3) == 0.003)
        & (frontier["mu"].between(0.674, 0.686))
        & (frontier["evidence_scope"].isin(["principal_frontier", "frontier_refinement", "repeatability_check"]))
    ].copy()
    df = df.sort_values("mu")
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    for _, row in df.iterrows():
        ax.scatter(row["mu"], row["disp_pct_deq"], s=58, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8, zorder=3)
        ax.text(row["mu"], row["disp_pct_deq"] + 0.24, label_class(row["criterion_class"]), ha="center", fontsize=8)
    ax.axhline(5, color=RED, linestyle="--", linewidth=1.1, label="umbral 5% d_eq")
    ax.axvspan(0.68050, 0.68075, color=AMBER, alpha=0.20, label="intervalo de transición")
    ax.annotate(
        "frontera práctica\nacotada",
        xy=(0.680625, 9.2),
        xytext=(0.6762, 8.4),
        arrowprops=dict(arrowstyle="->", lw=0.9, color=AMBER),
        fontsize=8,
        color="#74510f",
    )
    ax.set_xlabel("Coeficiente de fricción bloque-suelo, μ")
    ax.set_ylabel("Desplazamiento máximo (% d_eq)")
    ax.set_title("Uso posterior del dp adoptado: frontera de estabilidad")
    ax.set_xlim(0.674, 0.686)
    ax.set_ylim(0, 10.6)
    ax.legend(frameon=False, loc="lower right")
    save("06_frontera_posterior_dp003")


def plot_07_resolution_sensitivity(frontier: pd.DataFrame) -> None:
    df = frontier[
        (frontier["dp"].round(3).isin([0.002, 0.003]))
        & (frontier["mu"].between(0.674, 0.686))
        & (frontier["evidence_scope"].isin(["principal_frontier", "frontier_refinement", "repeatability_check"]))
    ].copy()
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.0), sharey=True, constrained_layout=True)
    for ax, dp in zip(axes, [0.003, 0.002]):
        part = df[df["dp"].round(3) == dp].sort_values("mu")
        for _, row in part.iterrows():
            ax.scatter(row["mu"], row["disp_pct_deq"], s=52, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8)
            ax.text(row["mu"], row["disp_pct_deq"] + 0.28, label_class(row["criterion_class"]), ha="center", fontsize=8)
        ax.axhline(5, color=RED, linestyle="--", linewidth=1.1)
        ax.set_title(f"dp={dp:.3f} m")
        ax.set_xlabel("μ")
        ax.set_xlim(0.674, 0.686)
        ax.set_ylim(0, 10.6)
    axes[0].set_ylabel("Desplazamiento máximo (% d_eq)")
    axes[0].axvspan(0.68050, 0.68075, color=AMBER, alpha=0.18)
    axes[1].text(0.6744, 8.6, "en dp=0.002 los casos\ncercanos quedan bajo 5%", fontsize=8, color=BLUE)
    fig.suptitle("Sensibilidad de la clasificación al cambiar resolución", fontsize=12, fontweight="bold")
    save("07_sensibilidad_frontera_dp")


def plot_08_productive(prod: pd.DataFrame) -> None:
    if prod.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0), constrained_layout=True)
    base = prod[(prod["dam_height"].round(3) == 0.2) & (prod["slope_inv"].round(0) == 20)].copy()
    for _, row in base.sort_values("friction_coefficient").iterrows():
        axes[0].scatter(row["friction_coefficient"], row["disp_pct_deq"], s=58, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8)
    axes[0].axhline(5, color=RED, linestyle="--", linewidth=1.1)
    axes[0].set_title("Condición base posterior")
    axes[0].set_xlabel("μ")
    axes[0].set_ylabel("Desplazamiento máximo (% d_eq)")
    hcases = prod[(prod["slope_inv"].round(0) == 20) & (prod["friction_coefficient"].between(0.67, 0.73))].copy()
    for _, row in hcases.sort_values("dam_height").iterrows():
        axes[1].scatter(row["dam_height"], row["disp_pct_deq"], s=58, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8)
        if row["disp_pct_deq"] > 10:
            axes[1].text(row["dam_height"], row["disp_pct_deq"] + 4, f"{row['disp_pct_deq']:.0f}%", ha="center", fontsize=8)
    axes[1].axhline(5, color=RED, linestyle="--", linewidth=1.1)
    axes[1].set_title("Variación hidráulica posterior")
    axes[1].set_xlabel("Altura inicial H (m)")
    axes[1].set_ylabel("Desplazamiento máximo (% d_eq)")
    fig.suptitle("Lotes posteriores con dp=0.003", fontsize=12, fontweight="bold")
    save("08_lotes_posteriores")


def productive_rows(prod: pd.DataFrame) -> str:
    if prod.empty:
        return ""
    rows = []
    for _, row in prod.sort_values(["lote", "dam_height", "friction_coefficient", "slope_inv"]).iterrows():
        cls = "fail" if str(row["criterion_class"]).upper() == "FALLO" else "stable"
        rows.append(
            f"<tr><td>{row['lote']}</td><td><code>{row['case_id']}</code></td>"
            f"<td>{row['dam_height']:.3f}</td><td>{row['friction_coefficient']:.4f}</td>"
            f"<td>1:{row['slope_inv']:.0f}</td><td><span class='pill {cls}'>{row['criterion_class']}</span></td>"
            f"<td>{row['disp_pct_deq']:.2f}%</td><td>{row['max_rotation_deg']:.2f}°</td></tr>"
        )
    return "\n".join(rows)


LIGHTBOX = """
<div id="lightbox" class="lightbox" aria-hidden="true">
  <button class="lightbox-close" type="button" aria-label="Cerrar">×</button>
  <img alt="">
  <p></p>
</div>
<script>
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = lightbox.querySelector('img');
  const lightboxCaption = lightbox.querySelector('p');
  const closeLightbox = () => {
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    lightboxImg.removeAttribute('src');
  };
  document.querySelectorAll('figure img').forEach((img) => {
    img.setAttribute('tabindex', '0');
    img.setAttribute('role', 'button');
    img.setAttribute('title', 'Clic para ampliar');
    const open = () => {
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt || '';
      const caption = img.closest('figure')?.querySelector('figcaption')?.textContent || '';
      lightboxCaption.textContent = caption;
      lightbox.classList.add('open');
      lightbox.setAttribute('aria-hidden', 'false');
    };
    img.addEventListener('click', open);
    img.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        open();
      }
    });
  });
  lightbox.addEventListener('click', (event) => {
    if (event.target === lightbox || event.target.classList.contains('lightbox-close')) closeLightbox();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeLightbox();
  });
</script>
"""


def write_page(prod: pd.DataFrame) -> None:
    html = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Convergencia de resolución SPH</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
<main class="page">
  <header class="top">
    <div>
      <p class="meta">Tesis UCN · modelo SPH-Chrono</p>
      <h1>Convergencia de resolución SPH y uso posterior en estabilidad</h1>
      <p>Esta página separa dos niveles de análisis: primero se revisa cómo cambian variables continuas al disminuir <code>dp</code>; después se usa la resolución adoptada para estudiar estabilidad del bloque.</p>
    </div>
    <aside class="summary">
      <dl>
        <div><dt>Resolución adoptada</dt><dd>dp = 0.003 m</dd></div>
        <div><dt>Convergencia</dt><dd>variables temporales y máximos</dd></div>
        <div><dt>Estabilidad</dt><dd>análisis posterior al dp elegido</dd></div>
        <div><dt>Criterio de movimiento</dt><dd>D_max &gt; 5% d_eq</dd></div>
      </dl>
    </aside>
  </header>

  <section>
    <h2>1. Enfoque del estudio</h2>
    <p>SPH no usa una malla fija; usa partículas. Por eso aquí <code>dp</code> significa <strong>espaciamiento inicial entre partículas</strong> y se interpreta como resolución espacial del modelo.</p>
    <p>El análisis se ordena así: primero se comparan variables continuas para distintos <code>dp</code>, como desplazamiento del bloque, velocidad del bloque, velocidad del flujo y altura de agua en gauges. Esa es la parte de convergencia o sensibilidad de resolución.</p>
    <p>Luego, con una resolución seleccionada por equilibrio entre respuesta y costo, se analiza si el bloque inicia movimiento bajo un criterio operacional. Esa segunda parte es el estudio de estabilidad, no el reemplazo del análisis de convergencia.</p>
    <figure>
      <img src="figures/00_orden_metodologico.png" alt="Orden metodológico del análisis">
      <figcaption>La lectura final separa convergencia de variables, selección de resolución y análisis posterior de estabilidad.</figcaption>
    </figure>
  </section>

  <section>
    <h2>2. Variables temporales comparadas al refinar dp</h2>
    <p>La primera revisión mira curvas en el tiempo. Esto responde directamente a la pregunta clásica de convergencia: si se disminuye <code>dp</code>, las variables relevantes deberían tender a una respuesta similar o al menos mostrar una sensibilidad interpretable.</p>
    <figure>
      <img src="figures/01_desplazamiento_tiempo_dp.png" alt="Desplazamiento temporal del bloque para varios dp">
      <figcaption>Desplazamiento acumulado del bloque para varias resoluciones. La línea de 5% se muestra como referencia del criterio de movimiento, pero la lectura principal aquí es la forma temporal de la variable.</figcaption>
    </figure>
    <div class="grid">
      <figure>
        <img src="figures/02_velocidad_rotacion_tiempo_dp.png" alt="Velocidad y rotación del bloque para varios dp">
        <figcaption>Velocidad del bloque y rotación acumulada observada. La rotación se reporta como variable física adicional, no como criterio único de movimiento.</figcaption>
      </figure>
      <figure>
        <img src="figures/03_gauges_tiempo_dp.png" alt="Variables hidráulicas de gauges para varios dp">
        <figcaption>Velocidad del flujo y altura/cota máxima en gauges cercanos. Estas variables ayudan a revisar si el forzante hidráulico cambia fuertemente con la resolución.</figcaption>
      </figure>
    </div>
  </section>

  <section>
    <h2>3. Resumen clásico por resolución</h2>
    <p>Además de las curvas temporales, se comparan máximos de variables continuas contra <code>dp</code>. Esta vista resume la sensibilidad de la respuesta al refinar la resolución.</p>
    <div class="grid">
      <figure>
        <img src="figures/04_metricas_continuas_vs_dp.png" alt="Métricas continuas contra dp">
        <figcaption>Máximos de desplazamiento, velocidad del bloque, velocidad del flujo y altura/cota de agua. No todas las variables evolucionan de forma perfectamente monótona.</figcaption>
      </figure>
      <figure>
        <img src="figures/05_costo_vs_dp.png" alt="Costo computacional contra dp">
        <figcaption>El refinamiento reduce <code>dp</code>, pero aumenta fuertemente partículas, memoria y tiempo. Esto pesa en la selección de resolución productiva.</figcaption>
      </figure>
    </div>
    <p class="note"><strong>Lectura:</strong> <code>dp=0.003 m</code> se adopta como resolución operativa porque permite ejecutar lotes productivos con costo manejable y mantiene una respuesta comparable con el refinamiento fino en varias variables, aunque no autoriza afirmar convergencia asintótica fuerte de toda la dinámica.</p>
  </section>

  <section>
    <h2>4. Uso posterior: estabilidad y frontera</h2>
    <p>Una vez fijado <code>dp=0.003 m</code>, se puede estudiar estabilidad. Aquí <strong>frontera</strong> significa el intervalo de fricción <code>μ</code> donde, bajo la misma geometría y forzante, el bloque cambia entre no superar y superar el umbral de movimiento.</p>
    <p>El umbral usado es <code>D_max &gt; 5% d_eq</code>, donde <code>D_max</code> es el desplazamiento máximo del bloque y <code>d_eq</code> su diámetro equivalente. La rotación se informa aparte como variable observada.</p>
    <div class="grid">
      <figure>
        <img src="figures/06_frontera_posterior_dp003.png" alt="Frontera posterior con dp 0.003">
        <figcaption>Con <code>dp=0.003 m</code>, la condición base queda acotada entre <code>μ=0.68050</code> y <code>μ=0.68075</code>.</figcaption>
      </figure>
      <figure>
        <img src="figures/07_sensibilidad_frontera_dp.png" alt="Sensibilidad de la frontera al cambiar dp">
        <figcaption>Al refinar a <code>dp=0.002 m</code>, los casos cercanos quedan bajo el umbral. Esto se reporta como sensibilidad de resolución de la frontera.</figcaption>
      </figure>
    </div>
  </section>

  <section>
    <h2>5. Qué se lanzó después</h2>
    <p>Después de adoptar <code>dp=0.003 m</code>, se ejecutaron lotes controlados. Su objetivo no fue seguir demostrando convergencia, sino verificar el flujo productivo y comenzar a leer tendencias de estabilidad bajo la resolución seleccionada.</p>
    <figure>
      <img src="figures/08_lotes_posteriores.png" alt="Resultados de lotes posteriores">
      <figcaption>El piloto y batch2 muestran casos estables y de falla bajo la resolución adoptada. Estos resultados pertenecen a la etapa de aplicación, no a la prueba de convergencia.</figcaption>
    </figure>
  </section>

  <section>
    <h2>6. Tabla resumida de lotes posteriores</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Lote</th><th>Caso</th><th>H (m)</th><th>μ</th><th>Pendiente</th><th>Clase</th><th>Despl.</th><th>Rot.</th></tr></thead>
        <tbody>{productive_rows(prod)}</tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>7. Términos usados</h2>
    <dl class="terms">
      <div><dt>dp</dt><dd>Espaciamiento inicial entre partículas SPH. Menor <code>dp</code> implica mayor resolución y mayor costo computacional.</dd></div>
      <div><dt>Resolución SPH</dt><dd>Nivel de detalle espacial dado por el tamaño/separación de partículas, no por una malla fija.</dd></div>
      <div><dt>μ</dt><dd>Coeficiente de fricción bloque-suelo usado para explorar el inicio de movimiento.</dd></div>
      <div><dt>d_eq</dt><dd>Diámetro equivalente del bloque, usado para normalizar desplazamientos.</dd></div>
      <div><dt>Umbral de movimiento</dt><dd>Condición operacional <code>D_max &gt; 5% d_eq</code>.</dd></div>
      <div><dt>Frontera</dt><dd>Intervalo de valores de <code>μ</code> donde cambia la respuesta estable/falla para una resolución y condición física dadas.</dd></div>
      <div><dt>Rotación observada</dt><dd>Variable física que se reporta para interpretar el comportamiento del bloque; no decide sola la clase de movimiento.</dd></div>
      <div><dt>Familias conv_*</dt><dd>Nombres de trazabilidad interna para corridas de exploración, refinamiento, repetición y prueba fina.</dd></div>
    </dl>
  </section>
</main>
{LIGHTBOX}
</body>
</html>
"""
    (OUT / "index.html").write_text(html, encoding="utf-8")


def write_css() -> None:
    css = """
:root {
  --ink: #17202a;
  --muted: #536171;
  --line: #d8dee8;
  --bg: #f4f6f9;
  --paper: #ffffff;
  --red: #b73b3b;
  --green: #2f7d4f;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  color: var(--ink);
  background: var(--bg);
  line-height: 1.5;
}
.page {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
  padding: 28px 0 56px;
}
.top {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(260px, .7fr);
  gap: 24px;
  align-items: start;
  border-bottom: 1px solid var(--line);
  padding-bottom: 22px;
  margin-bottom: 24px;
}
.meta {
  margin: 0 0 6px;
  color: var(--muted);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: .04em;
}
h1 {
  margin: 0 0 10px;
  font-size: clamp(28px, 4vw, 40px);
  line-height: 1.08;
}
h2 {
  font-size: 22px;
  margin: 0 0 12px;
}
p { margin: 0 0 12px; }
section {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 20px;
  margin: 18px 0;
}
.summary {
  background: #fbfcfe;
  border: 1px solid var(--line);
  padding: 14px 16px;
  border-radius: 4px;
}
.summary dl { margin: 0; }
.summary div {
  display: grid;
  gap: 2px;
  border-bottom: 1px solid var(--line);
  padding: 8px 0;
}
.summary div:last-child { border-bottom: 0; }
dt { font-weight: 700; color: var(--ink); }
dd { margin: 0; color: var(--muted); }
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
figure {
  margin: 16px 0 6px;
  border: 1px solid var(--line);
  background: white;
  padding: 10px;
  border-radius: 4px;
}
figure img {
  display: block;
  width: 100%;
  height: auto;
  cursor: zoom-in;
}
figcaption {
  color: var(--muted);
  font-size: 13px;
  margin-top: 8px;
}
.note {
  border-left: 4px solid #aab4c0;
  background: #f7f9fc;
  padding: 10px 12px;
  margin-top: 14px;
}
.table-wrap { overflow-x: auto; border: 1px solid var(--line); }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
th, td {
  border-bottom: 1px solid var(--line);
  padding: 8px 9px;
  text-align: left;
}
th { background: #eef2f6; }
.pill {
  display: inline-block;
  border-radius: 3px;
  padding: 2px 6px;
  font-weight: 700;
  font-size: 12px;
}
.pill.fail { color: #7c1f1f; background: #f8e6e6; }
.pill.stable { color: #1f5a39; background: #e5f2ea; }
.terms {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 22px;
  margin: 0;
}
.terms div {
  border-top: 1px solid var(--line);
  padding-top: 10px;
}
code {
  background: #eef2f6;
  padding: 1px 4px;
  border-radius: 3px;
}
.lightbox {
  position: fixed;
  inset: 0;
  display: none;
  align-items: center;
  justify-content: center;
  background: rgba(8, 12, 18, .88);
  z-index: 1000;
  padding: 24px;
}
.lightbox.open { display: flex; flex-direction: column; }
.lightbox img {
  max-width: min(96vw, 1500px);
  max-height: 86vh;
  background: white;
  border-radius: 4px;
  object-fit: contain;
}
.lightbox p {
  color: white;
  max-width: min(96vw, 1100px);
  margin: 12px 0 0;
  font-size: 14px;
}
.lightbox-close {
  position: fixed;
  top: 12px;
  right: 18px;
  width: 42px;
  height: 42px;
  border: 1px solid rgba(255,255,255,.45);
  background: rgba(255,255,255,.12);
  color: white;
  border-radius: 4px;
  font-size: 30px;
  line-height: 1;
  cursor: pointer;
}
@media (max-width: 860px) {
  .top, .grid, .terms { grid-template-columns: 1fr; }
  section { padding: 16px; }
}
"""
    (OUT / "styles.css").write_text(css, encoding="utf-8")


def write_data(summary: pd.DataFrame, frontier: pd.DataFrame, prod: pd.DataFrame) -> None:
    summary.to_csv(DATA / "continuous_convergence_summary.csv", index=False)
    frontier.to_csv(DATA / "master_convergence_frontier.csv", index=False)
    if not prod.empty:
        prod.to_csv(DATA / "productive_lots_combined.csv", index=False)


def main() -> None:
    init()
    summary = read_csv(RESULTS / "conv3_f05_full.csv", sep=";")
    frontier = load_frontier()
    prod = load_productive()
    plot_00_method_flow()
    plot_01_block_displacement_time()
    plot_02_block_speed_rotation_time()
    plot_03_hydraulic_gauges_time()
    plot_04_classic_summary_vs_dp(summary)
    plot_05_cost_vs_dp(summary)
    plot_06_frontier_after_resolution(frontier)
    plot_07_resolution_sensitivity(frontier)
    plot_08_productive(prod)
    write_data(summary, frontier, prod)
    write_css()
    write_page(prod)
    print(f"Web generated: {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
