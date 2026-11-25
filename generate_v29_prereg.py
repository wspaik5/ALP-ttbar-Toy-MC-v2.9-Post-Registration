#!/usr/bin/env python3
"""Generate v2.9 Preregistration PDF: Background-Focused Diagnostics."""

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
import os

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

# Figure paths (relative to this script)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FIG1_PATH = os.path.join(_SCRIPT_DIR, "fig1_per_seed_delta_deg.png")
FIG2_PATH = os.path.join(_SCRIPT_DIR, "fig2_deg_distribution.png")
FIG3_PATH = os.path.join(_SCRIPT_DIR, "fig3_signal_background.png")
FIG4_PATH = os.path.join(_SCRIPT_DIR, "fig4_scatter_trim_vs_untrim.png")
FIG5_PATH = os.path.join(_SCRIPT_DIR, "fig5_upper_limit_waterfall.png")
FIG6_PATH = os.path.join(_SCRIPT_DIR, "fig6_geometry_schematic.png")
FIG7_PATH = os.path.join(_SCRIPT_DIR, "fig7_z_distribution_prediction.png")
FIG8_PATH = os.path.join(_SCRIPT_DIR, "fig8_background_elimination_prediction.png")
FIG9_PATH = os.path.join(_SCRIPT_DIR, "fig9_cv_scaling_prediction.png")

# Table styles
sTH = ParagraphStyle("TH", fontName="DejaVu-Bold", fontSize=7.5, leading=10,
                     alignment=TA_CENTER, textColor=WHITE)
sTD = ParagraphStyle("TD", fontName="DejaVu", fontSize=7.5, leading=10,
                     alignment=TA_CENTER, textColor=DARK)
sTDL = ParagraphStyle("TDL", fontName="DejaVu", fontSize=7.5, leading=10,
                      alignment=TA_LEFT, textColor=DARK)
sTDB = ParagraphStyle("TDB", fontName="DejaVu-Bold", fontSize=7.5, leading=10,
                      alignment=TA_CENTER, textColor=DARK)

def make_table(header, rows, col_widths):
    """Create a styled table."""
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


# Shorthand for special characters in Paragraph XML
lam = "λ"
dchi = "Δχ<super>2</super>"
delt = "Δ"


# --- Build PDF ---
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PDF = os.path.join(OUT_DIR,
    "ALP-ttbar_Toy-MC_v2.9_Preregistration_Background-Focused-Diagnostics_2026-11-24.pdf")

doc = SimpleDocTemplate(OUT_PDF, pagesize=A4,
                        topMargin=15*mm, bottomMargin=12*mm,
                        leftMargin=18*mm, rightMargin=18*mm)

story = []

# ============================================================
# TITLE PAGE / HEADER
# ============================================================
story.append(Paragraph(
    "ALP-ttbar Toy MC v2.9 — Preregistration:<br/>"
    "Background-Focused Diagnostics<br/>"
    "in Displaced Light ALP → e<super>+</super>e<super>−</super>",
    sTitle))
story.append(Paragraph("Won Shik Paik (Independent Researcher, Auckland, New Zealand)", sAuthor))
story.append(Paragraph("2026-11-24", sDate))
story.append(Paragraph(
    "DOI: 10.5281/zenodo.24466187  |  Previous: 10.5281/zenodo.24437855 (v2.8 post-reg)",
    sDOILine))

story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT))

story.append(Paragraph(
    "<i>Disclaimer.</i> Independent personal toy study, not affiliated with the authors of "
    "arXiv:2610.38932 or arXiv:2306.08686, nor with the CMS, ATLAS, LHCb or ALICE "
    "Collaborations or the FCC study. Detector numbers are assumed; only qualitative "
    "trends and ratios are meaningful.",
    sDisclaimer))

# ============================================================
# 1. MOTIVATION AND CONTEXT
# ============================================================
story.append(Paragraph("1. Motivation and Context", sH1))
story.append(Paragraph(
    "The v2.8 post-registration study confirmed the trimmed Tag estimator (k = 1%) as the "
    "default discriminator for the ALP-ttbar Toy MC framework: 8 of 9 preregistered predictions "
    "were confirmed across 50 independent seeds (i = 50–99), and all 5 core predictions "
    "{S1, S2, D1, D2, D3} were confirmed at 17 MeV. The key v2.8 results at 17 MeV are:",
    sBody))

story.append(Paragraph(
    "• <b>Stability.</b> The trimmed Tag achieves CV = 0.09% across the 50-seed ensemble, "
    "compared with CV = 6.84% for the untrimmed Tag — a 76-fold improvement that exceeds "
    "even the HV material-veto discriminator (CV = 0.10%).",
    sBullet))
story.append(Paragraph(
    "• <b>Sensitivity.</b> The mean degradation ratio drops from 1.5762 (untrimmed) to "
    "1.0648 (trimmed), an 89% reduction in excess degradation toward the ideal value of 1.0. "
    "The trimmed Tag range across seeds is [1.0628, 1.0666], compared with "
    "[1.333, 1.849] for untrimmed.",
    sBullet))
story.append(Paragraph(
    "• <b>Universality.</b> All 50 seeds show trimmed Tag &lt; untrimmed Tag (D3: frac = 1.00), "
    "and the per-seed improvement Δ(deg) is uniform (CV of Δ(deg) = 21.1%, X2 CONFIRMED).",
    sBullet))
story.append(Paragraph(
    "• <b>Mechanism insight (X1 REFUTED).</b> The single refuted prediction — X1 predicted "
    "a change in the optimal λ threshold under trimming — reveals a two-part improvement "
    "mechanism: trimming preserves the optimal λ threshold (all 50 seeds retain "
    "t<sub>opt</sub> = 25 before and after trimming) while shifting the optimal mass window, "
    "so that background reduction and signal yield increase operate jointly. The mean "
    "background B drops from ≈3.6 to ≈0, and the mean signal S increases by ≈17%.",
    sBullet))

story.append(Spacer(1, 2*mm))
story.append(Paragraph(
    "These results establish <i>that</i> trimming works, but they do not fully explain "
    "<i>why</i>. In particular, the question of <b>which conversion vertices</b> trimming "
    "removes and why those vertices carry disproportionate leverage over the degradation "
    "ratio remains unanswered. This preregistration designs a systematic diagnostic study "
    "to address that question through three complementary investigations.",
    sBody))

# --- Key v2.8 figures (2 of 5 from v2.8 post-reg, selected for motivation) ---
story.append(Spacer(1, 3*mm))

fig_width = 145*mm
fig_height_std = fig_width * (4.0 / 7.0)
fig_height_wide = fig_width * (4.0 / 7.5)

