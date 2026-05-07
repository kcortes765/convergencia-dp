from __future__ import annotations

import io
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "convergence_story_web"
FIG = OUT / "figures"
DATA = OUT / "data"
REMOTE_REF = "origin/master"


def git_text(path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{REMOTE_REF}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout


def read_csv(path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(io.StringIO(git_text(path)))
    except Exception:
        return pd.read_csv(ROOT / path)


def init() -> None:
    for path in [OUT, FIG, DATA]:
        path.mkdir(parents=True, exist_ok=True)
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


GREEN = "#2f7d4f"
RED = "#b73b3b"
BLUE = "#2b6f9f"
GRAY = "#7d8794"
AMBER = "#b98524"
INK = "#1d2733"


def save(name: str) -> None:
    for ext in ("png", "svg"):
        plt.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", facecolor="white")
    plt.close()


def cls_color(value: str) -> str:
    return RED if str(value).upper() == "FALLO" else GREEN


def label_class(value: str) -> str:
    return "F" if str(value).upper() == "FALLO" else "E"


def plot_01_convergence_decision(conv: pd.DataFrame) -> None:
    df = conv[
        (conv["dp"].round(3).isin([0.002, 0.003]))
        & (conv["mu"].between(0.674, 0.686))
        & (conv["evidence_scope"].isin(["principal_frontier", "frontier_refinement", "repeatability_check"]))
    ].copy()
    df = df.sort_values(["dp", "mu"])

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8), sharey=True)
    for ax, dp in zip(axes, [0.003, 0.002]):
        part = df[df["dp"].round(3) == dp].copy()
        for _, row in part.iterrows():
            ax.scatter(
                row["mu"],
                row["disp_pct_deq"],
                s=52,
                color=cls_color(row["criterion_class"]),
                edgecolor="white",
                linewidth=0.8,
                zorder=3,
            )
            ax.text(row["mu"], row["disp_pct_deq"] + 0.28, label_class(row["criterion_class"]), ha="center", fontsize=8, color=INK)
        ax.axhline(5, color=RED, linestyle="--", linewidth=1.1)
        ax.set_title(f"dp = {dp:.3f} m")
        ax.set_xlabel("μ")
        ax.set_xlim(0.674, 0.686)
        ax.set_ylim(0, 10.6)
    axes[0].set_ylabel("Desplazamiento máx. (% d_eq)")
    axes[0].axvspan(0.68050, 0.68075, color=AMBER, alpha=0.18)
    axes[0].annotate("frontera acotada\n0.68050-0.68075", xy=(0.680625, 9.15), xytext=(0.6762, 8.5),
                     arrowprops=dict(arrowstyle="->", lw=0.8, color=AMBER), fontsize=8, color="#74510f")
    axes[1].text(0.6744, 8.7, "en la malla fina\nlos casos quedan bajo 5%", fontsize=8, color=BLUE)
    fig.suptitle("Comparación de la frontera entre dp=0.003 y dp=0.002", fontsize=12, fontweight="bold")
    save("01_convergencia_decision")


def plot_00_process_overview(conv: pd.DataFrame) -> None:
    counts = (
        conv.groupby(["family", "evidence_scope"])
        .size()
        .reset_index(name="n")
        .sort_values("family")
    )
    labels = {
        "conv_edge": "1. Exploración\nprincipal",
        "conv_reassure": "2. Refinamiento\ncerca del umbral",
        "conv_repeat": "3. Repetición\n/ robustez",
        "conv_probe": "4. Probe fino\ncomplementario",
    }
    notes = {
        "conv_edge": "barre μ y dp",
        "conv_reassure": "0.68050-0.68075",
        "conv_repeat": "repite marginales",
        "conv_probe": "dp=0.002, μ=0.6625",
    }
    colors = {
        "conv_edge": BLUE,
        "conv_reassure": AMBER,
        "conv_repeat": GRAY,
        "conv_probe": GREEN,
    }
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    families = ["conv_edge", "conv_reassure", "conv_repeat", "conv_probe"]
    y = np.arange(len(families))
    nvals = [int(counts.loc[counts["family"] == f, "n"].sum()) for f in families]
    ax.barh(y, nvals, color=[colors[f] for f in families], height=0.55)
    ax.set_yticks(y)
    ax.set_yticklabels([labels[f] for f in families])
    ax.invert_yaxis()
    ax.set_xlabel("número de casos en tabla consolidada")
    ax.set_title("Estructura del estudio de convergencia")
    for yi, f, n in zip(y, families, nvals):
        ax.text(n + 0.25, yi, f"{n} casos · {notes[f]}", va="center", fontsize=8, color=INK)
    ax.set_xlim(0, max(nvals) + 5)
    save("00_proceso_convergencia")


