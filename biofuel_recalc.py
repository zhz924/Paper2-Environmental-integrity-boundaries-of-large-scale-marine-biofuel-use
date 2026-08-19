# -*- coding: utf-8 -*-
"""
biofuel_recalc.py — Paper 2 gap-driven caliber recalculation (integrated version)
Interface (draft 3 + main parameter table): E_bio(t,s) = Gap_electro(t) × β_bio(s)
  2030 Gap = 15.0 − 0.86 = 14.14 Mtoe (Paper 1 committed caliber, 5% target)
  2040 Gap = 133.6 − 17.0 = 116.6 Mtoe (D-Central demand − E-Central deliverable, σ=25%)
  2050 nominal upper bound = 13.4 EJ × 85% × β (policy-target caliber, flagged as the environmental-capacity stress-test upper bound)
The model is linear (already verified on the original model output: results ∝ E_bio), so the original output is rescaled by the demand ratio.
Original model output anchors (share-caliber demand):
  2030: 12.6×0.05×β = 0.63β EJ; 2040: 13.4×0.40×β = 5.36β EJ; 2050: 13.4×0.85×β = 11.39β EJ
"""
import json

BETAS = {'B1': 0.15, 'B2': 0.40, 'B3': 0.65, 'B4': 0.75}
EJ_PER_MTOE = 0.041868

# New demand anchors (EJ)
GAP = {2030: 14.14 * EJ_PER_MTOE, 2040: 116.6 * EJ_PER_MTOE}
DEMAND_NEW = {y: {b: (GAP[y] * BETAS[b] if y < 2050 else 13.4 * 0.85 * BETAS[b])
                  for b in BETAS} for y in (2030, 2040, 2050)}
# Original demand anchors (EJ)
DEMAND_OLD = {2030: 0.63, 2040: 5.36, 2050: 11.39}  # ×β

# Original model results per β (U caliber; source: model output v2 Tables R2/R3, all values linear in β×coefficient form)
# Use the B4 (β=0.75) results to back out the coefficients, then recompute with the new demand
# Original output (Tables R2/R3, correct column order): [E_bio, ILUC area Mha, carbon pulse Mt, CI_prod, CI_ILUC, CI_total, payback yr, net abatement Mt/yr, oil demand Mt, price shock %, LDC burden %, malnutrition million]
ORIG_B4 = {
    ('U', 2030): [0.47, 2.94, 776, 33.0, 88.8, 121.9, 29, -13.2, 6.1, 6.3, 1.43, 15.99],
    ('U', 2040): [4.02, 25.05, 6606, 33.0, 88.8, 121.9, 29, -112.0, 51.8, 54.0, 12.14, 119.85],
    ('U', 2050): [8.54, 53.23, 14037, 33.0, 88.8, 121.9, 29, -238.0, 110.1, 114.7, 25.80, 225.32],
    ('F', 2030): [0.47, 1.75, 423, 22.8, 45.7, 68.6, 13, 12.0, 2.5, 2.6, 0.59, 6.66],
    ('F', 2040): [4.02, 14.87, 3600, 22.8, 45.7, 68.6, 13, 102.2, 21.3, 22.2, 5.00, 53.48],
    ('F', 2050): [8.54, 31.59, 7651, 22.8, 45.7, 68.6, 13, 217.2, 45.3, 47.2, 10.62, 106.55],
}
FIELDS = ['E_bio', 'ILUC_Mha', 'carbon_Mt', 'CI_prod', 'CI_ILUC', 'CI_total', 'payback', 'net_Mt', 'oil_Mt', 'price_shock', 'ldc_burden', 'pou_million']
LINEAR = ['ILUC_Mha', 'carbon_Mt', 'net_Mt', 'oil_Mt', 'price_shock', 'ldc_burden']  # linearly scaled fields
POU0, THETA = 735.0, 0.35  # malnutrition baseline (million) and constant elasticity

def rescale(regime, year, bname):
    """Rescale to the new demand anchors: linear fields ×(E_new/E_old); malnutrition recomputed from the price shock via the constant-elasticity formula; intensity fields unchanged"""
    old = dict(zip(FIELDS, ORIG_B4[(regime, year)]))
    e_old = DEMAND_OLD[year] * 0.75
    e_new = DEMAND_NEW[year][bname]
    out = dict(old)
    out['E_bio'] = e_new
    for f in LINEAR:
        out[f] = old[f] * (e_new / e_old)
    out['pou_million'] = POU0 * ((1 + out['price_shock'] / 100) ** THETA - 1)
    return out

