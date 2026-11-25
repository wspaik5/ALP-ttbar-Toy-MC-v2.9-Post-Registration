#!/usr/bin/env python3
"""Generate v2.9 Post-Registration PDF: Background-Focused Diagnostics — Results."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, Image
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, json

# --- Font setup ---
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DejaVu", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", f"{FONT_DIR}/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-BoldOblique", f"{FONT_DIR}/DejaVuSans-BoldOblique.ttf"))

# --- Colors ---
DARK = HexColor("#1a1a1a")
ACCENT = HexColor("#2c5f8a")
LIGHT_BG = HexColor("#f0f4f8")
BORDER = HexColor("#cccccc")
WHITE = HexColor("#ffffff")
GREY = HexColor("#666666")
GREEN = HexColor("#10B981")
RED = HexColor("#EF4444")
GOLD = HexColor("#F59E0B")

# --- Styles ---
sTitle = ParagraphStyle("Title", fontName="DejaVu-Bold", fontSize=14.5, leading=18,
                        alignment=TA_CENTER, textColor=ACCENT, spaceAfter=3*mm)
sSubtitle = ParagraphStyle("Sub", fontName="DejaVu", fontSize=9, leading=12,
                           alignment=TA_CENTER, textColor=DARK, spaceAfter=2*mm)
sAuthor = ParagraphStyle("Auth", fontName="DejaVu-Oblique", fontSize=8.5, leading=11,
                         alignment=TA_CENTER, textColor=DARK, spaceAfter=1.5*mm)
sDate = ParagraphStyle("Date", fontName="DejaVu", fontSize=8, leading=10,
                       alignment=TA_CENTER, textColor=GREY, spaceAfter=1*mm)
sDOILine = ParagraphStyle("DOILine", fontName="DejaVu", fontSize=7.5, leading=10,
                          alignment=TA_CENTER, textColor=GREY, spaceAfter=4*mm)
sDisclaimer = ParagraphStyle("Disc", fontName="DejaVu-Oblique", fontSize=7, leading=9.5,
                             alignment=TA_JUSTIFY, textColor=GREY, leftIndent=10*mm,
                             rightIndent=10*mm, spaceBefore=2*mm, spaceAfter=4*mm)
sH1 = ParagraphStyle("H1", fontName="DejaVu-Bold", fontSize=12, leading=15,
                     textColor=ACCENT, spaceBefore=6*mm, spaceAfter=3*mm)
sH2 = ParagraphStyle("H2", fontName="DejaVu-Bold", fontSize=10, leading=13,
                     textColor=ACCENT, spaceBefore=4*mm, spaceAfter=2*mm)
sBody = ParagraphStyle("Body", fontName="DejaVu", fontSize=8.5, leading=12,
                       alignment=TA_JUSTIFY, textColor=DARK, spaceAfter=2*mm)
sBodyBold = ParagraphStyle("BodyBold", fontName="DejaVu-Bold", fontSize=8.5, leading=12,
                           alignment=TA_JUSTIFY, textColor=DARK, spaceAfter=2*mm)
sBullet = ParagraphStyle("Bullet", fontName="DejaVu", fontSize=8.5, leading=12,
                         leftIndent=12, textColor=DARK, bulletIndent=4,
                         bulletFontName="DejaVu", bulletFontSize=8.5, spaceAfter=1*mm)
sCode = ParagraphStyle("Code", fontName="DejaVu", fontSize=7.5, leading=10,
                       textColor=DARK, leftIndent=8*mm, spaceAfter=2*mm,
                       backColor=LIGHT_BG)
sFooter = ParagraphStyle("Footer", fontName="DejaVu", fontSize=7, leading=9,
                         alignment=TA_CENTER, textColor=GREY, spaceBefore=3*mm)
sCaption = ParagraphStyle("Caption", fontName="DejaVu-Oblique", fontSize=7.5, leading=10,
                          alignment=TA_CENTER, textColor=DARK, spaceBefore=1*mm, spaceAfter=3*mm)
sFigLabel = ParagraphStyle("FigLabel", fontName="DejaVu-Bold", fontSize=8, leading=10,
                           alignment=TA_CENTER, textColor=ACCENT, spaceBefore=2*mm, spaceAfter=0.5*mm)

# Table styles
sTH = ParagraphStyle("TH", fontName="DejaVu-Bold", fontSize=7.5, leading=10,
                     alignment=TA_CENTER, textColor=WHITE)
sTD = ParagraphStyle("TD", fontName="DejaVu", fontSize=7.5, leading=10,
                     alignment=TA_CENTER, textColor=DARK)
sTDL = ParagraphStyle("TDL", fontName="DejaVu", fontSize=7.5, leading=10,
                      alignment=TA_LEFT, textColor=DARK)
sTDB = ParagraphStyle("TDB", fontName="DejaVu-Bold", fontSize=7.5, leading=10,
                      alignment=TA_CENTER, textColor=DARK)
sTDG = ParagraphStyle("TDG", fontName="DejaVu-Bold", fontSize=7.5, leading=10,
                      alignment=TA_CENTER, textColor=GREEN)
sTDR = ParagraphStyle("TDR", fontName="DejaVu-Bold", fontSize=7.5, leading=10,
                      alignment=TA_CENTER, textColor=RED)

def make_table(header, rows, col_widths):
    all_rows = [header] + rows
    t = Table(all_rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


# Figure paths
_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_A_Z = os.path.join(_DIR, "fig_inv_a_z_distribution.png")
FIG_A_FI = os.path.join(_DIR, "fig_inv_a_f_inter.png")
FIG_B = os.path.join(_DIR, "fig_inv_b_background.png")
FIG_C = os.path.join(_DIR, "fig_inv_c_scaling.png")
FIG_SC = os.path.join(_DIR, "fig_prediction_scorecard.png")

# Load results
with open(os.path.join(_DIR, "v29_postreg_results.json")) as f:
    R = json.load(f)
preds = R['predictions']
summary = R['summary']

# --- Build PDF ---
OUT_PDF = os.path.join(_DIR,
    "ALP-ttbar_Toy-MC_v2.9_Post-Registration_Background-Focused-Diagnostics_2026-11-25.pdf")

doc = SimpleDocTemplate(OUT_PDF, pagesize=A4,
                        topMargin=15*mm, bottomMargin=12*mm,
                        leftMargin=18*mm, rightMargin=18*mm)

story = []

fig_width = 145*mm
fig_height_std = fig_width * (4.0 / 7.0)
fig_height_wide = fig_width * (5.0 / 13.0)

# ============================================================
# TITLE
# ============================================================
story.append(Paragraph(
    "ALP-ttbar Toy MC v2.9 — Post-Registration:<br/>"
    "Background-Focused Diagnostics<br/>"
    "in Displaced Light ALP → e<super>+</super>e<super>−</super>",
    sTitle))
story.append(Paragraph("Won Shik Paik (Independent Researcher, Auckland, New Zealand)", sAuthor))
story.append(Paragraph("2026-11-25", sDate))
story.append(Paragraph(
    "DOI: 10.5281/zenodo.24527398  |  Preregistration: 10.5281/zenodo.24466187  |  Previous: 10.5281/zenodo.24437855 (v2.8 post-reg)",
    sDOILine))

story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT))

story.append(Paragraph(
    "<i>Disclaimer.</i> Independent personal toy study, not affiliated with the authors of "
    "arXiv:2610.38932 (Alimena et al., 2026) or arXiv:2306.08686 (Rygaard et al., 2023), "
    "nor with the CMS, ATLAS, LHCb or ALICE Collaborations or the FCC study. Detector "
    "numbers are assumed; only qualitative trends and ratios are meaningful.",
    sDisclaimer))

# ============================================================
# 1. EXECUTIVE SUMMARY
# ============================================================
story.append(Paragraph("1. Executive Summary", sH1))

n_conf = sum(1 for p in preds if p['result'] == 'CONFIRMED')
n_ref  = sum(1 for p in preds if p['result'] == 'REFUTED')
n_ne   = sum(1 for p in preds if p['result'] == 'NOT EVALUABLE')
core_conf = sum(1 for p in preds if p['tier'] == 'Core' and p['result'] == 'CONFIRMED')

story.append(Paragraph(
    f"This post-registration report presents the results of three diagnostic investigations "
    f"preregistered in DOI 10.5281/zenodo.24466187. Of the 9 preregistered predictions, "
    f"<b>{n_conf} are CONFIRMED, {n_ref} are REFUTED, and {n_ne} is NOT EVALUABLE</b>, "
    f"yielding <b>PARTIAL</b> overall "
    f"support ({core_conf}/3 core predictions confirmed). The Z-distribution predictions "
    f"(Z1–Z2) are refuted and Z3 is not evaluable (zero mean precludes CV), while the "
    f"background-elimination predictions (B1–B3) "
    f"and N-scaling diagnostics (N1–N2) are uniformly confirmed.",
    sBody))

story.append(Paragraph(
    "The central finding is a <b>surprise</b>: the preregistered hypothesis that inter-band "
    "vertices (those between material bands where p<sub>conv</sub> hits the numerical floor) "
    "would dominate the removed set proves entirely wrong. All removed vertices lie near band "
    "centres (f<sub>inter</sub> = 0.000 across all 50 seeds), and none exhibit floor-applied "
    "p<sub>conv</sub>. This refutation is itself informative: it rules out the floor-artefact "
    "mechanism and points toward a question for future investigation: what property of these "
    "near-band vertices produces extreme λ values? One candidate hypothesis is unusual "
    "Δχ<super>2</super> values (poor vertex-fit quality), but this has not yet been tested.",
    sBody))

story.append(Paragraph(
    "Despite the Z-axis surprise, the background-elimination channel yields the strongest "
    "possible results: trimming captures 100% of B-contributing vertices (f<sub>B,rem</sub> = "
    "1.000 across all 50 seeds), with 50-fold enrichment of B-contributors in the removed set. "
    "The N<sub>conv</sub> scaling study shows that the untrimmed CV declined more slowly than "
    "the 1/√N reference over the tested range, and that the trimming benefit grows with sample "
    "size, reaching a 108.6-fold CV reduction at N<sub>conv</sub> = 50,000.",
    sBody))

# ============================================================
# 2. CONFIGURATION
# ============================================================
story.append(Paragraph("2. Configuration", sH1))

story.append(Paragraph(
    "All settings follow the preregistered analysis plan (DOI 10.5281/zenodo.24466187, §3) "
    "without modification. The frozen simulation modules are identical to those archived in "
    "the v2.8 post-registration repository (DOI 10.5281/zenodo.24437855).",
    sBody))

config_header = [Paragraph(h, sTH) for h in ['Parameter', 'Value', 'Note']]
config_rows = [
    [Paragraph('Config', sTD), Paragraph('E3', sTDB), Paragraph('f = 0.25, 9 sensor disks', sTDL)],
    [Paragraph('Geometry', sTD), Paragraph('17-band', sTDB), Paragraph('9 sensor + 8 service bands', sTDL)],
    [Paragraph('m_ALP', sTD), Paragraph('17 MeV', sTDB), Paragraph('Focus mass; 200 MeV not needed (v2.8)', sTDL)],
    [Paragraph('Seeds', sTD), Paragraph('i = 50–99', sTDB), Paragraph('50 seeds, same as v2.8', sTDL)],
    [Paragraph('Inv C seeds', sTD), Paragraph('i = 50–59', sTDB), Paragraph('10 seeds, 5 N_conv caps each', sTDL)],
    [Paragraph('k (trim)', sTD), Paragraph('1%', sTDB), Paragraph('1% from each tail → 2% total removal', sTDL)],
    [Paragraph('d_band', sTD), Paragraph('17.5 mm', sTDB), Paragraph('Half minimum inter-band gap', sTDL)],
    [Paragraph('N_sig cap', sTD), Paragraph('50,000', sTDB), Paragraph('Signal vertices per seed', sTDL)],
    [Paragraph('N_conv cap', sTD), Paragraph('100,000', sTDB), Paragraph('Conversion vertices per seed', sTDL)],
]
story.append(make_table(config_header, config_rows, [30*mm, 25*mm, 110*mm]))

story.append(Spacer(1, 2*mm))

# Frozen file hashes
story.append(Paragraph("2.1 Frozen Module Verification", sH2))
story.append(Paragraph(
    "All three frozen modules were verified against their archived MD5 checksums before execution:",
    sBody))

hash_header = [Paragraph(h, sTH) for h in ['File', 'MD5', 'Frozen Since']]
hash_rows = [
    [Paragraph('endcap_sim.py', sTDL), Paragraph('7daa81b2...8c2d0', sTD), Paragraph('v2.5', sTD)],
    [Paragraph('mtag_v24.py', sTDL), Paragraph('39451a21...54c6e', sTD), Paragraph('v2.4', sTD)],
    [Paragraph('mtag_v22.py', sTDL), Paragraph('a687701e...8c39', sTD), Paragraph('v2.2', sTD)],
]
story.append(make_table(hash_header, hash_rows, [45*mm, 60*mm, 25*mm]))

# ============================================================
# 3. INVESTIGATION A: Z-DISTRIBUTION
# ============================================================
story.append(PageBreak())
story.append(Paragraph("3. Investigation A: z-Distribution of Removed Vertices", sH1))

story.append(Paragraph(
    "Investigation A classifies the 2% of conversion vertices removed by trimming (k = 1% from "
    "each tail of the per-vertex λ distribution) as either <b>near-band</b> (measured z within "
    "d<sub>band</sub> = 17.5 mm of any of the 17 band centres) or <b>inter-band</b> (all others). "
    "The preregistered hypothesis predicted that inter-band vertices — where p<sub>conv</sub>(z) "
    "hits the numerical floor (10<super>−300</super>) — would dominate the removed set, since "
    "floor-applied p<sub>conv</sub> produces extreme λ values via the log(p<sub>sig</sub> / "
    "p<sub>conv</sub>) term.",
    sBody))

story.append(Paragraph("3.1 Result: f<sub>inter</sub> = 0.000 Across All 50 Seeds", sH2))

story.append(Paragraph(
    "The result is a <b>complete refutation</b> of the preregistered hypothesis. Across all 50 "
    "seeds, every removed vertex is classified as near-band; not a single inter-band vertex "
    "appears in the removed set. The f<sub>inter</sub> fraction is identically zero for both "
    "the removed set and the full conversion sample:",
    sBody))

story.append(Paragraph(
    "• <b>f<sub>inter</sub>(removed) = 0.000</b> — all 1,184 removed vertices (representative "
    "seed 50; range across 50 seeds: 1,168–1,192) are "
    "near-band, all lie within 17.5 mm of a sensor disk centre",
    sBullet))
story.append(Paragraph(
    "• <b>f<sub>inter</sub>(all) = 0.000</b> — the entire conversion sample contains zero "
    "inter-band vertices, as all conversions are generated at sensor disk z positions",
    sBullet))
story.append(Paragraph(
    "• <b>Floor-applied count: 0/1,184</b> — no removed vertex has p<sub>conv</sub> at the "
    "numerical floor; the extreme λ values are not driven by the p<sub>conv</sub> denominator",
    sBullet))

story.append(Spacer(1, 2*mm))

story.append(Paragraph("<b>Figure 1.</b> z-Distribution of Removed Vertices (Representative Seed 50)",
             sFigLabel))
story.append(Image(FIG_A_Z, width=fig_width, height=fig_width * 5.0/12.0))
story.append(Paragraph(
    "Figure 1. z-distribution of all base conversion vertices (grey) and removed vertices (blue) "
    "for seed 50. Sensor disk bands (blue shading) and service bands (amber shading) mark the 17 "
    "material-band positions. All 1,184 removed vertices cluster tightly at sensor disk z positions; "
    "no inter-band (red) vertices are visible. The annotation confirms d_band = 17.5 mm, "
    "f_inter = 0.000, and zero floor-applied vertices.",
    sCaption))

story.append(Paragraph("3.2 Physical Interpretation", sH2))

story.append(Paragraph(
    "The f<sub>inter</sub> = 0 result is physically expected in retrospect: the endcap simulation "
    "generates conversions exclusively at the 9 sensor disk z positions (within their half-width "
    "of 1.5–6.0 mm), and vertex z measurement smearing of ~1 mm is far smaller than "
    "d<sub>band</sub> = 17.5 mm. Thus all measured z values remain well within the near-band "
    "zone. The 8 service bands at inter-disk midpoints contribute to the p<sub>conv</sub> model "
    "but host no actual conversions in the simulation.",
    sBody))

story.append(Paragraph(
    "The extreme-λ vertices that trimming removes are therefore near-band vertices, not vertices "
    "at floor-applied p<sub>conv</sub> positions. Since floor = 0 out of 1,184 removed vertices, "
    "this observation is evidence <i>against</i> the floor-artefact hypothesis. What property of "
    "these near-band vertices produces extreme λ remains an open question; one candidate is unusual "
    "Δχ<super>2</super> values (poor vertex-fit quality), but this hypothesis has not been tested.",
    sBody))

story.append(Spacer(1, 2*mm))
story.append(Paragraph("<b>Figure 2.</b> f<sub>inter</sub> Across 50 Seeds (Z1, Z2, Z3)",
             sFigLabel))
story.append(Image(FIG_A_FI, width=fig_width, height=fig_width * 5.0/13.0))
story.append(Paragraph(
    "Figure 2. Left: scatter plot of f_inter for the removed set (red circles) and all conversions "
    "(blue diamonds) across 50 seeds. The Z1 threshold (dashed gold line at 0.5) is never "
    "approached; all points sit at exactly zero. Right: boxplot confirms zero variance. "
    "Z1 and Z2 are refuted. Z3 is not evaluable because the mean inter-band fraction is zero.",
    sCaption))


# ============================================================
# 4. INVESTIGATION B: BACKGROUND ELIMINATION
# ============================================================
story.append(PageBreak())
story.append(Paragraph("4. Investigation B: Background Elimination by Trimming", sH1))

story.append(Paragraph(
    "Investigation B identifies <b>B-contributing vertices</b> — conversion vertices that pass "
    "the optimal untrimmed Tag cut (λ ≥ t<sub>opt</sub>) and the mass window at the untrimmed "
    "optimum — and measures what fraction of them fall within the removal mask. This directly "
    "tests whether trimming's effectiveness comes from eliminating background-driving vertices.",
    sBody))

story.append(Paragraph("4.1 Results", sH2))

# Key metrics
ab_data = R['results_ab']
import numpy as np
fBr_arr = np.array([r['f_B_rem'] for r in ab_data])
enr_arr = np.array([r['enrichment'] for r in ab_data])
n_B_total = sum(r['n_B'] for r in ab_data)
n_B_in_mask_total = sum(r['n_B_in_mask'] for r in ab_data)

story.append(Paragraph(
    f"• <b>B1 (Core): CONFIRMED.</b> f<sub>B,rem</sub> = {fBr_arr.mean():.4f} across all 50 "
    f"seeds — the removal mask captures all {n_B_total:,} B-contributing vertices "
    f"(those passing the untrimmed optimal λ cut and mass window) across the full ensemble. "
    f"This is the strongest possible "
    f"confirmation of the core prediction (threshold: &gt; 0.5).",
    sBullet))
story.append(Paragraph(
    f"• <b>B2 (Derived): CONFIRMED.</b> Mean enrichment = {enr_arr.mean():.1f}× — "
    f"B-contributors are enriched 50-fold in the removed set relative to their baseline "
    f"fraction (enrichment = f<sub>B,rem</sub> / removal_fraction = 1.0 / 0.02 = 50). "
    f"The preregistered threshold was &gt; 1.",
    sBullet))
story.append(Paragraph(
    f"• <b>B3 (Secondary): CONFIRMED.</b> CV(f<sub>B,rem</sub>) = 0.00% — the elimination "
    f"fraction is perfectly consistent across seeds (threshold: &lt; 20%).",
    sBullet))
story.append(Paragraph(
    "• <b>Floor fraction among removed B-contributors: 0.000.</b> No B-contributing vertex "
    "in the removed set has floor-applied p<sub>conv</sub>, consistent with the Investigation A "
    "finding that the floor mechanism is not operative.",
    sBullet))

story.append(Spacer(1, 2*mm))

story.append(Paragraph("<b>Figure 3.</b> Background Elimination by Trimming (B1, B2, B3)",
             sFigLabel))
story.append(Image(FIG_B, width=fig_width, height=fig_width * 5.0/15.0))
story.append(Paragraph(
    "Figure 3. Three-panel view of Investigation B results across 50 seeds. "
    "Left: f_B,rem distribution — all seeds show f_B,rem = 1.000, far exceeding the B1 threshold "
    "(gold dashed, 0.5). Centre: enrichment ratio distribution — all seeds show 50× enrichment, "
    "far exceeding the B2 threshold (1.0). Right: floor fraction among removed B-contributors — "
    "all seeds show 0.000, confirming that p_conv floor effects are not responsible.",
    sCaption))

story.append(Paragraph("4.2 Interpretation", sH2))

story.append(Paragraph(
    "The B-elimination result (f<sub>B,rem</sub> = 1.000, capturing all 2,715 B-contributing "
    "vertices across 50 seeds) explains the near-ideal "
    "degradation ratios observed in v2.8: trimming eliminates the specific conversion vertices "
    "that survive the optimal λ cut "
    "and contaminate the mass window. The 2% removal fraction captures all B-contributors "
    "because those vertices sit at the extreme tails of the λ distribution, precisely where "
    "k = 1% trimming operates.",
    sBody))
story.append(Paragraph(
    "This result is consistent with the two-part mechanism identified in v2.8 (X1 REFUTED): "
    "the optimal λ threshold is preserved under trimming, while the mass window shifts, "
    "jointly reducing B to approximately zero and increasing S.",
    sBody))


# ============================================================
# 5. INVESTIGATION C: N_CONV SCALING
# ============================================================
story.append(PageBreak())
story.append(Paragraph("5. Investigation C: N<sub>conv</sub> Scaling Test", sH1))

story.append(Paragraph(
    "Investigation C varies N<sub>conv</sub> from 3,125 to 50,000 across 10 seeds (i = 50–59) "
    "to distinguish structural from finite-sample effects in the degradation ratio variance. "
    "If the seed-to-seed CV of the degradation ratio follows 1/√N, the variance is a statistical "
    "artefact that disappears with more data; if it deviates, the variance reflects a structural "
    "feature of the estimator.",
    sBody))

story.append(Paragraph("5.1 Results", sH2))

cv_data = R['cv_scaling']
ns_str = sorted(cv_data['cv_u'].keys(), key=lambda x: int(x))
ns = [int(n) for n in ns_str]
cvu_vals = [cv_data['cv_u'][n] * 100 for n in ns_str]
cvt_vals = [cv_data['cv_t'][n] * 100 for n in ns_str]

cv_ratio = cvu_vals[-1] / cvu_vals[0] * np.sqrt(ns[-1] / ns[0]) if cvu_vals[0] > 0 else 0
benefit_50k = cvu_vals[-1] / cvt_vals[-1] if cvt_vals[-1] > 0 else 0

n1_val = [p for p in preds if p['id'] == 'N1'][0]['value']
story.append(Paragraph(
    f"• <b>N1 (Diagnostic): CONFIRMED.</b> The endpoint CV ratio "
    f"CV(50,000)/CV(3,125) = {n1_val:.4f}, substantially above the "
    f"threshold of 0.25. The untrimmed CV declined from {cvu_vals[0]:.2f}% at "
    f"N = 3,125 to {cvu_vals[-1]:.2f}% at N = 50,000 — more slowly than the "
    f"1/√N reference over the tested range.",
    sBullet))
story.append(Paragraph(
    f"• <b>N2 (Diagnostic): CONFIRMED.</b> The trimming benefit ratio at N = 50,000 is "
    f"{benefit_50k:.1f}×, far exceeding the threshold of 5. The benefit increases monotonically "
    f"with N<sub>conv</sub>, consistent with trimming addressing a component of variance that "
    f"does not diminish as 1/√N.",
    sBullet))

cv_trim_max = max(cvt_vals)
cv_trim_max_n = ns[cvt_vals.index(cv_trim_max)]
story.append(Paragraph(
    f"• <b>N3 (Secondary): REFUTED.</b> The trimmed CV is not below 1% at all N<sub>conv</sub> "
    f"values: max CV(trimmed) = {cv_trim_max:.2f}% at N = {cv_trim_max_n:,}. While trimming "
    f"dramatically reduces the CV at all sample sizes, the small-N regime (N = 3,125) has "
    f"insufficient vertices for the trimmed estimator to achieve the sub-percent stability "
    f"seen at larger N.",
    sBullet))

story.append(Spacer(1, 2*mm))

# CV table
story.append(Paragraph("Table 1. CV Scaling Results (10-Seed Ensemble)", sH2))
cv_header = [Paragraph(h, sTH) for h in ['N_conv', 'CV untrim [%]', 'CV trim [%]',
                                           'Benefit ratio', '1/√N ref [%]']]
cv_rows = []
for j, n_s in enumerate(ns_str):
    n = int(n_s)
    ref_val = cvu_vals[0] * np.sqrt(ns[0] / n)
    ben = cvu_vals[j] / cvt_vals[j] if cvt_vals[j] > 0 else 0
    cv_rows.append([
        Paragraph(f'{n:,}', sTDB),
        Paragraph(f'{cvu_vals[j]:.2f}', sTD),
        Paragraph(f'{cvt_vals[j]:.2f}', sTD),
        Paragraph(f'{ben:.1f}×', sTDB),
        Paragraph(f'{ref_val:.2f}', sTD),
    ])
story.append(make_table(cv_header, cv_rows, [28*mm, 30*mm, 28*mm, 28*mm, 28*mm]))

story.append(Spacer(1, 3*mm))
story.append(Paragraph("<b>Figure 4.</b> N<sub>conv</sub> Scaling (N1, N2, N3)",
             sFigLabel))
story.append(Image(FIG_C, width=fig_width, height=fig_width * 5.5/13.0))
story.append(Paragraph(
    "Figure 4. Left: log-log plot of CV vs N_conv. The untrimmed CV (red) declines far more "
    "slowly than the 1/√N reference (grey dashed), consistent with a non-statistical component "
    "in the variance (N1 CONFIRMED). "
    "The trimmed CV (green) drops steeply and approaches 0.1% at large N. "
    "Right: trimming benefit ratio, growing from 1.4× at 3k to 108.6× at 50k. "
    "The N2 threshold (gold dashed, 5.0) is exceeded from N = 12,500 onward.",
    sCaption))


# ============================================================
# 6. PREDICTION SCORECARD
# ============================================================
story.append(PageBreak())
story.append(Paragraph("6. Prediction Scorecard", sH1))

story.append(Paragraph(
    "Table 2 summarises the outcome of all 9 preregistered predictions. The preregistered "
    "success criteria (§7) define <b>Strong</b> support as all 3 core predictions {Z1, Z2, B1} "
    "confirmed, <b>Partial</b> as 1 or 2 of 3, and <b>Weak</b> as 0 of 3. With B1 confirmed "
    "among the core set (1/3), the overall assessment is <b>PARTIAL</b> support. "
    "B2 is a derived quantity (enrichment = f<sub>B,rem</sub> / removal fraction) that follows "
    "mechanically from B1 and is not counted as an independent judgment.",
    sBody))

# Full scorecard table
sc_header = [Paragraph(h, sTH) for h in ['ID', 'Description', 'Criterion', 'Tier', 'Measured', 'Result']]
sc_rows = []
for p in preds:
    res_style = sTDG if p['result'] == 'CONFIRMED' else (sTD if p['result'] == 'NOT EVALUABLE' else sTDR)
    val_str = 'N/A' if p['value'] is None else str(p['value'])
    if val_str == 'inf':
        val_str = '∞'
    sc_rows.append([
        Paragraph(p['id'], sTDB),
        Paragraph(p['desc'][:42], sTDL),
        Paragraph(p['criterion'], sTDL),
        Paragraph(p['tier'], sTD),
        Paragraph(val_str, sTD),
        Paragraph(p['result'], res_style),
    ])
story.append(make_table(sc_header, sc_rows, [12*mm, 42*mm, 38*mm, 20*mm, 18*mm, 22*mm]))

story.append(Spacer(1, 3*mm))
story.append(Paragraph("<b>Figure 5.</b> Prediction Scorecard — Visual Summary",
             sFigLabel))
story.append(Image(FIG_SC, width=fig_width, height=fig_width * 6.0/12.0))
story.append(Paragraph(
    "Figure 5. Visual scorecard of all 9 predictions. Green rows: CONFIRMED. "
    "Red rows: REFUTED. Yellow row: NOT EVALUABLE (undefined metric). "
    "The overall assessment is PARTIAL support (1/3 core predictions confirmed).",
    sCaption))

# ============================================================
# 7. DISCUSSION
# ============================================================
story.append(PageBreak())
story.append(Paragraph("7. Discussion", sH1))

story.append(Paragraph("7.1 The Z-Distribution Surprise", sH2))
story.append(Paragraph(
    "The refutation of Z1–Z2 is the most informative result of this study. The "
    "preregistered hypothesis — that inter-band vertices at floor-applied p<sub>conv</sub> "
    "positions dominate the removed set — appeared well-motivated from the structure of the "
    "17-band tag formula: the 8 service bands between sensor disks create regions where "
    "p<sub>conv</sub> could potentially be very low, producing extreme λ via the log ratio. "
    "The hypothesis failed because the simulation generates conversions only at sensor disk "
    "positions, never at inter-band locations.",
    sBody))
story.append(Paragraph(
    "The measured fact is that floor = 0 out of 1,184 removed vertices: the numerical floor "
    "plays no role. This is direct evidence <i>against</i> the floor-artefact hypothesis. "
    "What drives the extreme λ values of these near-band vertices remains undetermined. "
    "One candidate explanation is unusual Δχ<super>2</super> values — poorly reconstructed "
    "vertex fits at material-rich z positions — but this hypothesis has not been tested in "
    "the current study. A future investigation could profile Δχ<super>2</super> for the "
    "removed vertices to discriminate among candidate mechanisms.",
    sBody))

story.append(Paragraph("7.2 The Background Elimination Channel", sH2))
story.append(Paragraph(
    f"The B-elimination result (f<sub>B,rem</sub> = 1.000, capturing all {n_B_total:,} "
    "B-contributing vertices across 50 seeds) is striking in its completeness. "
    "Every B-contributing conversion vertex — those that survive the optimal λ cut and "
    "contaminate the signal mass window — is captured by the 2% removal mask. This is not "
    "a tautology: the removal mask is defined by extreme λ values, while B-contribution "
    "is defined by the intersection of λ ≥ t<sub>opt</sub>, the mass window, and the base "
    "selection. The result implies that the same vertices driving the extreme tails of the "
    "λ distribution are exactly those responsible for background contamination.",
    sBody))
story.append(Paragraph(
    "The 50-fold enrichment (B2) makes this precise: the removed 2% contain all B-contributors, "
    "so the enrichment is 1.0/0.02 = 50. Any reduction in removal fraction while maintaining "
    "complete B-elimination would increase the enrichment further, suggesting that the optimal "
    "trim fraction could be refined below k = 1%.",
    sBody))

story.append(Paragraph("7.3 Structural vs Statistical Variance", sH2))
story.append(Paragraph(
    "Investigation C shows that the untrimmed CV declined more slowly than the 1/√N reference "
    "over the tested range: from 20.65% at N = 3,125 to 9.83% at N = 50,000, compared with the "
    "4-fold reduction expected from pure 1/√N scaling. The endpoint CV ratio of 0.4763 "
    "(threshold: 0.25) exceeds the preregistered criterion, though "
    "the exact decomposition into structural and statistical parts has not been measured.",
    sBody))
story.append(Paragraph(
    "The trimmed CV, by contrast, falls steeply at large N, "
    "consistent with trimming reducing the non-statistical component. "
    f"The N3 refutation (max trimmed CV = {cvt_vals[0]:.2f}% at N = 3,125) is a small-sample "
    "effect: with ~63 removed vertices from a sample of 3,125, the trimmed estimator has "
    "insufficient resolution, but converges rapidly as N increases.",
    sBody))

# ============================================================
# 8. CONCLUSIONS AND OUTLOOK
# ============================================================
story.append(Paragraph("8. Conclusions and Outlook", sH1))

story.append(Paragraph(
    "This v2.9 post-registration study yields three main conclusions:",
    sBody))

story.append(Paragraph(
    "1. <b>The floor-artefact hypothesis is refuted.</b> Trimming does not remove inter-band "
    "vertices at floor-applied p<sub>conv</sub>; it removes near-band vertices (floor = 0 "
    "out of 1,184). What property of these vertices produces extreme λ remains an open "
    "question; a Δχ<super>2</super>-driven mechanism is one candidate hypothesis for "
    "future investigation.",
    sBullet))
story.append(Paragraph(
    f"2. <b>Trimming captures all B-contributing vertices.</b> The 2% removal mask captures "
    f"all {n_B_total:,} B-contributing vertices across 50 seeds (f<sub>B,rem</sub> = 1.000) "
    "with 50-fold enrichment, explaining the near-ideal degradation ratios observed in v2.8.",
    sBullet))
story.append(Paragraph(
    "3. <b>Untrimmed CV declines more slowly than 1/√N.</b> The N<sub>conv</sub> scaling test "
    "shows that the untrimmed CV declined more slowly than the 1/√N reference over the tested "
    "range, while the trimming benefit grows monotonically from 1.4× to 108.6× as N increases.",
    sBullet))

story.append(Spacer(1, 3*mm))
story.append(Paragraph(
    "<b>Outlook.</b> A natural next step would be to profile the Δχ<super>2</super> distribution "
    "of the removed vertices to test the candidate hypothesis that poor vertex-fit quality drives "
    "the extreme λ values. Additionally, investigating "
    "whether the optimal trim fraction k could be reduced below 1% while maintaining full "
    "B-contributor capture could improve signal retention. The preregistration-postregistration cycle "
    "continues to prove valuable: the Z1–Z2 refutation would not have been anticipated without "
    "the commitment to test the floor-artefact hypothesis before seeing the data.",
    sBody))


# ============================================================
# 9. FUTURE DIRECTIONS
# ============================================================
story.append(Paragraph("9. Future Directions", sH1))

story.append(Paragraph(
    "The diagnostic findings from v2.9 inform and update the future-research roadmap originally "
    "outlined in the preregistration (§9). Directions are grouped into those motivated by "
    "v2.9 results (§9.1–§9.2) and those carried forward from the preregistration roadmap "
    "(§9.3–§9.7), updated to reflect the diagnostic context.",
    sBody))

# --- 9.1  Δχ² Profiling ---
story.append(Spacer(1, 2*mm))
story.append(Paragraph("9.1 Δχ² Profiling of Removed Near-Band Vertices", sH2))
story.append(Paragraph(
    "The refutation of the floor-artefact hypothesis (Z1–Z2) leaves the driving mechanism "
    "unexplained: why do these near-band vertices produce extreme λ values? A leading "
    "candidate is mismatch with the conversion hypothesis in the toy model. For each removed "
    "conversion vertex, the Δχ<super>2</super> contribution to the nearby material-band fit "
    "could be decomposed into its transverse and longitudinal components "
    "(Δχ<super>2</super><sub>T</sub>/2, Δχ<super>2</super><sub>L</sub>/2) and the position "
    "log-likelihood term, then compared between upper- and lower-tail vertices. Rather than "
    "interpreting a high aggregate Δχ<super>2</super> directly as poor reconstruction quality, "
    "this decomposition would reveal which geometric degree of freedom drives the mismatch. "
    "This investigation would be the centrepiece of a v3.0 preregistration.",
    sBody))

# --- 9.2  k < 1% Optimisation ---
story.append(Spacer(1, 2*mm))
story.append(Paragraph("9.2 Trim-Fraction Optimisation (k &lt; 1%)", sH2))
story.append(Paragraph(
    "Investigation B showed that the 2% removal mask captures all 2,715 B-contributing "
    "vertices with perfect consistency across 50 seeds. This raises the question of whether "
    "the fixed 1% trim fraction is larger than necessary. A systematic scan over "
    "k ∈ {0.1%, 0.2%, 0.5%, 0.75%, 1.0%} could identify the minimum trim fraction that "
    "maintains 100% B-contributor capture (f<sub>B,rem</sub> = 1.000). The benefit of a "
    "smaller k should be evaluated by comparing B-capture rate, signal efficiency, and the "
    "toy upper-limit proxy max(3, 2√B)/S jointly, rather than by B-capture alone.",
    sBody))

# --- 9.3  Signal-Side λ Regularisation ---
story.append(Spacer(1, 2*mm))
story.append(Paragraph("9.3 Signal-Side λ Regularisation", sH2))
story.append(Paragraph(
    "If Investigation A had confirmed that inter-band conversion vertices dominate the "
    "removed set (Z1, Z2 CONFIRMED), regularising p<sub>conv</sub> for signal vertices "
    "in inter-band gaps would have been the logical next step. Although Z1–Z2 were "
    "refuted — the removed vertices are all near-band — the question of whether the same "
    "p<sub>conv</sub> floor mechanism affects signal vertices remains relevant. "
    "Regularising p<sub>conv</sub> for signal vertices — imposing a physical minimum "
    "above the P<sub>FLOOR</sub> = 10<super>−300</super> — may reduce the extreme "
    "signal-vertex λ tail. The v2.7 finding that signal-vertex randomness contributes "
    "only 0.19% of Tag variance suggests the effect may be small. The v2.9 diagnostics "
    "found zero floor-applied vertices among the removed conversion-background population, "
    "and the signal-side effect was not evaluated. A dedicated test of whether signal-vertex "
    "λ values are sensitive to the P<sub>FLOOR</sub> setting would clarify the scope of any "
    "regularisation. Any change to the tag formula itself would require a fresh preregistration.",
    sBody))

# --- 9.4  Other Configurations and Mass Grid ---
story.append(Spacer(1, 2*mm))
story.append(Paragraph("9.4 Extension to Other Configurations and Mass Grid", sH2))
story.append(Paragraph(
    "The diagnostic results at f = 0.25 may not generalise to other material scales. "
    "Changing f alters both the material budget and the amount of scattering, potentially "
    "changing the inter-band/near-band balance revealed by Investigation A. However, the "
    "current generator places conversion vertices only inside sensor disks; to test "
    "conversions in the inter-disk gaps the generative model would need to be extended. "
    "A systematic scan over f ∈ {0.10, 0.25, 0.50, 1.00} with the same diagnostic "
    "decomposition would map how the trimming mechanism varies with material density. "
    "The v2.8 results suggest trimming is concentrated at low mass (17 MeV); a broader "
    "mass grid (5–500 MeV) would identify the boundary of where trimming provides benefit.",
    sBody))

# --- 9.5  Alternative Discriminator Architectures ---
story.append(Spacer(1, 2*mm))
story.append(Paragraph("9.5 Alternative Discriminator Architectures", sH2))
story.append(Paragraph(
    "Investigation B showed that the removal mask captures 100% of B-contributing vertices "
    "(B1 CONFIRMED). This suggests a targeted pre-filter approach: rather than trimming a "
    "fixed 1% of the λ distribution, a future discriminator could directly identify and "
    "remove the near-band conversion vertices that contribute most to B. Such a "
    "'targeted material-aware trimming' approach could achieve the benefits of the current "
    "trimming procedure with a physical rather than statistical criterion, potentially "
    "making it more robust to changes in geometry and material scale.",
    sBody))

# --- 9.6  Dimuon Control Sample ---
story.append(Spacer(1, 2*mm))
story.append(Paragraph("9.6 Dimuon Control Sample (ALP → μ⁺μ⁻)", sH2))
story.append(Paragraph(
    "The dimuon channel (ALP → μ⁺μ⁻) is kinematically accessible only above approximately "
    "211.3 MeV (twice the muon mass), making it a separate control sample rather than a "
    "same-mass comparison for the 17 MeV benchmark. If the degradation ratio approaches 1.0 "
    "when conversion-photon background is absent, it would suggest that the signal loss "
    "mechanism is material-interaction driven; however, dimuon results alone cannot confirm "
    "the cause of signal loss at the 17 MeV mass point where conversions dominate. The v2.9 "
    "diagnostics address the same question from the other direction (by directly examining "
    "the removed background vertices), so the two studies are complementary.",
    sBody))

# --- 9.7  GSF Tracking and Realistic Validation ---
story.append(Spacer(1, 2*mm))
story.append(Paragraph("9.7 GSF Tracking and Realistic Validation", sH2))
story.append(Paragraph(
    "Gaussian-Sum Filter tracking (§10.6 of v2.8) and the phased validation programme "
    "(MadGraph5 + Pythia8, Delphes, Geant4; §10.8) remain longer-term directions. The "
    "v2.9 results inform which aspects of the validation programme are most informative: "
    "since the removed vertices are all near-band (Z1–Z2 REFUTED), realistic "
    "photon-conversion modelling in Geant4 — where the p<sub>conv</sub> distribution is "
    "physics-driven rather than formula-driven — would be the highest-priority validation "
    "step. A control experiment varying P<sub>FLOOR</sub> alone (§10.2 scope) would test "
    "whether the signal-side λ distribution is sensitive to the floor setting.",
    sBody))

# --- 9.8  Lessons for Preregistration Practice ---
story.append(Spacer(1, 2*mm))
story.append(Paragraph("9.8 Lessons for Preregistration Practice", sH2))
story.append(Paragraph(
    "The v2.8–v2.9 cycle illustrates several lessons for preregistration in exploratory "
    "computation. First, the v2.8 confirmation rate (8/9) demonstrates that preregistration "
    "need not be conservative: well-motivated predictions from a previous study's diagnostics "
    "were supported across the 50-seed v2.8 toy Monte Carlo ensemble. Second, the single REFUTED prediction in v2.8 "
    "(X1) was arguably more informative than a confirmation would have been: X1's clean "
    "refutation revealed the two-part improvement mechanism (λ threshold preserved, mass "
    "window shifted; background reduction and signal yield increase observed jointly), "
    "generating a new finding not anticipated in the preregistration.",
    sBody))
story.append(Paragraph(
    "The v2.9 results reinforce this lesson even more strongly: the Z1–Z2 refutation of the "
    "floor-artefact hypothesis — the study's central question — is the most informative "
    "outcome precisely because it was unexpected. The honest PARTIAL support judgment (1 of 3 "
    "core predictions confirmed) led directly to two concrete next-step hypotheses "
    "(Δχ<super>2</super> profiling and k-optimisation) that would not have emerged from a "
    "blanket confirmation. Third, the separation of core predictions from secondary and "
    "diagnostic predictions proved valuable in both studies: in v2.8 the 5/5 core score "
    "provided a clean adoption criterion, while in v2.9 the diagnostic predictions (N1–N3) "
    "enriched understanding without muddying the central mechanistic judgment. Future "
    "preregistrations could benefit from explicitly designating some predictions as "
    "'direction-agnostic' — where REFUTED is as informative as CONFIRMED — rather than "
    "treating all predictions as pass/fail tests.",
    sBody))

# --- 9.9  Toward Realistic Validation and Potential Experimental Application ---
story.append(Spacer(1, 2*mm))
story.append(Paragraph(
    "9.9 Toward Realistic Validation and Potential Experimental Application", sH2))
story.append(Paragraph(
    "The toy MC framework uses a simplified endcap geometry (9 sensor disks, 8 service bands, "
    "η = 2.0) with parametric vertex resolution and a scalar material scale f. While these "
    "simplifications suffice for establishing the discriminator's statistical properties, the "
    "natural next step is validation with increasingly realistic simulation tools. A phased "
    "approach could proceed as follows:",
    sBody))
story.append(Paragraph(
    "(a) <i>Event-generator validation</i> — replacing the parametric signal generator with "
    "MadGraph5 + Pythia8 for the full pp → tt̄ + a, a → e<super>+</super>e<super>−</super> "
    "chain, feeding the resulting signal four-vectors into the existing endcap geometry model. "
    "This would test whether the trimming benefit persists with realistic signal kinematic "
    "distributions. Photon-conversion background generation, which depends on detector "
    "material, would remain at the detector-simulation stage (b) or (c) rather than the "
    "event-generator level.",
    sBullet))
story.append(Paragraph(
    "(b) <i>Fast detector simulation</i> — using Delphes or a comparable parameterised detector "
    "response to approximate e<super>+</super>e<super>−</super> track-pair reconstruction "
    "efficiency and displaced-vertex resolution at relevant mass points, while remaining "
    "computationally tractable for large-ensemble studies.",
    sBullet))
story.append(Paragraph(
    "(c) <i>Detailed detector simulation and reconstruction</i> — a Geant4-based study at "
    "selected mass points, combined with detector-specific reconstruction software, to confirm "
    "that the λ-based trimming mechanism and the two-part improvement (background elimination "
    "+ signal yield increase via mass-window relaxation) survive detailed photon-conversion "
    "modelling, electromagnetic shower simulation, and realistic track reconstruction.",
    sBullet))
story.append(Paragraph(
    "If the validation programme confirms that the trimming benefit survives realistic "
    "simulation, the trimmed Tag algorithm could be of practical interest for existing or "
    "planned experiments. At 17 MeV, the v2.8 toy Monte Carlo gave mean degradation ratios "
    "of 1.0648 for the trimmed Tag and 1.0578 for the hard veto, a relative difference of "
    "0.66%. Detector-level follow-up should test whether such close electron pairs can be "
    "reconstructed efficiently and whether a single pre-defined selection, applied to all "
    "candidates, preserves the background rejection and signal efficiency. Note that the "
    "current Investigation C truncates the signal and conversion-background λ distributions "
    "separately; a combined analysis on mixed data would be needed to confirm that a fixed "
    "selection rule works in practice.",
    sBody))
story.append(Paragraph(
    "The current LHC Long Shutdown 3 (LS3) and HL-LHC upgrade period may present a timely "
    "opportunity for such investigations. Among existing LHC experiments, LHCb's forward "
    "disk-based vertex locator (VELO) is a comparable forward detector that could serve as "
    "a test case: its upgraded pixel VELO for Run 3 and beyond provides displaced-vertex "
    "resolution in the forward region. The first step would be to confirm that at 17 MeV "
    "the detector can separate the two tracks from ALP → e<super>+</super>e<super>−</super> "
    "and reconstruct their displaced vertex with sufficient efficiency. If both the track-pair "
    "reconstruction and a common selection rule are validated, the method could be evaluated "
    "in an offline analysis. Forward auxiliary beamline detectors and "
    "fixed-target configurations (SPS/PS energies) could similarly target the 10–50 MeV "
    "range, with 17 MeV as the initial benchmark where the trimming benefit is strongest in "
    "this study. We emphasise that these are extrapolations from a toy-level study; any "
    "experimental application would require the validation programme outlined above, and the "
    "question of track-pair resolution at the relevant mass scale is one that the detailed "
    "simulation stages (b) and (c) are designed to answer. This idea is recorded here to "
    "establish a timestamp for the concept within the preregistered study chain.",
    sBody))


# ============================================================
# 10. REFERENCES AND DOI CHAIN
# ============================================================
story.append(Paragraph("10. DOI Chain", sH1))

doi_header = [Paragraph(h, sTH) for h in ['Version', 'DOI', 'Description']]
doi_rows = [
    [Paragraph('v2.9 post-reg', sTDB), Paragraph('10.5281/zenodo.24527398', sTDB),
     Paragraph('Background-Focused Diagnostics results (this document)', sTDL)],
    [Paragraph('v2.9 prereg', sTD), Paragraph('10.5281/zenodo.24466187', sTD),
     Paragraph('Background-Focused Diagnostics prereg', sTDL)],
    [Paragraph('v2.8 post-reg', sTD), Paragraph('10.5281/zenodo.24437855', sTD),
     Paragraph('Trimmed Tag Estimator results', sTDL)],
    [Paragraph('v2.8 prereg', sTD), Paragraph('10.5281/zenodo.24414960', sTD),
     Paragraph('Trimmed Tag Estimator prereg', sTDL)],
    [Paragraph('v2.7 post-reg', sTD), Paragraph('10.5281/zenodo.24408990', sTD),
     Paragraph('Tag Formula Diagnostics results', sTDL)],
    [Paragraph('v2.7 prereg', sTD), Paragraph('10.5281/zenodo.24388228', sTD),
     Paragraph('Tag Formula Diagnostics prereg', sTDL)],
    [Paragraph('v2.6 post-reg', sTD), Paragraph('10.5281/zenodo.24373115', sTD),
     Paragraph('Multi-Seed Ensemble results', sTDL)],
    [Paragraph('v2.6 prereg', sTD), Paragraph('10.5281/zenodo.24361872', sTD),
     Paragraph('Multi-Seed Ensemble prereg', sTDL)],
    [Paragraph('v2.5 results', sTD), Paragraph('10.5281/zenodo.24341050', sTD),
     Paragraph('Deconflation post-reg', sTDL)],
    [Paragraph('v2.5 prereg', sTD), Paragraph('10.5281/zenodo.24329044', sTD),
     Paragraph('Deconflation prereg', sTDL)],
    [Paragraph('v2.4 results', sTD), Paragraph('10.5281/zenodo.24302619', sTD),
     Paragraph('17-band geometry post-reg', sTDL)],
    [Paragraph('v2.4 prereg', sTD), Paragraph('10.5281/zenodo.24296796', sTD),
     Paragraph('17-band geometry prereg', sTDL)],
    [Paragraph('v2.3 results', sTD), Paragraph('10.5281/zenodo.24273586', sTD),
     Paragraph('Endcap tag post-reg', sTDL)],
    [Paragraph('v2.3 prereg', sTD), Paragraph('10.5281/zenodo.24244893', sTD),
     Paragraph('Endcap tag prereg', sTDL)],
    [Paragraph('v2.2 results', sTD), Paragraph('10.5281/zenodo.24238224', sTD),
     Paragraph('Barrel → endcap post-reg', sTDL)],
    [Paragraph('v2.2 prereg', sTD), Paragraph('10.5281/zenodo.24189990', sTD),
     Paragraph('Barrel → endcap prereg', sTDL)],
    [Paragraph('v2.1 results', sTD), Paragraph('10.5281/zenodo.24136462', sTD),
     Paragraph('Barrel material-veto post-reg', sTDL)],
    [Paragraph('v2.1 prereg', sTD), Paragraph('10.5281/zenodo.24063091', sTD),
     Paragraph('Barrel material-veto prereg', sTDL)],
    [Paragraph('v2.0', sTD), Paragraph('10.5281/zenodo.24056097', sTD),
     Paragraph('Initial barrel study', sTDL)],
]
story.append(make_table(doi_header, doi_rows, [30*mm, 55*mm, 70*mm]))


# ============================================================
# 11. REFERENCES
# ============================================================
story.append(Paragraph("11. References", sH1))

story.append(Paragraph("11.1 External References", sH2))
story.append(Paragraph(
    "[E1] J. Alimena, F. Blekman, C. Cazzaniga, X. Cid Vidal, J. Niedziela, L. Rygaard, "
    "R. Soto Rey, \"Hunting for Long-Lived ALPs in Top Events via Displaced Dielectron Pairs "
    "at the LHC,\" arXiv:2610.38932 [hep-ph] (2026) (motivating analysis: generator-level "
    "sensitivity study for displaced ALP → e<super>+</super>e<super>−</super> in tt̄ events "
    "motivated by the CMS detector).",
    sBody))
story.append(Paragraph(
    "[E2] L. Rygaard, J. Niedziela, R. Schäfer, S. Bruggisser, J. Alimena, S. Westhoff, "
    "F. Blekman, \"Top Secrets: Long-Lived ALPs in Top Production,\" arXiv:2306.08686 "
    "[hep-ph] (2023) (predecessor analysis: displaced di-muon ALP search strategy in tt̄ "
    "production at the LHC and HL-LHC).",
    sBody))
story.append(Paragraph(
    "[E3] A. L. Read, \"Presentation of search results: the CL<sub>s</sub> technique,\" "
    "J. Phys. G 28 (2002) 2693 (methodological background for upper-limit setting; this "
    "study uses the toy upper-limit proxy max(3, 2√B)/S rather than the full "
    "CL<sub>s</sub> procedure).",
    sBody))
story.append(Paragraph(
    "[E4] D. Curtin et al., \"Long-Lived Particles at the Energy Frontier: The MATHUSLA "
    "Physics Case,\" Rep. Prog. Phys. 82 (2019) 116201, arXiv:1806.07396 (displaced-vertex "
    "physics context).",
    sBody))
story.append(Paragraph(
    "[E5] NumPy v1.26, numpy.org (pseudo-random number generation, array operations).",
    sBody))
story.append(Paragraph(
    "[E6] ReportLab v5.0.1, reportlab.com (PDF generation).",
    sBody))
story.append(Paragraph(
    "[E7] SciPy v1.14, scipy.org (normal CDF via scipy.special.ndtr, used to compute Gaussian "
    "probabilities across material bands in the conversion-density model).",
    sBody))

story.append(Spacer(1, 3*mm))
story.append(Paragraph("11.2 Internal References (ALP-ttbar Toy MC Series)", sH2))
story.append(Paragraph(
    "[I1] W. S. Paik, \"ALP-ttbar Toy MC v2.8 — Post-Registration: Trimmed Tag Estimator "
    "Results,\" DOI: 10.5281/zenodo.24437855 (confirmed trimmed Tag as default; 8/9 predictions "
    "confirmed; identified two-part improvement mechanism via REFUTED X1 — the primary motivation "
    "for this diagnostic study).",
    sBody))
story.append(Paragraph(
    "[I2] W. S. Paik, \"ALP-ttbar Toy MC v2.8 — Preregistration: Trimmed Tag Estimator as "
    "Default,\" DOI: 10.5281/zenodo.24414960 (preregistered the adoption study).",
    sBody))
story.append(Paragraph(
    "[I3] W. S. Paik, \"ALP-ttbar Toy MC v2.7 — Post-Registration: Tag Formula Diagnostics "
    "Results,\" DOI: 10.5281/zenodo.24408990 (identified conversion-background dominance, "
    "trimming effectiveness, and Winsorising failure).",
    sBody))
story.append(Paragraph(
    "[I4] W. S. Paik, \"ALP-ttbar Toy MC v2.7 — Preregistration: Tag Formula Diagnostics,\" "
    "DOI: 10.5281/zenodo.24388228.",
    sBody))
story.append(Paragraph(
    "[I5] W. S. Paik, \"ALP-ttbar Toy MC v2.6 — Post-Registration: Multi-Seed Ensemble "
    "Results,\" DOI: 10.5281/zenodo.24373115 (50-seed ensemble, identified Tag CV ≈ 7.4%).",
    sBody))
story.append(Paragraph(
    "[I6] W. S. Paik, \"ALP-ttbar Toy MC v2.6 — Preregistration: Multi-Seed Ensemble,\" "
    "DOI: 10.5281/zenodo.24361872.",
    sBody))
story.append(Paragraph(
    "[I7] W. S. Paik, \"ALP-ttbar Toy MC v2.5 — Post-Registration: Deconflation,\" "
    "DOI: 10.5281/zenodo.24341050.",
    sBody))
story.append(Paragraph(
    "[I8] W. S. Paik, \"ALP-ttbar Toy MC v2.5 — Preregistration: Deconflation,\" "
    "DOI: 10.5281/zenodo.24329044.",
    sBody))
story.append(Paragraph(
    "[I9] W. S. Paik, \"ALP-ttbar Toy MC v2.4 — Post-Registration: 17-Band Geometry,\" "
    "DOI: 10.5281/zenodo.24302619 (introduced the 17-band geometry used here).",
    sBody))
story.append(Paragraph(
    "[I10] W. S. Paik, \"ALP-ttbar Toy MC v2.4 — Preregistration: 17-Band Geometry,\" "
    "DOI: 10.5281/zenodo.24296796.",
    sBody))

story.append(Spacer(1, 4*mm))
story.append(HRFlowable(width="100%", thickness=0.5, color=GREY))
story.append(Paragraph(
    "Generated from frozen simulation modules archived in DOI 10.5281/zenodo.24437855. "
    "Analysis follows the preregistered plan (DOI 10.5281/zenodo.24466187) without modification.",
    sFooter))

# --- Build ---
doc.build(story)
print(f"PDF saved: {OUT_PDF}")
print(f"Pages: ~10")
