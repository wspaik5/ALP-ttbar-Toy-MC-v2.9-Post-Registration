#!/usr/bin/env python3
"""Generate colorful motivational figures for v2.9 preregistration from v2.8 data.

Produces 6 figures illustrating WHY background-focused diagnostics are needed.
"""

import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
V28_JSON = os.path.join(_SCRIPT_DIR, "v28_results.json")

with open(V28_JSON) as f:
    data = json.load(f)

seeds_17 = [s for s in data if abs(s["mass"] - 0.017) < 0.001]
deg_untrim = np.array([s["deg_untrim"] for s in seeds_17])
deg_trim   = np.array([s["deg_trim"]   for s in seeds_17])
deg_hv     = np.array([s["deg_hv"]     for s in seeds_17])
S_untrim   = np.array([s["S_untrim"]   for s in seeds_17])
B_untrim   = np.array([s["B_untrim"]   for s in seeds_17])
S_trim     = np.array([s["S_trim"]     for s in seeds_17])
B_trim     = np.array([s["B_trim"]     for s in seeds_17])
S_hv       = np.array([s["S_hv"]       for s in seeds_17])
B_hv       = np.array([s["B_hv"]       for s in seeds_17])
lim_untrim = np.array([s["lim_untrim"] for s in seeds_17])
lim_trim   = np.array([s["lim_trim"]   for s in seeds_17])
lim_hv     = np.array([s["lim_hv"]     for s in seeds_17])
delta_deg  = deg_untrim - deg_trim

# ── Color palette ──
C_BLUE    = "#2980b9"
C_DBLUE   = "#1a5276"
C_ORANGE  = "#e67e22"
C_RED     = "#e74c3c"
C_GREEN   = "#27ae60"
C_PURPLE  = "#8e44ad"
C_TEAL    = "#16a085"
C_GOLD    = "#f39c12"
C_PINK    = "#e91e63"
C_SLATE   = "#34495e"
BG_LIGHT  = "#fafcfe"