story.append(Paragraph("<b>Figure 1.</b> Degradation Ratio Distribution (v2.8 Results)", sFigLabel))
story.append(Image(FIG2_PATH, width=fig_width, height=fig_height_std + 5*mm))
story.append(Paragraph(
    "<b>Figure 1.</b> Violin + strip plot of the degradation ratio at m<sub>a</sub> = 17 MeV "
    "across the 50-seed ensemble (v2.8). Each dot is one seed; diamonds mark the ensemble mean. "
    "The untrimmed Tag (red, CV = 6.84%) shows wide spread [1.333, 1.849], while the trimmed "
    "Tag (blue, CV = 0.09%) and HV (green, CV = 0.10%) cluster near ideal. The question for "
    "v2.9 is: what is the z-distribution and λ profile of the ≈2% of vertices that trimming "
    "removes, and why do they carry such disproportionate leverage? "
    "Source: DOI 10.5281/zenodo.24437855.",
    sCaption))

story.append(Spacer(1, 3*mm))
story.append(Paragraph("<b>Figure 2.</b> Signal vs Background: The Two-Part Mechanism (v2.8)", sFigLabel))
story.append(Image(FIG3_PATH, width=fig_width, height=fig_height_wide))
story.append(Paragraph(
    "<b>Figure 2.</b> Left: Mean signal (S) and background (B) counts at 17 MeV for the three "
    "methods. Trimming increases S by ≈17% while driving B to zero. Right: S/B ratio on a "
    "logarithmic scale — the trimmed Tag achieves effectively infinite S/B. This two-part "
    "mechanism (B elimination + S increase) was identified via the REFUTED X1 prediction in "
    "v2.8. Source: DOI 10.5281/zenodo.24437855.",
    sCaption))

story.append(Spacer(1, 2*mm))

# ============================================================
# 2. REVIEW: BACKGROUND IN THE TRIMMED TAG FRAMEWORK
# ============================================================
story.append(Paragraph("2. Review: Background in the Trimmed Tag Framework", sH1))

story.append(Paragraph("2.1 Conversion-Photon Background in the 17-Band Geometry", sH2))
story.append(Paragraph(
    "In the ALP-ttbar Toy MC, conversion-photon backgrounds arise from photons that interact "
    "with detector material and produce e<super>+</super>e<super>−</super> pairs. The 17-band "
    "geometry models 9 sensor disks and 8 inter-disk service bands at η = 2.0, each with "
    "specified z positions and radiation-length thicknesses. The Tag discriminator's "
    "λ likelihood-ratio statistic is computed using the full 17-band material model: for each "
    "vertex, λ encodes the probability of arising from signal (uniform in a mass window) "
    "relative to arising from photon conversion (weighted by material-band proximity and "
    "thickness).",
    sBody))

story.append(Spacer(1, 2*mm))

story.append(Paragraph(
    "The <b>conversion probability floor</b> p<sub>conv</sub> plays a crucial role. For vertices "
    "between material bands (inter-band gaps), p<sub>conv</sub> can approach zero. The code "
    "applies a floor P<sub>FLOOR</sub> = 10<super>−300</super> (effectively zero; see "
    "mtag_v24.py line 52) via np.maximum(p<sub>conv</sub>, P<sub>FLOOR</sub>). For vertices "
    "where p<sub>conv</sub> ≈ 0, the log term −log(p<sub>conv</sub>) becomes very large, "
    "giving those vertices extremely large |λ| values — they are the 'most signal-like' "
    "by the likelihood metric, even though they are genuine background. Note that "
    "'inter-band' vertices (classified by measured z position relative to band centres) "
    "and 'floor-applied' vertices (where p<sub>conv</sub> numerically hits the floor) "
    "are related but distinct sets; Investigation A records both classifications.",
    sBody))

story.append(Paragraph("2.2 The Trimming Mechanism: What We Know and Don't Know", sH2))
story.append(Paragraph(
    "The v2.8 results tell us that trimming removes the extreme 1% tails of the per-vertex λ "
    "distribution and that this reduces the degradation ratio from 1.58 to 1.06 at 17 MeV. "
    "The refuted X1 prediction reveals the mechanism at a high level: the λ threshold is "
    "preserved, the mass window relaxes (or disappears), background B drops to near zero, and "
    "signal S increases by ≈17%. What we do <b>not</b> know is:",
    sBody))
story.append(Paragraph(
    "• <b>Spatial distribution.</b> Are the removed vertices predominantly located in "
    "inter-band gaps (where the p<sub>conv</sub> floor inflates λ) or near material bands "
    "(where anomalously large Δχ<super>2</super> from resolution mismatch inflates λ)?",
    sBullet))
story.append(Paragraph(
    "• <b>Per-vertex leverage.</b> When the threshold is set to its optimal value, which "
    "individual vertices contribute the most to ΔB (the background change that drives the "
    "degradation ratio improvement)? Are there 'swing voters' — a few vertices per seed "
    "that cause the majority of seed-to-seed variance?",
    sBullet))
story.append(Paragraph(
    "• <b>Finite-sample vs structural.</b> Does the extreme-λ leverage diminish with "
    "increasing statistics (suggesting a finite-sample effect that could be absorbed by "
    "larger N<sub>conv</sub>), or does it persist (suggesting a structural feature of the "
    "λ computation under the 17-band geometry)?",
    sBullet))

story.append(Spacer(1, 1*mm))
story.append(Paragraph(
    "Answering these questions is essential for understanding whether trimming is a "
    "generic statistical regularisation technique or a geometry-specific correction for "
    "the p<sub>conv</sub> floor artefact. The answer has implications for whether trimming "
    "would remain effective under alternative detector geometries (§10.3 of v2.8 post-reg) "
    "and whether signal-side λ regularisation (§10.2) would be complementary or redundant.",
    sBody))

# ============================================================
# 3. EXPERIMENTAL DESIGN
# ============================================================
story.append(Paragraph("3. Experimental Design", sH1))

story.append(Paragraph("3.1 Configuration", sH2))
story.append(Paragraph(
    "All experiments use configuration E3 (material scale f = 0.25; z resolution assigned "
    "per vertex based on the nearest of the 9 sensor disks in SENSOR_DISK_Z, i.e. 'all-disk "
    "z precision') at η = 2.0, consistent with v2.4–v2.8. The generation pipeline "
    "follows v2.6: endcap_signal generates 300,000 signal vertices and endcap_conversions "
    "generates 1,500,000 conversion-photon candidates per seed. After basic-cut selection "
    "(fiducial z range, minimum p<sub>T</sub>), up to N<sub>sig</sub> = 50,000 signal "
    "and up to N<sub>conv</sub> = 100,000 conversion vertices passing cuts are retained via "
    "subsample(); vertex weights are rescaled to preserve the total cross-section. "
    "At f = 0.25, the actual post-cut conversion yield is ≈58,600–59,600 per seed — well "
    "below the 100,000 cap — so the standard run uses all available conversions. "
    "Investigation C varies the cap downward to test N<sub>conv</sub> scaling.",
    sBody))
story.append(Paragraph(
    "Focus mass: m<sub>a</sub> = 17 MeV (the regime where trimming is effective and "
    "the extreme-λ leverage is largest). The 200 MeV comparison point is not needed for the "
    "diagnostic analyses in this study, since v2.8 confirmed that trimming is inert at "
    "200 MeV (S3, D4 CONFIRMED).",
    sBody))

