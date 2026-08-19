# -*- coding: utf-8 -*-
"""funnel_matrix.py — Paper 2 v1.2 year × scenario three-tier funnel core computation (reproducibility component)
Computes the 2030/2040/2050 × B1–B4 × U/F three-tier funnel:
  nominal demand → climate-eligible (38%/70%) → double-eligible = min(climate, food-security, physical)
Food-security constraint solved inversely from the Section 3.6 constant-elasticity model thresholds;
physical constraint = UCO (static) + 2nd-generation lignocellulosic (per year).
Calibration anchors (numbers already published in Paper 2 v1.1, must close):
  B2U 2050: ΔPoU = 133.6 million, Δp = 61.2%; B2F: 60.1; B4U: 225; B4F: 106.5
  U double-eligible 2050 ≈ 0.5–0.8 (UCO binding); F double-eligible 2050 ≈ 1.5–2.5 (pivot ≈ 2.0)
Run: python3 funnel_matrix.py
"""
import math

MTOE2EJ = 0.041868
POU0, THETA = 735.0, 0.35
D_MAP = {  # Table 2 nominal backfill demand (EJ)
    'B1': {2030: 0.09, 2040: 0.73, 2050: 1.71},
    'B2': {2030: 0.24, 2040: 1.95, 2050: 4.56},
    'B3': {2030: 0.38, 2040: 3.17, 2050: 7.40},
    'B4': {2030: 0.44, 2040: 3.66, 2050: 8.54}}
CLIMATE_RATE = {'U': 0.38, 'F': 0.70}
UCO_LO, UCO_HI = 0.5, 0.8          # UCO global physical cap (Steinbach, 2025)
# 2nd-generation lignocellulosic per-year eligible supply (EJ, range): anchored on Searle & Malins (2015) energy crops
# sustainable cap 40–110 EJ/yr (feedstock) and the IEA NZE (2023) advanced liquid biofuel trajectory
# (2030=4.4 / 2035=7.2 / 2050≈8.3 EJ), reduced by 55% conversion, collection radius, and soil-retention constraints.
GEN2 = {2030: (0.0, 0.2), 2040: (0.8, 1.5), 2050: (1.5, 2.0)}
# Four food-security eligibility tiers (price shock, ΔPoU threshold million/yr)
TIERS = {'strict': (0.10, 15.0), 'central': (0.15, 30.0), 'lenient': (0.20, 50.0)}

# ── Food-security model calibration (constant elasticity) ──
def k_from_anchor(D, dpou):
    dp = (1 + dpou / POU0) ** (1 / THETA) - 1
    return dp / D
K = {'U': k_from_anchor(4.56, 133.6), 'F': k_from_anchor(4.56, 60.1)}
print('══ Calibration check (4 anchors) ══')
for m, D, dpou_ref in [('U', 4.56, 133.6), ('F', 4.56, 60.1), ('U', 8.54, 225.0), ('F', 8.54, 106.5)]:
    dpv = K[m] * D
    dpouv = POU0 * ((1 + dpv) ** THETA - 1)
    ok = '✓' if abs(dpouv - dpou_ref) < 0.6 else '✗'
    print(f'  {m} D={D}: Δp={dpv*100:.1f}% ΔPoU={dpouv:.1f} million (anchor {dpou_ref}) {ok}')

# ── Food-security eligible supply inverse solve (threshold → max allowed supply, EJ; invariant to t, b) ──
def s_food(m, thr_p, thr_pou):
    if thr_pou <= 0:
        return 0.0
    dp_cap = (1 + thr_pou / POU0) ** (1 / THETA) - 1
    return min(thr_p, dp_cap) / K[m]
print('\n══ Four tiers → food-security eligible supply S_food (EJ) ══')
SF = {}
for tier, (tp, tpou) in TIERS.items():
    SF[tier] = {m: s_food(m, tp, tpou) for m in ('U', 'F')}
    print(f'  {tier:14s}(Δp<{tp*100:.0f}%, ΔPoU<{tpou:.0f} million): U={SF[tier]["U"]:.2f}, F={SF[tier]["F"]:.2f}'
          )

