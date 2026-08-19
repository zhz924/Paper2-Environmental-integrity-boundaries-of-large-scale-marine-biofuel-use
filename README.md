# Paper 2 (Environmental Eligibility) — Reproducibility Package

**Paper title (English):**
*Environmental Integrity Boundaries of Large-Scale Marine Biofuel Deployment: Indirect Land-Use Change, Carbon Debt, Food Security, and Eligible Supply Limits*

This is the code-publication package accompanying Paper 2 of the series (the "Environmental Eligibility" paper), prepared for **Transportation Research Part D (TR-D)**. It contains the scripts and figures needed to reproduce every numerical result reported in the paper, including the audit of Tables 2/7/8/9/10, Figure 2, the Section 4.8 sensitivity analysis, and the three-tier eligibility funnel (Table 11, Figures 3–5).

> **Zenodo DOI (placeholder):** `10.5281/zenodo.XXXXXXXX` — to be assigned upon deposit.

---

## Package contents

```
Paper2_Reproducibility/
├── README.md                    # this file
├── audit_paper2_v1.1.py         # reproducibility audit of the core published numbers
├── biofuel_recalc.py            # CORE MODEL: gap-driven biofuel backfill recalculation
├── funnel_matrix.py             # three-tier funnel computation (Table 11 engine)
├── funnel_matrix.json           # sample output of funnel_matrix.py (for figures/markdown)
├── make_figures_paper2_en.py      # generates figs
└── figures/
    ├── fig1_demand.png              # Fig. 1 — gap-driven biofuel backfill demand pathway
    ├── fig2_food_security.png       # Fig. 2 — food-security impact, U vs F regimes
    ├── fig3_funnel_matrix_2030.png  # Fig. 3 — three-tier funnel, 2030
    ├── fig4_funnel_matrix_2040.png  # Fig. 4 — three-tier funnel, 2040
    └── fig5_funnel_matrix_2050.png  # Fig. 5 — three-tier funnel, 2050
```

---

## Script purpose

| Script | What it does | Output |
| --- | --- | --- |
| `audit_paper2_v1.1.py` | Independently recomputes the key numbers of Tables 2/7/8/9/10, Figure 2, and the Section 4.8 sensitivity analysis from the parameters and formulas published in Sections 3.3–3.6. All assertions must pass. | Console: `[PASS] ...` lines, ending with `ALL NUMERICAL RELATIONS CLOSED ✓` |
| `biofuel_recalc.py` | **Core model.** Generates the gap-driven biofuel backfill results directly from the interface `E_bio(t,s) = Gap_electro(t) × β_bio(s)` (2030 Gap = 14.14 Mtoe, 2040 Gap = 116.6 Mtoe, 2050 nominal bound 13.4 EJ × 85% × β), rescaling the original model output and recomputing the U/F ILUC, carbon pulse, price shock and malnutrition columns. Standard library only. | Console summary tables (2030/2040/2050, U/F). |
| `funnel_matrix.py` | Computes the 24-cell three-tier funnel (2030/2040/2050 × B1–B4 × U/F): nominal demand → climate-eligible (38%/70%) → double-eligible = min(climate, food-security, physical). | Console matrix + closure checks; writes `funnel_matrix.json` |
| `make_figures_p2_v1_1.py` | Renders Figures 1–2 from the published data. | `figures/fig1_demand.png`, `figures/fig2_food_security.png` |
| `make_fig_funnel_matrix.py` | Renders Figures 3–5 (one per year) from the Table 11 funnel data. | `figures/fig3/4/5_funnel_matrix_2030/2040/2050.png` |

All numbers, formulas, and variable names are unchanged from the Chinese source scripts; only comments, print output, and check-assertion descriptions have been translated into English.

**Audit vs. core model.** `audit_paper2_v1.1.py` is the *audit* script: it verifies the numerical relationships already printed in the paper by recomputing each number independently and asserting that it matches. `biofuel_recalc.py` is the *core-model* script: it generates the results directly from the parameters and the Paper-1 gap interface. Together they provide complete reproduction — the core model produces the numbers and the audit confirms that every relation closes.