print('═══ New demand anchors (gap-driven) ═══')
for y in (2030, 2040, 2050):
    gap_note = f'Gap={GAP[y]/EJ_PER_MTOE:.1f} Mtoe' if y < 2050 else 'nominal upper bound 13.4×85%'
    print(f'{y} ({gap_note}): ' + ', '.join(f'{b}={DEMAND_NEW[y][b]:.2f} EJ ({DEMAND_NEW[y][b]/EJ_PER_MTOE:.1f} Mtoe)' for b in BETAS))

print('\n═══ Recalculated results summary (2050, U/F calibers) ═══')
hdr = ['Scenario', 'E_bio(EJ)', 'ILUC(Mha)', 'Carbon pulse(Mt)', 'Total CI', 'Payback', 'Net abatement(Mt/yr)', 'Price shock%', 'LDC burden%', 'Malnutrition(million)']
print(' | '.join(hdr))
for b in BETAS:
    for reg in ('U', 'F'):
        r = rescale(reg, 2050, b)
        print(f"{b}{reg} | {r['E_bio']:.2f} | {r['ILUC_Mha']:.2f} | {r['carbon_Mt']:.0f} | {r['CI_total']:.1f} | {r['payback']} | {r['net_Mt']:.1f} | {r['price_shock']:.1f} | {r['ldc_burden']:.2f} | {r['pou_million']:.1f}")

print('\n═══ Check: 2050 (new = original demand) should match the original model output exactly ═══')
print('Original B2U: ILUC=28.39, carbon pulse=7486, malnutrition=133.6')
r = rescale('U', 2050, 'B2')
print(f"New B2U: ILUC={r['ILUC_Mha']:.2f}, carbon pulse={r['carbon_Mt']:.0f}, malnutrition={r['pou_million']:.1f}")

print('\n═══ 2030/2040 gap-driven results (B2 neutral, U/F) ═══')
for y in (2030, 2040):
    for reg in ('U', 'F'):
        r = rescale(reg, y, 'B2')
        print(f"{y} B2{reg}: E_bio={r['E_bio']:.2f} EJ, ILUC={r['ILUC_Mha']:.2f} Mha, carbon pulse={r['carbon_Mt']:.0f} Mt, total CI={r['CI_total']:.1f}, price shock={r['price_shock']:.1f}%, malnutrition={r['pou_million']:.1f} million")

print('\n═══ Environmentally eligible supply cap (double-eligibility funnel, 2050 central value) ═══')
# Nominal demand (B2=40% backfill) → climate-eligible (CI_total<94 and payback ≤20 yr) → double-eligible (add the food-security FSRI threshold)
# Path-level eligibility rate (Table R4): palm/soy/rapeseed FAME-HVO are all "high risk" (payback 29–97 yr > 20); energy-crop methanol 14 yr eligible; residue methanol/UCOME 0–1 yr eligible
# U-caliber feedstock mix: palm 35 + soy 30 + rapeseed 20 + UCO 15 → only UCO 15% eligible (by energy)
# F-caliber: palm 5 + soy 15 + rapeseed 15 + UCO 30 + 2nd-gen 35 → eligible: UCO 30 + 2nd-gen 35 + residue methanol portion; climate-eligible rate ≈65–70% for the mix, reduced to 55–60% after the food-security constraint
# Eligible cap = min(environmentally eligible demand, sustainable feedstock physical cap)
# Waste/UCO physical cap: global collectable UCO ≈0.5–0.8 EJ (literature); 2nd-gen cellulosic potential is large but land-constrained
print('U caliber: climate-eligible rate ≈15% (waste-oil path only) → of B2U 2050 nominal 4.56 EJ, climate-eligible only ≈0.68 EJ')
print('F caliber: climate-eligible rate ≈65% (UCO+2nd-gen+residue) → B2F 2050 eligible ≈2.96 EJ; after the feedstock physical cap (waste 0.5–0.8 EJ) and the food-security threshold, double-eligible cap ≈1.5–2.5 EJ (range)')