story.append(Paragraph("3.2 Seed Range", sH2))
story.append(Paragraph(
    "The diagnostic analyses reuse the same seed range as v2.8: i = 50, 51, …, 99. "
    "Because the diagnostics examine the <i>internal structure</i> of each simulation "
    "(which vertices are removed, their z positions, their per-vertex ΔB contributions), "
    "reusing the same seeds that generated the v2.8 results is scientifically appropriate — "
    "the diagnostics explain the same data, rather than testing on new data.",
    sBody))

seed_header = [Paragraph("Parameter", sTH), Paragraph("Formula", sTH)]
seed_rows = [
    [Paragraph("SEED_CONV", sTDL), Paragraph("100i + 5  for i = 50, 51, …, 99", sTDL)],
    [Paragraph("SEED_SIG", sTDL), Paragraph("100i + 11  for i = 50, 51, …, 99", sTDL)],
]
story.append(make_table(seed_header, seed_rows, [50*mm, 120*mm]))
story.append(Spacer(1, 2*mm))

story.append(Paragraph("3.3 Three Diagnostic Investigations", sH2))
story.append(Paragraph(
    "The study consists of three investigations that together characterise the vertices "
    "removed by trimming:",
    sBody))

story.append(Paragraph(
    "<b>Investigation A: z-Distribution of Removed Vertices.</b> For each seed, identify "
    "the conversion vertices removed by the k = 1% trim (the removal mask). Classify each "
    "removed vertex as 'near-band' (within d<sub>band</sub> mm of the nearest material-band "
    "centre) or 'inter-band' (all others). The boundary d<sub>band</sub> is set to half the "
    "minimum gap between adjacent bands, ensuring a natural partition. Report the fraction "
    "f<sub>inter</sub> of removed vertices that are inter-band, and compare the z-distribution "
    "of removed vertices to the z-distribution of all conversion vertices.",
    sBullet))

# --- Fig 3: Investigation A prediction schematic ---
story.append(Spacer(1, 2*mm))
story.append(Image(FIG7_PATH, width=fig_width, height=fig_width * (5.5 / 10.0)))
story.append(Paragraph("Figure 3", sFigLabel))
story.append(Paragraph(
    "<b>Figure 3.</b> <i>Schematic / Preregistered Hypothesis (Not Data).</i> Expected "
    "z-distribution of removed vertices (partial range: 9 of 17 bands visible at z = 750–2,800 mm; "
    "full model spans z = 230–2,300 mm). "
    "Blue bands: sensor disks; orange bands: service material. Hypothesis: inter-band vertices "
    "(red) dominate the removal set (Z1: f<sub>inter</sub> > 0.5), and are enriched above "
    "their baseline fraction (Z2). Purple dots show the predicted minority of near-band "
    "removals.",
    sCaption))

story.append(Spacer(1, 1*mm))
story.append(Paragraph(
    "<b>Investigation B: Background Elimination by Trimming.</b> At the untrimmed Tag's "
    "optimal (t<sub>opt</sub>, mass-window) combination, identify the set of conversion vertices "
    "that contribute to B (those passing the λ ≥ t cut and falling within the mass window). "
    "Because all conversion vertices carry equal weight (w = σ · f / n ≈ 0.067), "
    "individual vertex 'ranking by weight' is uninformative; instead, the diagnostic "
    "measures whether the <i>removal mask</i> from trimming overlaps with the "
    "B-contributing set. For each seed, compute: (a) the fraction f<sub>B,rem</sub> of "
    "total background B that is eliminated by trimming (i.e., belongs to the removed set), "
    "and (b) the enrichment ratio of B-contributing vertices among removed vertices relative "
    "to the full conversion sample.",
    sBullet))

# --- Fig 4: Investigation B prediction schematic ---
story.append(Spacer(1, 2*mm))
story.append(Image(FIG8_PATH, width=fig_width, height=fig_width * (5.0 / 10.0)))
story.append(Paragraph("Figure 4", sFigLabel))
story.append(Paragraph(
    "<b>Figure 4.</b> <i>Schematic / Preregistered Hypothesis (Not Data).</i> Expected background "
    "elimination by trimming. Left: fraction of total B removed by the trimming mask "
    "(B1: f<sub>B,rem</sub> > 0.5). Right: enrichment of B-contributing vertices in the "
    "removed set (B2, derived: enrichment = f<sub>B,rem</sub> / removal fraction ≈ 32.5×; "
    "automatically satisfied when B1 > 0.5). All conversion "
    "vertices carry equal weight w ≈ 0.067, so this analysis uses the removal mask overlap "
    "with the B-contributing set rather than individual weight rankings.",
    sCaption))

story.append(Spacer(1, 1*mm))
story.append(Paragraph(
    "<b>Investigation C: N<sub>conv</sub> Scaling Test.</b> Repeat the standard trimmed and "
    "untrimmed Tag computation at m<sub>a</sub> = 17 MeV for a subset of seeds (the first 10, "
    "i = 50–59) at multiple N<sub>conv</sub> values: {3125, 6250, 12500, 25000, 50000}. "
    "With f = 0.25, 1.5 M candidates yield ≈58.6–59.6 k conversions after basic cuts, so all "
    "five levels lie below the actual count and each produces a genuinely different subsample "
    "size. The smallest-to-largest ratio is 16×, providing adequate dynamic range. "
    "For each N<sub>conv</sub>, measure the ensemble CV of the untrimmed Tag and the trimmed "
    "Tag. If the extreme-λ leverage is a finite-sample effect, the untrimmed CV should decline "
    "as ≈1/√N<sub>conv</sub> and the benefit of trimming should diminish at large N<sub>conv</sub>. "
    "If the leverage is structural, the untrimmed CV should plateau and trimming should remain "
    "necessary regardless of sample size.",
    sBullet))

# --- Fig 5: Investigation C prediction schematic ---
story.append(Spacer(1, 2*mm))
story.append(Image(FIG9_PATH, width=fig_width, height=fig_width * (5.5 / 9.0)))
story.append(Paragraph("Figure 5", sFigLabel))
story.append(Paragraph(
    "<b>Figure 5.</b> <i>Schematic / Preregistered Hypothesis (Not Data).</i> Expected CV of "
    "the degradation ratio as a function of N<sub>conv</sub> (log-log scale). Red: untrimmed "
    "Tag CV is predicted to stay well above the 1/√N reference (grey dashed), indicating "
    "structural rather than finite-sample variability (N1). Blue: trimmed Tag CV remains "
    "below 1% at all sample sizes (N3). The CV ratio at N<sub>conv</sub> = 50,000 is predicted "
    "to exceed 5× (N2). X-axis: {3,125; 6,250; 12,500; 25,000; 50,000}.",
    sCaption))

# ============================================================
# 4. ANALYSIS PLAN
# ============================================================
story.append(Paragraph("4. Analysis Plan", sH1))

story.append(Paragraph("4.1 Investigation A: z-Distribution Analysis", sH2))
story.append(Paragraph(
    "For each of the 50 seeds at 17 MeV:",
    sBody))
