# -*- coding: utf-8 -*-
# Figure 2 - Hydrodynamic characterization (5 panels)
# Revised for Hydrogeology Journal technical-editor comments (HYJO-D-26-00525R1)

import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# ══════════════════════════════════════════════════════════════
#  USER SETTINGS
# ══════════════════════════════════════════════════════════════

EXCEL_PATH = r"c:\Users\mhaghi2\Desktop\Article 9\data\hydrodynamice\hydrodynamic.xlsx"
SHEET_NAME = "hydrodynamic"
OUTPUT     = r"c:\Users\mhaghi2\Desktop\Article 9\map\Fig2.pdf"
ALSO_PNG   = True          # also write a PNG copy for quick viewing
DPI        = 1000          # applies to the PNG, and to any RASTER element
                           # inside the PDF. Lines and text in the PDF are
                           # vector: they have no resolution and stay sharp
                           # at any zoom or print size, whatever DPI says.

SYM_COL  = "Symbol"
NAME_COL = "Spring"
Q_COLUMNS = ["Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
Q_LABELS  = ["Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

HIGH_Q_SYMS = ["S4","S8","S10","Q1"]

FIG_W  = 22
FIG_H  = 20
HSPACE = 0.2
WSPACE = 0.34    # horizontal gap between left and right panels.
                 # Raise this if the (a) right-hand axis title and the
                 # (b) left-hand axis title still sit too close together.

LABEL_FONTSIZE  = 20
LABEL_X         = 0.00
LABEL_Y         = 1.02
AXIS_TITLE_SIZE = 20
AXIS_TICK_SIZE  = 18

# ══════════════════════════════════════════════════════════════
#  EDITOR FIX 1  -  panels (a) and (c):
#  distance between the RIGHT vertical axis and its title.
#  Increase these numbers if the title still touches the value labels.
# ══════════════════════════════════════════════════════════════
RIGHT_AXIS_LABELPAD_A = 34     # panel (a) right-hand axis title offset
RIGHT_AXIS_LABELPAD_C = 38     # panel (c) right-hand axis title offset

# ══════════════════════════════════════════════════════════════
#  EDITOR FIX 2  -  panel (b):
#  the alpha value printed at the END of each curve is now switched
#  off, since the same values are already labelled in panel (c).
#  Set SHOW to True to bring them back; the font size is then used.
# ══════════════════════════════════════════════════════════════
PANEL_B_SHOW_ALPHA     = False  # True = print alpha at the end of each line
PANEL_B_ALPHA_FONTSIZE = 13
PANEL_B_ALPHA_XOFFSET  = 243
PANEL_B_ALPHA_BOLD     = True

LEG_FONTSIZE_A = 17
LEG_FONTSIZE_C = 17
LEG_FONTSIZE_D = 17
LEG_FONTSIZE_E = 15

LEG_LOC_A = "upper right"
LEG_LOC_C = "upper right"
LEG_LOC_D = "upper right"
LEG_LOC_E = "upper right"

LEG_BBOX_A = None
LEG_BBOX_C = None
LEG_BBOX_D = None
LEG_BBOX_E = None

REC_LINE_WIDTH     = 2.5
REC_MARKER_SIZE    = 14
REC_LABEL_FONTSIZE = 13
REC_COLOR          = "#C0392B"

# ── PANEL (c) text sizes ──
PANEL_C_XTICK_FONTSIZE  = 13
PANEL_C_CLASS_FONTSIZE  = 12
PANEL_C_VALUE_FONTSIZE  = 12
PANEL_C_ALPHA_FONTSIZE  = REC_LABEL_FONTSIZE

# ── PANEL (d) text sizes ──
PANEL_D_XTICK_FONTSIZE = 13
PANEL_D_CLASS_FONTSIZE = 11
PANEL_D_VALUE_FONTSIZE = 11

# ── PANEL (e) ──
PANEL_E_POINT_SIZE   = 270
PANEL_E_LABEL_SIZE   = 12
PANEL_E_SHOW_CORR    = True
PANEL_E_CORR_COLOR   = "#34495E"
PANEL_E_CORR_LS      = "--"
PANEL_E_CORR_LW      = 1.8
PANEL_E_NOTE_SIZE    = 11

# Keep text as real text in the PDF (editable, scalable, never pixelated)
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"]  = 42

SHARED_STYLE = {
    "S1":  {"color":"#E67E22","lw":1.8,"ls":"-",   "marker":"o","ms":6,"obs_ms":6},
    "S2":  {"color":"#27AE60","lw":1.8,"ls":"-",   "marker":"s","ms":6,"obs_ms":6},
    "S3":  {"color":"#8E44AD","lw":1.6,"ls":"--",  "marker":"^","ms":6,"obs_ms":6},
    "S4":  {"color":"#1A5C96","lw":2.5,"ls":"-",   "marker":"o","ms":8,"obs_ms":8},
    "S5":  {"color":"#F39C12","lw":1.5,"ls":":",   "marker":"D","ms":5,"obs_ms":5},
    "S6":  {"color":"#16A085","lw":1.5,"ls":"-.",  "marker":"v","ms":5,"obs_ms":5},
    "S7":  {"color":"#E74C3C","lw":1.5,"ls":"--",  "marker":"p","ms":5,"obs_ms":5},
    "S8":  {"color":"#2E86C1","lw":2.2,"ls":"-",   "marker":"s","ms":6,"obs_ms":6},
    "S9":  {"color":"#C0392B","lw":1.8,"ls":"--",  "marker":"p","ms":5,"obs_ms":5},
    "S10": {"color":"#5DADE2","lw":2.0,"ls":"--",  "marker":"^","ms":6,"obs_ms":6},
    "S11": {"color":"#884EA0","lw":1.5,"ls":":",   "marker":"*","ms":7,"obs_ms":7},
    "S12": {"color":"#17A589","lw":1.5,"ls":"-.",  "marker":"h","ms":5,"obs_ms":5},
    "S13": {"color":"#D35400","lw":1.5,"ls":":",   "marker":"8","ms":5,"obs_ms":5},
    "S14": {"color":"#1A5276","lw":1.5,"ls":"--",  "marker":"P","ms":5,"obs_ms":5},
    "Q1":  {"color":"#7F8C8D","lw":2.0,"ls":":",   "marker":"D","ms":7,"obs_ms":7},
    "Q2":  {"color":"#ABB2B9","lw":1.5,"ls":"--",  "marker":"d","ms":5,"obs_ms":5},
    "Q3":  {"color":"#5D6D7E","lw":1.5,"ls":"-.",  "marker":"D","ms":5,"obs_ms":5},
    "Q4":  {"color":"#283747","lw":1.5,"ls":":",   "marker":"d","ms":5,"obs_ms":5},
}
DEF_ST = {"color":"#888888","lw":1.5,"ls":"-","marker":"o","ms":5,"obs_ms":5}

# ══════════════════════════════════════════════════════════════
#  READ DATA & CALCULATE RECESSION PARAMETERS
# ══════════════════════════════════════════════════════════════

def load_data(path, sheet, sym_col, name_col, q_cols):
    df = pd.read_excel(path, engine="openpyxl", sheet_name=sheet)
    df.columns = [str(c).strip() for c in df.columns]
    springs = {}
    for _, row in df.iterrows():
        sym  = str(row.get(sym_col,"")).strip()
        name = str(row.get(name_col,"")).strip()
        if not sym or sym == "nan": continue
        Q = []
        for col in q_cols:
            try:    Q.append(float(row[col]))
            except: Q.append(None)
        Q_clean = [v for v in Q if v is not None and v > 0]
        if len(Q_clean) < 2: continue
        Q_arr = np.array(Q_clean, dtype=float)
        Q0, Qt = Q_arr[0], Q_arr[-1]
        if Q0 <= 0 or Qt <= 0: continue
        t       = np.arange(len(Q_arr))
        lr      = np.log(Q_arr / Q0)
        alpha_m = max(float(-np.polyfit(t, lr, 1)[0]), 0.0001)
        alpha_d = alpha_m / 30.0
        i_idx   = max(0.0, (Q0 - Qt) / Q0)
        V_Mm3   = max(0.0, (Q0 - Qt) / alpha_d * 86400 / 1e6)
        t0_days = np.log(Q0 / Qt) / alpha_d if alpha_d > 0 and Qt > 0 else 0
        springs[sym] = {
            "name": name, "Q": Q_clean,
            "Q0": Q0, "Qt": Qt,
            "alpha": alpha_d, "alpha_m": alpha_m,
            "i": i_idx, "V": V_Mm3,
            "t0": t0_days,
        }
    return springs

try:
    DATA = load_data(EXCEL_PATH, SHEET_NAME, SYM_COL, NAME_COL, Q_COLUMNS)
    print("[Data] Loaded %d springs." % len(DATA))
except Exception as e:
    print("[Data] ERROR: %s - using hardcoded fallback." % e)
    DATA = {
        "S1": {"name":"Chamborak",  "Q":[17.25,15.00,12.40,10.27,8.76,7.80,7.00,6.84],
               "Q0":17.25,"Qt":6.84,"alpha":0.00470,"alpha_m":0.1409,"i":0.603,"V":191.50,"t0":198},
        "S2": {"name":"Pebbleh",    "Q":[11.09,10.00,9.11,8.00,7.10,6.40,6.00,5.73],
               "Q0":11.09,"Qt":5.73,"alpha":0.00332,"alpha_m":0.0995,"i":0.483,"V":139.68,"t0":203},
        "S3": {"name":"Nazarkardeh","Q":[13.00,12.00,10.96,9.96,9.05,8.45,8.02,7.88],
               "Q0":13.00,"Qt":7.88,"alpha":0.00254,"alpha_m":0.0762,"i":0.394,"V":174.27,"t0":199},
        "S4": {"name":"Valian",     "Q":[142.00,124.19,95.50,68.60,40.40,20.50,11.43,8.00],
               "Q0":142.00,"Qt":8.00,"alpha":0.01477,"alpha_m":0.4430,"i":0.944,"V":784.08,"t0":197},
        "S5": {"name":"Sirud",      "Q":[1.40,1.25,1.06,0.85,0.64,0.51,0.40,0.37],
               "Q0":1.40,"Qt":0.37,"alpha":0.00690,"alpha_m":0.2071,"i":0.733,"V":12.84,"t0":196},
        "S6": {"name":"Azadbar",    "Q":[2.46,2.10,1.50,0.90,0.60,0.37,0.24,0.18],
               "Q0":2.46,"Qt":0.18,"alpha":0.01337,"alpha_m":0.4010,"i":0.926,"V":14.71,"t0":197},
        "S8": {"name":"Sepahsalar", "Q":[41.70,34.93,26.80,18.10,11.20,7.40,4.82,4.00],
               "Q0":41.70,"Qt":4.00,"alpha":0.01216,"alpha_m":0.3649,"i":0.904,"V":267.79,"t0":196},
        "S9": {"name":"Hassankdar", "Q":[4.90,4.00,3.00,2.04,1.43,0.97,0.70,0.62],
               "Q0":4.90,"Qt":0.62,"alpha":0.01069,"alpha_m":0.3206,"i":0.873,"V":34.61,"t0":196},
        "S10":{"name":"Goshnadar",  "Q":[36.20,31.94,26.30,20.71,17.00,14.80,13.29,12.90],
               "Q0":36.20,"Qt":12.90,"alpha":0.00537,"alpha_m":0.1610,"i":0.644,"V":375.02,"t0":191},
        "Q1": {"name":"Shalamzar",  "Q":[40.15,37.37,34.43,31.36,29.62,28.21,27.41,26.87],
               "Q0":40.15,"Qt":26.87,"alpha":0.00199,"alpha_m":0.0597,"i":0.331,"V":576.42,"t0":203},
    }

ALL_SYMS  = list(DATA.keys())
high_syms = [s for s in HIGH_Q_SYMS if s in DATA]
low_syms  = [s for s in ALL_SYMS if s not in high_syms]

# ══════════════════════════════════════════════════════════════
#  KARST CLASS
# ══════════════════════════════════════════════════════════════

def karst_class(sym, i, alpha_m):
    if i >= 0.90 and alpha_m >= 0.20:                return "I"
    if i >= 0.85 or (i >= 0.70 and alpha_m >= 0.10): return "II"
    if i >= 0.65:                                     return "III"
    if i >= 0.45:                                     return "IV"
    return "V"

CLASS_COLOR = {"I":"#1A3A6C","II":"#1A5C96","III":"#2E86C1",
               "IV":"#5DADE2","V":"#D6EAF8"}
CLASS_LABEL = {
    "I":  "Class I - conduit-dominant",
    "II": "Class II - well-developed",
    "III":"Class III - moderate",
    "IV": "Class IV - fissure/transitional",
    "V":  "Class V - stable/alluvial",
}

for sym, d in DATA.items():
    d["class"]     = karst_class(sym, d["i"], d["alpha_m"])
    d["bar_color"] = CLASS_COLOR[d["class"]]

# ══════════════════════════════════════════════════════════════
#  FIGURE LAYOUT
# ══════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor="white")
gs  = gridspec.GridSpec(3, 2, figure=fig,
                        height_ratios=[1.0, 1.2, 1.0],
                        hspace=HSPACE, wspace=WSPACE,
                        left=0.07, right=0.95,
                        top=0.97, bottom=0.05)

ax_a = fig.add_subplot(gs[0, 0])
ax_b = fig.add_subplot(gs[0, 1])
ax_c = fig.add_subplot(gs[1, :])
ax_d = fig.add_subplot(gs[2, 0])
ax_e = fig.add_subplot(gs[2, 1])

for ax in [ax_a, ax_b, ax_c, ax_d, ax_e]:
    ax.set_facecolor("#FAFAFA")
    for sp in ax.spines.values():
        sp.set_color("#CCCCCC"); sp.set_linewidth(0.7)

def panel_label(ax, letter):
    ax.text(LABEL_X, LABEL_Y, "(%s)" % letter,
            transform=ax.transAxes,
            fontsize=LABEL_FONTSIZE, fontweight="bold",
            color="#1C1C1C", va="bottom", ha="right")

# ══════════════════════════════════════════════════════════════
#  PANEL (a)  MONTHLY DISCHARGE HYDROGRAPHS
# ══════════════════════════════════════════════════════════════

ax_ar = ax_a.twinx()
leg_a = []

for sym in high_syms:
    d = DATA[sym]; st = SHARED_STYLE.get(sym, DEF_ST)
    Q = d["Q"]; t = np.arange(len(Q))
    ax_a.plot(t, Q, color=st["color"], lw=st["lw"], ls=st["ls"],
              marker=st["marker"], ms=st["ms"],
              markerfacecolor="white", markeredgewidth=1.3, zorder=4)
    leg_a.append(Line2D([],[],color=st["color"],lw=st["lw"],ls=st["ls"],
        marker=st["marker"],ms=st["ms"],markerfacecolor="white",
        markeredgewidth=1.3, label="%s %s" % (sym, d["name"])))

for sym in low_syms:
    d = DATA[sym]; st = SHARED_STYLE.get(sym, DEF_ST)
    Q = d["Q"]; t = np.arange(len(Q))
    ax_ar.plot(t, Q, color=st["color"], lw=st["lw"], ls=st["ls"],
               marker=st["marker"], ms=st["ms"],
               markerfacecolor="white", markeredgewidth=1.2,
               zorder=3, alpha=0.92)
    leg_a.append(Line2D([],[],color=st["color"],lw=st["lw"],ls=st["ls"],
        marker=st["marker"],ms=st["ms"],markerfacecolor="white",
        markeredgewidth=1.2, label="%s %s" % (sym, d["name"])))

n_pts  = max(len(d["Q"]) for d in DATA.values())
t_ax   = np.arange(n_pts)
x_lbls = (Q_LABELS + ["C%d" % (i+1) for i in range(len(Q_LABELS), n_pts)])[:n_pts]

ax_a.set_xticks(t_ax)
ax_a.set_xticklabels(x_lbls, fontsize=AXIS_TICK_SIZE, rotation=30, ha="right")
ax_a.set_xlabel("Month", fontsize=AXIS_TITLE_SIZE)
ax_a.set_ylabel("$Q$ (L/s) - %s" % ", ".join(high_syms),
                fontsize=AXIS_TITLE_SIZE,
                color=SHARED_STYLE.get(high_syms[0], DEF_ST)["color"] if high_syms else "#333")

# FIX 1a: push the right-hand axis title away from its value labels
ax_ar.set_ylabel("$Q$ (L/s) - others",
                 fontsize=AXIS_TITLE_SIZE-1, color="#555",
                 rotation=-90, labelpad=RIGHT_AXIS_LABELPAD_A)

ax_a.tick_params(axis="both", labelsize=AXIS_TICK_SIZE)
ax_ar.tick_params(axis="y", labelsize=AXIS_TICK_SIZE-1, colors="#555")
ax_a.yaxis.grid(True, ls=":", lw=0.5, color="#DDD", zorder=0)

ncol_a = 2 if len(ALL_SYMS) > 5 else 1
kw_a = dict(fontsize=LEG_FONTSIZE_A, framealpha=0.88,
            edgecolor="#CCC", labelspacing=0.22, ncol=ncol_a)
if LEG_BBOX_A: ax_a.legend(handles=leg_a, bbox_to_anchor=LEG_BBOX_A, **kw_a)
else:          ax_a.legend(handles=leg_a, loc=LEG_LOC_A, **kw_a)
panel_label(ax_a, "a")

# ══════════════════════════════════════════════════════════════
#  PANEL (b)  SEMI-LOG RECESSION CURVES
#  FIX 2: alpha labels at the end of each line are now sized by
#         PANEL_B_ALPHA_FONTSIZE (top of file).
# ══════════════════════════════════════════════════════════════

t_days = np.linspace(0, 240, 500)
b_weight = "bold" if PANEL_B_ALPHA_BOLD else "normal"

for sym, d in DATA.items():
    st    = SHARED_STYLE.get(sym, DEF_ST)
    Q0    = d["Q0"]
    alpha = d["alpha"]
    Q_fit = Q0 * np.exp(-alpha * t_days)
    ax_b.semilogy(t_days, Q_fit,
                  color=st["color"], lw=st["lw"], ls=st["ls"], zorder=4)
    t_total = (len(d["Q"]) - 1) * 30
    ax_b.semilogy([0, t_total], [Q0, d["Qt"]],
                  marker=st["marker"], ms=st["obs_ms"],
                  color=st["color"], markerfacecolor="white",
                  markeredgewidth=1.2, linestyle="none", zorder=5)
    if PANEL_B_SHOW_ALPHA:
        ax_b.text(PANEL_B_ALPHA_XOFFSET, Q_fit[-1],
                  r"$\alpha$ = %.4f" % alpha,
                  fontsize=PANEL_B_ALPHA_FONTSIZE, color=st["color"],
                  va="center", fontweight=b_weight)

# no trailing labels to clear, so the axis ends with the curves
ax_b.set_xlim(-5, 260) if not PANEL_B_SHOW_ALPHA else ax_b.set_xlim(-5, 330)
ax_b.set_xlabel("Time (days from peak discharge)", fontsize=AXIS_TITLE_SIZE)
ax_b.set_ylabel("log $Q$ (L/s)", fontsize=AXIS_TITLE_SIZE)
ax_b.tick_params(axis="both", labelsize=AXIS_TICK_SIZE)
ax_b.yaxis.grid(True, which="both", ls=":", lw=0.4, color="#DDD")
ax_b.xaxis.grid(True, ls=":", lw=0.4, color="#DDD")
panel_label(ax_b, "b")

# ══════════════════════════════════════════════════════════════
#  PANEL (c)  KARST DEVELOPMENT RANKING
#  FIX 1c: right-axis title spacing.
#  FIX 3 : "(Mm3)" replaced by "(x10^6 m^3)" with superscripts.
# ══════════════════════════════════════════════════════════════

ranked = sorted(DATA.items(), key=lambda x: x[1]["V"], reverse=True)
V_vals = [d["V"]         for _, d in ranked]
alphas = [d["alpha"]     for _, d in ranked]
names  = [d["name"]      for _, d in ranked]
sids_r = [sid            for sid, _ in ranked]
bcols  = [d["bar_color"] for _, d in ranked]
blines = [SHARED_STYLE.get(s, DEF_ST)["color"] for s in sids_r]

x     = np.arange(len(ranked))
ax_cr = ax_c.twinx()

ax_c.bar(x, V_vals, width=0.60, color=bcols,
         edgecolor=blines, linewidth=2.0, zorder=3)

for xi, d_item, v in zip(x, [d for _, d in ranked], V_vals):
    fc = "white" if d_item["class"] in ["I","II","III"] else "#333"
    ax_c.text(xi, v * 0.44, "Class\n%s" % d_item["class"],
              ha="center", va="center",
              fontsize=PANEL_C_CLASS_FONTSIZE, color=fc, fontweight="bold")

for xi, v in zip(x, V_vals):
    ax_c.text(xi, v + max(V_vals) * 0.012, "%.1f" % v,
              ha="center", va="bottom",
              fontsize=PANEL_C_VALUE_FONTSIZE, color="#1C1C1C", fontweight="bold")

ax_cr.plot(x, alphas, color=REC_COLOR, lw=REC_LINE_WIDTH,
           alpha=0.50, zorder=4)
ax_cr.plot(x, alphas, marker="D", ms=REC_MARKER_SIZE,
           color=REC_COLOR, markeredgecolor="white",
           markeredgewidth=1.3, linestyle="none", zorder=5)
for xi, a in zip(x, alphas):
    ax_cr.text(xi, a + max(alphas) * 0.05, "%.4f" % a,
               ha="center", va="bottom",
               fontsize=PANEL_C_ALPHA_FONTSIZE,
               color=REC_COLOR, fontweight="bold")

xlbls = ["%s\n%s" % (sid, name) for sid, name in zip(sids_r, names)]
ax_c.set_xticks(x)
ax_c.set_xticklabels(xlbls, fontsize=PANEL_C_XTICK_FONTSIZE)

# FIX 3: units written as x10^6 m^3 with true superscripts
ax_c.set_ylabel(r"Dynamic storage volume $V$ ($\times$10$^{6}$ m$^{3}$)",
                fontsize=AXIS_TITLE_SIZE, color="#1C1C1C")

# FIX 1c: push the right-hand axis title away from its value labels
ax_cr.set_ylabel(r"Recession coefficient $\alpha$ (day$^{-1}$)",
                 fontsize=AXIS_TITLE_SIZE, color=REC_COLOR,
                 rotation=-90, labelpad=RIGHT_AXIS_LABELPAD_C)

ax_c.tick_params(axis="y", labelsize=AXIS_TICK_SIZE)
ax_cr.tick_params(axis="y", labelsize=AXIS_TICK_SIZE, colors=REC_COLOR)
ax_c.yaxis.grid(True, ls=":", lw=0.5, color="#DDD", zorder=0)
ax_c.set_xlim(-0.55, len(ranked) - 0.45)
ax_c.set_ylim(0, max(V_vals) * 1.28)

class_patches = [Patch(facecolor=CLASS_COLOR[c], edgecolor="#AAA",
                        label=CLASS_LABEL[c])
                 for c in ["I","II","III","IV","V"]]
alpha_h = Line2D([0],[0], marker="D", color=REC_COLOR,
                 markeredgecolor="white", ms=REC_MARKER_SIZE,
                 lw=REC_LINE_WIDTH,
                 label=r"Recession coeff. $\alpha$ (day$^{-1}$)")

kw_c = dict(fontsize=LEG_FONTSIZE_C, framealpha=0.90,
            edgecolor="#CCC", labelspacing=0.25, ncol=3)
if LEG_BBOX_C: ax_c.legend(handles=class_patches+[alpha_h],
                            bbox_to_anchor=LEG_BBOX_C, **kw_c)
else:          ax_c.legend(handles=class_patches+[alpha_h],
                            loc=LEG_LOC_C, **kw_c)
panel_label(ax_c, "c")

# ══════════════════════════════════════════════════════════════
#  PANEL (d)  DRYING TIME (t0) BAR CHART
# ══════════════════════════════════════════════════════════════

ranked_t0 = sorted(DATA.items(), key=lambda x: x[1]["t0"], reverse=True)
t0_vals   = [d["t0"]        for _, d in ranked_t0]
t0_sids   = [sid            for sid, _ in ranked_t0]
t0_bcols  = [d["bar_color"] for _, d in ranked_t0]
t0_blines = [SHARED_STYLE.get(s, DEF_ST)["color"] for s in t0_sids]

x_d = np.arange(len(ranked_t0))

ax_d.bar(x_d, t0_vals, width=0.62, color=t0_bcols,
         edgecolor=t0_blines, linewidth=1.8, zorder=3)

for xi, d_item, v in zip(x_d, [d for _, d in ranked_t0], t0_vals):
    fc = "white" if d_item["class"] in ["I","II","III"] else "#333"
    ax_d.text(xi, v * 0.44, "Class\n%s" % d_item["class"],
              ha="center", va="center",
              fontsize=PANEL_D_CLASS_FONTSIZE, color=fc, fontweight="bold")

for xi, v in zip(x_d, t0_vals):
    ax_d.text(xi, v + max(t0_vals) * 0.012, "%.0f" % v,
              ha="center", va="bottom",
              fontsize=PANEL_D_VALUE_FONTSIZE, color="#1C1C1C", fontweight="bold")

ax_d.set_xticks(x_d)
ax_d.set_xticklabels(t0_sids, fontsize=PANEL_D_XTICK_FONTSIZE)
ax_d.set_ylabel(r"Drying time $t_{0}$ (days)", fontsize=AXIS_TITLE_SIZE)
ax_d.tick_params(axis="y", labelsize=AXIS_TICK_SIZE)
ax_d.yaxis.grid(True, ls=":", lw=0.5, color="#DDD", zorder=0)
ax_d.set_xlim(-0.55, len(ranked_t0) - 0.45)
ax_d.set_ylim(0, max(t0_vals) * 1.22)

kw_d = dict(fontsize=LEG_FONTSIZE_D, framealpha=0.90,
            edgecolor="#CCC", labelspacing=0.25, ncol=2)
if LEG_BBOX_D: ax_d.legend(handles=class_patches, bbox_to_anchor=LEG_BBOX_D, **kw_d)
else:          ax_d.legend(handles=class_patches, loc=LEG_LOC_D, **kw_d)

panel_label(ax_d, "d")

# ══════════════════════════════════════════════════════════════
#  PANEL (e)  V vs alpha SCATTER
# ══════════════════════════════════════════════════════════════

leg_e = []

for sym, d in DATA.items():
    st = SHARED_STYLE.get(sym, DEF_ST)
    ax_e.scatter(d["alpha"], d["V"],
                 color=st["color"],
                 s=PANEL_E_POINT_SIZE, marker=st["marker"],
                 edgecolors="white", linewidths=1.2,
                 zorder=5)
    ax_e.annotate(sym,
                  xy=(d["alpha"], d["V"]),
                  xytext=(4, 4), textcoords="offset points",
                  fontsize=PANEL_E_LABEL_SIZE, color=st["color"], fontweight="bold")
    leg_e.append(Line2D([],[],
        color=st["color"], lw=0,
        marker=st["marker"], ms=8,
        markerfacecolor=st["color"],
        markeredgecolor="white", markeredgewidth=1.2,
        label="%s %s (Class %s)" % (sym, d["name"], d["class"])))

if PANEL_E_SHOW_CORR:
    alpha_arr = np.array([d["alpha"] for d in DATA.values()], dtype=float)
    V_arr     = np.array([d["V"]     for d in DATA.values()], dtype=float)
    if len(alpha_arr) >= 2:
        slope, intercept = np.polyfit(alpha_arr, V_arr, 1)
        x_fit = np.linspace(alpha_arr.min(), alpha_arr.max(), 100)
        y_fit = slope * x_fit + intercept
        r_val = np.corrcoef(alpha_arr, V_arr)[0, 1]
        ax_e.plot(x_fit, y_fit,
                  color=PANEL_E_CORR_COLOR, ls=PANEL_E_CORR_LS,
                  lw=PANEL_E_CORR_LW, zorder=3)
        leg_e.append(Line2D([],[],
            color=PANEL_E_CORR_COLOR, ls=PANEL_E_CORR_LS, lw=PANEL_E_CORR_LW,
            label=r"Linear correlation ($r$ = %.2f)" % r_val))

ax_e.set_xlabel(r"Recession coefficient $\alpha$ (day$^{-1}$)", fontsize=AXIS_TITLE_SIZE)
ax_e.set_ylabel(r"Dynamic storage volume $V$ ($\times$10$^{6}$ m$^{3}$)",
                fontsize=AXIS_TITLE_SIZE)
ax_e.tick_params(axis="both", labelsize=AXIS_TICK_SIZE)
ax_e.yaxis.grid(True, ls=":", lw=0.4, color="#DDD")
ax_e.xaxis.grid(True, ls=":", lw=0.4, color="#DDD")

ax_e.text(0.97, 0.97,
          "Upper-left: large storage,\nslow drainage\n(well-developed karst)\n\n"
          "Lower-right: small storage,\nfast drainage\n(conduit-dominant)",
          transform=ax_e.transAxes, fontsize=PANEL_E_NOTE_SIZE, color="#555",
          va="top", ha="right",
          bbox=dict(boxstyle="round,pad=0.4", facecolor="#F0F4F8",
                    edgecolor="#CCC", alpha=0.9))

ncol_e = 2 if len(ALL_SYMS) > 5 else 1
kw_e = dict(fontsize=LEG_FONTSIZE_E, framealpha=0.88,
            edgecolor="#CCC", labelspacing=0.22, ncol=ncol_e)
if LEG_BBOX_E: ax_e.legend(handles=leg_e, bbox_to_anchor=LEG_BBOX_E, **kw_e)
else:          ax_e.legend(handles=leg_e, loc=LEG_LOC_E, **kw_e)
panel_label(ax_e, "e")

# ══════════════════════════════════════════════════════════════
#  SAVE
# ══════════════════════════════════════════════════════════════

out_dir = os.path.dirname(OUTPUT)
if out_dir: os.makedirs(out_dir, exist_ok=True)

plt.savefig(OUTPUT, dpi=DPI, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print("[Done] Saved -> %s" % OUTPUT)

if ALSO_PNG:
    png_path = os.path.splitext(OUTPUT)[0] + ".png"
    plt.savefig(png_path, dpi=DPI, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    print("[Done] Saved -> %s" % png_path)

plt.close()