# ── Double-eligible upper bounds (central criterion) ──
print('\n══ 24-cell three-tier funnel matrix (central criterion, EJ) ══')
print(f'{"year":<6}{"scen":<5}{"nom":>6} | {"climU":>6}{"doubleU":>14} | {"climF":>6}{"doubleF":>14}')
ROWS = []
for t in (2030, 2040, 2050):
    g2lo, g2hi = GEN2[t]
    for b in ('B1', 'B2', 'B3', 'B4'):
        D = D_MAP[b][t]
        out = {'t': t, 'b': b, 'D': D}
        for m in ('U', 'F'):
            clim = D * CLIMATE_RATE[m]
            plo = UCO_LO + (g2lo if m == 'F' else 0.0)
            phi = UCO_HI + (g2hi if m == 'F' else 0.0)
            elo = min(clim, SF['central'][m], plo)
            ehi = min(clim, SF['central'][m], phi)
            out[m] = (clim, elo, ehi)
        ROWS.append(out)
        print(f'{t:<6}{b:<5}{D:>6.2f} | {out["U"][0]:>6.2f}'
              f'{out["U"][1]:>5.2f}–{out["U"][2]:<5.2f} | {out["F"][0]:>6.2f}'
              f'{out["F"][1]:>5.2f}–{out["F"][2]:<5.2f}')

# ── Closure check against numbers already published in Paper 2 v1.1 ──
print('\n══ Closure check against numbers already published in Paper 2 v1.1 ══')
chk = []
r = next(x for x in ROWS if x['t'] == 2050 and x['b'] == 'B2')
chk.append(('2050B2U double-eligible ∈ [0.5, 0.8]', abs(r['U'][1] - UCO_LO) < 1e-9 and abs(r['U'][2] - UCO_HI) < 1e-9,
            f'{r["U"][1]:.2f}–{r["U"][2]:.2f}'))
chk.append(('2050B2F double-eligible pivot ≈2.0 ∈ [1.5, 2.5]', 1.5 <= (r['F'][1] + r['F'][2]) / 2 <= 2.5,
            f'{r["F"][1]:.2f}–{r["F"][2]:.2f} pivot {(r["F"][1]+r["F"][2])/2:.2f}'))
chk.append(('Paper 3 interface 2030 bio-cap = UCO convention 10.9 Mtoe',
            abs(UCO_LO * 0.912 / MTOE2EJ - 10.9) < 0.2, f'{UCO_LO*0.912/MTOE2EJ:.1f}'))
for name, ok, info in chk:
    print(f'  {"✓" if ok else "✗"} {name}: {info}')

# ── Double-eligible under the four tiers (2050 B2 focus cell) ──
print('\n══ 2050 B2 double-eligible response to the four tiers (EJ) ══')
for tier in TIERS:
    g2lo, g2hi = GEN2[2050]
    vals = {}
    for m in ('U', 'F'):
        clim = 4.56 * CLIMATE_RATE[m]
        plo = UCO_LO + (g2lo if m == 'F' else 0.0)
        phi = UCO_HI + (g2hi if m == 'F' else 0.0)
        vals[m] = (min(clim, SF[tier][m], plo), min(clim, SF[tier][m], phi))
    print(f'  {tier:14s}: U={vals["U"][0]:.2f}–{vals["U"][1]:.2f}, F={vals["F"][0]:.2f}–{vals["F"][1]:.2f}')

import json
with open('funnel_matrix.json', 'w', encoding='utf-8') as f:
    json.dump({'K': K, 'SF': SF, 'GEN2': {str(k): v for k, v in GEN2.items()},
               'rows': [{'t': r['t'], 'b': r['b'], 'D': r['D'],
                         'U': list(r['U']), 'F': list(r['F'])} for r in ROWS]},
              f, ensure_ascii=False, indent=1)
print('\nfunnel_matrix.json written (for figure generation and markdown-table use)')