story.append(Paragraph(
    "• Generate signal and conversion vertices using the frozen modules.",
    sBullet))
story.append(Paragraph(
    "• Compute the per-vertex λ values using mtag_v24.py.",
    sBullet))
story.append(Paragraph(
    "• Apply the k = 1% trim: identify the n<sub>rem</sub> = ⌊0.01 × N<sub>conv</sub>⌋ "
    "vertices from each tail of the conversion-λ distribution. Record their z positions.",
    sBullet))
story.append(Paragraph(
    "• Classify each removed vertex as <b>near-band</b> or <b>inter-band</b> using the "
    "17-band geometry positions from mtag_v24.py (d<sub>band</sub> boundary from §3.3).",
    sBullet))
story.append(Paragraph(
    "• For each removed vertex, also record whether p<sub>conv</sub> numerically "
    "equals the floor (P<sub>FLOOR</sub> = 10<super>−300</super>), and whether the vertex "
    "was removed from the upper tail, the lower tail, or both tails of the λ distribution. "
    "These three per-vertex flags (z-classification, floor status, λ-tail membership) "
    "are recorded independently.",
    sBullet))
story.append(Paragraph(
    "• Compute f<sub>inter</sub> = (number of inter-band removed vertices) / (total removed "
    "vertices) for each seed. Report the ensemble mean and standard deviation of "
    "f<sub>inter</sub>.",
    sBullet))

story.append(Paragraph("4.2 Investigation B: Background Elimination by Trimming", sH2))
story.append(Paragraph(
    "For each of the 50 seeds at 17 MeV:",
    sBody))
story.append(Paragraph(
    "• At the untrimmed Tag's optimal (t<sub>opt</sub>, mass-window) combination, identify "
    "all conversion vertices that pass the λ ≥ t cut and fall within the mass window. These "
    "are the B-contributing vertices. Denote their count n<sub>B</sub> and total weighted "
    "contribution B = n<sub>B</sub> × w (since all weights are identical).",
    sBullet))
story.append(Paragraph(
    "• Identify the removal mask: the set of vertices removed by the k = 1% trim "
    "(same mask used in Investigation A).",
    sBullet))
story.append(Paragraph(
    "• Compute the fraction of B eliminated by trimming: f<sub>B,rem</sub> = "
    "(number of B-contributing vertices in the removal mask) / n<sub>B</sub>. "
    "This directly measures how much background trimming removes at the fixed optimal cut.",
    sBullet))
story.append(Paragraph(
    "• Compute the enrichment ratio: (fraction of removed vertices that are B-contributing) / "
    "(fraction of all conversion vertices that are B-contributing). Note: B2 (enrichment &gt; 1) "
    "is algebraically derived from B1 and the fixed 2% removal fraction, so it is reported "
    "but not an independent judgment.",
    sBullet))
story.append(Paragraph(
    "• Report the fraction of removed B-contributing vertices that are floor-applied "
    "(p<sub>conv</sub> = P<sub>FLOOR</sub>). This connects Investigation A (z-distribution) "
    "to Investigation B (background elimination): floor-applied vertices may account for "
    "a large fraction of the removed background contributors, linking the two mechanisms.",
    sBullet))

story.append(Paragraph("4.3 Investigation C: N<sub>conv</sub> Scaling", sH2))
story.append(Paragraph(
    "For the first 10 seeds (i = 50–59) at 17 MeV, run the full Tag computation "
    "(untrimmed and trimmed) at five N<sub>conv</sub> values: {3125, 6250, 12500, 25000, "
    "50000}. The generation pipeline remains unchanged (1,500,000 conversion-photon candidates "
    "per seed); only the subsample() cap is varied. At f = 0.25, approximately 58,600–59,600 "
    "conversion vertices pass basic cuts per seed, so all five cap values lie well below the "
    "actual count. Each level therefore produces a genuinely distinct subsample, and no level "
    "collapses to 'use all available.' Weights are rescaled by subsample() to preserve the "
    "total cross-section at each cap.",
    sBody))
story.append(Paragraph(
    "For each N<sub>conv</sub>, compute:",
    sBody))
story.append(Paragraph(
    "• CV of the untrimmed Tag across the 10 seeds.",
    sBullet))
story.append(Paragraph(
    "• CV of the trimmed Tag across the 10 seeds.",
    sBullet))
story.append(Paragraph(
    "• Mean degradation ratio for both methods.",
    sBullet))
story.append(Paragraph(
    "• The ratio CV(untrimmed) / CV(trimmed) — the 'trimming benefit ratio.'",
    sBullet))
story.append(Spacer(1, 1*mm))
story.append(Paragraph(
    "If the extreme-λ leverage is a finite-sample effect, CV(untrimmed) should follow "
    "approximately CV ∝ 1/√N<sub>conv</sub>, and the trimming benefit ratio should approach "
    "1.0 at large N<sub>conv</sub>. If the leverage is structural, CV(untrimmed) should "
    "plateau and the trimming benefit ratio should remain large.",
    sBody))

story.append(Paragraph("4.4 Outputs", sH2))
story.append(Paragraph(
    "The post-registration code produces:",
    sBody))
story.append(Paragraph(
    "• A JSON file with per-seed results for all three investigations.",
    sBullet))
story.append(Paragraph(
    "• A NumPy archive (.npz) with arrays: z positions of removed vertices, "
    "near-band/inter-band classifications, per-vertex B contributions, overlap statistics, "
    "and N<sub>conv</sub> scaling curves.",
    sBullet))
story.append(Paragraph(
    "• Figures: (1) z-distribution of removed vs retained vertices with material-band overlay, "
    "(2) cumulative B contribution curve, (3) N<sub>conv</sub> scaling plot.",
    sBullet))

# ============================================================
# 5. PREDICTIONS
# ============================================================
story.append(Paragraph("5. Predictions", sH1))
story.append(Paragraph(
    "All predictions are for the E3 configuration (f = 0.25, η = 2.0, 17-band geometry) "
    "at m<sub>a</sub> = 17 MeV. Predictions are labelled CONFIRMED if the stated inequality "
    "or threshold is met; otherwise REFUTED. Predictions are classified into three tiers:",
    sBody))
story.append(Paragraph(
    "• <b>Core</b> predictions test the central hypothesis about the trimming mechanism.",
    sBullet))
story.append(Paragraph(
    "• <b>Secondary</b> predictions provide supporting evidence for the mechanism.",
    sBullet))
story.append(Paragraph(
    "• <b>Diagnostic</b> predictions are informative regardless of direction (designed to be "
    "direction-agnostic per the §10.7 lesson from v2.8).",
    sBullet))

story.append(Paragraph("5.1 z-Distribution Predictions (Investigation A)", sH2))

pred_a_header = [Paragraph("ID", sTH), Paragraph("Prediction", sTH),
                 Paragraph("Threshold", sTH), Paragraph("Tier", sTH),
                 Paragraph("Rationale", sTH)]