def style_ax(ax, title, xlabel, ylabel):
    ax.set_facecolor(BG_LIGHT)
    ax.set_title(title, fontsize=12, fontweight="bold", color=C_SLATE, pad=12)
    ax.set_xlabel(xlabel, fontsize=10, color=C_SLATE)
    ax.set_ylabel(ylabel, fontsize=10, color=C_SLATE)
    ax.tick_params(colors=C_SLATE, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#bdc3c7")
        spine.set_linewidth(0.8)
    ax.grid(True, alpha=0.3, linestyle="--", color="#bdc3c7")


# ════════════════════════════════════════════
# Fig 1: Per-Seed Improvement Gradient Bar
# ════════════════════════════════════════════
fig1, ax1 = plt.subplots(figsize=(7, 4))
fig1.patch.set_facecolor("white")

norm = plt.Normalize(delta_deg.min(), delta_deg.max())
cmap = plt.cm.viridis
colors_bar = cmap(norm(delta_deg))

bars = ax1.bar(np.arange(50), delta_deg, color=colors_bar, width=0.85,
               edgecolor="white", linewidth=0.3)
ax1.axhline(y=np.mean(delta_deg), color=C_ORANGE, linewidth=2, linestyle="--", zorder=5,
            label=f"Mean Δdeg = {np.mean(delta_deg):.4f}")

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig1.colorbar(sm, ax=ax1, pad=0.02, aspect=30, shrink=0.85)
cbar.set_label("Improvement magnitude", fontsize=9, color=C_SLATE)
cbar.ax.tick_params(labelsize=8, colors=C_SLATE)

ax1.text(0.98, 0.95, "50/50 seeds improved\nAll Δdeg > 0",
         transform=ax1.transAxes, fontsize=9, va="top", ha="right", fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#e8f8f5", edgecolor=C_TEAL, alpha=0.95))

style_ax(ax1, "Per-Seed Improvement from Trimming at 17 MeV (v2.8)",
         "Seed Index (i = 50–99)", "Δdeg = deg(untrimmed) − deg(trimmed)")
ax1.legend(fontsize=9, loc="upper left", framealpha=0.9)
ax1.set_xlim(-1, 50)
fig1.tight_layout()
fig1.savefig(os.path.join(_SCRIPT_DIR, "fig1_per_seed_delta_deg.png"), dpi=200, facecolor="white")
plt.close(fig1)
print("  → fig1_per_seed_delta_deg.png")


# ════════════════════════════════════════════
# Fig 2: Degradation Ratio Violin + Strip
# ════════════════════════════════════════════
fig2, ax2 = plt.subplots(figsize=(7, 4.5))
fig2.patch.set_facecolor("white")

datasets = [deg_untrim, deg_trim, deg_hv]
labels = ["Untrimmed\nTag", "Trimmed Tag\n(k = 1%)", "HV\n(Material Veto)"]
vcolors = [C_RED, C_BLUE, C_GREEN]

parts = ax2.violinplot(datasets, positions=[0, 1, 2], showmeans=False,
                       showmedians=False, showextrema=False)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(vcolors[i])
    pc.set_alpha(0.25)
    pc.set_edgecolor(vcolors[i])
    pc.set_linewidth(1.5)

# Strip plot (jittered dots)
for i, (d, c) in enumerate(zip(datasets, vcolors)):
    jitter = np.random.default_rng(42).uniform(-0.12, 0.12, size=len(d))
    ax2.scatter(np.full_like(d, i) + jitter, d, color=c, alpha=0.5, s=18,
                edgecolors="white", linewidths=0.3, zorder=3)
    ax2.plot(i, np.mean(d), "D", color=c, markersize=10,
             markeredgecolor="white", markeredgewidth=1.5, zorder=5)

cvs = [100*np.std(d)/np.mean(d) for d in datasets]
means = [np.mean(d) for d in datasets]
for i in range(3):
    ax2.text(i, max(datasets[i]) + 0.03, f"CV = {cvs[i]:.2f}%",
             ha="center", fontsize=9, fontweight="bold", color=vcolors[i])
    ax2.text(i, means[i] - 0.055, f"μ = {means[i]:.4f}",
             ha="center", fontsize=8, color=vcolors[i], fontstyle="italic")

ax2.axhline(y=1.0, color=C_SLATE, linewidth=1, linestyle=":", alpha=0.7,
            label="Ideal (deg = 1.0)")

ax2.annotate("v2.9 asks:\nWHICH vertices\ncause this spread?",
             xy=(0, np.mean(deg_untrim)), xytext=(0.6, 1.65),
             fontsize=8.5, fontstyle="italic", color=C_PURPLE, fontweight="bold",
             arrowprops=dict(arrowstyle="fancy", color=C_PURPLE, lw=1.5,
                             connectionstyle="arc3,rad=0.2"),
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f5eef8",
                       edgecolor=C_PURPLE, alpha=0.95))

ax2.set_xticks([0, 1, 2])
ax2.set_xticklabels(labels, fontsize=10)
style_ax(ax2, "Degradation Ratio Distribution at 17 MeV (v2.8, 50 Seeds)",
         "", "Degradation Ratio")
ax2.legend(fontsize=9, loc="upper right", framealpha=0.9)
ax2.set_ylim(0.95, max(deg_untrim) + 0.12)
fig2.tight_layout()
fig2.savefig(os.path.join(_SCRIPT_DIR, "fig2_deg_distribution.png"), dpi=200, facecolor="white")
plt.close(fig2)
print("  → fig2_deg_distribution.png")


# ════════════════════════════════════════════
# Fig 3: Signal vs Background Bar Comparison
# ════════════════════════════════════════════
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(7.5, 4),
                                   gridspec_kw={"width_ratios": [1.6, 1]})
fig3.patch.set_facecolor("white")

methods = ["Untrimmed", "Trimmed\n(k=1%)", "HV\n(Mat. Veto)"]
mean_S = [np.mean(S_untrim), np.mean(S_trim), np.mean(S_hv)]
mean_B = [np.mean(B_untrim), np.mean(B_trim), np.mean(B_hv)]
x = np.arange(3)
bw = 0.35

bars_s = ax3a.bar(x - bw/2, mean_S, bw, label="Signal (S)", color=C_BLUE,
                  edgecolor="white", linewidth=0.5, alpha=0.85)
bars_b = ax3a.bar(x + bw/2, mean_B, bw, label="Background (B)", color=C_RED,
                  edgecolor="white", linewidth=0.5, alpha=0.85)

for bar, v in zip(bars_s, mean_S):
    ax3a.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
              f"{v:.0f}", ha="center", fontsize=8, color=C_BLUE, fontweight="bold")
for bar, v in zip(bars_b, mean_B):
    ax3a.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
              f"{v:.2f}", ha="center", fontsize=8, color=C_RED, fontweight="bold")

ax3a.set_xticks(x)
ax3a.set_xticklabels(methods, fontsize=9)
style_ax(ax3a, "Mean Signal & Background at 17 MeV", "", "Count")
ax3a.legend(fontsize=9, framealpha=0.9)

# Right: S/B ratio (log scale)
sb_ratios = [mean_S[0]/max(mean_B[0], 0.01),
             mean_S[1]/max(mean_B[1], 0.01),
             mean_S[2]/max(mean_B[2], 0.01)]
sb_display = [sb_ratios[0], min(sb_ratios[1], 1e6), sb_ratios[2]]
bar_colors3 = [C_RED, C_BLUE, C_GREEN]

