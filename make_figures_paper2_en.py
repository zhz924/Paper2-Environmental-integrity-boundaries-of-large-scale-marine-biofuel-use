# -*- coding: utf-8 -*-
"""
make_figures_paper2_en.py — Paper 2 (environmental eligibility) English figure script.

Generates 5 publication figures at 500 dpi:

    Fig. 1  Gap-driven biofuel deficit-demand pathway (Table 2)
    Fig. 2  Food-security shock: U vs F regime comparison (2050)
    Fig. 3  Three-level funnel of environmentally compliant supply, 2030 (Table 11)
    Fig. 4  Three-level funnel of environmentally compliant supply, 2040 (Table 11)
    Fig. 5  Three-level funnel of environmentally compliant supply, 2050 (Table 11)

Output: PNG files written to ./figures_en next to this script.

All data are identical to the final-draft values (Table 2 and Table 11);
see verify_data() which asserts the key numbers before plotting.
"""

import sys
import traceback
from pathlib import Path

import matplotlib

# Headless backend; must be set before importing pyplot.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Polygon

# ----------------------------------------------------------------------
# Global settings
# ----------------------------------------------------------------------
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

SCRIPT_DIR = Path(__file__).resolve().parent
OUT = SCRIPT_DIR / "figures_en"
OUT.mkdir(parents=True, exist_ok=True)

DPI = 500

# Colors: B1 blue / B2 green / B3 orange / B4 red; U red / F green.
C_B = ["#1565C0", "#2E7D32", "#E65100", "#C62828"]
C_U, C_F = "#C62828", "#2E7D32"

# Funnel palette (identical to the Chinese source script).
COLORS = {
    "nominal": "#7C878D",   # nominal demand: grey
    "climate": "#39728A",   # climate-compliant: blue
    "u_double": "#B45F52",  # U double-compliant: red
    "f_double": "#4E8A72",  # F double-compliant: green
    "text": "#263238",
    "muted": "#65727A",
    "line": "#D7DEE1",
    "white": "#FFFFFF",
}

# ----------------------------------------------------------------------
# Data (do NOT change these numbers — they match the final draft)
# ----------------------------------------------------------------------

# Table 2 — biofuel deficit-demand (EJ/yr), used in Fig. 1.
TABLE2 = {
    "B1": [0.09, 0.73, 1.71],
    "B2": [0.24, 1.95, 4.56],
    "B3": [0.38, 3.17, 7.40],
    "B4": [0.44, 3.66, 8.54],
}

# Fig. 2 — food-security shock in 2050 (U vs F regime comparison).
PRICE_U, PRICE_F = [23, 61, 99, 115], [9, 25, 41, 47]
POU_U, POU_F = [55, 134, 201, 225], [24, 60, 94, 106]

# Table 11 — three-level funnel data.
# Row order: (nominal, U climate-compliant, U double-compliant,
#             F climate-compliant, F double-compliant); unit EJ.
# Interval values use (lower, upper).
DATA = {
    2030: {
        "B1": (0.09, 0.03, 0.03, 0.06, 0.06),
        "B2": (0.24, 0.09, 0.09, 0.17, 0.17),
        "B3": (0.38, 0.14, 0.14, 0.27, 0.27),
        "B4": (0.44, 0.17, 0.17, 0.31, 0.31),
    },
    2040: {
        "B1": (0.73, 0.28, 0.28, 0.51, 0.51),
        "B2": (1.95, 0.74, (0.50, 0.74), 1.37, 1.37),
        "B3": (3.17, 1.20, (0.50, 0.80), 2.22, (1.30, 2.19)),
        "B4": (3.66, 1.39, (0.50, 0.80), 2.56, (1.30, 2.19)),
    },
    2050: {
        "B1": (1.71, 0.65, (0.50, 0.65), 1.20, 1.20),
        "B2": (4.56, 1.73, (0.50, 0.80), 3.19, (2.00, 2.19)),
        "B3": (7.40, 2.81, (0.50, 0.80), 5.18, (2.00, 2.19)),
        "B4": (8.54, 3.25, (0.50, 0.80), 5.98, (2.00, 2.19)),
    },
}