pred_a_rows = [
    [Paragraph("Z1", sTDB),
     Paragraph("Inter-band vertices<br/>dominate the<br/>removed set", sTDL),
     Paragraph("Mean f<sub>inter</sub> &gt; 0.5<br/>across 50 seeds", sTDL),
     Paragraph("Core", sTD),
     Paragraph("Inter-band vertices<br/>receive inflated λ<br/>from p<sub>conv</sub> floor;<br/>they should be<br/>over-represented<br/>in the tails", sTDL)],
    [Paragraph("Z2", sTDB),
     Paragraph("Inter-band fraction<br/>exceeds population<br/>baseline", sTDL),
     Paragraph("Mean f<sub>inter</sub>(removed)<br/>&gt; f<sub>inter</sub>(all conv)", sTDL),
     Paragraph("Core", sTD),
     Paragraph("If inter-band vertices<br/>are enriched in the<br/>removed set beyond<br/>their population share,<br/>the p<sub>conv</sub> floor is<br/>the driver", sTDL)],
    [Paragraph("Z3", sTDB),
     Paragraph("f<sub>inter</sub> is consistent<br/>across seeds", sTDL),
     Paragraph("CV(f<sub>inter</sub>) &lt; 20%<br/>across 50 seeds", sTDL),
     Paragraph("Secondary", sTD),
     Paragraph("Low CV would indicate<br/>the z-distribution of<br/>removed vertices is a<br/>stable geometric<br/>property, not a<br/>stochastic fluctuation", sTDL)],
]
story.append(make_table(pred_a_header, pred_a_rows, [14*mm, 36*mm, 38*mm, 18*mm, 40*mm]))

story.append(Spacer(1, 3*mm))
story.append(Paragraph("5.2 Background-Elimination Predictions (Investigation B)", sH2))

pred_b_header = [Paragraph("ID", sTH), Paragraph("Prediction", sTH),
                 Paragraph("Threshold", sTH), Paragraph("Tier", sTH),
                 Paragraph("Rationale", sTH)]
pred_b_rows = [
    [Paragraph("B1", sTDB),
     Paragraph("Trimming removes<br/>majority of<br/>background", sTDL),
     Paragraph("Mean f<sub>B,rem</sub> &gt; 0.5<br/>(trimming eliminates<br/>&gt;50% of B)", sTDL),
     Paragraph("Core", sTD),
     Paragraph("v2.8 shows B drops<br/>from ≈3.6 to ≈0<br/>after trimming;<br/>the removal mask<br/>should capture most<br/>B-contributing vertices", sTDL)],
    [Paragraph("B2", sTDB),
     Paragraph("B-contributing vertices<br/>are enriched in the<br/>removed set", sTDL),
     Paragraph("Mean enrichment<br/>ratio &gt; 1<br/>(B-contributors over-<br/>represented among<br/>removed vertices)", sTDL),
     Paragraph("Derived", sTD),
     Paragraph("Derived from B1:<br/>enrichment = f<sub>B,rem</sub><br/>/ (removal fraction).<br/>With 2% removal,<br/>B1 &gt; 0.5 implies<br/>B2 &gt; 25×. Reported<br/>but not an independent<br/>judgment", sTDL)],
    [Paragraph("B3", sTDB),
     Paragraph("B-elimination fraction<br/>is consistent<br/>across seeds", sTDL),
     Paragraph("CV(f<sub>B,rem</sub>) &lt; 20%<br/>across 50 seeds", sTDL),
     Paragraph("Secondary", sTD),
     Paragraph("Low CV would indicate<br/>the overlap between<br/>extreme-λ tails and<br/>B-contributors is a<br/>stable geometric<br/>property", sTDL)],
]
story.append(make_table(pred_b_header, pred_b_rows, [14*mm, 36*mm, 38*mm, 18*mm, 40*mm]))

story.append(Spacer(1, 3*mm))
story.append(Paragraph("5.3 N<sub>conv</sub> Scaling Predictions (Investigation C)", sH2))

pred_c_header = [Paragraph("ID", sTH), Paragraph("Prediction", sTH),
                 Paragraph("Threshold", sTH), Paragraph("Tier", sTH),
                 Paragraph("Rationale", sTH)]
pred_c_rows = [
    [Paragraph("N1", sTDB),
     Paragraph("Untrimmed CV does<br/>not follow 1/√N<br/>scaling", sTDL),
     Paragraph("CV(N=50k) / CV(N=3125)<br/>&gt; (3125/50000)<super>0.5</super><br/>= 0.25", sTDL),
     Paragraph("Diagnostic", sTD),
     Paragraph("If the leverage is<br/>structural (p<sub>conv</sub><br/>floor geometry),<br/>CV should plateau,<br/>not scale as 1/√N", sTDL)],
    [Paragraph("N2", sTDB),
     Paragraph("Trimming benefit<br/>persists at large<br/>N<sub>conv</sub>", sTDL),
     Paragraph("CV(untrim)/CV(trim)<br/>&gt; 5 at<br/>N<sub>conv</sub> = 50k", sTDL),
     Paragraph("Diagnostic", sTD),
     Paragraph("If trimming addresses<br/>a structural artefact,<br/>it should remain<br/>necessary even with<br/>more statistics", sTDL)],
    [Paragraph("N3", sTDB),
     Paragraph("Trimmed Tag CV<br/>is stable across<br/>N<sub>conv</sub>", sTDL),
     Paragraph("CV(trimmed) &lt; 1%<br/>at all five N<sub>conv</sub><br/>values", sTDL),
     Paragraph("Secondary", sTD),
     Paragraph("Trimmed Tag should<br/>be insensitive to<br/>N<sub>conv</sub> because the<br/>extreme-λ fraction<br/>is removed", sTDL)],
]
story.append(make_table(pred_c_header, pred_c_rows, [14*mm, 36*mm, 38*mm, 18*mm, 40*mm]))

# ============================================================
# 6. IMPLEMENTATION NOTES
# ============================================================
story.append(Paragraph("6. Implementation Notes", sH1))

story.append(Paragraph("6.1 Code Structure", sH2))
story.append(Paragraph(
    "The post-registration code will consist of:",
    sBody))
story.append(Paragraph(
    "<b>run_v29_diagnostics.py</b> — Orchestrator that runs the three diagnostic "
    "investigations. For Investigation A, it extracts the removal mask and classifies "
    "removed vertices by z position. For Investigation B, it computes per-vertex B "
    "contributions at the optimal threshold. For Investigation C, it reruns the Tag "
    "computation at multiple N<sub>conv</sub> values. Imports endcap_sim.py and "
    "mtag_v24.py (frozen). Outputs a JSON file with per-seed results and a NumPy "
    "archive (.npz).",
    sBullet))
story.append(Paragraph(
    "<b>generate_figures.py</b> — Generates diagnostic figures from the saved results.",
    sBullet))
story.append(Paragraph(
    "<b>generate_v29_postreg.py</b> — Generates the post-registration PDF from the "
    "saved results, including tables and figures for all predictions.",
    sBullet))

story.append(Paragraph("6.2 Frozen Components", sH2))
story.append(Paragraph(
    "The following modules are frozen from previous versions and must not be modified:",
    sBody))