def plot_02_dp003_frontier(conv: pd.DataFrame) -> None:
    df = conv[
        (conv["dp"].round(3) == 0.003)
        & (conv["mu"].between(0.6798, 0.6814))
        & (conv["evidence_scope"].isin(["frontier_refinement", "repeatability_check", "principal_frontier"]))
    ].copy().sort_values("mu")
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    for _, row in df.iterrows():
        ax.scatter(row["mu"], row["disp_pct_deq"], s=58, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8, zorder=3)
        ax.text(row["mu"], row["disp_pct_deq"] + 0.22, label_class(row["criterion_class"]), ha="center", fontsize=8)
    ax.axhline(5, color=RED, linestyle="--", linewidth=1.1)
    ax.axvspan(0.68050, 0.68075, color=AMBER, alpha=0.22)
    ax.set_title("Frontera práctica en dp=0.003 m")
    ax.set_xlabel("μ")
    ax.set_ylabel("Desplazamiento máx. (% d_eq)")
    ax.set_xlim(0.6798, 0.6814)
    ax.set_ylim(3.0, 10.3)
    ax.text(0.68052, 9.45, "FALLO en 0.68050", color=RED, fontsize=8)
    ax.text(0.68078, 3.45, "ESTABLE en 0.68075", color=GREEN, fontsize=8)
    save("02_frontera_dp003")


def plot_03_resolution_cost(conv: pd.DataFrame) -> None:
    cost = conv.groupby("dp", as_index=False).agg(
        tiempo_min=("tiempo_min", "median"),
        n_particles=("n_particles", "median"),
        mem_gpu_mb=("mem_gpu_mb", "median"),
    ).sort_values("dp")
    fig, axes = plt.subplots(1, 3, figsize=(9.4, 3.2))
    items = [
        ("tiempo_min", "tiempo mediano\n(min)", BLUE),
        ("n_particles", "partículas\n(millones)", GREEN),
        ("mem_gpu_mb", "memoria GPU\n(GB)", AMBER),
    ]
    for ax, (col, title, color) in zip(axes, items):
        y = cost[col].copy()
        if col == "n_particles":
            y = y / 1e6
        if col == "mem_gpu_mb":
            y = y / 1024
        ax.plot(cost["dp"], y, marker="o", color=color, linewidth=1.8)
        ax.invert_xaxis()
        ax.set_title(title)
        ax.set_xlabel("dp (m)")
        for xval, yval in zip(cost["dp"], y):
            ax.text(xval, yval, f"{yval:.1f}" if yval < 100 else f"{yval:.0f}", ha="center", va="bottom", fontsize=7)
    fig.suptitle("Costo computacional del refinamiento", fontsize=12, fontweight="bold")
    save("03_costo_refinamiento")


def plot_07_classic_convergence_metrics(conv: pd.DataFrame) -> None:
    # Casos comparables de la familia principal. Se muestran como sensibilidad, no como prueba fuerte.
    df = conv[(conv["family"] == "conv_edge") & (conv["mu"].isin([0.675, 0.68, 0.681, 0.685]))].copy()
    metrics = [
        ("disp_pct_deq", "Desplazamiento (% d_eq)"),
        ("max_rotation_deg", "Rotación máx. (°)"),
        ("max_velocity_ms", "Velocidad máx. (m/s)"),
        ("max_sph_force_N", "Fuerza SPH máx. (N)"),
    ]
    colors = {0.675: "#2b6f9f", 0.68: "#b98524", 0.681: "#2f7d4f", 0.685: "#7d8794"}
    fig, axes = plt.subplots(2, 2, figsize=(9.6, 7.0), constrained_layout=True)
    for ax, (col, title) in zip(axes.flat, metrics):
        for mu, part in df.groupby("mu"):
            part = part.sort_values("dp")
            ax.plot(part["dp"], part[col], marker="o", linewidth=1.5, color=colors.get(float(mu), GRAY), label=f"μ={mu:g}")
        ax.invert_xaxis()
        ax.set_title(title)
        ax.set_xlabel("dp (m)")
        ax.axvline(0.003, color="#111", linestyle=":", linewidth=1.0)
        if col == "disp_pct_deq":
            ax.axhline(5, color=RED, linestyle="--", linewidth=1.0)
            ax.set_ylabel("valor")
        else:
            ax.set_ylabel("valor")
    axes[0, 0].legend(frameon=False, ncol=2)
    fig.suptitle("Gráficos clásicos: métrica continua vs resolución", fontsize=12, fontweight="bold")
    save("07_metricas_clasicas_vs_dp")


