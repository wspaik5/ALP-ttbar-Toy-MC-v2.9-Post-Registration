#!/usr/bin/env python3
"""v2.9 Post-Registration: Background-Focused Diagnostics.

Implements three investigations preregistered in DOI 10.5281/zenodo.24466187:
  A) z-distribution of removed vertices relative to 17 material bands
  B) Background elimination by trimming (f_B,rem, enrichment)
  C) N_conv scaling test

Configuration: E3 (f = 0.25, η = 2.0, 17-band geometry)
Seeds: i = 50–99 (50 seeds), Investigation C uses i = 50–59 (10 seeds)
Focus mass: 17 MeV
"""

import os, sys, json, time
import numpy as np

# ── Set material scale BEFORE importing endcap_sim (E3: f = 0.25) ──
os.environ['V16_F'] = '0.25'

_FROZEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frozen')
sys.path.insert(0, _FROZEN)
import endcap_sim
import mtag_v24
import mtag_v22

# ════════════════════════════════════════════════════════════
# Parameters (from preregistration)
# ════════════════════════════════════════════════════════════
M_ALP       = 0.017        # 17 MeV in GeV
N_SIG_CAP   = 50_000
N_CONV_CAP  = 100_000
K_TRIM      = 0.01         # 1 % from each tail → 2 % total
SEEDS       = list(range(50, 100))       # 50 seeds
INV_C_SEEDS = list(range(50, 60))        # 10 seeds for Inv C
N_CONV_GRID = [3125, 6250, 12500, 25000, 50000]

# d_band: half the minimum gap between adjacent 17-band centres
BAND_Z   = np.array(sorted([d[0] for d in mtag_v24.DISKS]))
BAND_HW  = np.array([d[2] for d in sorted(mtag_v24.DISKS, key=lambda d: d[0])])
BAND_X0  = np.array([d[1] for d in sorted(mtag_v24.DISKS, key=lambda d: d[0])])
_gaps    = np.diff(BAND_Z)
D_BAND   = float(_gaps.min() / 2.0)   # 17.5 mm

TGRID = mtag_v24.TGRID

# Which of the 17 bands are sensor disks vs service bands
_sensor_z  = set(d[0] for d in mtag_v24._SENSOR_DISKS)
_service_z = set(d[0] for d in mtag_v24._SERVICE_BANDS)
IS_SENSOR  = np.array([z in _sensor_z for z in BAND_Z])

_DIR = os.path.dirname(os.path.abspath(__file__))


# ════════════════════════════════════════════════════════════
# Helper functions
# ════════════════════════════════════════════════════════════

def scan_with_window(sig, bkg, lam_sig, lam_conv):
    """Like scan_tag_endcap but also returns mass-window bounds."""
    m = M_ALP
    S0 = sig['w'][sig['base']].sum()
    lim0 = endcap_sim.upper_limit(S0, 0)
    best = None

    cands = [(np.ones(len(sig['z']), bool),
              np.ones(len(bkg['z']), bool), None, None)]
    for lo in np.linspace(0, 1.5 * m, 31):
        for hi in (3 * m + 0.01, np.inf):
            cands.append(((sig['m'] > lo) & (sig['m'] < hi),
                          (bkg['m'] > lo) & (bkg['m'] < hi), lo, hi))

    for t in TGRID:
        if t is None:
            ts = np.ones(len(sig['z']), bool)
            tb = np.ones(len(bkg['z']), bool)
        else:
            ts = lam_sig >= t
            tb = lam_conv >= t
        for ms, mb, lo, hi in cands:
            cs = sig['base'] & ts & ms
            cb = bkg['base'] & tb & mb
            S = sig['w'][cs].sum()
            B = bkg['w'][cb].sum()
            lim = endcap_sim.upper_limit(S, B)
            if best is None or lim < best['limit']:
                best = dict(limit=lim, deg=lim / lim0, t=t,
                            B=float(B), S=float(S), m_lo=lo, m_hi=hi)
    return best


def apply_trim(lam_conv, base_conv, k=K_TRIM):
    """Apply k% trim from each tail of the λ distribution.

    Returns (removal_mask, n_rem_per_tail, removed_idx, lower_idx, upper_idx).
    """
    base_indices = np.where(base_conv)[0]
    n_base = len(base_indices)
    n_rem = int(np.floor(k * n_base))

    if n_rem == 0:
        empty = np.array([], dtype=int)
        return np.zeros(len(lam_conv), bool), 0, empty, empty, empty

    lam_base = lam_conv[base_indices]
    order = np.argsort(lam_base)
    lower_local = order[:n_rem]
    upper_local = order[-n_rem:]
    removed_local = np.union1d(lower_local, upper_local)

    removed_full = base_indices[removed_local]
    lower_full  = base_indices[lower_local]
    upper_full  = base_indices[upper_local]

    mask = np.zeros(len(lam_conv), bool)
    mask[removed_full] = True
    return mask, n_rem, removed_full, lower_full, upper_full