story.append(Paragraph(
    "• endcap_sim.py — Simulation engine (frozen since v2.5). Generates 300,000 signal and "
    "1,500,000 conversion-photon candidates; after basic cuts, subsample() retains up to "
    "N<sub>sig</sub> = 50,000 signal and up to N<sub>conv</sub> = 100,000 conversion vertices. "
    "For Investigation C, the N<sub>conv</sub> cap is varied; this is achieved by passing "
    "a different max_conv parameter to subsample(), not by modifying the module.",
    sBullet))
story.append(Paragraph(
    "• mtag_v24.py — Tag formula, 17-band geometry (frozen since v2.4). Provides the material-"
    "band positions, thicknesses, and p<sub>conv</sub> computation used to classify vertices "
    "as near-band or inter-band in Investigation A.",
    sBullet))
story.append(Paragraph(
    "• mtag_v22.py — 9-band baseline for endcap_sim import (frozen since v2.2).",
    sBullet))

story.append(Paragraph("6.3 Computational Requirements", sH2))
story.append(Paragraph(
    "Investigations A and B analyse the internal structure of simulations that are already "
    "run as part of the standard Tag computation. The main cost is Investigation C, which "
    "requires 10 seeds × 5 N<sub>conv</sub> values × 2 methods (trimmed/untrimmed) = 100 "
    "Tag scans. All five N<sub>conv</sub> caps (3125–50000) lie below the default "
    "N<sub>conv</sub> = 100,000, so each scan is faster than a standard run. "
    "Total computation is well within the resources used for the v2.8 50-seed ensemble.",
    sBody))

# ============================================================
# 7. SUCCESS CRITERIA AND INTERPRETATION GUIDE
# ============================================================
story.append(Paragraph("7. Success Criteria and Interpretation Guide", sH1))

story.append(Paragraph(
    "This study is diagnostic rather than evaluative: unlike v2.8 (which tested whether to "
    "<i>adopt</i> trimmed Tag), v2.9 investigates <i>why</i> trimming works. Accordingly, "
    "the success criteria focus on explanatory power rather than a pass/fail adoption decision.",
    sBody))
story.append(Spacer(1, 1*mm))

story.append(Paragraph(
    "<b>Strong mechanistic understanding:</b> All 3 core predictions {Z1, Z2, B1} "
    "CONFIRMED. This would establish that (a) inter-band conversion vertices with inflated "
    "λ from the p<sub>conv</sub> floor are over-represented among the trimmed vertices, "
    "and (b) the removal mask captures a majority of the B-contributing vertices (B1). "
    "B2 (enrichment) is derived from B1 and the fixed 2% removal fraction, so it is reported "
    "but not counted as an independent judgment. Additionally, the fraction of removed "
    "B-contributing vertices that are floor-applied will be reported to connect the z-distribution "
    "(Investigation A) to background elimination (Investigation B). Together, these would link "
    "the p<sub>conv</sub> floor to background elimination. Note: concluding that the floor is "
    "the <i>root cause</i> would additionally require a control experiment (e.g., varying "
    "P<sub>FLOOR</sub>) beyond this study's scope.",
    sBody))
story.append(Spacer(1, 1*mm))
story.append(Paragraph(
    "<b>Partial understanding:</b> 1 or 2 of {Z1, Z2, B1} CONFIRMED. The mechanism is "
    "partially identified but not complete — for example, if inter-band vertices dominate "
    "the removed set (Z1, Z2 CONFIRMED) but the removed set captures little B "
    "(B1 REFUTED), trimming may improve sensitivity by a route other than direct "
    "B-elimination at the fixed optimal cut.",
    sBody))
story.append(Spacer(1, 1*mm))
story.append(Paragraph(
    "<b>Unexpected mechanism:</b> 0 of {Z1, Z2, B1} CONFIRMED. The trimming "
    "improvement has a mechanism that is not primarily driven by inter-band vertices or "
    "direct B-elimination. This would be a valuable negative result, redirecting attention "
    "to alternative explanations (e.g., near-band Δχ<super>2</super> effects, signal-side "
    "interactions, or correlation structure in the λ distribution).",
    sBody))
story.append(Spacer(1, 1*mm))
story.append(Paragraph(
    "<b>Scaling insight (N1, N2):</b> These diagnostic predictions are designed to be "
    "informative regardless of direction. If N1 is CONFIRMED (CV does not follow 1/√N), "
    "the data are <i>consistent with</i> structural leverage — a necessary condition for a "
    "geometric artefact, though not conclusive on its own (a plateau or root-cause diagnosis "
    "would require a wider N<sub>conv</sub> range or a P<sub>FLOOR</sub> variation experiment). "
    "N1 is refuted if the endpoint CV ratio is ≤ 0.25.",
    sBody))
story.append(Spacer(1, 1*mm))
story.append(Paragraph(
    "<b>Secondary predictions (Z3, B3, N3)</b> provide supporting detail but do not affect "
    "the mechanistic interpretation. Z3 tests whether the z-distribution pattern is stable "
    "across seeds; B3 tests whether the B-elimination fraction is consistent; N3 confirms "
    "trimmed Tag stability.",
    sBody))

# ============================================================
# 8. SUMMARY OF PREDICTIONS
# ============================================================
story.append(Paragraph("8. Summary of Predictions", sH1))

sum_header = [Paragraph("ID", sTH), Paragraph("Short Description", sTH),
              Paragraph("Criterion", sTH), Paragraph("Tier", sTH)]
sum_rows = [
    [Paragraph("Z1", sTD), Paragraph("Inter-band vertices dominate removed set", sTDL),
     Paragraph("Mean f<sub>inter</sub> &gt; 0.5", sTDL), Paragraph("Core", sTD)],
    [Paragraph("Z2", sTD), Paragraph("Inter-band enrichment above baseline", sTDL),
     Paragraph("f<sub>inter</sub>(removed) &gt; f<sub>inter</sub>(all)", sTDL), Paragraph("Core", sTD)],
    [Paragraph("Z3", sTD), Paragraph("f<sub>inter</sub> consistent across seeds", sTDL),
     Paragraph("CV(f<sub>inter</sub>) &lt; 20%", sTDL), Paragraph("Secondary", sTD)],
    [Paragraph("B1", sTD), Paragraph("Trimming removes majority of background", sTDL),
     Paragraph("Mean f<sub>B,rem</sub> &gt; 0.5", sTDL), Paragraph("Core", sTD)],
    [Paragraph("B2", sTD), Paragraph("B-contributors enriched in removed set", sTDL),
     Paragraph("Mean enrichment &gt; 1", sTDL), Paragraph("Derived", sTD)],
    [Paragraph("B3", sTD), Paragraph("B-elimination fraction consistent across seeds", sTDL),
     Paragraph("CV(f<sub>B,rem</sub>) &lt; 20%", sTDL), Paragraph("Secondary", sTD)],
    [Paragraph("N1", sTD), Paragraph("Untrimmed CV does not follow 1/√N", sTDL),
     Paragraph("CV ratio &gt; 0.25", sTDL), Paragraph("Diagnostic", sTD)],
    [Paragraph("N2", sTD), Paragraph("Trimming benefit persists at large N", sTDL),
     Paragraph("CV(untrim)/CV(trim) &gt; 5 at 50k", sTDL), Paragraph("Diagnostic", sTD)],
    [Paragraph("N3", sTD), Paragraph("Trimmed CV stable across N<sub>conv</sub>", sTDL),
     Paragraph("CV(trimmed) &lt; 1% at all N", sTDL), Paragraph("Secondary", sTD)],
]
story.append(make_table(sum_header, sum_rows, [14*mm, 50*mm, 55*mm, 22*mm]))
story.append(Spacer(1, 2*mm))
story.append(Paragraph(
    "<b>Total: 9 predictions.</b> 3 z-distribution (Z1–Z3), 3 background (B1–B3), "
    "3 N<sub>conv</sub> scaling (N1–N3). Core predictions: {Z1, Z2, B1}. "
    "B2 is derived from B1 (enrichment = f<sub>B,rem</sub> / removal fraction) and is "
    "reported but not counted as an independent core judgment.",
    sBody))

