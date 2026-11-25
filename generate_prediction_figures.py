#!/usr/bin/env python3
"""Generate three schematic prediction figures for v2.9 preregistration.

These are ILLUSTRATIVE HYPOTHESES, not real data.
Each figure is clearly labelled 'Schematic / Preregistered Hypothesis (Not Data)'.

Fig 7 — Investigation A: z-distribution of removed vertices (Z1, Z2, Z3)
Fig 8 — Investigation B: Background elimination by trimming (B1, B2, B3)
Fig 9 — Investigation C: CV vs N_conv scaling (N1, N2, N3)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.ticker as ticker

# ── Shared style ──
DISCLAIMER = "Schematic / Preregistered Hypothesis (Not Data)"
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'figure.dpi': 180,
})

# 17-band geometry (from frozen/mtag_v24.py)
SENSOR_Z = [230, 300, 450, 620, 820, 1100, 1500, 1900, 2300]
SERVICE_Z = [265, 375, 535, 720, 960, 1300, 1700, 2100]
ALL_BAND_Z = sorted(SENSOR_Z + SERVICE_Z)

# Half-widths
SENSOR_HW = {230: 1.5, 300: 3.0, 450: 3.0, 620: 3.0, 820: 3.5,
             1100: 4.5, 1500: 5.0, 1900: 5.5, 2300: 6.0}
SERVICE_HW = {z: 1.5 for z in SERVICE_Z}


# ════════════════════════════════════════════════════════════════
# Figure 7: Investigation A — z-distribution of removed vertices
# ════════════════════════════════════════════════════════════════
def make_fig7():
    fig, ax = plt.subplots(figsize=(10, 5.5))

    z_lo, z_hi = 750, 2800

    # Draw sensor disk bands (blue)
    for z in SENSOR_Z:
        hw = SENSOR_HW[z]
        rect = FancyBboxPatch((z - hw, 0), 2 * hw, 1.0,
                              boxstyle="round,pad=0.3",
                              facecolor='#3B82F6', alpha=0.7, edgecolor='#1E40AF', lw=1.2)
        ax.add_patch(rect)

    # Draw service material bands (amber)
    for z in SERVICE_Z:
        hw = SERVICE_HW[z]
        rect = FancyBboxPatch((z - hw, 0), 2 * hw, 1.0,
                              boxstyle="round,pad=0.3",
                              facecolor='#F59E0B', alpha=0.7, edgecolor='#B45309', lw=1.2)
        ax.add_patch(rect)

    # Hypothesised removed-vertex density: peaks in inter-band regions
    np.random.seed(42)
    # Near-band vertices (minority in removed set) — small clusters near bands
    near_band_z = []
    for z in ALL_BAND_Z:
        n = np.random.randint(2, 5)
        near_band_z.extend(np.random.normal(z, 3, n))

    # Inter-band vertices (majority in removed set) — scattered between bands
    inter_band_z = []
    gaps = []
    sorted_bands = sorted(ALL_BAND_Z)
    for i in range(len(sorted_bands) - 1):
        gap_lo = sorted_bands[i] + 5
        gap_hi = sorted_bands[i + 1] - 5
        if gap_hi > gap_lo:
            gaps.append((gap_lo, gap_hi))
    # Also edges
    gaps.insert(0, (z_lo, sorted_bands[0] - 5))
    gaps.append((sorted_bands[-1] + 5, z_hi))

    for gap_lo, gap_hi in gaps:
        n = int((gap_hi - gap_lo) / 8)  # density proportional to gap width
        inter_band_z.extend(np.random.uniform(gap_lo, gap_hi, max(n, 3)))

    # Plot removed vertices
    y_near = np.random.uniform(0.15, 0.85, len(near_band_z))
    y_inter = np.random.uniform(0.15, 0.85, len(inter_band_z))

    ax.scatter(inter_band_z, y_inter, c='#EF4444', s=28, alpha=0.8,
               edgecolors='#991B1B', linewidths=0.5, zorder=5,
               label=f'Inter-band removed (predicted majority, n≈{len(inter_band_z)})')
    ax.scatter(near_band_z, y_near, c='#A78BFA', s=28, alpha=0.8,
               edgecolors='#5B21B6', linewidths=0.5, zorder=5,
               label=f'Near-band removed (predicted minority, n≈{len(near_band_z)})')

    # Prediction annotations
    total = len(near_band_z) + len(inter_band_z)
    f_inter = len(inter_band_z) / total
    ax.text(0.5, 1.12, DISCLAIMER,
            transform=ax.transAxes, ha='center', va='bottom',
            fontsize=9, fontstyle='italic', color='#DC2626',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF2F2', edgecolor='#DC2626', alpha=0.9))

    # Prediction box
    pred_text = (f"Prediction Z1: f_inter > 0.5\n"
                 f"(illustrated: f_inter ≈ {f_inter:.2f})\n"
                 f"Prediction Z2: enrichment above baseline")
    ax.text(0.98, 0.95, pred_text, transform=ax.transAxes, ha='right', va='top',
            fontsize=8.5, fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#ECFDF5', edgecolor='#059669', alpha=0.9))

    # Legend for bands
    sensor_patch = mpatches.Patch(color='#3B82F6', alpha=0.7, label='Sensor disk (9)')
    service_patch = mpatches.Patch(color='#F59E0B', alpha=0.7, label='Service band (8)')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=[sensor_patch, service_patch] + handles,
              loc='lower right', fontsize=8, framealpha=0.9)

    ax.set_xlim(z_lo - 20, z_hi + 20)
    ax.set_ylim(-0.1, 1.15)
    ax.set_xlabel('z position [mm]')
    ax.set_yticks([])
    ax.set_ylabel('')
    ax.set_title('Fig 3 — Investigation A: Expected z-Distribution of Removed Vertices\n'
                 '(partial range: 9 of 17 bands visible; full model spans 230–2300 mm)',
                 fontweight='bold', fontsize=11, pad=25)

    plt.tight_layout()
    plt.savefig('fig7_z_distribution_prediction.png', dpi=180, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print("✓ fig7_z_distribution_prediction.png")


# ════════════════════════════════════════════════════════════════
# Figure 8: Investigation B — Background elimination by trimming
# ════════════════════════════════════════════════════════════════
def make_fig8():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5),
                                    gridspec_kw={'width_ratios': [1.2, 1]})

    # --- Left panel: Stacked bar showing B composition before/after trimming ---
    # Hypothesised scenario (schematic)
    # Before trimming: Total B = 100% (B from floor-affected + B from normal)
    # After trimming: f_B,rem ≈ 0.65 of B removed

    categories = ['Before\nTrimming', 'After\nTrimming']
    B_total = 1.0
    f_B_rem = 0.65  # predicted > 0.5

    # Before: all B present
    # After: only (1 - f_B_rem) of B remains
    B_remaining = B_total * (1 - f_B_rem)
    B_removed = B_total * f_B_rem

    # Stacked bars
    bar_width = 0.45
    # Before trimming
    ax1.bar(0, B_total, bar_width, color='#EF4444', alpha=0.8,
            edgecolor='#991B1B', linewidth=1.2, label='B (background)')
    # After trimming — remaining + removed (ghosted)
    ax1.bar(1, B_remaining, bar_width, color='#EF4444', alpha=0.8,
            edgecolor='#991B1B', linewidth=1.2)
    ax1.bar(1, B_removed, bar_width, bottom=B_remaining,
            color='#EF4444', alpha=0.15, edgecolor='#991B1B',
            linewidth=1.2, linestyle='--', label='B removed by trimming')

    # Arrow showing removal
    ax1.annotate('', xy=(1.35, B_remaining + 0.02), xytext=(1.35, B_total - 0.02),
                 arrowprops=dict(arrowstyle='<->', color='#059669', lw=2.5))
    ax1.text(1.55, (B_remaining + B_total) / 2,
             f'f_B,rem ≈ {f_B_rem:.0%}\n(predicted > 50%)',
             ha='left', va='center', fontsize=9, fontweight='bold', color='#059669')

    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(categories, fontsize=10)
    ax1.set_ylabel('Fraction of total background B', fontsize=10)
    ax1.set_ylim(0, 1.25)
    ax1.set_title('B1: Trimming Removes\nMajority of B', fontweight='bold', fontsize=11)
    ax1.legend(loc='upper left', fontsize=8)

    # Percentage labels
    ax1.text(0, B_total + 0.03, '100%', ha='center', va='bottom', fontweight='bold', fontsize=10)
    ax1.text(1, B_remaining + 0.03, f'{(1-f_B_rem):.0%}', ha='center', va='bottom',
             fontweight='bold', fontsize=10, color='#991B1B')

    # --- Right panel: Enrichment concept ---
    # Bar chart: fraction of B-contributors in all vertices vs in removed set
    labels = ['All vertices\n(baseline)', 'Removed set\n(trimmed 2%)']
    # With 2% removal and f_B,rem ≈ 65%, enrichment = 0.65/0.02 = 32.5×
    # B-contributors are ~2% of all vertices, but ~65% of removed set
    baseline_frac = 0.02
    removed_frac = 0.65
    enrichment = removed_frac / baseline_frac

    bars = ax2.bar(labels, [baseline_frac, removed_frac], width=0.5,
                   color=['#94A3B8', '#8B5CF6'], alpha=0.85,
                   edgecolor=['#475569', '#5B21B6'], linewidth=1.2)

    # Enrichment arrow
    ax2.annotate('', xy=(1, removed_frac + 0.01),
                 xytext=(0, baseline_frac + 0.01),
                 arrowprops=dict(arrowstyle='->', color='#DC2626', lw=2.5,
                                 connectionstyle='arc3,rad=0.3'))
    ax2.text(0.5, (baseline_frac + removed_frac) / 2 + 0.04,
             f'Enrichment ≈ {enrichment:.1f}×\n(derived from B1;\nalways > 1 if B1 > 0.5)',
             ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#DC2626')

    ax2.set_ylabel('Fraction that are B-contributors', fontsize=10)
    ax2.set_ylim(0, 0.85)
    ax2.yaxis.set_major_formatter(ticker.PercentFormatter(1.0, decimals=0))
    ax2.set_title('B2 (derived): B-Contributors\nEnriched in Removed Set', fontweight='bold', fontsize=11)

    # Value labels on bars
    for bar, val in zip(bars, [baseline_frac, removed_frac]):
        ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.01,
                 f'{val:.0%}', ha='center', va='bottom', fontweight='bold', fontsize=10)

    # Shared disclaimer
    fig.text(0.5, 1.02, DISCLAIMER,
             ha='center', va='bottom', fontsize=9, fontstyle='italic', color='#DC2626',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF2F2', edgecolor='#DC2626', alpha=0.9))

    fig.suptitle('Fig 4 — Investigation B: Expected Background Elimination by Trimming',
                 fontweight='bold', fontsize=12, y=1.09)

    plt.tight_layout()
    plt.savefig('fig8_background_elimination_prediction.png', dpi=180, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print("✓ fig8_background_elimination_prediction.png")


# ════════════════════════════════════════════════════════════════
# Figure 9: Investigation C — CV vs N_conv scaling
# ════════════════════════════════════════════════════════════════
def make_fig9():
    fig, ax = plt.subplots(figsize=(9, 5.5))

    # Corrected N_conv values
    N_conv = np.array([3125, 6250, 12500, 25000, 50000])

    # Hypothesised CV curves (schematic)
    # Untrimmed: does NOT follow 1/√N — structural floor ~5-7%, weak N dependence
    cv_untrim = np.array([9.5, 8.2, 7.4, 7.0, 6.8])  # structural plateau

    # 1/√N reference: normalised to match untrimmed at N=3125
    cv_ref = cv_untrim[0] * np.sqrt(N_conv[0] / N_conv)

    # Trimmed: stable and low across all N
    cv_trim = np.array([0.15, 0.12, 0.10, 0.09, 0.09])

    # Plot
    ax.plot(N_conv, cv_untrim, 'o-', color='#EF4444', lw=2.5, markersize=9,
            markeredgecolor='#991B1B', markeredgewidth=1.2, label='Untrimmed (predicted)', zorder=5)
    ax.plot(N_conv, cv_ref, 's--', color='#94A3B8', lw=1.8, markersize=7,
            markeredgecolor='#475569', markeredgewidth=1, alpha=0.7,
            label='1/√N reference', zorder=4)
    ax.plot(N_conv, cv_trim, 'D-', color='#3B82F6', lw=2.5, markersize=9,
            markeredgecolor='#1E40AF', markeredgewidth=1.2, label='Trimmed (predicted)', zorder=5)

    # Fill between untrimmed and 1/sqrt(N) to show deviation
    ax.fill_between(N_conv, cv_untrim, cv_ref, alpha=0.12, color='#EF4444',
                    label='Structural excess (N1)')

    # Ratio annotation at N=50000
    ratio_at_50k = cv_untrim[-1] / cv_trim[-1]
    ax.annotate('', xy=(50000, cv_trim[-1]), xytext=(50000, cv_untrim[-1]),
                arrowprops=dict(arrowstyle='<->', color='#059669', lw=2.5))
    ax.text(52000, np.sqrt(cv_untrim[-1] * cv_trim[-1]) * 1.3,
            f'CV ratio ≈ {ratio_at_50k:.0f}×\n(N2: predicted > 5)',
            ha='left', va='center', fontsize=9, fontweight='bold', color='#059669')

    # Prediction boxes
    pred_n1 = "N1: CV(50k)/CV(3125) > 0.25\n(1/√N would give 0.25)"
    n1_ratio = cv_untrim[-1] / cv_untrim[0]
    ax.text(0.02, 0.35, f"{pred_n1}\n(illustrated: {n1_ratio:.2f})",
            transform=ax.transAxes, fontsize=8, fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF7ED', edgecolor='#EA580C', alpha=0.9))

    pred_n3 = "N3: Trimmed CV < 1% at all N"
    ax.text(0.02, 0.12, pred_n3, transform=ax.transAxes, fontsize=8, fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#EFF6FF', edgecolor='#2563EB', alpha=0.9))

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('N_conv (conversion vertices)', fontsize=11)
    ax.set_ylabel('CV of degradation ratio [%]', fontsize=11)

    # Title + disclaimer as suptitle/subtitle
    fig.suptitle('Fig 5 — Investigation C: Expected CV vs N_conv Scaling',
                 fontweight='bold', fontsize=12, y=1.04)
    fig.text(0.5, 1.00, DISCLAIMER,
             ha='center', va='top', fontsize=9, fontstyle='italic', color='#DC2626',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF2F2', edgecolor='#DC2626', alpha=0.9))

    # Custom x-ticks for the exact N_conv values
    ax.set_xticks(N_conv)
    ax.set_xticklabels([f'{n:,}' for n in N_conv], fontsize=9)
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())

    # Y-axis formatting
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{y:.1f}%' if y >= 1 else f'{y:.2f}%'))
    ax.set_ylim(0.05, 15)

    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, which='both')

    plt.tight_layout()
    plt.savefig('fig9_cv_scaling_prediction.png', dpi=180, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print("✓ fig9_cv_scaling_prediction.png")


if __name__ == '__main__':
    make_fig7()
    make_fig8()
    make_fig9()
    print("\nAll prediction figures generated.")