def classify_z(zm, sz):
    """Near-band / inter-band classification and p_conv floor check."""
    dist = np.abs(zm[:, None] - BAND_Z[None, :]).min(axis=1)
    near_band = dist <= D_BAND
    pc = mtag_v24.p_conv(zm, sz)
    floor_applied = pc <= mtag_v24.P_FLOOR * 1.01
    return near_band, floor_applied


# ════════════════════════════════════════════════════════════
# Investigation A & B  —  per-seed runner
# ════════════════════════════════════════════════════════════

def run_seed_ab(i, save_rep=False):
    """Run one seed for Investigations A & B.  Returns result dict
    (and optionally a dict of arrays for the representative figure)."""
    t0 = time.time()
    seed_conv = 100 * i + 5
    seed_sig  = 100 * i + 11

    # Generate
    conv = endcap_sim.endcap_conversions(n=1_500_000, seed=seed_conv, config='E2')
    sig  = endcap_sim.endcap_signal(M_ALP, n=300_000, seed=seed_sig, config='E2')

    # Subsample
    conv_s, _ = endcap_sim.subsample(conv, N_CONV_CAP)
    sig_s,  _ = endcap_sim.subsample(sig,  N_SIG_CAP)

    # Δχ²
    dchi2_c, _ = endcap_sim.compute_dchi2_endcap(conv_s)
    dchi2_s, _ = endcap_sim.compute_dchi2_endcap(sig_s)

    # λ  (17-band tag)
    lam_c = mtag_v24.lam(conv_s['zm'], conv_s['sz'], dchi2_c)
    lam_s = mtag_v24.lam(sig_s['zm'], sig_s['sz'], dchi2_s)

    n_base = int(conv_s['base'].sum())

    # ── Untrimmed scan ──
    best_u = scan_with_window(sig_s, conv_s, lam_s, lam_c)

    # ── Trim ──
    mask, n_rem, removed, lower, upper = apply_trim(lam_c, conv_s['base'])
    n_removed = int(mask.sum())

    # ── Trimmed scan ──
    conv_t = dict(conv_s)
    conv_t['base'] = conv_s['base'] & ~mask
    best_t = scan_with_window(sig_s, conv_t, lam_s, lam_c)

    # ── Investigation A ──
    zm_rem = conv_s['zm'][removed]
    sz_rem = conv_s['sz'][removed]
    near_rem, floor_rem = classify_z(zm_rem, sz_rem)
    inter_rem = ~near_rem
    f_inter = float(inter_rem.sum() / len(removed)) if len(removed) > 0 else 0.0

    base_idx = np.where(conv_s['base'])[0]
    near_all, floor_all = classify_z(conv_s['zm'][base_idx], conv_s['sz'][base_idx])
    f_inter_all = float((~near_all).sum() / len(base_idx))

    in_upper = np.isin(removed, upper)
    in_lower = np.isin(removed, lower)

    # ── Investigation B ──
    t_opt = best_u['t']
    m_lo, m_hi = best_u['m_lo'], best_u['m_hi']

    b_mask = conv_s['base'].copy()
    if t_opt is not None:
        b_mask = b_mask & (lam_c >= t_opt)
    if m_lo is not None:
        b_mask = b_mask & (conv_s['m'] > m_lo) & (conv_s['m'] < m_hi)

    n_B          = int(b_mask.sum())
    n_B_in_mask  = int((b_mask & mask).sum())
    f_B_rem      = float(n_B_in_mask / n_B) if n_B > 0 else 0.0
    removal_frac = float(n_removed / n_base) if n_base > 0 else 0.0
    b_frac_all   = float(n_B / n_base) if n_base > 0 else 0.0
    b_frac_rem   = float(b_mask[removed].sum() / n_removed) if n_removed > 0 else 0.0
    enrichment   = float(b_frac_rem / b_frac_all) if b_frac_all > 0 else 0.0

    # Floor-applied among B-contributors in removal mask
    b_in_mask_idx = np.where(b_mask & mask)[0]
    if len(b_in_mask_idx) > 0:
        _, floor_b = classify_z(conv_s['zm'][b_in_mask_idx], conv_s['sz'][b_in_mask_idx])
        f_floor_B = float(floor_b.sum() / len(b_in_mask_idx))
    else:
        f_floor_B = 0.0

    dt = time.time() - t0

    result = dict(
        seed_i        = i,
        time_s        = round(dt, 1),
        n_base_conv   = n_base,
        n_removed     = n_removed,
        n_rem_per_tail= int(n_rem),
        # untrimmed
        deg_untrim    = round(best_u['deg'], 6),
        B_untrim      = round(best_u['B'], 4),
        t_opt         = t_opt,
        m_lo          = m_lo,
        m_hi          = float(m_hi) if m_hi is not None and np.isfinite(m_hi) else None,
        # trimmed
        deg_trim      = round(best_t['deg'], 6),
        B_trim        = round(best_t['B'], 4),
        # Inv A
        f_inter       = round(f_inter, 6),
        f_inter_all   = round(f_inter_all, 6),
        n_near_band   = int(near_rem.sum()),
        n_inter_band  = int(inter_rem.sum()),
        n_floor_rem   = int(floor_rem.sum()),
        n_upper_tail  = int(in_upper.sum()),
        n_lower_tail  = int(in_lower.sum()),
        # Inv B
        n_B           = n_B,
        n_B_in_mask   = n_B_in_mask,
        f_B_rem       = round(f_B_rem, 6),
        enrichment    = round(enrichment, 4),
        f_floor_B     = round(f_floor_B, 6),
        removal_frac  = round(removal_frac, 6),
    )

    rep_data = None
    if save_rep:
        rep_data = dict(
            zm_all_base  = conv_s['zm'][base_idx].copy(),
            sz_all_base  = conv_s['sz'][base_idx].copy(),
            lam_all_base = lam_c[base_idx].copy(),
            zm_removed   = zm_rem.copy(),
            sz_removed   = sz_rem.copy(),
            lam_removed  = lam_c[removed].copy(),
            near_band    = near_rem.copy(),
            floor_applied= floor_rem.copy(),
            in_upper     = in_upper.copy(),
            in_lower     = in_lower.copy(),
            b_contributor= b_mask[removed].copy(),
        )
    return result, rep_data