def plot_08_relative_changes(conv: pd.DataFrame) -> None:
    df = conv[(conv["family"] == "conv_edge") & (conv["mu"].isin([0.675, 0.68, 0.681, 0.685]))].copy()
    metric_map = {
        "disp_pct_deq": "desplazamiento",
        "max_rotation_deg": "rotación",
        "max_velocity_ms": "velocidad",
        "max_sph_force_N": "fuerza SPH",
    }
    rows = []
    for mu, part in df.groupby("mu"):
        part = part.sort_values("dp", ascending=False)
        for col, label in metric_map.items():
            vals = part[["dp", col]].dropna().sort_values("dp", ascending=False).reset_index(drop=True)
            for i in range(len(vals) - 1):
                coarse = vals.iloc[i]
                fine = vals.iloc[i + 1]
                if coarse[col] == 0:
                    continue
                rows.append(
                    {
                        "mu": mu,
                        "metric": label,
                        "step": f"{coarse['dp']:.3f}→{fine['dp']:.3f}",
                        "rel_change_pct": 100 * (fine[col] - coarse[col]) / abs(coarse[col]),
                    }
                )
    rel = pd.DataFrame(rows)
    rel.to_csv(DATA / "relative_changes_convergence.csv", index=False)
    focus = rel[rel["step"].isin(["0.004→0.003", "0.003→0.002"])].copy()
    fig, ax = plt.subplots(figsize=(9.0, 4.3))
    order = ["desplazamiento", "rotación", "velocidad", "fuerza SPH"]
    x = np.arange(len(order))
    width = 0.36
    for j, step in enumerate(["0.004→0.003", "0.003→0.002"]):
        vals = []
        for metric in order:
            sub = focus[(focus["step"] == step) & (focus["metric"] == metric)]
            vals.append(sub["rel_change_pct"].median() if not sub.empty else np.nan)
        ax.bar(x + (j - 0.5) * width, vals, width=width, label=step, color=BLUE if j == 0 else AMBER)
    ax.axhline(0, color="#111", linewidth=0.8)
    ax.axhspan(-5, 5, color=GREEN, alpha=0.08, label="±5% referencia visual")
    ax.set_xticks(x)
    ax.set_xticklabels(order)
    ax.set_ylabel("Cambio relativo mediano (%)")
    ax.set_title("Cambios relativos al refinar la malla")
    ax.legend(frameon=False, ncol=3)
    save("08_cambios_relativos_refinamiento")


def plot_09_displacement_by_mu_classic(conv: pd.DataFrame) -> None:
    df = conv[(conv["family"] == "conv_edge") & (conv["mu"].isin([0.675, 0.68, 0.681, 0.685]))].copy()
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    for mu, part in df.groupby("mu"):
        part = part.sort_values("dp", ascending=False)
        ax.plot(part["dp"], part["disp_pct_deq"], marker="o", linewidth=1.5, label=f"μ={mu:g}")
    ax.invert_xaxis()
    ax.axhline(5, color=RED, linestyle="--", linewidth=1.1, label="umbral 5%")
    ax.axvline(0.003, color="#111", linestyle=":", linewidth=1.0, label="malla adoptada")
    ax.set_xlabel("dp (m)")
    ax.set_ylabel("Desplazamiento máx. (% d_eq)")
    ax.set_title("Lectura clásica esperable: desplazamiento vs dp")
    ax.legend(frameon=False, ncol=3)
    save("09_desplazamiento_vs_dp_clasico")