SCENARIOS = ["B1", "B2", "B3", "B4"]
YEARS = [2030, 2040, 2050]


def verify_data():
    """Assert that the numbers match the final-draft values."""
    expected_t2 = {
        "B1": [0.09, 0.73, 1.71],
        "B2": [0.24, 1.95, 4.56],
        "B3": [0.38, 3.17, 7.40],
        "B4": [0.44, 3.66, 8.54],
    }
    assert TABLE2 == expected_t2, "Table 2 mismatch"

    assert PRICE_U == [23, 61, 99, 115] and PRICE_F == [9, 25, 41, 47], \
        "Fig. 2 price-shock data mismatch"
    assert POU_U == [55, 134, 201, 225] and POU_F == [24, 60, 94, 106], \
        "Fig. 2 undernourished-population data mismatch"

    for year in YEARS:
        for sc in SCENARIOS:
            nominal, u_c, u_d, f_c, f_d = DATA[year][sc]
            # Climate-compliant pass rates: U = 38%, F = 70% of nominal demand.
            assert abs(u_c - 0.38 * nominal) < 0.007, (year, sc, "U climate")
            assert abs(f_c - 0.70 * nominal) < 0.007, (year, sc, "F climate")
            # Double-compliant intervals (where intervals are used).
            if isinstance(u_d, (tuple, list)):
                lo, hi = float(u_d[0]), float(u_d[1])
                assert lo >= 0.50 - 1e-9 and hi <= 0.80 + 1e-9, \
                    (year, sc, "U double-compliant range")
            if isinstance(f_d, (tuple, list)):
                lo, hi = float(f_d[0]), float(f_d[1])
                assert lo >= 1.30 - 1e-9 and hi <= 2.19 + 1e-9, \
                    (year, sc, "F double-compliant range")

    print("Data verification passed: Table 2, Fig. 2, and Table 11 "
          "(U climate = 38%, F climate = 70%).")


# ----------------------------------------------------------------------
# Fig. 1 — gap-driven deficit-demand pathway (grouped bars: year x scenario)
# ----------------------------------------------------------------------
def make_fig1():
    years = [
        "2030\n(Gap 14.14 Mtoe)",
        "2040\n(Gap 116.6 Mtoe)",
        "2050\n(Nominal upper bound,\nstress test)",
    ]
    scen = [
        "B1 Conservative baseline (15%)",
        "B2 Neutral (40%)",
        "B3 High dependency (65%)",
        "B4 Extreme stress (75%)",
    ]

    fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=DPI)
    x, w = np.arange(3), 0.19

    for k, (b, col) in enumerate(zip(["B1", "B2", "B3", "B4"], C_B)):
        bars = ax.bar(
            x + (k - 1.5) * w, TABLE2[b], w,
            label=scen[k], color=col, edgecolor="white", lw=0.5,
        )
        for xi, v in zip(x + (k - 1.5) * w, TABLE2[b]):
            ax.text(xi, v + 0.09, f"{v:.2f}", ha="center", fontsize=8)

    ax.axhline(4.5, ls="--", lw=1, color="#555555")
    ax.text(
        0.02, 4.58,
        "2023 global road-transport biofuel total \u2248 4.5 EJ",
        fontsize=8, color="#444444", ha="left", va="bottom",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=8.5)
    ax.set_ylabel("Marine biofuel demand (EJ/yr)", fontsize=10)
    ax.set_ylim(0, 9.2)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(
        "Fig. 1  Gap-driven biofuel deficit-demand pathway (model estimate)",
        fontsize=11,
    )

    fig.tight_layout()
    path = OUT / "Fig1_gap_driven_biofuel_deficit_demand.png"
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return path