---

## Dependencies

- **Python 3.8+**
- `audit_paper2_v1.1.py`, `biofuel_recalc.py` and `funnel_matrix.py` depend on the **standard library only** (no third-party packages).
- `make_figures_p2_v1_1.py` and `make_fig_funnel_matrix.py` require:
  - `numpy`
  - `matplotlib`
  - (optional) a CJK-capable font for the figure annotations. The scripts try to register
    `/usr/local/share/fonts/custom/NotoSansSC-Regular.ttf` and `NotoSansSC-Bold.ttf`; if absent,
    they fall back to DejaVu Sans.

Install the plotting dependencies with:

```bash
pip install numpy matplotlib
```

---

## How to run

```bash
# 1. Reproduce the core-number audit (standard library only)
python3 audit_paper2_v1.1.py

# 2. Core model: gap-driven biofuel backfill recalculation (standard library only)
python3 biofuel_recalc.py

# 3. Reproduce the three-tier funnel matrix and its JSON output
python3 funnel_matrix.py

# 4. Reproduce Figures 1–2
python3 make_figures_p2_v1_1.py

# 5. Reproduce Figures 3–5
python3 make_fig_funnel_matrix.py
```

Figure scripts write PNG files to the `figures/` sub-directory next to each script. The pre-rendered figures shipped in this package are the exact originals, renamed in English; re-running the scripts reproduces the same content.

> Note: the figure *annotations* (titles, axis and legend labels) remain in Chinese, matching the paper's original figures. Only the file names were translated.

---

## Data sources

The numerical inputs come from the published literature parameters stated in Sections 3.1–3.7:

- **E-fuel backfill gap** (the demand input of Table 2): from the companion project-level supply assessment of green hydrogen-derived fuels — Zhou, H., 2026a, *Physical supply boundaries of green hydrogen-derived marine fuels: A project-level assessment* (Paper 1 of this series). 2030: 15.0 Mtoe policy demand vs 0.86 Mtoe committed deliverable supply; 2040: 133.6 Mtoe vs 17.0 Mtoe. Unit conversion 1 Mtoe = 0.041868 EJ.
- **Used cooking oil (UCO) global physical cap** of ≈0.5–0.8 EJ (binds the U double-eligible supply in the funnel): Steinbach, S., 2025, *The used cooking oil dilemma: Feedstock competitiveness, certification integrity, and U.S. biofuel policy*, Food Policy 134, 102907.
- **2nd-generation lignocellulosic eligible supply** (2030: 0–0.2 EJ; 2040: 0.8–1.5 EJ; 2050: 1.5–2.0 EJ): anchored on Searle, S., Malins, C., 2015b, *A reassessment of global bioenergy potential in 2050* (sustainable cap 40–110 EJ/yr) and the IEA, 2023, *Net Zero Roadmap* advanced liquid biofuel trajectory, reduced by the 55% conversion efficiency of Section 3.3.
- **Fossil comparator** 94 gCO₂e/MJ (WtW); **ILUC emission factors** 480/950/130/250 tCO₂/ha (forest/peatland/grassland/other wooded land); **peat oxidation** 55 tCO₂/ha/yr; **supply/demand elasticities** ε_s = 0.15, ε_d = −0.25 (Persson, 2015; Al-Riffai et al., 2010); **malnutrition elasticity** θ = 0.35.

All other parameters are the paper's own scenario assumptions or model estimates and are documented in-line in each script.

---

## Licensing and citation

When using this package, please cite the paper and the assigned Zenodo DOI. The scripts are provided for reproducibility and peer review under the terms stated in the journal submission.

**Suggested citation (placeholder):**
Zhou, H. (2026). *Environmental Integrity Boundaries of Large-Scale Marine Biofuel Deployment: Indirect Land-Use Change, Carbon Debt, Food Security, and Eligible Supply Limits*. Transportation Research Part D (under review). Code and data: https://doi.org/10.5281/zenodo.XXXXXXXX