def combine_productive(pilot: pd.DataFrame, batch2: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "case_id", "status", "dp", "dam_height", "boulder_mass", "boulder_rot_z",
        "friction_coefficient", "slope_inv", "classification_mode", "reference_time_s",
        "criterion_class", "moved", "rotated", "max_displacement_m", "disp_pct_deq",
        "max_rotation_deg", "max_velocity_ms", "max_sph_force_N", "max_contact_force_N",
        "max_flow_velocity_ms", "max_water_height_m", "tiempo_min", "n_particles", "mem_gpu_mb",
        "quality_flags",
    ]
    for frame in [pilot, batch2]:
        for col in cols:
            if col not in frame.columns:
                frame[col] = np.nan
    p = pilot[cols].copy()
    p["lote"] = "piloto"
    b = batch2[cols].copy()
    b["lote"] = "batch2"
    return pd.concat([p, b], ignore_index=True)


def plot_04_productive_base(prod: pd.DataFrame) -> None:
    df = prod[(prod["dam_height"].round(3) == 0.2) & (prod["slope_inv"].round(0) == 20)].copy()
    df = df.sort_values("friction_coefficient")
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    for _, row in df.iterrows():
        ax.scatter(row["friction_coefficient"], row["disp_pct_deq"], s=58, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8)
        if row["disp_pct_deq"] > 12 or 4.5 <= row["disp_pct_deq"] <= 6.5:
            ax.text(row["friction_coefficient"], row["disp_pct_deq"] + 0.7, f"{row['disp_pct_deq']:.1f}%", ha="center", fontsize=8)
    ax.axhline(5, color=RED, linestyle="--", linewidth=1.1)
    ax.axvspan(0.675, 0.685, color=AMBER, alpha=0.14)
    ax.set_title("Producción: condición base H=0.20 m, pendiente 1:20")
    ax.set_xlabel("μ")
    ax.set_ylabel("Desplazamiento máx. (% d_eq)")
    ax.set_ylim(0, 45)
    ax.text(0.686, 37, "batch2 refuerza:\n0.675 falla\n0.685 estable", fontsize=8, color=INK)
    save("04_produccion_base")


def plot_05_hydraulic_and_slope(prod: pd.DataFrame) -> None:
    hydro = prod[(prod["slope_inv"].round(0) == 20) & (prod["friction_coefficient"].between(0.679, 0.681))].copy()
    slope = prod[prod["slope_inv"].round(0) == 10].copy()
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.7))

    ax = axes[0]
    for _, row in hydro.sort_values("dam_height").iterrows():
        ax.scatter(row["dam_height"], row["disp_pct_deq"], s=58, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8)
        ax.text(row["dam_height"], row["disp_pct_deq"] + 3, f"{row['disp_pct_deq']:.1f}%", ha="center", fontsize=8)
    ax.axhline(5, color=RED, linestyle="--", linewidth=1.1)
    ax.set_title("Efecto de H con μ≈0.68")
    ax.set_xlabel("H (m)")
    ax.set_ylabel("Desplazamiento máx. (% d_eq)")
    ax.set_ylim(0, 122)

    ax = axes[1]
    for _, row in slope.sort_values("friction_coefficient").iterrows():
        ax.scatter(row["friction_coefficient"], row["disp_pct_deq"], s=58, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8)
        ax.text(row["friction_coefficient"], row["disp_pct_deq"] + 0.35, f"rot {row['max_rotation_deg']:.1f}°", ha="center", fontsize=8, color=GRAY)
    ax.axhline(5, color=RED, linestyle="--", linewidth=1.1)
    ax.set_title("Pendiente 1:10: estable por desplazamiento")
    ax.set_xlabel("μ")
    ax.set_ylabel("Desplazamiento máx. (% d_eq)")
    ax.set_ylim(0, 10)
    fig.suptitle("Lecturas físicas del batch2", fontsize=12, fontweight="bold")
    save("05_hidraulica_pendiente")