bars_sb = ax3b.bar(x, sb_display, color=bar_colors3, edgecolor="white",
                   linewidth=0.5, alpha=0.85, width=0.6)
ax3b.set_yscale("log")
for bar, v, c in zip(bars_sb, sb_display, bar_colors3):
    label = f"{v:.0f}" if v < 1e5 else "→ ∞"
    ax3b.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.5,
              label, ha="center", fontsize=9, color=c, fontweight="bold")

ax3b.set_xticks(x)
ax3b.set_xticklabels(methods, fontsize=9)
style_ax(ax3b, "S/B Ratio", "", "S / B")

ax3b.annotate("B → 0\nTrimming\neliminates\nbackground",
              xy=(1, sb_display[1]), xytext=(1.8, sb_display[1]/50),
              fontsize=7.5, color=C_PURPLE, fontweight="bold", ha="center",
              arrowprops=dict(arrowstyle="->", color=C_PURPLE, lw=1.2),
              bbox=dict(boxstyle="round,pad=0.3", facecolor="#f5eef8",
                        edgecolor=C_PURPLE, alpha=0.9))

fig3.tight_layout()
fig3.savefig(os.path.join(_SCRIPT_DIR, "fig3_signal_background.png"), dpi=200, facecolor="white")
plt.close(fig3)
print("  → fig3_signal_background.png")


# ════════════════════════════════════════════
# Fig 4: Scatter — Trimmed vs Untrimmed Deg
# ════════════════════════════════════════════
fig4, ax4 = plt.subplots(figsize=(5.5, 5.5))
fig4.patch.set_facecolor("white")

lo, hi = 1.0, max(deg_untrim) * 1.05
ax4.plot([lo, hi], [lo, hi], "--", color=C_SLATE, alpha=0.5, linewidth=1,
         label="Identity line")
ax4.fill_between([lo, hi], [lo, lo], [lo, hi], alpha=0.07, color=C_GREEN,
                 label="Trimmed better")
ax4.fill_between([lo, hi], [lo, hi], [hi, hi], alpha=0.07, color=C_RED,
                 label="Untrimmed better")

scatter = ax4.scatter(deg_untrim, deg_trim, c=delta_deg, cmap="plasma", s=50,
                      edgecolors="white", linewidths=0.5, zorder=3, alpha=0.85)
cbar4 = fig4.colorbar(scatter, ax=ax4, pad=0.02, aspect=30, shrink=0.85)
cbar4.set_label("Improvement Δdeg", fontsize=9, color=C_SLATE)
cbar4.ax.tick_params(labelsize=8, colors=C_SLATE)

ax4.plot(np.mean(deg_untrim), np.mean(deg_trim), "*", color=C_GOLD, markersize=18,
         markeredgecolor=C_SLATE, markeredgewidth=0.8, zorder=6, label="Ensemble mean")

style_ax(ax4, "Trimmed vs Untrimmed Degradation Ratio (17 MeV)",
         "Untrimmed deg", "Trimmed deg")
ax4.set_xlim(1.3, hi)
ax4.set_ylim(1.0, 1.1)
ax4.legend(fontsize=8, loc="upper left", framealpha=0.9)
ax4.set_aspect("auto")
fig4.tight_layout()
fig4.savefig(os.path.join(_SCRIPT_DIR, "fig4_scatter_trim_vs_untrim.png"), dpi=200, facecolor="white")
plt.close(fig4)
print("  → fig4_scatter_trim_vs_untrim.png")


# ════════════════════════════════════════════
# Fig 5: Upper Limit Improvement Waterfall
# ════════════════════════════════════════════
fig5, ax5 = plt.subplots(figsize=(7, 4))
fig5.patch.set_facecolor("white")

sort_idx = np.argsort(lim_untrim)[::-1]
x5 = np.arange(50)

ax5.fill_between(x5, lim_untrim[sort_idx]*1e3, lim_trim[sort_idx]*1e3,
                 alpha=0.3, color=C_ORANGE, label="Improvement region")
ax5.plot(x5, lim_untrim[sort_idx]*1e3, "o-", color=C_RED, markersize=4, linewidth=1.2,
         alpha=0.8, label=f"Untrimmed (mean={np.mean(lim_untrim)*1e3:.3f})")
ax5.plot(x5, lim_trim[sort_idx]*1e3, "s-", color=C_BLUE, markersize=4, linewidth=1.2,
         alpha=0.8, label=f"Trimmed (mean={np.mean(lim_trim)*1e3:.3f})")
ax5.plot(x5, lim_hv[sort_idx]*1e3, "^-", color=C_GREEN, markersize=3, linewidth=0.8,
         alpha=0.6, label=f"HV (mean={np.mean(lim_hv)*1e3:.3f})")

style_ax(ax5, "95% CL Upper Limit per Seed at 17 MeV (Sorted by Untrimmed)",
         "Seed rank (worst → best untrimmed)", "Upper limit (×10⁻³)")
