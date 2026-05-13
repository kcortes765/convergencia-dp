from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
D_EQ = 0.100421


def save(fig: plt.Figure, name: str) -> None:
    FIG.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", facecolor="white", dpi=220)
    plt.close(fig)


def build_scenario() -> None:
    fig, ax = plt.subplots(figsize=(10.6, 4.0))
    ax.set_xlim(0, 30)
    ax.set_ylim(-0.30, 1.08)
    ax.axis("off")

    bottom_x = [0, 9, 30]
    bottom_y = [0, 0, 1.05]
    ax.plot(bottom_x, bottom_y, color="#3e4854", lw=2.2)

    water = Polygon(
        [(0, 0), (0, 0.62), (7.8, 0.62), (9, 0), (0, 0)],
        closed=True,
        facecolor="#9ecae1",
        edgecolor="#2b6f9f",
        alpha=0.55,
        lw=1.5,
    )
    ax.add_patch(water)
    ax.text(0.45, 0.66, "columna inicial\nde agua H=0,20 m", color="#214f75", fontsize=10, va="bottom")

    ax.add_patch(Rectangle((7.8, 0.0), 0.25, 0.62, facecolor="#5f6c7b", edgecolor="none", alpha=0.9))
    ax.text(7.35, 0.08, "compuerta\nidealizada", fontsize=8, ha="center", va="bottom", color="#536171")

    arrow = FancyArrowPatch((8.7, 0.42), (14.0, 0.42), arrowstyle="->", mutation_scale=20, lw=2, color="#2b6f9f")
    ax.add_patch(arrow)
    ax.text(10.0, 0.49, "flujo transitorio tipo dam-break", color="#2b6f9f", fontsize=10)

    boulder = Polygon(
        [(18.9, 0.56), (19.35, 0.72), (20.05, 0.69), (20.42, 0.51), (20.28, 0.31), (19.55, 0.28), (18.95, 0.39)],
        closed=True,
        facecolor="#8d6e52",
        edgecolor="#4c3a2a",
        lw=1.4,
    )
    ax.add_patch(boulder)
    ax.text(19.7, 0.78, "bloque BLIR3\nm=1,0 kg", fontsize=9, ha="center", color="#4c3a2a")

    ax.plot([18.0, 18.0], [0.45, 0.78], color="#b98524", lw=1.1, linestyle="--")
    ax.plot([21.0, 21.0], [0.58, 0.91], color="#b98524", lw=1.1, linestyle="--")
    ax.text(17.55, 0.88, "gauge\naguas arriba", fontsize=8, ha="center", color="#7a5915")
    ax.text(21.65, 1.00, "gauge\nbloque/salida", fontsize=8, ha="center", color="#7a5915")

    ax.text(14.2, 0.1, "playa/canal con pendiente 1:20", fontsize=10, color="#3e4854", rotation=2.5)
    ax.text(23.1, 0.84, "dp variable:\n0,010 a 0,002 m", fontsize=10, color="#17202a")
    ax.text(
        23.1,
        0.52,
        "se mantiene fijo:\nH=0,20 m, m=1,0 kg,\nμ=0,50, rot_z=0°,\nforma y pendiente",
        fontsize=9,
        color="#536171",
    )

    box = Rectangle((0.0, -0.26), 30.0, 0.12, facecolor="#f4f6f9", edgecolor="#d8dee8", lw=1)
    ax.add_patch(box)
    ax.text(
        0.4,
        -0.20,
        "Esquema sin escala: la convergencia compara la respuesta del mismo problema físico al cambiar solo la resolución SPH.",
        fontsize=9,
        color="#536171",
        va="center",
    )

    fig.suptitle("Escenario base usado para el análisis de resolución", fontsize=14, fontweight="bold", y=0.98)
    save(fig, "00b_escenario_convergencia")


def fmt_value(value: float, unit: str) -> str:
    if unit == "m":
        return f"{value:.5f} m"
    if unit == "m/s":
        return f"{value:.4f} m/s"
    if unit == "deg":
        return f"{value:.2f}°"
    return f"{value:.4f}"


def fmt_delta(delta: float, unit: str, variable: str) -> str:
    sign = "+" if delta >= 0 else "-"
    value = abs(delta)
    if variable == "max_displacement_m":
        return f"{sign}{value * 1000:.2f} mm"
    if unit == "m":
        return f"{sign}{value * 1000:.2f} mm"
    if unit == "m/s":
        return f"{sign}{value:.4f} m/s"
    if unit == "deg":
        return f"{sign}{value:.2f}°"
    return f"{delta:.4f}"


def build_absolute_difference_table() -> None:
    summary = pd.read_csv(DATA / "continuous_convergence_summary.csv")
    row_003 = summary.loc[summary["dp"].round(3) == 0.003].iloc[0]
    row_002 = summary.loc[summary["dp"].round(3) == 0.002].iloc[0]

    specs = [
        ("max_water_height_m", "Altura/cota agua máx.", "m", "principal"),
        ("max_velocity_ms", "Velocidad bloque máx.", "m/s", "principal"),
        ("max_displacement_m", "Desplazamiento máx.", "m", "principal"),
        ("max_flow_velocity_ms", "Velocidad flujo puntual", "m/s", "sensible"),
        ("max_rotation_deg", "Rotación acumulada", "deg", "sensible"),
    ]

    rows = []
    colors = []
    for col, label, unit, group in specs:
        v003 = float(row_003[col])
        v002 = float(row_002[col])
        delta = v003 - v002
        pct = delta / v002 * 100
        extra = ""
        if col == "max_displacement_m":
            extra = f" ({delta / D_EQ * 100:+.2f}% d_eq)"
        rows.append(
            [
                label,
                fmt_value(v003, unit),
                fmt_value(v002, unit),
                f"{fmt_delta(delta, unit, col)}{extra}",
                f"{pct:+.1f}%",
            ]
        )
        colors.append("#eaf3ed" if group == "principal" else "#f8f1e4")

    fig, ax = plt.subplots(figsize=(11.0, 3.8))
    ax.axis("off")
    table = ax.table(
        cellText=rows,
        colLabels=["Variable", "dp=0,003", "dp=0,002", "Δ absoluto", "Δ relativo"],
        cellLoc="left",
        colLoc="left",
        loc="center",
        colWidths=[0.29, 0.16, 0.16, 0.24, 0.15],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.55)

    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#d8dee8")
        if r == 0:
            cell.set_facecolor("#eef2f6")
            cell.set_text_props(weight="bold", color="#17202a")
        else:
            cell.set_facecolor(colors[r - 1])
            if c == 0 and r <= 3:
                cell.set_text_props(weight="bold")

    ax.text(
        0,
        0.96,
        "Diferencias entre dp=0,003 m y el caso fino dp=0,002 m",
        fontsize=14,
        fontweight="bold",
        color="#17202a",
        transform=ax.transAxes,
    )
    ax.text(
        0,
        0.04,
        "Δ = valor(dp=0,003) - valor(dp=0,002). Verde: variables principales; amarillo: salidas sensibles.",
        fontsize=9,
        color="#536171",
        transform=ax.transAxes,
    )
    save(fig, "01b_diferencias_absolutas_dp003")


def main() -> None:
    build_scenario()
    build_absolute_difference_table()


if __name__ == "__main__":
    main()