def plot_06_rotation(prod: pd.DataFrame) -> None:
    df = prod.copy()
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    for _, row in df.iterrows():
        x = min(row["disp_pct_deq"], 140)
        ax.scatter(x, row["max_rotation_deg"], s=54, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8)
    ax.axvline(5, color=RED, linestyle="--", linewidth=1.1, label="umbral desplazamiento")
    ax.axhline(5, color=AMBER, linestyle=":", linewidth=1.4, label="5° rotación")
    ax.set_title("Rotación: variable diagnóstica")
    ax.set_xlabel("Desplazamiento máx. (% d_eq), recortado en 140%")
    ax.set_ylabel("Rotación máxima (°)")
    ax.legend(frameon=False, loc="upper left")
    ax.text(35, 2.2, "La clase se define por desplazamiento,\nno por rotación.", fontsize=8, color=INK)
    save("06_rotacion_diagnostica")


def productive_rows(prod: pd.DataFrame) -> str:
    rows = []
    table = prod.copy().sort_values(["lote", "dam_height", "slope_inv", "friction_coefficient"])
    for _, row in table.iterrows():
        cls = "fail" if row["criterion_class"] == "FALLO" else "stable"
        rows.append(
            f"<tr><td>{row['lote']}</td><td><code>{row['case_id']}</code></td>"
            f"<td>{row['dam_height']:.3f}</td><td>{row['friction_coefficient']:.4f}</td>"
            f"<td>1:{row['slope_inv']:.0f}</td><td><span class='pill {cls}'>{row['criterion_class']}</span></td>"
            f"<td>{row['disp_pct_deq']:.2f}%</td><td>{row['max_rotation_deg']:.2f}°</td></tr>"
        )
    return "\n".join(rows)


def write_page(prod: pd.DataFrame) -> None:
    total = len(prod)
    html_process = """
    <ol class="process">
      <li><strong>Se corrigió y congeló la geometría.</strong> El bloque quedó alineado con la pendiente, apoyado sobre la playa y tratado como cuerpo rígido acoplado con Chrono.</li>
      <li><strong>Se definió el criterio de clase.</strong> La falla se mide por desplazamiento máximo mayor a 5% de <code>d_eq</code>. La rotación se conserva solo como diagnóstico.</li>
      <li><strong>Se exploró la frontera con <code>conv_edge</code>.</strong> Para varios valores de <code>μ</code> y <code>dp</code>, se observó dónde el bloque pasa de estable a falla.</li>
      <li><strong>Se refinó la zona crítica con <code>conv_reassure</code>.</strong> Se agregaron puntos cerca de <code>μ≈0.6805-0.68075</code> para acotar mejor la transición en <code>dp=0.003</code>.</li>
      <li><strong>Se hicieron repeticiones con <code>conv_repeat</code>.</strong> Sirven para comprobar que los casos marginales no fueran un accidente operacional.</li>
      <li><strong>Se agregó un caso fino <code>conv_probe</code>.</strong> En <code>dp=0.002</code> y <code>μ=0.6625</code>, el bloque siguió estable por desplazamiento. Eso muestra sensibilidad de resolución.</li>
      <li><strong>Se tomó una decisión productiva.</strong> Usar <code>dp=0.003 m</code> como malla de trabajo y reportar la frontera como práctica, no como valor universal.</li>
    </ol>
    """
    html = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Informe de convergencia y lotes productivos</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
