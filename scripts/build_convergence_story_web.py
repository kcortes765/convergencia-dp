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


def interp_valid(t: np.ndarray, y: np.ndarray, common_t: np.ndarray) -> np.ndarray:
    mask = np.isfinite(t) & np.isfinite(y)
    t = t[mask]
    y = y[mask]
    if len(t) < 2:
        return np.full_like(common_t, np.nan, dtype=float)
    order = np.argsort(t)
    t = t[order]
    y = y[order]
    inside = (common_t >= t.min()) & (common_t <= t.max())
    out = np.full_like(common_t, np.nan, dtype=float)
    out[inside] = np.interp(common_t[inside], t, y)
    return out


def temporal_variable(case_dir: str, variable: str) -> tuple[np.ndarray, np.ndarray]:
    if variable in {"disp_pct", "block_speed", "rotation_deg"}:
        df = load_chrono(case_dir)
        return df["t_rel"].to_numpy(float), df[variable].to_numpy(float)
    if variable == "flow_speed":
        df = load_gauge(case_dir, "GaugesVel_V05.csv")
        return df["time [s]"].to_numpy(float), df["vel_mag"].to_numpy(float)
    if variable == "water_height":
        df = load_gauge(case_dir, "GaugesMaxZ_hmax03.csv")
        return df["time [s]"].to_numpy(float), df["zmax [m]"].to_numpy(float)
    raise ValueError(variable)


def temporal_error_table() -> pd.DataFrame:
    variables = {
        "disp_pct": "Desplazamiento",
        "block_speed": "Velocidad bloque",
        "flow_speed": "Velocidad flujo",
        "water_height": "Altura/cota agua",
        "rotation_deg": "Rotación",
    }
    fine_case = TEMPORAL_CASES[0.002]
    rows = []
    for var, label in variables.items():
        tf, yf = temporal_variable(fine_case, var)
        for dp, case_dir in TEMPORAL_CASES.items():
            t, y = temporal_variable(case_dir, var)
            t_min = max(np.nanmin(tf), np.nanmin(t))
            t_max = min(np.nanmax(tf), np.nanmax(t))
            common_t = np.linspace(t_min, t_max, 1500)
            yf_i = interp_valid(tf, yf, common_t)
            y_i = interp_valid(t, y, common_t)
            mask = np.isfinite(yf_i) & np.isfinite(y_i)
            if mask.sum() < 10:
                rmse_pct = np.nan
            else:
                scale = np.nanmax(yf_i[mask]) - np.nanmin(yf_i[mask])
                if scale <= 1e-12:
                    scale = max(np.nanmax(np.abs(yf_i[mask])), 1.0)
                rmse_pct = np.sqrt(np.nanmean((y_i[mask] - yf_i[mask]) ** 2)) / scale * 100
            rows.append({"dp": dp, "variable": var, "label": label, "temporal_rmse_pct": rmse_pct})
    return pd.DataFrame(rows)


def max_difference_table(summary: pd.DataFrame) -> pd.DataFrame:
    specs = {
        "max_displacement_m": "Desplazamiento máximo",
        "max_velocity_ms": "Velocidad bloque máx.",
        "max_flow_velocity_ms": "Velocidad flujo máx.",
        "max_water_height_m": "Altura/cota agua máx.",
        "max_rotation_deg": "Rotación máxima",
    }
    fine = summary.loc[np.isclose(summary["dp"], 0.002)].iloc[0]
    rows = []
    for col, label in specs.items():
        ref = float(fine[col])
        for _, row in summary.iterrows():
            value = float(row[col])
            rows.append(
                {
                    "dp": float(row["dp"]),
                    "variable": col,
                    "label": label,
                    "value": value,
                    "reference_dp": 0.002,
                    "reference_value": ref,
                    "delta_vs_fine_pct": (value - ref) / ref * 100 if ref else np.nan,
                }
            )
    return pd.DataFrame(rows)


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