ax5.legend(fontsize=8.5, loc="upper right", framealpha=0.9)
ax5.set_xlim(-1, 50)
fig5.tight_layout()
fig5.savefig(os.path.join(_SCRIPT_DIR, "fig5_upper_limit_waterfall.png"), dpi=200, facecolor="white")
plt.close(fig5)
print("  → fig5_upper_limit_waterfall.png")


# ════════════════════════════════════════════
# Fig 6: 17-Band Geometry Schematic
# ════════════════════════════════════════════
fig6, ax6 = plt.subplots(figsize=(7.5, 3.5))
fig6.patch.set_facecolor("white")
ax6.set_facecolor("#f8f9fa")

# 17-band geometry at η=2.0 (approximate z positions)
sensor_z  = np.array([800, 900, 1050, 1250, 1500, 1750, 2050, 2400, 2800])
service_z = np.array([850, 975, 1150, 1375, 1625, 1900, 2225, 2600])

y_sensor = 0.6
band_hw = 12

for i, z in enumerate(sensor_z):
    rect = FancyBboxPatch((z - band_hw, y_sensor - 0.12), 2*band_hw, 0.24,
                          boxstyle="round,pad=2", facecolor=C_BLUE, alpha=0.8,
                          edgecolor=C_DBLUE, linewidth=1.2)
    ax6.add_patch(rect)
    ax6.text(z, y_sensor, f"S{i+1}", ha="center", va="center", fontsize=7,
             color="white", fontweight="bold")

for i, z in enumerate(service_z):
    rect = FancyBboxPatch((z - band_hw*0.7, 0.35 - 0.09), 2*band_hw*0.7, 0.18,
                          boxstyle="round,pad=2", facecolor=C_ORANGE, alpha=0.7,
                          edgecolor="#d35400", linewidth=1)
    ax6.add_patch(rect)
    ax6.text(z, 0.35, f"M{i+1}", ha="center", va="center", fontsize=6.5,
             color="white", fontweight="bold")

# Inter-band question marks
gap_z = [(sensor_z[i] + service_z[i])/2 for i in range(8)]
for z in gap_z:
    ax6.text(z, 0.1, "?", ha="center", va="center", fontsize=14, color=C_PURPLE,
             fontweight="bold", alpha=0.6)

ax6.axhline(y=0.0, color=C_SLATE, linewidth=0.5, linestyle="-", alpha=0.3)
ax6.text(750, 0.0, "beam axis →", fontsize=7, color=C_SLATE, va="center", fontstyle="italic")

# Conversion vertex scatter
np.random.seed(99)
n_vtx = 40
vtx_z = np.random.uniform(780, 2850, n_vtx)
vtx_y = np.random.uniform(-0.05, 0.05, n_vtx)
all_bands = np.concatenate([sensor_z, service_z])
near_mask = np.array([min(abs(z - all_bands)) < 30 for z in vtx_z])

ax6.scatter(vtx_z[near_mask], vtx_y[near_mask] + 0.85, marker="v", s=25,
            color=C_TEAL, alpha=0.7, edgecolors="white", linewidths=0.3,
            label="Near-band vertex", zorder=4)
ax6.scatter(vtx_z[~near_mask], vtx_y[~near_mask] + 0.85, marker="v", s=25,
            color=C_PINK, alpha=0.7, edgecolors="white", linewidths=0.3,
            label="Inter-band vertex", zorder=4)

ax6.text(1800, 1.05, "Conversion vertices (schematic)",
         ha="center", fontsize=9, color=C_SLATE, fontstyle="italic")

ax6.plot([], [], "s", color=C_BLUE, markersize=8, label="Sensor disk")
ax6.plot([], [], "s", color=C_ORANGE, markersize=8, label="Service band")

ax6.set_xlim(720, 2900)
ax6.set_ylim(-0.15, 1.15)
ax6.set_xlabel("z position (mm, schematic)", fontsize=10, color=C_SLATE)
ax6.set_title("17-Band Endcap Geometry at η = 2.0 — Where Do Removed Vertices Come From?",
              fontsize=11, fontweight="bold", color=C_SLATE, pad=10)
ax6.set_yticks([])
ax6.legend(fontsize=8, loc="lower right", ncol=2, framealpha=0.9)
for spine in ax6.spines.values():
    spine.set_visible(False)
ax6.spines["bottom"].set_visible(True)
ax6.spines["bottom"].set_color("#bdc3c7")

fig6.tight_layout()
fig6.savefig(os.path.join(_SCRIPT_DIR, "fig6_geometry_schematic.png"), dpi=200, facecolor="white")
plt.close(fig6)
print("  → fig6_geometry_schematic.png")


print("\nAll 6 figures generated successfully.")