<main class="page">
  <header class="top">
    <div>
      <p class="meta">Tesis UCN · modelo SPH–Chrono</p>
      <h1>Estudio de convergencia y decisión de malla</h1>
      <p>Documento técnico para explicar cómo se planteó el estudio de resolución: qué se mantuvo fijo, qué se varió, cómo se ubicó la frontera de estabilidad y por qué se adoptó <code>dp=0.003 m</code> para las simulaciones productivas.</p>
    </div>
    <aside class="summary">
      <dl>
        <div><dt>Malla productiva</dt><dd>dp = 0.003 m</dd></div>
        <div><dt>Criterio principal</dt><dd>desplazamiento &gt; 5% d_eq</dd></div>
        <div><dt>Rotación</dt><dd>diagnóstico</dd></div>
        <div><dt>Lotes posteriores</dt><dd>5/5 OK + 8/8 OK</dd></div>
      </dl>
    </aside>
  </header>

  <section>
    <h2>1. Cómo se planteó el estudio</h2>
    <p>La pregunta práctica no fue “cuál es el valor exacto final de una variable al refinar indefinidamente la malla”. La pregunta fue: <strong>qué resolución SPH permite estudiar de forma trazable el movimiento incipiente del bloque</strong>, sin convertir la tesis en una campaña de refinamiento interminable.</p>
    <p>Por eso el análisis se planteó como un estudio de <strong>decisión de malla y sensibilidad de frontera</strong>. El fenómeno combina superficie libre, contacto bloque-suelo, fricción y un criterio de umbral. Cerca del límite, cambios pequeños en resolución pueden cambiar la clase ESTABLE/FALLO, aunque las magnitudes continuas sigan siendo físicamente interpretables.</p>
    <p>La estrategia fue congelar el problema físico base y variar solo lo necesario para responder esa pregunta:</p>
    <ul class="compact">
      <li><code>dp</code>: controla la resolución SPH y el costo computacional.</li>
      <li><code>μ</code>: se usa como variable de barrido para ubicar la frontera entre estabilidad y falla.</li>
      <li><code>D_max/d_eq</code>: desplazamiento máximo normalizado, usado como respuesta principal.</li>
      <li><code>5% d_eq</code>: umbral operativo para clasificar el caso como ESTABLE o FALLO.</li>
    </ul>
    <p>En términos simples: no se buscó demostrar una convergencia asintótica fuerte de toda la dinámica, sino decidir una malla operativa y dejar explícito cuánto se mueve la frontera al cambiar la resolución.</p>
  </section>

  <section>
    <h2>2. Secuencia usada</h2>
    <p>El estudio se organizó en familias de corridas. Los nombres internos se mantienen solo para trazabilidad; abajo se indica qué significa cada una.</p>
    {html_process}
    <figure>
      <img src="figures/00_proceso_convergencia.png" alt="Estructura del estudio de convergencia">
      <figcaption>La tabla consolidada reúne 27 casos comparables de convergencia/frontera. No todos tienen el mismo rol metodológico.</figcaption>
    </figure>
  </section>

  <section>
    <h2>3. Resultado de la comparación de mallas</h2>
    <p>En <code>dp=0.003 m</code>, los casos alrededor de <code>μ≈0.68</code> cruzan el umbral de desplazamiento. En <code>dp=0.002 m</code>, los casos equivalentes quedan bajo el umbral. Por eso el resultado se interpreta como sensibilidad de resolución.</p>
    <figure>
      <img src="figures/01_convergencia_decision.png" alt="Convergencia tratada como sensibilidad de frontera">
      <figcaption>E = estable, F = falla. En <code>dp=0.003</code> aparece una frontera práctica clara. En <code>dp=0.002</code>, los casos cercanos quedan bajo el umbral.</figcaption>
    </figure>
  </section>

  <section>
    <h2>4. Decisión de malla</h2>
    <p>En <code>dp=0.003 m</code>, la transición de la condición base queda acotada entre <code>μ=0.68050</code> y <code>μ=0.68075</code>. Por eso se adopta <code>dp=0.003 m</code> como malla operativa para producción.</p>
    <div class="grid">
      <figure>
        <img src="figures/02_frontera_dp003.png" alt="Frontera práctica en dp 0.003">
        <figcaption>La frontera práctica se reporta como intervalo, no como valor universal exacto.</figcaption>
      </figure>
      <figure>
        <img src="figures/03_costo_refinamiento.png" alt="Costo computacional del refinamiento">
        <figcaption>El refinamiento a <code>dp=0.002</code> aumenta fuertemente partículas, memoria y tiempo.</figcaption>
      </figure>
    </div>
    <p class="note"><strong>Interpretación:</strong> no se afirma convergencia asintótica fuerte. Se reporta una frontera práctica condicionada a la malla <code>dp=0.003 m</code>, porque el problema es de umbral y muestra sensibilidad de resolución. La malla fina <code>dp=0.002 m</code> se usa como evidencia de sensibilidad, no como nueva malla productiva.</p>
  </section>

  <section>
    <h2>5. Gráficos clásicos de convergencia</h2>
    <p>Además de la lectura por frontera, se pueden mostrar los gráficos típicos de convergencia: una métrica continua contra <code>dp</code>. Estos gráficos son útiles para responder a la expectativa metodológica clásica, pero deben leerse como <strong>sensibilidad de resolución</strong>.</p>
    <p>La razón es que el caso está cerca de un umbral de movimiento: el desplazamiento puede cruzar o no el 5% de <code>d_eq</code> con cambios pequeños de resolución. Por eso no se espera necesariamente una curva monótona limpia.</p>
    <figure>
      <img src="figures/09_desplazamiento_vs_dp_clasico.png" alt="Desplazamiento máximo versus dp">
      <figcaption>Este es el gráfico más parecido al esperado en una revisión clásica: desplazamiento máximo contra resolución. La línea vertical marca la malla adoptada.</figcaption>
    </figure>
    <div class="grid">
      <figure>
        <img src="figures/07_metricas_clasicas_vs_dp.png" alt="Métricas continuas versus dp">
        <figcaption>Desplazamiento, rotación, velocidad y fuerza SPH como funciones de <code>dp</code>. No todas evolucionan de forma monótona.</figcaption>
      </figure>
      <figure>
        <img src="figures/08_cambios_relativos_refinamiento.png" alt="Cambios relativos al refinar malla">
        <figcaption>Los cambios relativos ayudan a cuantificar sensibilidad, pero no se usan como prueba automática de convergencia fuerte.</figcaption>
      </figure>
    </div>
  </section>

  <section>
    <h2>6. Qué se hizo después</h2>
    <p>Después de cerrar la convergencia no se siguió refinando <code>dp</code>. Se pasó a producción controlada con <code>dp=0.003 m</code>. Primero se ejecutó un piloto productivo de 5 casos y luego un segundo lote dirigido de 8 casos. Ambos terminaron sin fallos numéricos.</p>
    <p>Estos lotes no son todavía una campaña paramétrica completa. Su función fue verificar que el flujo productivo funciona y empezar a leer tendencias físicas bajo la malla ya fijada.</p>
    <figure>
      <img src="figures/04_produccion_base.png" alt="Producción en condición base">
      <figcaption>La condición base posterior refuerza la zona de transición: <code>μ=0.675</code> falla, mientras <code>μ=0.685</code> y <code>μ=0.700</code> son estables.</figcaption>
    </figure>
    <div class="grid">
      <figure>
        <img src="figures/05_hidraulica_pendiente.png" alt="Efecto hidráulico y pendiente">
        <figcaption>Con mayor altura hidráulica, la falla aparece con fricciones mayores. Los casos de pendiente 1:10 se mantienen estables por desplazamiento, aunque rotan.</figcaption>
      </figure>
      <figure>
        <img src="figures/06_rotacion_diagnostica.png" alt="Rotación diagnóstica">
        <figcaption>La rotación se conserva como salida diagnóstica; no cambia la clase bajo el criterio <code>displacement_only</code>.</figcaption>
      </figure>
    </div>
  </section>

  <section>
    <h2>7. Tabla resumida de lotes productivos</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Lote</th><th>Caso</th><th>H (m)</th><th>μ</th><th>Pendiente</th><th>Clase</th><th>Despl.</th><th>Rot.</th></tr></thead>
        <tbody>{productive_rows(prod)}</tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>8. Términos usados</h2>
    <dl class="terms">
      <div><dt>dp</dt><dd>Espaciamiento inicial de partículas SPH. Menor <code>dp</code> implica más resolución y más costo.</dd></div>
      <div><dt>μ</dt><dd>Coeficiente de fricción bloque-suelo.</dd></div>
      <div><dt>d_eq</dt><dd>Diámetro equivalente del bloque, usado para normalizar desplazamientos.</dd></div>
      <div><dt>displacement_only</dt><dd>Modo de clasificación donde solo el desplazamiento decide ESTABLE/FALLO.</dd></div>
      <div><dt>Frontera práctica</dt><dd>Intervalo de transición observado para una configuración y resolución específicas.</dd></div>
      <div><dt><code>conv_edge</code></dt><dd>Familia principal de corridas para ubicar la frontera en distintas mallas y fricciones.</dd></div>
      <div><dt><code>conv_reassure</code></dt><dd>Corridas adicionales cerca del umbral para reforzar el acotamiento fino.</dd></div>
      <div><dt><code>conv_repeat</code></dt><dd>Repeticiones de casos marginales para revisar consistencia operacional.</dd></div>
      <div><dt><code>conv_probe</code></dt><dd>Caso fino suplementario usado para diagnosticar sensibilidad en <code>dp=0.002</code>.</dd></div>
    </dl>
  </section>