def plot_01_defensible_variables(diff: pd.DataFrame, errors: pd.DataFrame) -> None:
    labels = ["Altura/cota agua máx.", "Velocidad bloque máx.", "Desplazamiento máximo"]
    y = np.arange(len(labels))
    max_vals = [
        float(diff[(diff["label"] == label) & np.isclose(diff["dp"], 0.003)]["delta_vs_fine_pct"].iloc[0])
        for label in labels
    ]
    err_label_map = {
        "Altura/cota agua máx.": "Altura/cota agua",
        "Velocidad bloque máx.": "Velocidad bloque",
        "Desplazamiento máximo": "Desplazamiento",
    }
    err_vals = [
        float(errors[(errors["label"] == err_label_map[label]) & np.isclose(errors["dp"], 0.003)]["temporal_rmse_pct"].iloc[0])
        for label in labels
    ]

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.0))
    axes[0].axvspan(-5, 5, color=GREEN, alpha=0.12, label="±5%")
    axes[0].axvspan(-7, 7, color=AMBER, alpha=0.10, label="zona cercana ±7%")
    axes[0].axvline(0, color=INK, lw=0.8)
    axes[0].barh(y, max_vals, color=[GREEN, GREEN, AMBER], alpha=0.9)
    for yi, val in zip(y, max_vals):
        axes[0].text(val + (0.35 if val >= 0 else -0.35), yi, f"{val:+.1f}%", va="center", ha="left" if val >= 0 else "right", fontsize=9)
    axes[0].set_yticks(y, labels)
    axes[0].set_xlabel("Diferencia del valor máximo respecto a dp=0.002 (%)\n0% = igual al caso fino; negativo = menor que el caso fino")
    axes[0].set_title("A. Máximos: cuánto cambia cada variable")
    axes[0].text(
        0.02,
        0.98,
        "Verde: dentro de ±5%\nAmarillo: cercano (±5 a ±7%)",
        transform=axes[0].transAxes,
        va="top",
        fontsize=8,
        color=GRAY,
        bbox=dict(fc="white", ec="#d8dee8", alpha=0.86, pad=4),
    )

    axes[1].axvspan(0, 5, color=GREEN, alpha=0.12, label="≤5%")
    axes[1].axvspan(5, 7, color=AMBER, alpha=0.10, label="cercano")
    axes[1].barh(y, err_vals, color=[GREEN, AMBER, AMBER], alpha=0.9)
    for yi, val in zip(y, err_vals):
        axes[1].text(val + 0.18, yi, f"{val:.1f}%", va="center", fontsize=9)
    axes[1].set_yticks(y, [""] * len(labels))
    axes[1].set_xlabel("Error relativo de la curva completa (RMSE, %)\nmenor = curva temporal más parecida a dp=0.002")
    axes[1].set_title("B. Forma temporal: cuánto se parece la curva")
    axes[1].text(
        0.02,
        0.98,
        "Verde: error ≤5%\nAmarillo: cercano (5 a 7%)",
        transform=axes[1].transAxes,
        va="top",
        fontsize=8,
        color=GRAY,
        bbox=dict(fc="white", ec="#d8dee8", alpha=0.86, pad=4),
    )
    fig.suptitle("Comparación de dp=0.003 contra la referencia fina dp=0.002", fontsize=13, fontweight="bold")
    fig.subplots_adjust(left=0.18, right=0.98, top=0.80, bottom=0.17, wspace=0.30)
    save("01_variables_defendibles_dp003")


def plot_02_principal_trends(diff: pd.DataFrame) -> None:
    labels = ["Desplazamiento máximo", "Velocidad bloque máx.", "Altura/cota agua máx."]
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    for label in labels:
        part = diff[(diff["label"] == label) & (diff["dp"] <= 0.006)].sort_values("dp")
        ax.plot(part["dp"], 100 + part["delta_vs_fine_pct"], marker="o", lw=1.6, label=label)
    ax.axhspan(95, 105, color=GREEN, alpha=0.12, label="±5% del caso fino")
    ax.axhspan(93, 107, color=AMBER, alpha=0.08, label="zona cercana")
    ax.axhline(100, color=INK, lw=0.8)
    ax.axvline(0.003, color=BLUE, ls=":", lw=1.2)
    ax.invert_xaxis()
    ax.set_xlabel("dp (m), menor hacia la derecha")
    ax.set_ylabel("Valor relativo a dp=0.002 (%)")
    ax.set_ylim(84, 146)
    ax.set_title("Tendencia de variables principales en el rango fino")
    ax.legend(frameon=False, ncol=2)
    save("02_tendencia_variables_principales")