# ----------------------------------------------------------------------
# Fig. 2 — food-security shock: U vs F (2050, two panels)
# ----------------------------------------------------------------------
def make_fig2():
    bs = ["B1", "B2", "B3", "B4"]

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.0), dpi=DPI)
    x, w = np.arange(4), 0.36

    panels = [
        (axes[0], PRICE_U, PRICE_F,
         "Vegetable-oil price shock (%)", "(a) Vegetable-oil price shock"),
        (axes[1], POU_U, POU_F,
         "Additional undernourished people (million)",
         "(b) Additional undernourished people"),
    ]

    for ax, du, df, ylab, ttl in panels:
        ax.bar(x - w / 2, du, w, label="U Unconstrained",
               color=C_U, edgecolor="white", lw=0.5)
        ax.bar(x + w / 2, df, w, label="F Firewall",
               color=C_F, edgecolor="white", lw=0.5)

        for xi, v in zip(x - w / 2, du):
            ax.text(xi, v + max(du) * 0.015, str(v), ha="center", fontsize=8.5)
        for xi, v in zip(x + w / 2, df):
            ax.text(xi, v + max(du) * 0.015, str(v), ha="center", fontsize=8.5)

        ax.set_xticks(x)
        ax.set_xticklabels(bs, fontsize=10)
        ax.set_ylabel(ylab, fontsize=10)
        ax.set_title(ttl, fontsize=10)
        ax.legend(fontsize=8.5, frameon=False, loc="upper left")
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylim(0, max(du) * 1.18)

    fig.suptitle(
        "Fig. 2  Food-security shock: U vs F regime comparison "
        "(2050, model estimate)",
        fontsize=11,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])

    path = OUT / "Fig2_food_security_shock_U_vs_F_2050.png"
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return path


# ----------------------------------------------------------------------
# Figs. 3-5 — three-level funnel (Table 11)
# ----------------------------------------------------------------------
def value_range(value):
    """Return (lower, upper) floats for a scalar or interval value."""
    if isinstance(value, (tuple, list)):
        if len(value) != 2:
            raise ValueError(f"Interval must have two values: {value}")
        low = float(value[0])
        high = float(value[1])
    else:
        low = float(value)
        high = float(value)

    if low < 0 or high < 0:
        raise ValueError(f"Values must be non-negative: {value}")
    if low > high:
        raise ValueError(f"Lower bound must not exceed upper bound: {value}")

    return low, high


def value_text(value):
    """Format the value label shown in the funnel."""
    low, high = value_range(value)
    if abs(low - high) < 1e-12:
        return f"{low:.2f} EJ"
    return f"{low:.2f}\u2013{high:.2f} EJ"


def validate_data():
    """Check the funnel data structure before plotting."""
    for year in YEARS:
        if year not in DATA:
            raise KeyError(f"Missing data for {year}")
        for scenario in SCENARIOS:
            if scenario not in DATA[year]:
                raise KeyError(f"Missing {year} {scenario} data")
            row = DATA[year][scenario]
            if len(row) != 5:
                raise ValueError(
                    f"{year} {scenario} must have 5 items, got {len(row)}"
                )
            for value in row:
                value_range(value)