</main>
<div id="lightbox" class="lightbox" aria-hidden="true">
  <button class="lightbox-close" type="button" aria-label="Cerrar">×</button>
  <img alt="">
  <p></p>
</div>
<script>
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = lightbox.querySelector('img');
  const lightboxCaption = lightbox.querySelector('p');
  const closeLightbox = () => {{
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    lightboxImg.removeAttribute('src');
  }};
  document.querySelectorAll('figure img').forEach((img) => {{
    img.setAttribute('tabindex', '0');
    img.setAttribute('role', 'button');
    img.setAttribute('title', 'Clic para ampliar');
    const open = () => {{
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt || '';
      const caption = img.closest('figure')?.querySelector('figcaption')?.textContent || '';
      lightboxCaption.textContent = caption;
      lightbox.classList.add('open');
      lightbox.setAttribute('aria-hidden', 'false');
    }};
    img.addEventListener('click', open);
    img.addEventListener('keydown', (event) => {{
      if (event.key === 'Enter' || event.key === ' ') {{
        event.preventDefault();
        open();
      }}
    }});
  }});
  lightbox.addEventListener('click', (event) => {{
    if (event.target === lightbox || event.target.classList.contains('lightbox-close')) closeLightbox();
  }});
  document.addEventListener('keydown', (event) => {{
    if (event.key === 'Escape') closeLightbox();
  }});