# ════════════════════════════════════════════════════════════
# Investigation C  —  per-seed runner (all N_conv caps)
# ════════════════════════════════════════════════════════════

def run_inv_c_seed(i):
    """Run one seed across all N_conv caps for Investigation C.

    v2.8 standard method: trim BOTH signal and conversion λ distributions,
    normalise degradation by pre-trimming signal count (S0).
    Also records conversion-only trim results as supplementary.
    """
    t0 = time.time()
    seed_conv = 100 * i + 5
    seed_sig  = 100 * i + 11

    # Generate ONCE
    conv = endcap_sim.endcap_conversions(n=1_500_000, seed=seed_conv, config='E2')
    sig  = endcap_sim.endcap_signal(M_ALP, n=300_000, seed=seed_sig, config='E2')

    # Signal: always at N_SIG_CAP
    sig_s, _ = endcap_sim.subsample(sig, N_SIG_CAP)
    dchi2_s, _ = endcap_sim.compute_dchi2_endcap(sig_s)
    lam_s = mtag_v24.lam(sig_s['zm'], sig_s['sz'], dchi2_s)

    # Conversion: compute dchi2 and λ on full data (before subsample)
    dchi2_c, _ = endcap_sim.compute_dchi2_endcap(conv)
    lam_c = mtag_v24.lam(conv['zm'], conv['sz'], dchi2_c)

    rows = []
    for nc in N_CONV_GRID:
        conv_s, _ = endcap_sim.subsample(conv, nc)
        # Untrimmed
        best_u = scan_with_window(sig_s, conv_s, lam_s, lam_c)

        # ── v2.8 standard: trim BOTH signal and conversion ──
        mask_c, _, _, _, _ = apply_trim(lam_c, conv_s['base'])
        mask_s, _, _, _, _ = apply_trim(lam_s, sig_s['base'])
        sig_t = dict(sig_s)
        sig_t['base'] = sig_s['base'] & ~mask_s
        conv_t = dict(conv_s)
        conv_t['base'] = conv_s['base'] & ~mask_c
        best_t = scan_with_window(sig_t, conv_t, lam_s, lam_c)
        # Normalise by pre-trimming S0 (not trimmed S0)
        # best_t['limit'] already includes mass window from scan_with_window
        S0_pre = sig_s['w'][sig_s['base']].sum()
        lim_pre = endcap_sim.upper_limit(S0_pre, 0)
        deg_trim_std = float(best_t['limit'] / lim_pre) if lim_pre > 0 else best_t['deg']

        # ── Supplementary: conversion-only trim ──
        conv_t2 = dict(conv_s)
        conv_t2['base'] = conv_s['base'] & ~mask_c
        best_t2 = scan_with_window(sig_s, conv_t2, lam_s, lam_c)

        rows.append(dict(
            seed_i     = i,
            n_conv_cap = nc,
            n_base     = int(conv_s['base'].sum()),
            deg_untrim = round(best_u['deg'], 6),
            deg_trim   = round(deg_trim_std, 6),     # v2.8 standard
            deg_trim_conv_only = round(best_t2['deg'], 6),  # supplementary
        ))

    dt = time.time() - t0
    print(f"  Inv C seed {i}: {dt:.1f}s")
    return rows


# ════════════════════════════════════════════════════════════
# Prediction evaluation
# ════════════════════════════════════════════════════════════