def draw_funnel(ax, x, y_levels, nominal, climate, double_value,
                regime, label_side):
    """Draw a single three-level funnel.

    label_side:
        "left"  — narrow-bar labels go to the left of the funnel (U regime);
        "right" — narrow-bar labels go to the right of the funnel (F regime).

    Each level's width is relative to the nominal demand of the same funnel.
    The interval lower bound is drawn as a solid body; the upper bound is
    drawn as a semi-transparent extension.
    """
    if label_side not in ("left", "right"):
        raise ValueError("label_side must be 'left' or 'right'")

    nominal_high = max(value_range(nominal)[1], 0.001)
    max_width = 1.36
    bar_height = 0.48
    label_gap = 0.12  # spacing between external value labels and bar edges

    def calculate_widths(value):
        low, high = value_range(value)
        return (
            max_width * low / nominal_high,
            max_width * high / nominal_high,
        )

    levels = [
        (nominal, COLORS["nominal"]),
        (climate, COLORS["climate"]),
        (double_value, COLORS[regime]),
    ]

    widths_by_level = [calculate_widths(value) for value, _ in levels]

    # Light connector faces between successive levels.
    for index in range(2):
        current_high = widths_by_level[index][1]
        next_high = widths_by_level[index + 1][1]

        y_top = y_levels[index] - bar_height / 2
        y_bottom = y_levels[index + 1] + bar_height / 2

        connector = Polygon(
            [
                (x - current_high / 2, y_top),
                (x + current_high / 2, y_top),
                (x + next_high / 2, y_bottom),
                (x - next_high / 2, y_bottom),
            ],
            closed=True,
            facecolor=levels[index + 1][1],
            edgecolor="none",
            alpha=0.12,
            zorder=1,
        )
        ax.add_patch(connector)

    # Three solid bodies with value labels.
    for index, ((value, color), width_pair) in enumerate(
        zip(levels, widths_by_level)
    ):
        low_width, high_width = width_pair
        y = y_levels[index]

        # Interval upper bound: semi-transparent background.
        if high_width > low_width + 1e-12:
            upper_patch = Polygon(
                [
                    (x - high_width / 2, y + bar_height / 2),
                    (x + high_width / 2, y + bar_height / 2),
                    (x + high_width / 2, y - bar_height / 2),
                    (x - high_width / 2, y - bar_height / 2),
                ],
                closed=True,
                facecolor=color,
                edgecolor=color,
                linewidth=0.6,
                alpha=0.25,
                zorder=2,
            )
            ax.add_patch(upper_patch)

        # Interval lower bound (or scalar): solid body.
        lower_patch = Polygon(
            [
                (x - low_width / 2, y + bar_height / 2),
                (x + low_width / 2, y + bar_height / 2),
                (x + low_width / 2, y - bar_height / 2),
                (x - low_width / 2, y - bar_height / 2),
            ],
            closed=True,
            facecolor=color,
            edgecolor=COLORS["white"],
            linewidth=0.9,
            zorder=3,
        )
        ax.add_patch(lower_patch)

        text = value_text(value)

        # The nominal-demand bar is the widest: its label is always inside.
        # Other levels are labeled inside only when wide enough.
        place_inside = index == 0 or low_width >= 0.80

        if place_inside:
            text_x = x
            text_color = COLORS["white"]
            horizontal_alignment = "center"
            font_weight = "bold"
        else:
            # Use the visible (upper-bound) width so labels do not overlap
            # the semi-transparent interval extension.
            visible_width = max(low_width, high_width)

            if label_side == "left":
                # U regime: labels go to the left of its own funnel.
                text_x = x - visible_width / 2 - label_gap
                horizontal_alignment = "right"
            else:
                # F regime: labels go to the right of its own funnel.
                text_x = x + visible_width / 2 + label_gap
                horizontal_alignment = "left"

            text_color = COLORS["text"]
            font_weight = "normal"

        ax.text(
            text_x, y, text,
            ha=horizontal_alignment, va="center",
            fontsize=7.8, color=text_color, fontweight=font_weight,
            zorder=5, clip_on=False,
        )