# ============================================================
# 9. FUTURE DIRECTIONS
# ============================================================
story.append(Paragraph("9. Future Directions", sH1))

story.append(Paragraph(
    "The diagnostic findings from v2.9 will inform the prioritisation of subsequent studies. "
    "The following directions remain from the v2.8 post-registration roadmap (§10), updated "
    "to reflect the diagnostic context.",
    sBody))

story.append(Paragraph("9.1 Signal-Side λ Regularisation", sH2))
story.append(Paragraph(
    "If Investigation A confirms that inter-band conversion vertices dominate the removed set "
    "(Z1, Z2 CONFIRMED), the same p<sub>conv</sub> floor mechanism affects signal vertices "
    "in inter-band gaps. Regularising p<sub>conv</sub> for <i>signal</i> vertices — imposing "
    "a physical minimum above the P<sub>FLOOR</sub> = 10<super>−300</super> — could reduce the extreme "
    "signal-vertex λ tail. The v2.7 finding that signal-vertex randomness contributes only "
    "0.19% of Tag variance suggests the effect may be small, but the v2.9 diagnostics will "
    "reveal whether the same p<sub>conv</sub> floor artefact operates on both populations. "
    "Any change to the tag formula itself would require a fresh preregistration.",
    sBody))

story.append(Paragraph("9.2 Extension to Other Configurations and Mass Grid", sH2))
story.append(Paragraph(
    "The diagnostic results at f = 0.25 may not generalise to other material scales. At "
    "higher f (denser material), more conversions occur near bands and fewer in gaps, "
    "potentially changing the inter-band/near-band balance revealed by Investigation A. "
    "A systematic scan over f ∈ {0.10, 0.25, 0.50, 1.00} with the same diagnostic "
    "decomposition would map how the trimming mechanism varies with material density. "
    "The v2.8 results suggest trimming is concentrated at low mass (17 MeV); a broader "
    "mass grid (5–500 MeV) would identify the boundary of the regime where trimming "
    "provides benefit.",
    sBody))

story.append(Paragraph("9.3 Alternative Discriminator Architectures", sH2))
story.append(Paragraph(
    "If Investigation B shows the removal mask captures most B-contributing vertices "
    "(B1 CONFIRMED), this suggests a targeted "
    "pre-filter approach: rather than trimming a fixed 1% of the λ distribution, a future "
    "discriminator could directly identify and remove the inter-band conversion vertices "
    "that contribute most to B. Such a 'targeted material-aware trimming' approach could "
    "achieve the benefits of the current trimming procedure with a physical rather than "
    "statistical criterion, potentially making it more robust to changes in geometry and "
    "material scale.",
    sBody))

story.append(Paragraph(
    "9.4 Dimuon Control Sample (ALP → μ<super>+</super>μ<super>−</super>)", sH2))
story.append(Paragraph(
    "The dimuon control channel (§10.5 of v2.8 post-reg) remains a valuable cross-check: "
    "if the degradation ratio approaches 1.0 when conversion-photon background is absent, "
    "it confirms that the signal loss mechanism is material-interaction driven. The v2.9 "
    "diagnostics address the same question from the other direction (by directly examining "
    "the removed background vertices), so the two studies are complementary.",
    sBody))

story.append(Paragraph("9.5 GSF Tracking and Realistic Validation", sH2))
story.append(Paragraph(
    "Gaussian-Sum Filter tracking (§10.6 of v2.8) and the phased validation programme "
    "(MadGraph5 + Pythia8, Delphes, Geant4; §10.8) remain longer-term directions. The v2.9 "
    "diagnostic results may inform which aspects of the validation programme are most "
    "informative: if inter-band vertices dominate the removed set (Z1, Z2 CONFIRMED), "
    "realistic photon-conversion modelling in Geant4 — where the p<sub>conv</sub> "
    "distribution is physics-driven rather than formula-driven — would be the highest-priority "
    "validation step. A control experiment varying P<sub>FLOOR</sub> alone (§10.2 scope) "
    "would be needed to confirm the floor as the root cause.",
    sBody))

# ============================================================
# 10. DOI CHAIN
# ============================================================
story.append(Paragraph("10. DOI Chain", sH1))

doi_header = [Paragraph("Version", sTH), Paragraph("DOI", sTH),
              Paragraph("Description", sTH)]