def plot_03_temporal_curves_fine_set() -> None:
    dps = [0.004, 0.003, 0.002]
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.0), constrained_layout=True)
    for dp in dps:
        case_dir = TEMPORAL_CASES[dp]
        chrono = load_chrono(case_dir)
        hmax = load_gauge(case_dir, "GaugesMaxZ_hmax03.csv")
        label = f"dp={dp:.3f}"
        axes[0].plot(chrono["t_rel"], chrono["disp_pct"], lw=1.35, label=label)
        axes[1].plot(chrono["t_rel"], chrono["block_speed"], lw=1.25, label=label)
        axes[2].plot(hmax["time [s]"], hmax["zmax [m]"], lw=1.25, label=label)
    axes[0].axhline(5, color=RED, ls="--", lw=1.0)
    axes[0].set_title("Desplazamiento")
    axes[0].set_ylabel("% d_eq")
    axes[1].set_title("Velocidad del bloque")
    axes[1].set_ylabel("m/s")
    axes[2].set_title("Altura/cota de agua")
    axes[2].set_ylabel("m")
    for ax in axes:
        ax.set_xlabel("Tiempo (s)")
    axes[1].legend(frameon=False, fontsize=7)
    fig.suptitle("Curvas temporales del rango fino usadas para defender la resolución operativa", fontsize=12, fontweight="bold")
    save("03_curvas_temporales_finas")


def plot_04_sensitive_outputs(diff: pd.DataFrame, errors: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.0), constrained_layout=True)
    for ax, label, color in [
        (axes[0], "Velocidad flujo máx.", BLUE),
        (axes[1], "Rotación máxima", AMBER),
    ]:
        part = diff[diff["label"] == label].sort_values("dp")
        ax.axhspan(-5, 5, color=GREEN, alpha=0.10)
        ax.axhline(0, color=INK, lw=0.8)
        ax.plot(part["dp"], part["delta_vs_fine_pct"], marker="o", color=color, lw=1.6)
        ax.scatter([0.003], part.loc[np.isclose(part["dp"], 0.003), "delta_vs_fine_pct"], color=RED, zorder=4)
        ax.invert_xaxis()
        ax.set_xlabel("dp (m)")
        ax.set_ylabel("Cambio vs dp=0.002 (%)")
        ax.set_title(label)
    fig.suptitle("Salidas sensibles: se reportan, pero no sostienen solas la decisión", fontsize=12, fontweight="bold")
    save("04_salidas_sensibles")


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
        <div><dt>Uso posterior</dt><dd>movimiento si D_max &gt; 5% d_eq</dd></div>
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
    <h2>2. Variables que sostienen la resolución adoptada</h2>
    <p>La lectura de convergencia se concentró en variables continuas, antes de clasificar estabilidad. Para defender <code>dp=0.003 m</code> no se usan todas las salidas con el mismo peso: se priorizan las que describen el movimiento principal del bloque y el forzante hidráulico.</p>
    <p>El caso <code>dp=0.002 m</code> se usa como referencia fina. En <code>dp=0.003 m</code>, la altura/cota de agua y la velocidad máxima del bloque quedan dentro o muy cerca de una banda de 5%; el desplazamiento máximo queda levemente fuera, pero cercano. Esa lectura permite defender una resolución operativa, no una convergencia perfecta de todo el sistema.</p>
    <figure>
      <img src="figures/01_variables_defendibles_dp003.png" alt="Variables principales que sostienen dp 0.003">
      <figcaption>Variables principales en <code>dp=0.003 m</code> comparadas con <code>dp=0.002 m</code>. La evidencia más fuerte está en altura/cota de agua y velocidad del bloque; el desplazamiento queda cercano, aunque no exactamente dentro de ±5%.</figcaption>
      <div class="read-guide">
        <strong>Cómo leer esta figura:</strong>
        <ul>
          <li><strong>Panel A:</strong> compara solo el valor máximo. Cero significa igual al caso fino <code>dp=0.002 m</code>.</li>
          <li><strong>Panel B:</strong> compara la forma completa de la curva temporal. Menor porcentaje significa curva más parecida al caso fino.</li>
          <li><strong>Conclusión:</strong> el agua y la velocidad del bloque son las evidencias más limpias; el desplazamiento queda cercano y se acepta con cautela.</li>
        </ul>
      </div>
    </figure>
    <div class="grid">
      <figure>
        <img src="figures/02_tendencia_variables_principales.png" alt="Tendencia de variables principales hacia el caso fino">
        <figcaption>En el rango fino, las variables principales se acercan al caso <code>dp=0.002 m</code>. El punto <code>dp=0.003 m</code> queda suficientemente cerca para una resolución productiva defendible.</figcaption>
      </figure>
      <figure>
        <img src="figures/03_curvas_temporales_finas.png" alt="Curvas temporales de desplazamiento, velocidad del bloque y altura de agua">
        <figcaption>Curvas temporales del rango fino. La comparación revisa la forma de la respuesta, no solo el máximo, y se centra en desplazamiento, velocidad del bloque y altura/cota de agua.</figcaption>
      </figure>
    </div>
  </section>

  <section>
    <h2>3. Salidas sensibles y límite de la conclusión</h2>
    <p>No todas las salidas tienen el mismo nivel de cierre. La velocidad de flujo puntual en un gauge y la rotación acumulada del bloque son más sensibles al refinamiento. Por eso se muestran como límite del análisis, pero no se usan como base principal para fijar <code>dp</code> ni para clasificar el movimiento.</p>
    <div class="grid">
      <figure>
        <img src="figures/04_salidas_sensibles.png" alt="Salidas sensibles al refinamiento de dp">
        <figcaption>La velocidad de flujo puntual y la rotación muestran mayor sensibilidad. Esto se declara explícitamente para no presentar una convergencia más fuerte que la observada.</figcaption>
      </figure>
      <figure>
        <img src="figures/05_costo_vs_dp.png" alt="Costo computacional contra dp">
        <figcaption>El refinamiento reduce <code>dp</code>, pero aumenta fuertemente partículas, memoria y tiempo. El caso <code>dp=0.002 m</code> es útil como referencia fina, pero costoso como resolución productiva.</figcaption>
      </figure>
    </div>
    <p class="note"><strong>Lectura defendible:</strong> <code>dp=0.003 m</code> se adopta porque las variables principales quedan cerca del caso fino y el costo de <code>dp=0.002 m</code> crece mucho. La conclusión no es “todo converge perfectamente”, sino “la resolución es suficiente para continuar con un análisis productivo conservador”.</p>
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
.read-guide {
  margin-top: 10px;
  border-top: 1px solid var(--line);
  padding-top: 10px;
  font-size: 13px;
  color: var(--muted);
}
.read-guide ul {
  margin: 6px 0 0 18px;
  padding: 0;
}
.read-guide li { margin: 4px 0; }
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