def evaluate_predictions(results_ab, results_c):
    """Evaluate 9 preregistered predictions.  Returns list of dicts."""

    # Collect arrays
    f_inter  = np.array([r['f_inter']     for r in results_ab])
    fi_all   = np.array([r['f_inter_all'] for r in results_ab])
    f_B_rem  = np.array([r['f_B_rem']     for r in results_ab])
    enrich   = np.array([r['enrichment']  for r in results_ab])

    mean_fi   = float(f_inter.mean())
    cv_fi     = None if f_inter.mean() == 0 else float(f_inter.std() / f_inter.mean())
    mean_fia  = float(fi_all.mean())
    mean_fBr  = float(f_B_rem.mean())
    cv_fBr    = float(f_B_rem.std() / f_B_rem.mean()) if f_B_rem.mean() > 0 else np.inf
    mean_enr  = float(enrich.mean())

    # ── Investigation C: aggregate by N_conv ──
    c_data = {}
    for row in results_c:
        nc = row['n_conv_cap']
        c_data.setdefault(nc, {'u': [], 't': []})
        c_data[nc]['u'].append(row['deg_untrim'])
        c_data[nc]['t'].append(row['deg_trim'])

    cv_u, cv_t = {}, {}
    for nc in sorted(c_data):
        arr_u = np.array(c_data[nc]['u'])
        arr_t = np.array(c_data[nc]['t'])
        cv_u[nc] = float(arr_u.std() / arr_u.mean()) if arr_u.mean() > 0 else 0.0
        cv_t[nc] = float(arr_t.std() / arr_t.mean()) if arr_t.mean() > 0 else 0.0

    ns = sorted(cv_u.keys())
    n_lo, n_hi = ns[0], ns[-1]
    cv_ratio_n1 = cv_u[n_hi] / cv_u[n_lo] if cv_u[n_lo] > 0 else 0.0
    benefit_50k = cv_u[n_hi] / cv_t[n_hi] if cv_t[n_hi] > 0 else np.inf
    cv_trim_max = max(cv_t[nc] for nc in ns)

    preds = [
        dict(id='Z1', desc='Inter-band vertices dominate removed set',
             criterion='Mean f_inter > 0.5', tier='Core',
             value=round(mean_fi, 4),
             detail=f'Mean f_inter = {mean_fi:.4f}',
             result='CONFIRMED' if mean_fi > 0.5 else 'REFUTED'),

        dict(id='Z2', desc='Inter-band enrichment above baseline',
             criterion='f_inter(removed) > f_inter(all)', tier='Core',
             value=round(mean_fi - mean_fia, 4),
             detail=f'f_inter(rem) = {mean_fi:.4f}, f_inter(all) = {mean_fia:.4f}',
             result='CONFIRMED' if mean_fi > mean_fia else 'REFUTED'),

        dict(id='Z3', desc='f_inter consistent across seeds',
             criterion='CV(f_inter) < 20%', tier='Secondary',
             value=None,  # 0/0 undefined: all values are zero
             detail='Not evaluable — zero mean',
             result='NOT EVALUABLE'),

        dict(id='B1', desc='Trimming removes majority of background',
             criterion='Mean f_B,rem > 0.5', tier='Core',
             value=round(mean_fBr, 4),
             detail=f'Mean f_B,rem = {mean_fBr:.4f}',
             result='CONFIRMED' if mean_fBr > 0.5 else 'REFUTED'),

        dict(id='B2', desc='B-contributors enriched in removed set',
             criterion='Mean enrichment > 1', tier='Derived',
             value=round(mean_enr, 2),
             detail=f'Mean enrichment = {mean_enr:.1f}×',
             result='CONFIRMED' if mean_enr > 1 else 'REFUTED'),

        dict(id='B3', desc='B-elimination fraction consistent',
             criterion='CV(f_B,rem) < 20%', tier='Secondary',
             value=round(cv_fBr * 100, 2),
             detail=f'CV(f_B,rem) = {cv_fBr*100:.2f}%',
             result='CONFIRMED' if cv_fBr < 0.20 else 'REFUTED'),

        dict(id='N1', desc='Untrimmed CV does not follow 1/√N',
             criterion='Endpoint CV ratio > 0.25', tier='Diagnostic',
             value=round(cv_ratio_n1, 4),
             detail=f'CV({n_hi})/CV({n_lo}) = {cv_ratio_n1:.4f} (1/√N predicts {np.sqrt(n_lo/n_hi):.4f})',
             result='CONFIRMED' if cv_ratio_n1 > 0.25 else 'REFUTED'),

        dict(id='N2', desc='Trimming benefit persists at large N',
             criterion='CV(untrim)/CV(trim) > 5 at 50k', tier='Diagnostic',
             value=round(benefit_50k, 2),
             detail=f'Benefit ratio at 50k = {benefit_50k:.1f}',
             result='CONFIRMED' if benefit_50k > 5 else 'REFUTED'),

        dict(id='N3', desc='Trimmed CV stable across N_conv',
             criterion='CV(trimmed) < 1% at all N', tier='Secondary',
             value=round(cv_trim_max * 100, 2),
             detail=f'Max CV(trimmed) = {cv_trim_max*100:.2f}% (at N={ns[np.argmax([cv_t[nc] for nc in ns])]})',
             result='CONFIRMED' if cv_trim_max < 0.01 else 'REFUTED'),
    ]

    return preds, dict(cv_u=cv_u, cv_t=cv_t)


# ════════════════════════════════════════════════════════════
# Figure generation
# ════════════════════════════════════════════════════════════