doi_rows = [
    [Paragraph("v2.9 prereg (this)", sTD),
     Paragraph("10.5281/zenodo.24466187", sTDL),
     Paragraph("Background-Focused Diagnostics prereg", sTDL)],
    [Paragraph("v2.8 post-reg", sTD),
     Paragraph("10.5281/zenodo.24437855", sTDL),
     Paragraph("Trimmed Tag Estimator results", sTDL)],
    [Paragraph("v2.8 prereg", sTD),
     Paragraph("10.5281/zenodo.24414960", sTDL),
     Paragraph("Trimmed Tag Estimator prereg", sTDL)],
    [Paragraph("v2.7 post-reg", sTD),
     Paragraph("10.5281/zenodo.24408990", sTDL),
     Paragraph("Tag Formula Diagnostics results", sTDL)],
    [Paragraph("v2.7 prereg", sTD),
     Paragraph("10.5281/zenodo.24388228", sTDL),
     Paragraph("Tag Formula Diagnostics prereg", sTDL)],
    [Paragraph("v2.6 post-reg", sTD),
     Paragraph("10.5281/zenodo.24373115", sTDL),
     Paragraph("Multi-Seed Ensemble results", sTDL)],
    [Paragraph("v2.6 prereg", sTD),
     Paragraph("10.5281/zenodo.24361872", sTDL),
     Paragraph("Multi-Seed Ensemble prereg", sTDL)],
    [Paragraph("v2.5 results", sTD),
     Paragraph("10.5281/zenodo.24341050", sTDL),
     Paragraph("Deconflation post-reg", sTDL)],
    [Paragraph("v2.5 prereg", sTD),
     Paragraph("10.5281/zenodo.24329044", sTDL),
     Paragraph("Deconflation prereg", sTDL)],
    [Paragraph("v2.4 results", sTD),
     Paragraph("10.5281/zenodo.24302619", sTDL),
     Paragraph("17-band geometry post-reg", sTDL)],
    [Paragraph("v2.4 prereg", sTD),
     Paragraph("10.5281/zenodo.24296796", sTDL),
     Paragraph("17-band geometry prereg", sTDL)],
    [Paragraph("v2.3 results", sTD),
     Paragraph("10.5281/zenodo.24273586", sTDL),
     Paragraph("Endcap tag post-reg", sTDL)],
    [Paragraph("v2.3 prereg", sTD),
     Paragraph("10.5281/zenodo.24244893", sTDL),
     Paragraph("Endcap tag prereg", sTDL)],
    [Paragraph("v2.2 results", sTD),
     Paragraph("10.5281/zenodo.24238224", sTDL),
     Paragraph("Barrel → endcap post-reg", sTDL)],
    [Paragraph("v2.2 prereg", sTD),
     Paragraph("10.5281/zenodo.24189990", sTDL),
     Paragraph("Barrel → endcap prereg", sTDL)],
    [Paragraph("v2.1 results", sTD),
     Paragraph("10.5281/zenodo.24136462", sTDL),
     Paragraph("Barrel material-veto post-reg", sTDL)],
    [Paragraph("v2.1 prereg", sTD),
     Paragraph("10.5281/zenodo.24063091", sTDL),
     Paragraph("Barrel material-veto prereg", sTDL)],
    [Paragraph("v2.0", sTD),
     Paragraph("10.5281/zenodo.24056097", sTDL),
     Paragraph("Initial barrel study", sTDL)],
]
story.append(make_table(doi_header, doi_rows, [30*mm, 55*mm, 60*mm]))

# ============================================================
# 11. REFERENCES
# ============================================================
story.append(Paragraph("11. References", sH1))

story.append(Paragraph("11.1 External References", sH2))

refs_ext = [
    "[E1] J. Alimena, F. Blekman, C. Cazzaniga, X. Cid Vidal, J. Niedziela, L. Rygaard, "
    "R. Soto Rey, \"Hunting for Long-Lived ALPs in Top Events via Displaced Dielectron "
    "Pairs at the LHC,\" arXiv:2610.38932 [hep-ph] (2026) (motivating analysis: "
    "generator-level sensitivity study for displaced ALP → e<super>+</super>e<super>−</super> "
    "in tt̄ events at the CMS detector).",

    "[E2] L. Rygaard, J. Niedziela, R. Schäfer, S. Bruggisser, J. Alimena, S. Westhoff, "
    "F. Blekman, \"Top Secrets: Long-Lived ALPs in Top Production,\" arXiv:2306.08686 "
    "[hep-ph] (2023) (predecessor analysis: displaced di-muon ALP search strategy in "
    "tt̄ production at the LHC and HL-LHC).",

    "[E3] A. L. Read, \"Presentation of search results: the CL<sub>s</sub> technique,\" "
    "J. Phys. G <b>28</b> (2002) 2693 (upper-limit methodology background).",

    "[E4] D. Curtin et al., \"Long-Lived Particles at the Energy Frontier: The MATHUSLA "
    "Physics Case,\" Rep. Prog. Phys. <b>82</b> (2019) 116201, arXiv:1806.07396 "
    "(displaced-vertex physics context).",

    "[E5] NumPy v1.26, numpy.org (pseudo-random number generation, array operations).",
    "[E6] ReportLab v5.0.1, reportlab.com (PDF generation).",
    "[E7] SciPy v1.14, scipy.org (Pearson correlation, scipy.stats.pearsonr).",
]

sRef = ParagraphStyle("Ref", fontName="DejaVu", fontSize=7.5,
                      leading=10, textColor=DARK,
                      leftIndent=8*mm, firstLineIndent=-8*mm,
                      spaceAfter=1.5*mm)
for ref in refs_ext:
    story.append(Paragraph(ref, sRef))

story.append(Paragraph("11.2 Internal References (ALP-ttbar Toy MC Series)", sH2))

refs_int = [
    "[I1] W. S. Paik, \"ALP-ttbar Toy MC v2.8 — Post-Registration: Trimmed Tag Estimator "
    "Results,\" DOI: 10.5281/zenodo.24437855 (confirmed trimmed Tag as default; 8/9 predictions "
    "confirmed; identified two-part improvement mechanism via REFUTED X1 — the primary "
    "motivation for this diagnostic study).",

    "[I2] W. S. Paik, \"ALP-ttbar Toy MC v2.8 — Preregistration: Trimmed Tag Estimator as "
    "Default,\" DOI: 10.5281/zenodo.24414960 (preregistered the adoption study).",

    "[I3] W. S. Paik, \"ALP-ttbar Toy MC v2.7 — Post-Registration: Tag Formula Diagnostics "
    "Results,\" DOI: 10.5281/zenodo.24408990 (identified conversion-background dominance, "
    "trimming effectiveness, and Winsorising failure).",

    "[I4] W. S. Paik, \"ALP-ttbar Toy MC v2.7 — Preregistration: Tag Formula Diagnostics,\" "
    "DOI: 10.5281/zenodo.24388228.",

    "[I5] W. S. Paik, \"ALP-ttbar Toy MC v2.6 — Post-Registration: Multi-Seed Ensemble "
    "Results,\" DOI: 10.5281/zenodo.24373115 (50-seed ensemble, identified Tag CV ≈ 7.4%).",

    "[I6] W. S. Paik, \"ALP-ttbar Toy MC v2.6 — Preregistration: Multi-Seed Ensemble,\" "
    "DOI: 10.5281/zenodo.24361872.",

    "[I7] W. S. Paik, \"ALP-ttbar Toy MC v2.5 — Post-Registration: Deconflation,\" "
    "DOI: 10.5281/zenodo.24341050.",

    "[I8] W. S. Paik, \"ALP-ttbar Toy MC v2.5 — Preregistration: Deconflation,\" "
    "DOI: 10.5281/zenodo.24329044.",

    "[I9] W. S. Paik, \"ALP-ttbar Toy MC v2.4 — Post-Registration: 17-Band Geometry,\" "
    "DOI: 10.5281/zenodo.24302619 (introduced the 17-band geometry used here).",

    "[I10] W. S. Paik, \"ALP-ttbar Toy MC v2.4 — Preregistration: 17-Band Geometry,\" "
    "DOI: 10.5281/zenodo.24296796.",
]

for ref in refs_int:
    story.append(Paragraph(ref, sRef))

# --- Build ---
doc.build(story)

from pypdf import PdfReader
reader = PdfReader(OUT_PDF)
n_pages = len(reader.pages)
size_mb = os.path.getsize(OUT_PDF) / (1024 * 1024)
print(f"PDF generated: {n_pages} pages, {size_mb:.2f} MB")
print(f"  → {OUT_PDF}")