def write_data(
    summary: pd.DataFrame,
    frontier: pd.DataFrame,
    prod: pd.DataFrame,
    max_diff: pd.DataFrame,
    temporal_errors: pd.DataFrame,
) -> None:
    summary.to_csv(DATA / "continuous_convergence_summary.csv", index=False)
    max_diff.to_csv(DATA / "convergence_max_differences_vs_dp0002.csv", index=False)
    temporal_errors.to_csv(DATA / "convergence_temporal_errors_vs_dp0002.csv", index=False)
    frontier.to_csv(DATA / "master_convergence_frontier.csv", index=False)
    if not prod.empty:
        prod.to_csv(DATA / "productive_lots_combined.csv", index=False)


def main() -> None:
    init()
    summary = read_csv(RESULTS / "conv3_f05_full.csv", sep=";")
    frontier = load_frontier()
    prod = load_productive()
    max_diff = max_difference_table(summary)
    temporal_errors = temporal_error_table()
    plot_00_method_flow()
    plot_01_defensible_variables(max_diff, temporal_errors)
    plot_02_principal_trends(max_diff)
    plot_03_temporal_curves_fine_set()
    plot_04_sensitive_outputs(max_diff, temporal_errors)
    plot_05_cost_vs_dp(summary)
    plot_06_frontier_after_resolution(frontier)
    plot_07_resolution_sensitivity(frontier)
    plot_08_productive(prod)
    write_data(summary, frontier, prod, max_diff, temporal_errors)
    write_css()
    write_page(prod)
    print(f"Web generated: {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