def generate_figures(results_ab, results_c, predictions, cv_data, rep_data):
    """Generate 5 colorful post-registration figures."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib import ticker

    # ── Colour palette ──
    C = dict(
        sensor   = '#3B82F6',   # blue
        service  = '#F59E0B',   # amber
        near     = '#60A5FA',   # light blue
        inter    = '#EF4444',   # red / coral
        all_conv = '#D1D5DB',   # grey-300
        untrim   = '#EF4444',   # red
        trim     = '#10B981',   # emerald
        ref_line = '#9CA3AF',   # grey-400
        confirm  = '#10B981',   # green
        refute   = '#EF4444',   # red
        derived  = '#8B5CF6',   # violet
        bg       = '#FFFFFF',
        text     = '#1F2937',
        grid     = '#E5E7EB',
        accent   = '#6366F1',   # indigo
        gold     = '#F59E0B',
        pink     = '#EC4899',
    )

    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': 10,
        'axes.facecolor': C['bg'],
        'figure.facecolor': C['bg'],
        'axes.edgecolor': C['grid'],
        'axes.grid': True,
        'grid.color': C['grid'],
        'grid.alpha': 0.5,
        'text.color': C['text'],
    })

    figs = []

    # ────────────────────────────────────────────────
    # FIG 1 : z-Distribution of removed vertices
    # ────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 5))
    zm_all  = rep_data['zm_all_base']
    zm_rem  = rep_data['zm_removed']
    nb_flag = rep_data['near_band']

    bins = np.linspace(200, 2500, 200)
    ax.hist(zm_all, bins=bins, color=C['all_conv'], alpha=0.6, label='All base conv.', zorder=1)
    ax.hist(zm_rem[~nb_flag], bins=bins, color=C['inter'], alpha=0.85,
            label=f'Removed: inter-band ({(~nb_flag).sum()})', zorder=3)
    ax.hist(zm_rem[nb_flag], bins=bins, color=C['near'], alpha=0.85,
            label=f'Removed: near-band ({nb_flag.sum()})', zorder=3)

    ymax = ax.get_ylim()[1]
    for j, z in enumerate(BAND_Z):
        hw = BAND_HW[j]
        c = C['sensor'] if IS_SENSOR[j] else C['service']
        ax.add_patch(Rectangle((z - hw, 0), 2 * hw, ymax, alpha=0.12, color=c,
                                zorder=0, linewidth=0))
        ax.axvline(z, color=c, alpha=0.35, lw=0.7, zorder=0)

    ax.set_xlabel('Measured vertex z  [mm]', fontsize=11)
    ax.set_ylabel('Vertices per bin', fontsize=11)
    ax.set_title('Investigation A — z-Distribution of Removed Vertices (seed 50)',
                 fontsize=13, fontweight='bold', color=C['accent'])
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

    # Annotation
    fi = rep_data['zm_removed']
    f_inter_seed = float((~nb_flag).sum() / len(nb_flag)) if len(nb_flag) > 0 else 0
    ax.text(0.02, 0.95, f'd_band = {D_BAND:.1f} mm\n'
            f'f_inter = {f_inter_seed:.3f}\n'
            f'floor-applied: {rep_data["floor_applied"].sum()}/{len(nb_flag)}',
            transform=ax.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#F0F4FF', edgecolor=C['accent'],
                      alpha=0.9))

    # Sensor / service legend
    from matplotlib.patches import Patch
    legend2 = ax.legend(handles=[Patch(facecolor=C['sensor'], alpha=0.3, label='Sensor disk'),
                                  Patch(facecolor=C['service'], alpha=0.3, label='Service band')],
                         loc='upper center', fontsize=8, ncol=2, framealpha=0.8)
    ax.add_artist(legend2)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

    fig.tight_layout()
    p = os.path.join(_DIR, 'fig_inv_a_z_distribution.png')
    fig.savefig(p, dpi=200, bbox_inches='tight')
    figs.append(p)
    plt.close(fig)

    # ────────────────────────────────────────────────
    # FIG 2 : f_inter across 50 seeds
    # ────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={'width_ratios': [2, 1]})

    fi_arr  = np.array([r['f_inter'] for r in results_ab])
    fia_arr = np.array([r['f_inter_all'] for r in results_ab])
    seeds_x = np.array([r['seed_i'] for r in results_ab])

    ax = axes[0]
    ax.scatter(seeds_x, fi_arr, c=C['inter'], s=50, zorder=3, alpha=0.8, edgecolors='white',
               linewidth=0.5, label='f_inter (removed)')
    ax.scatter(seeds_x, fia_arr, c=C['near'], s=30, marker='D', zorder=2, alpha=0.6,
               edgecolors='white', linewidth=0.5, label='f_inter (all conv.)')
    ax.axhline(0.5, color=C['gold'], ls='--', lw=1.5, label='Z1 threshold (0.5)')
    ax.set_xlabel('Seed index i', fontsize=11)
    ax.set_ylabel('f_inter', fontsize=11)
    ax.set_title('Z-Distribution: f_inter Across 50 Seeds',
                 fontsize=12, fontweight='bold', color=C['accent'])
    ax.legend(fontsize=9, loc='lower right', framealpha=0.9)

    ax2 = axes[1]
    bp = ax2.boxplot([fi_arr, fia_arr], widths=0.5, patch_artist=True,
                      tick_labels=['Removed', 'All conv.'],
                      medianprops=dict(color=C['text'], lw=2))
    bp['boxes'][0].set_facecolor(C['inter'])
    bp['boxes'][0].set_alpha(0.4)
    bp['boxes'][1].set_facecolor(C['near'])
    bp['boxes'][1].set_alpha(0.4)
    ax2.axhline(0.5, color=C['gold'], ls='--', lw=1.5)
    ax2.set_ylabel('f_inter', fontsize=11)
    ax2.set_title('Distribution', fontsize=12, fontweight='bold', color=C['accent'])

    # Annotate
    mu = fi_arr.mean()
    if mu > 0:
        cv_text = f'CV = {fi_arr.std()/mu*100:.1f}%'
    else:
        cv_text = 'CV undefined (mean = 0)'
    ax2.text(0.5, 0.02, f'Mean = {mu:.4f}\n{cv_text}',
             transform=ax2.transAxes, fontsize=9, ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#F0FFF0', edgecolor=C['trim']))

    fig.suptitle('Investigation A — Inter-Band Fraction (Z1, Z2, Z3)',
                 fontsize=14, fontweight='bold', color=C['accent'], y=1.02)
    fig.tight_layout()
    p = os.path.join(_DIR, 'fig_inv_a_f_inter.png')
    fig.savefig(p, dpi=200, bbox_inches='tight')
    figs.append(p)
    plt.close(fig)

    # ────────────────────────────────────────────────
    # FIG 3 : Investigation B — Background Elimination
    # ────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    fBr = np.array([r['f_B_rem'] for r in results_ab])
    enr = np.array([r['enrichment'] for r in results_ab])
    ffl = np.array([r['f_floor_B'] for r in results_ab])

    # Panel a: f_B,rem
    ax = axes[0]
    ax.hist(fBr, bins=20, color=C['trim'], alpha=0.7, edgecolor='white', lw=0.8)
    ax.axvline(0.5, color=C['gold'], ls='--', lw=2, label='B1 threshold (0.5)')
    ax.axvline(fBr.mean(), color=C['accent'], ls='-', lw=2, label=f'Mean = {fBr.mean():.4f}')
    ax.set_xlabel('f_B,rem', fontsize=11)
    ax.set_ylabel('Seeds', fontsize=11)
    ax.set_title('B-Elimination Fraction', fontsize=12, fontweight='bold', color=C['accent'])
    ax.legend(fontsize=9, framealpha=0.9)

    # Panel b: enrichment
    ax = axes[1]
    ax.hist(enr, bins=20, color=C['derived'], alpha=0.7, edgecolor='white', lw=0.8)
    ax.axvline(1.0, color=C['gold'], ls='--', lw=2, label='B2 threshold (1.0)')
    ax.axvline(enr.mean(), color=C['accent'], ls='-', lw=2, label=f'Mean = {enr.mean():.1f}×')
    ax.set_xlabel('Enrichment ratio', fontsize=11)
    ax.set_ylabel('Seeds', fontsize=11)
    ax.set_title('B-Contributor Enrichment', fontsize=12, fontweight='bold', color=C['derived'])
    ax.legend(fontsize=9, framealpha=0.9)

    # Panel c: floor fraction among removed B-contributors
    ax = axes[2]
    ax.hist(ffl, bins=20, color=C['pink'], alpha=0.7, edgecolor='white', lw=0.8)
    ax.axvline(ffl.mean(), color=C['accent'], ls='-', lw=2, label=f'Mean = {ffl.mean():.3f}')
    ax.set_xlabel('Floor fraction (removed B-contrib.)', fontsize=11)
    ax.set_ylabel('Seeds', fontsize=11)
    ax.set_title('Floor-Applied Linkage', fontsize=12, fontweight='bold', color=C['pink'])
    ax.legend(fontsize=9, framealpha=0.9)

    fig.suptitle('Investigation B — Background Elimination by Trimming (B1, B2, B3)',
                 fontsize=14, fontweight='bold', color=C['accent'], y=1.02)
    fig.tight_layout()
    p = os.path.join(_DIR, 'fig_inv_b_background.png')
    fig.savefig(p, dpi=200, bbox_inches='tight')
    figs.append(p)
    plt.close(fig)

    # ────────────────────────────────────────────────
    # FIG 4 : Investigation C — N_conv Scaling
    # ────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    ns = sorted(cv_data['cv_u'].keys())
    cvu = [cv_data['cv_u'][n] * 100 for n in ns]
    cvt = [cv_data['cv_t'][n] * 100 for n in ns]

    # 1/√N reference (normalised to match CV at smallest N)
    ref = [cvu[0] * np.sqrt(ns[0] / n) for n in ns]

    ax = axes[0]
    ax.plot(ns, cvu, 'o-', color=C['untrim'], lw=2.5, ms=9, label='Untrimmed CV',
            zorder=3, markeredgecolor='white', markeredgewidth=1.5)
    ax.plot(ns, cvt, 's-', color=C['trim'], lw=2.5, ms=9, label='Trimmed CV',
            zorder=3, markeredgecolor='white', markeredgewidth=1.5)
    ax.plot(ns, ref, '--', color=C['ref_line'], lw=1.5, label='1/√N reference', zorder=2)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('N_conv', fontsize=11)
    ax.set_ylabel('CV  [%]', fontsize=11)
    ax.set_title('CV vs N_conv', fontsize=12, fontweight='bold', color=C['accent'])
    ax.legend(fontsize=9, framealpha=0.9)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.set_xticks(ns)

    # Panel b: benefit ratio
    ax = axes[1]
    benefit = [cvu[j] / cvt[j] if cvt[j] > 0 else 0 for j in range(len(ns))]
    bars = ax.bar(range(len(ns)), benefit, color=[C['accent']] * len(ns), alpha=0.75,
                  edgecolor='white', linewidth=1.5)
    ax.set_xticks(range(len(ns)))
    ax.set_xticklabels([f'{n//1000}k' for n in ns], fontsize=10)
    ax.axhline(5.0, color=C['gold'], ls='--', lw=2, label='N2 threshold (5.0)')
    ax.set_xlabel('N_conv', fontsize=11)
    ax.set_ylabel('CV(untrim) / CV(trim)', fontsize=11)
    ax.set_title('Trimming Benefit Ratio', fontsize=12, fontweight='bold', color=C['accent'])
    ax.legend(fontsize=9, framealpha=0.9)

    # Annotate bars
    for j, (b, v) in enumerate(zip(bars, benefit)):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3,
                f'{v:.1f}×', ha='center', fontsize=9, fontweight='bold', color=C['text'])

    fig.suptitle('Investigation C — N_conv Scaling (N1, N2, N3)',
                 fontsize=14, fontweight='bold', color=C['accent'], y=1.02)
    fig.tight_layout()
    p = os.path.join(_DIR, 'fig_inv_c_scaling.png')
    fig.savefig(p, dpi=200, bbox_inches='tight')
    figs.append(p)
    plt.close(fig)

    # ────────────────────────────────────────────────
    # FIG 5 : Prediction Scorecard
    # ────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')

    n_pred = len(predictions)
    cols = ['ID', 'Description', 'Criterion', 'Tier', 'Measured', 'Result']
    col_x = [0.02, 0.08, 0.38, 0.62, 0.72, 0.88]
    header_y = 0.94
    row_h = 0.085

    # Header
    for cx, label in zip(col_x, cols):
        ax.text(cx, header_y, label, fontsize=10, fontweight='bold', color=C['bg'],
                transform=ax.transAxes, va='center')
    ax.add_patch(plt.Rectangle((0.01, header_y - 0.025), 0.98, 0.05,
                                transform=ax.transAxes, facecolor=C['accent'],
                                clip_on=False, zorder=2))

    n_confirmed = sum(1 for p in predictions if p['result'] == 'CONFIRMED')

    for j, pred in enumerate(predictions):
        y = header_y - (j + 1) * row_h
        bg_c = '#F0FFF0' if pred['result'] == 'CONFIRMED' else ('#FFFFF0' if pred['result'] == 'NOT EVALUABLE' else '#FFF0F0')
        ax.add_patch(plt.Rectangle((0.01, y - 0.03), 0.98, row_h - 0.005,
                                    transform=ax.transAxes, facecolor=bg_c,
                                    edgecolor=C['grid'], lw=0.5, clip_on=False))
        val_str = 'N/A' if pred['value'] is None else str(pred['value'])
        vals = [pred['id'], pred['desc'][:35], pred['criterion'],
                pred['tier'], val_str, pred['result']]
        for cx, v in zip(col_x, vals):
            clr = C['confirm'] if v == 'CONFIRMED' else (C['refute'] if v == 'REFUTED' else (C['gold'] if v == 'NOT EVALUABLE' else C['text']))
            fw = 'bold' if cx in (col_x[0], col_x[-1]) else 'normal'
            ax.text(cx, y + 0.01, v, fontsize=8.5, color=clr, fontweight=fw,
                    transform=ax.transAxes, va='center')

    ax.set_title(f'v2.9 Prediction Scorecard  —  {n_confirmed}/{n_pred} CONFIRMED',
                 fontsize=14, fontweight='bold', color=C['accent'], pad=20)

    # Footer
    core = [p for p in predictions if p['tier'] == 'Core']
    n_core_conf = sum(1 for p in core if p['result'] == 'CONFIRMED')
    strength = 'STRONG' if n_core_conf == 3 else ('PARTIAL' if n_core_conf >= 1 else 'WEAK')
    s_color = C['confirm'] if strength == 'STRONG' else (C['gold'] if strength == 'PARTIAL' else C['refute'])
    ax.text(0.5, 0.02, f'Overall: {strength} support ({n_core_conf}/3 core predictions confirmed)',
            transform=ax.transAxes, fontsize=11, fontweight='bold', color=s_color,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8F8FF', edgecolor=s_color, alpha=0.9))

    fig.tight_layout()
    p = os.path.join(_DIR, 'fig_prediction_scorecard.png')
    fig.savefig(p, dpi=200, bbox_inches='tight')
    figs.append(p)
    plt.close(fig)

    return figs


# ════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("v2.9 Post-Registration: Background-Focused Diagnostics")
    print(f"Config: E3 (f = 0.25), m = 17 MeV, 17-band geometry")
    print(f"d_band = {D_BAND} mm (half minimum inter-band gap)")
    print(f"Seeds: {SEEDS[0]}–{SEEDS[-1]} (Inv A&B), {INV_C_SEEDS[0]}–{INV_C_SEEDS[-1]} (Inv C)")
    print("=" * 70)

    # ── 1. Run Investigations A & B  (50 seeds) ──
    print("\n▶ Investigation A & B: 50-seed ensemble")
    results_ab = []
    rep_data = None
    t_total = time.time()

    for idx, i in enumerate(SEEDS):
        save_rep = (i == SEEDS[0])    # save arrays for first seed
        r, rd = run_seed_ab(i, save_rep=save_rep)
        results_ab.append(r)
        if rd is not None:
            rep_data = rd
        print(f"  [{idx+1:2d}/50]  seed {i}: deg_untrim={r['deg_untrim']:.4f}  "
              f"deg_trim={r['deg_trim']:.4f}  f_inter={r['f_inter']:.3f}  "
              f"f_B_rem={r['f_B_rem']:.3f}  ({r['time_s']:.1f}s)")

    dt_ab = time.time() - t_total
    print(f"  → Inv A&B done in {dt_ab:.0f}s")

    # ── 2. Run Investigation C  (10 seeds × 5 N_conv) ──
    print("\n▶ Investigation C: N_conv scaling (10 seeds × 5 caps)")
    results_c = []
    t_c = time.time()

    for i in INV_C_SEEDS:
        rows = run_inv_c_seed(i)
        results_c.extend(rows)

    dt_c = time.time() - t_c
    print(f"  → Inv C done in {dt_c:.0f}s")

    # ── 3. Evaluate predictions ──
    print("\n▶ Evaluating 9 predictions...")
    predictions, cv_data = evaluate_predictions(results_ab, results_c)

    for p in predictions:
        status = '✓' if p['result'] == 'CONFIRMED' else ('?' if p['result'] == 'NOT EVALUABLE' else '✗')
        print(f"  {status} {p['id']} ({p['tier']}): {p['result']}  —  {p['detail']}")

    core = [p for p in predictions if p['tier'] == 'Core']
    n_core = sum(1 for p in core if p['result'] == 'CONFIRMED')
    print(f"\n  Core predictions: {n_core}/3 CONFIRMED")
    print(f"  Overall: {'STRONG' if n_core == 3 else ('PARTIAL' if n_core >= 1 else 'WEAK')} support")

    # ── 4. Save results ──
    out = dict(
        config = dict(m_alp_GeV=M_ALP, f_mat=0.25, eta_ref=2.0,
                       n_bands=17, d_band_mm=D_BAND, k_trim=K_TRIM,
                       n_seeds_ab=len(SEEDS), n_seeds_c=len(INV_C_SEEDS),
                       n_conv_grid=N_CONV_GRID),
        results_ab   = results_ab,
        results_c    = results_c,
        predictions  = predictions,
        cv_scaling   = cv_data,
        summary = dict(
            mean_deg_untrim = round(np.mean([r['deg_untrim'] for r in results_ab]), 6),
            cv_deg_untrim   = round(np.std([r['deg_untrim'] for r in results_ab]) /
                                    np.mean([r['deg_untrim'] for r in results_ab]) * 100, 2),
            mean_deg_trim   = round(np.mean([r['deg_trim'] for r in results_ab]), 6),
            cv_deg_trim     = round(np.std([r['deg_trim'] for r in results_ab]) /
                                    np.mean([r['deg_trim'] for r in results_ab]) * 100, 2),
            n_core_confirmed = n_core,
            overall_strength = 'STRONG' if n_core == 3 else ('PARTIAL' if n_core >= 1 else 'WEAK'),
            runtime_s       = round(time.time() - t_total, 1),
        ),
    )

    json_path = os.path.join(_DIR, 'v29_postreg_results.json')
    with open(json_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  Saved: {json_path}")

    # Save representative arrays for figures
    npz_path = os.path.join(_DIR, 'v29_postreg_data.npz')
    np.savez_compressed(npz_path, **{k: v for k, v in rep_data.items()})
    print(f"  Saved: {npz_path}")

    # ── 5. Generate figures ──
    print("\n▶ Generating figures...")
    fig_paths = generate_figures(results_ab, results_c, predictions, cv_data, rep_data)
    for fp in fig_paths:
        print(f"  Saved: {os.path.basename(fp)}")

    total = time.time() - t_total
    print(f"\n{'=' * 70}")
    print(f"All done in {total:.0f}s.  {sum(1 for p in predictions if p['result']=='CONFIRMED')}/9 predictions evaluated.")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