</script>
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
  font-size: clamp(28px, 4vw, 42px);
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
  grid-template-columns: 1fr;
  gap: 2px;
  border-bottom: 1px solid var(--line);
  padding: 8px 0;
}
.summary div:last-child { border-bottom: 0; }
dt {
  font-weight: 700;
  color: var(--ink);
}
dd {
  margin: 0;
  color: var(--muted);
}
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
.compact {
  margin: 8px 0 14px 18px;
  padding: 0;
}
.compact li {
  margin: 5px 0;
}
.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--line);
}
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
th {
  background: #eef2f6;
}
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
.lightbox.open {
  display: flex;
  flex-direction: column;
}
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
.process {
  margin: 12px 0 16px;
  padding-left: 22px;
}
.process li {
  margin: 8px 0;
}
code {
  background: #eef2f6;
  padding: 1px 4px;
  border-radius: 3px;
}
@media (max-width: 860px) {
  .top, .grid, .terms { grid-template-columns: 1fr; }
  section { padding: 16px; }
}
"""
    (OUT / "styles.css").write_text(css.strip() + "\n", encoding="utf-8")


def main() -> None:
    init()
    conv = read_csv("data/figures/derived_convergence_graphics/master_convergence_frontier.csv")
    pilot = read_csv("exports/pilot_productivo_20260501/pilot_summary.csv")
    batch2 = read_csv("exports/batch2_productivo_20260505/batch2_summary.csv")
    prod = combine_productive(pilot, batch2)

    conv.to_csv(DATA / "master_convergence_frontier.csv", index=False)
    pilot.to_csv(DATA / "pilot_summary.csv", index=False)
    batch2.to_csv(DATA / "batch2_summary.csv", index=False)
    prod.to_csv(DATA / "productive_lots_combined.csv", index=False)

    plot_00_process_overview(conv)
    plot_01_convergence_decision(conv)
    plot_02_dp003_frontier(conv)
    plot_03_resolution_cost(conv)
    plot_04_productive_base(prod)
    plot_05_hydraulic_and_slope(prod)
    plot_06_rotation(prod)
    plot_07_classic_convergence_metrics(conv)
    plot_08_relative_changes(conv)
    plot_09_displacement_by_mu_classic(conv)
    write_css()
    write_page(prod)
    print(f"Web generated: {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