def make_funnel_year(year, fig_num):
    """Generate the three-level funnel figure for a single year."""
    fig, ax = plt.subplots(figsize=(19.0, 8.5), dpi=DPI)

    # Wider spacing between the four scenario centres avoids label overlap.
    centers = {
        "B1": 0.00,
        "B2": 5.20,
        "B3": 10.40,
        "B4": 15.60,
    }

    y_levels = [2.25, 1.10, -0.05]

    # Distance between the U (left) and F (right) funnels in one scenario.
    regime_offset = 0.76

    # Horizontal reference lines.
    for y in [1.675, 0.525]:
        ax.axhline(y, color=COLORS["line"], linewidth=0.8, zorder=0)

    for scenario in SCENARIOS:
        nominal, u_climate, u_double, f_climate, f_double = DATA[year][scenario]

        center = centers[scenario]
        x_u = center - regime_offset
        x_f = center + regime_offset

        # U regime: narrow-bar labels on the left.
        draw_funnel(
            ax=ax, x=x_u, y_levels=y_levels,
            nominal=nominal, climate=u_climate, double_value=u_double,
            regime="u_double", label_side="left",
        )

        # F regime: narrow-bar labels on the right.
        draw_funnel(
            ax=ax, x=x_f, y_levels=y_levels,
            nominal=nominal, climate=f_climate, double_value=f_double,
            regime="f_double", label_side="right",
        )

        # U / F regime labels.
        ax.text(x_u, -0.58, "U Unconstrained",
                ha="center", va="top", fontsize=8.5, color=COLORS["muted"])
        ax.text(x_f, -0.58, "F Firewall",
                ha="center", va="top", fontsize=8.5, color=COLORS["muted"])

        # Scenario label.
        ax.text(center, -0.87, scenario,
                ha="center", va="top", fontsize=13, fontweight="bold",
                color=COLORS["text"])

    # Left-hand three-tier definitions.
    left = -3.00

    level_labels = [
        (
            "Tier 1: Nominal demand",
            "Marine biofuel nominal demand",
            y_levels[0],
        ),
        (
            "Tier 2: Climate-compliant",
            "ILUC intensity < 94 gCO\u2082e/MJ\n"
            "and carbon payback \u2264 20 years",
            y_levels[1],
        ),
        (
            "Tier 3: Double-compliant",
            "Food-security, traceability,\n"
            "and physical-supply constraints",
            y_levels[2],
        ),
    ]

    for title, subtitle, y in level_labels:
        ax.text(left, y + 0.04, title,
                ha="right", va="center", fontsize=9.5, fontweight="bold",
                color=COLORS["text"])
        ax.text(left, y - 0.27, subtitle,
                ha="right", va="top", fontsize=7.6, color=COLORS["muted"],
                linespacing=1.25)

    # Title and subtitle.
    ax.text(
        0.5, 1.08,
        f"Fig. {fig_num}  Three-level funnel of environmentally "
        f"compliant supply, {year}",
        transform=ax.transAxes, ha="center", va="bottom",
        fontsize=17, fontweight="bold", color=COLORS["text"],
    )

    ax.text(
        0.5, 1.035,
        "Table 11 central criteria | Unit: EJ | "
        "Semi-transparent shading shows the interval upper bound",
        transform=ax.transAxes, ha="center", va="bottom",
        fontsize=9.5, color=COLORS["muted"],
    )

    # Year conclusion.
    if year == 2030:
        conclusion = (
            "In 2030 supply is small; double-compliant volume roughly "
            "equals climate-compliant volume"
        )
    elif year == 2040:
        conclusion = (
            "From 2040, food-security and physical-supply constraints "
            "emerge; U/F divergence widens"
        )
    else:
        conclusion = (
            "In 2050, double-compliant supply is capped by physical "
            "ceilings on UCO and second-generation feedstocks"
        )

    ax.text(0.5, -0.14, conclusion,
            transform=ax.transAxes, ha="center", va="top",
            fontsize=8.8, color=COLORS["muted"])

    # Legend.
    legend_handles = [
        Patch(facecolor=COLORS["nominal"], edgecolor="none",
              label="Nominal demand"),
        Patch(facecolor=COLORS["climate"], edgecolor="none",
              label="Climate-compliant"),
        Patch(facecolor=COLORS["u_double"], edgecolor="none",
              label="U double-compliant"),
        Patch(facecolor=COLORS["f_double"], edgecolor="none",
              label="F double-compliant"),
    ]

    ax.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.24),
        ncol=4,
        frameon=False,
        fontsize=8.5,
        handlelength=1.4,
        columnspacing=1.8,
    )

    # Generous axes range so the B1 U-side labels and B4 F-side labels fit.
    ax.set_xlim(-5.50, 19.00)
    ax.set_ylim(-1.35, 2.85)
    ax.axis("off")

    path = OUT / f"Fig{fig_num}_three_level_funnel_{year}.png"
    fig.savefig(
        path, dpi=DPI, format="png",
        bbox_inches="tight", facecolor="white", edgecolor="none",
    )
    plt.close(fig)

    if not path.exists():
        raise RuntimeError(f"Figure was not written: {path}")
    if path.stat().st_size < 1000:
        raise RuntimeError(f"Figure file is suspiciously small: {path}")

    return path


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    verify_data()
    validate_data()

    paths = [
        make_fig1(),
        make_fig2(),
    ]
    for year in YEARS:
        paths.append(make_funnel_year(year, year // 10 - 200))

    print()
    print("Generated 5 figures at 500 dpi in:", OUT.resolve())
    for p in paths:
        print(f"  {p.name}  {p.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print()
        print("Figure generation failed; full traceback:")
        traceback.print_exc()
        sys.exit(1)
