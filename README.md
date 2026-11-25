# ALP-ttbar Toy MC v2.9 — Background-Focused Diagnostics

Preregistration and post-registration results for v2.9 of the ALP-ttbar Toy MC series: diagnosing which conversion vertices the trimmed Tag removes and why they carry disproportionate leverage over the degradation ratio. Three investigations — z-distribution of removed vertices relative to 17 material bands, per-vertex B-elimination, and N_conv scaling test — address whether trimming corrects a structural p_conv floor artefact or a finite-sample effect.

**Preregistration DOI:** [10.5281/zenodo.24466187](https://doi.org/10.5281/zenodo.24466187)

## Post-Registration Results Summary

The post-registration study executed all three preregistered investigations across 50 seeds. Key findings:

- **Z1–Z2 REFUTED, Z3 NOT EVALUABLE (floor-artefact hypothesis):** All removed vertices are near-band (f_inter = 0.000); 1,184 is the representative seed 50 count (range across 50 seeds: 1,168–1,192). No floor-applied p_conv vertices appear. What drives the extreme λ values of these near-band vertices remains an open question.
- **B1–B3 CONFIRMED (B-elimination channel):** The 2% removal mask captures 100% of B-contributing conversion vertices (f_B,rem = 1.000) with 50-fold enrichment, perfectly consistent across all 50 seeds (CV = 0.0%).
- **N1–N2 CONFIRMED (N_conv scaling):** Untrimmed CV declined more slowly than the 1/√N reference over the tested range (endpoint ratio 0.4763 > 0.25); trimming benefit grows from 1.4× to 108.6× as N_conv increases from 3,125 to 50,000.
- **N3 REFUTED (trimmed stability):** Max trimmed CV = 14.35% at N = 3,125 — a small-sample resolution effect that converges rapidly at larger N.

**Overall: 5 confirmed, 3 refuted, 1 not evaluable; 1/3 core confirmed → PARTIAL support** (preregistration §7: 1 or 2 core = Partial). The Z1–Z2 refutation is the most informative result: the floor-artefact hypothesis is ruled out. Z3 (CV of f_inter) is not evaluable because f_inter = 0 for all seeds, making CV = 0/0 undefined. What drives the extreme λ values of near-band vertices remains an open question for future investigation.

## Context

The v2.8 post-registration study confirmed the trimmed Tag estimator (k = 1%) as the default discriminator: 8/9 predictions confirmed across 50 seeds. Key results at 17 MeV:
- CV reduced from 6.84% (untrimmed) to 0.09% (trimmed), a 76-fold improvement
- Mean degradation ratio: 1.5762 → 1.0648, an 89% reduction in excess degradation
- All 50 seeds show trimmed Tag < untrimmed Tag (D3: frac = 1.00)
- X1 REFUTED: optimal λ threshold preserved, mass window shifts — two-part improvement mechanism (B elimination + S increase)

These results establish *that* trimming works. This preregistration asks *why*: which vertices does trimming remove, and why do they carry such leverage?

## Predictions (9 total)

| ID | Description | Criterion | Tier |
|----|-------------|-----------|------|
| Z1 | Inter-band vertices dominate removed set | Mean f_inter > 0.5 | Core |
| Z2 | Inter-band enrichment above baseline | f_inter(removed) > f_inter(all) | Core |
| Z3 | f_inter consistent across seeds | CV(f_inter) < 20% | Secondary |
| B1 | Trimming removes majority of background | Mean f_B,rem > 0.5 | Core |
| B2 | B-contributors enriched in removed set | Mean enrichment > 1 | Derived |
| B3 | B-elimination fraction consistent across seeds | CV(f_B,rem) < 20% | Secondary |
| N1 | Untrimmed CV does not follow 1/√N | CV ratio > 0.25 | Diagnostic |
| N2 | Trimming benefit persists at large N | CV(untrim)/CV(trim) > 5 at 50k | Diagnostic |
| N3 | Trimmed CV stable across N_conv | CV(trimmed) < 1% at all N | Secondary |

Core predictions: {Z1, Z2, B1}. B2 is derived from B1 (enrichment = f_B,rem / removal fraction) and reported but not an independent judgment.

## Three Diagnostic Investigations

1. **Investigation A: z-Distribution** — Classify removed vertices as near-band or inter-band; test whether the p_conv floor drives removal.
2. **Investigation B: Background Elimination** — Measure what fraction of B the removal mask captures; test enrichment of B-contributors among removed vertices.
3. **Investigation C: N_conv Scaling** — Vary N_conv from 3,125 to 50,000; test whether extreme-λ leverage is structural or finite-sample.

## Configuration

- E3: f = 0.25, η = 2.0, 17-band geometry (9 sensor disks + 8 service bands)
- 50-seed ensemble, i = 50–99 (SEED_CONV = 100i+5, SEED_SIG = 100i+11); same seeds as v2.8
- Up to N_sig = 50,000 signal vertices, up to N_conv = 100,000 conversion vertices per seed (actual post-cut yield ≈58.6–59.6k at f = 0.25)
- Focus mass: 17 MeV (200 MeV not needed; v2.8 confirmed trimming inert there)
- Investigation C uses 10 seeds (i = 50–59) at N_conv ∈ {3125, 6250, 12500, 25000, 50000}

## Reproduction

### Dependencies

```
pip install matplotlib numpy reportlab pypdf scipy
```

The PDF generation script requires **DejaVu Sans** TrueType fonts (Regular, Bold, Oblique, BoldOblique) installed on the system. On Debian/Ubuntu:

```
sudo apt install fonts-dejavu-core
```

### Execution Order

#### Preregistration PDF

```bash
python generate_v29_prereg.py
```

#### Post-registration (full simulation + figures + PDF)

```bash
# 1. Run all three investigations (50 seeds, ~5 min)
python run_v29_postreg.py

# 2. Generate the post-registration PDF from results
python generate_v29_postreg.py
```

To regenerate preregistration figures from scratch:

```bash
python generate_figures.py           # v2.8 motivational figures
python generate_prediction_figures.py # prediction schematics
python generate_v29_prereg.py         # rebuild PDF
```

The `v28_results.json` file is included in this archive for convenience. It is the same file archived in the v2.8 post-registration repository.

All paths are relative to the script directory — no hardcoded absolute paths.

## Files

### Post-Registration

- `ALP-ttbar_Toy-MC_v2.9_Post-Registration_Background-Focused-Diagnostics_2026-11-25.pdf` — Post-registration report (12 pages, 5 colour figures)
- `run_v29_postreg.py` — Simulation script: runs all 3 investigations, generates figures and JSON/NPZ
- `generate_v29_postreg.py` — PDF generation script for post-registration report (ReportLab)
- `v29_postreg_results.json` — Full per-seed results (50 seeds × 3 investigations, 9 predictions)
- `v29_postreg_data.npz` — Representative seed arrays (z, σ_z, λ distributions for removed/all vertices)
- `fig_inv_a_z_distribution.png` — Figure 1: z-distribution of removed vertices vs material bands
- `fig_inv_a_f_inter.png` — Figure 2: f_inter = 0.000 across all 50 seeds (Z1 REFUTED)
- `fig_inv_b_background.png` — Figure 3: B-elimination (f_B,rem = 1.0, enrichment = 50×)
- `fig_inv_c_scaling.png` — Figure 4: CV vs N_conv log-log scaling + benefit ratio
- `fig_prediction_scorecard.png` — Figure 5: 9-row prediction scorecard (5/9 CONFIRMED)

### Preregistration

- `ALP-ttbar_Toy-MC_v2.9_Preregistration_Background-Focused-Diagnostics_2026-11-24.pdf` — Preregistration document (10 pages, 5 colour figures)
- `generate_v29_prereg.py` — PDF generation script (ReportLab)
- `generate_figures.py` — Matplotlib script for v2.8 motivational figures
- `generate_prediction_figures.py` — Matplotlib script for prediction schematic figures (Figs 3–5)
- `fig2_deg_distribution.png` — Figure 1: Degradation ratio violin + strip plot (v2.8 data)
- `fig3_signal_background.png` — Figure 2: Signal vs Background counts and S/B ratio (v2.8 data)
- `fig7_z_distribution_prediction.png` — Figure 3: Investigation A predicted z-distribution (schematic)
- `fig8_background_elimination_prediction.png` — Figure 4: Investigation B predicted B-elimination (schematic)
- `fig9_cv_scaling_prediction.png` — Figure 5: Investigation C predicted CV vs N_conv scaling (schematic)
- `v28_results.json` — v2.8 post-registration results data (from DOI 10.5281/zenodo.24437855)

### Frozen Modules

- `frozen/endcap_sim.py` — Simulation engine (frozen since v2.5)
- `frozen/mtag_v24.py` — Tag formula, 17-band (frozen since v2.4)
- `frozen/mtag_v22.py` — 9-band baseline (frozen since v2.2)

### Frozen File Provenance

The `frozen/` directory contains simulation modules carried forward from earlier versions. These files are identical to the versions archived in the v2.8 post-registration repository (DOI: [10.5281/zenodo.24437855](https://doi.org/10.5281/zenodo.24437855)).

| File | MD5 | Frozen Since |
|------|-----|-------------|
| `frozen/endcap_sim.py` | `7daa81b2723a1c13df68ee69b428c2d0` | v2.5 |
| `frozen/mtag_v24.py` | `39451a2189d71ec4a9d5990eacb54c6e` | v2.4 |
| `frozen/mtag_v22.py` | `a687701efe4476a999e27b32341c8c39` | v2.2 |

## File Hashes

**Post-Registration PDF:**
- SHA-256: `9e150502d6ef936904f385fdd4a3afb1307f8bcf930dc06a20acd80acdb43f1d`
- MD5: `570d4eda2589da056fb2f0d906c29224`

**Preregistration PDF:**
- SHA-256: `3cb923c9595dee16e4c5bebaa38c6fc0e75ae5a848882030d4b134c517b38b6a`
- MD5: `fc64a9a234cd8ddb4f0f238c963a0cd5`

## DOI Chain

| Version | DOI | Description |
|---------|-----|-------------|
| v2.9 post-reg (this) | 10.5281/zenodo.24527398 | Background-Focused Diagnostics results |
| v2.9 prereg | 10.5281/zenodo.24466187 | Background-Focused Diagnostics prereg |
| v2.8 post-reg | 10.5281/zenodo.24437855 | Trimmed Tag Estimator results |
| v2.8 prereg | 10.5281/zenodo.24414960 | Trimmed Tag Estimator prereg |
| v2.7 post-reg | 10.5281/zenodo.24408990 | Tag Formula Diagnostics results |
| v2.7 prereg | 10.5281/zenodo.24388228 | Tag Formula Diagnostics prereg |
| v2.6 post-reg | 10.5281/zenodo.24373115 | Multi-Seed Ensemble results |
| v2.6 prereg | 10.5281/zenodo.24361872 | Multi-Seed Ensemble prereg |
| v2.5 results | 10.5281/zenodo.24341050 | Deconflation post-reg |
| v2.5 prereg | 10.5281/zenodo.24329044 | Deconflation prereg |
| v2.4 results | 10.5281/zenodo.24302619 | 17-band geometry post-reg |
| v2.4 prereg | 10.5281/zenodo.24296796 | 17-band geometry prereg |
| v2.3 results | 10.5281/zenodo.24273586 | Endcap tag post-reg |
| v2.3 prereg | 10.5281/zenodo.24244893 | Endcap tag prereg |
| v2.2 results | 10.5281/zenodo.24238224 | Barrel → endcap post-reg |
| v2.2 prereg | 10.5281/zenodo.24189990 | Barrel → endcap prereg |
| v2.1 results | 10.5281/zenodo.24136462 | Barrel material-veto post-reg |
| v2.1 prereg | 10.5281/zenodo.24063091 | Barrel material-veto prereg |
| v2.0 | 10.5281/zenodo.24056097 | Initial barrel study |

## Disclaimer

Independent personal toy study, not affiliated with the authors of arXiv:2610.38932 (Alimena et al., 2026) or arXiv:2306.08686 (Rygaard et al., 2023), nor with the CMS, ATLAS, LHCb or ALICE Collaborations or the FCC study. Detector numbers are assumed; only qualitative trends and ratios are meaningful.

## Author

Won Shik Paik (Independent Researcher, Auckland, New Zealand)
