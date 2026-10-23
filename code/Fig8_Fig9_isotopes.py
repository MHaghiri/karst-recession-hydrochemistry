"""
Isotope hydrology plots - Figures 8 and 9
==========================================
Reads "Isotope.xlsx" (Sheet1 = isotope/hydrochemistry data, IMWL = Iran
Meteoric Water Line data) and "study_area.shp", and produces:

FIGURE 8 - Isotopic source identification & spatial distribution (2 x 2)
    (a) d2H vs d18O with GMWL, LMWL and IMWL
    (b) d18O vs Elevation
    (c) Deuterium excess vs d18O
    (d) Spatial map of d18O at the sampling points

FIGURE 9 - Group comparison & hydrochemistry (2 x 2)
    (a) Boxplot of d18O by water type
    (b) Boxplot of d2H by water type
    (c) EC vs d18O (+ linear fit)
    (d) Temperature vs Elevation (+ linear fit)

Revised for Hydrogeology Journal technical-editor comments (HYJO-D-26-00525R1):
  Figs 8, 9 - "delta-" -> "δ"; mass numbers set as superscripts (δ¹⁸O, δ²H)
            - "spring", "qanat", "well" -> "Spring", "Qanat", "Well"
  8a, 9b    - "D" changed: hydrogen isotope written as δ²H, matching the
              manuscript text (see HYDROGEN_ISOTOPE_STYLE to switch to δD)
  8b, 9d    - "Altitude" -> "Elevation"
  8c        - "*" -> "×"
  9c        - "micro-" -> "μ"  (EC in μS/cm)
  9d        - "deg C" -> "°C"; "C/1000m" -> "°C/1000 m";
              "R2" -> R² with R italic and 2 superscript (upright)
  Output written as PDF (vector, for submission) and PNG.

The figures are SAVED ONLY (plt.show() is not called).
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

# Keep text as real text in the PDF (editable, scalable, never pixelated)
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"]  = 42

# ----------------------------------------------------------------------
# 1. FILE PATHS
# ----------------------------------------------------------------------
INPUT_FILE = r"c:\Users\mhaghi2\Desktop\Article 9\data\Isotop\Isotope.xlsx"
SHAPEFILE_PATH = r"c:\Users\mhaghi2\Desktop\Article 9\data\study_area.shp"
OUTPUT_DIR = r"C:\Users\mhaghi2\Desktop\Article 9\map"

FIG8_BASENAME = "Fig8"
FIG9_BASENAME = "Fig9"
FIG_DPI       = 1000

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# 2. CONFIG
# ----------------------------------------------------------------------

# --- hydrogen isotope notation (EDITOR FIX 8a / 9b) ---------------------
# "2H" -> δ²H  (matches the manuscript text and HJ isotope convention)
# "D"  -> δD
HYDROGEN_ISOTOPE_STYLE = "2H"

# --- display names for water types (EDITOR FIX: capitalised) -----------
DISPLAY_NAME = {
    "spring": "Spring",
    "qanat":  "Qanat",
    "well":   "Well",
    "River":  "River",
    "Snow":   "Snow",
    "Rain":   "Rain",
}

# --- global font sizes -------------------------------------------------
AXIS_LABEL_FONTSIZE = 16
TICK_FONTSIZE       = 14
LEGEND_FONTSIZE     = 15
PANEL_LABEL_FONTSIZE = 18
POINT_LABEL_OFFSET = (4, 4)

# --- per-panel POINT (marker) SIZE --------------------------------------
POINT_SIZE = {
    "fig1": {"a": 120, "b": 120, "c": 120, "d": 120},
    "fig2": {"c": 120, "d": 120},
}

# --- per-panel POINT-LABEL font size -------------------------------------
POINT_LABEL_FONTSIZE = {
    "fig1": {"a": 9, "b": 11, "c": 11, "d": 11},
    "fig2": {"c": 11, "d": 11},
}

# --- spacing between panels --------------------------------------------
FIG1_WSPACE, FIG1_HSPACE = 0.17, 0.15
FIG2_WSPACE, FIG2_HSPACE = 0.25, 0.15   # Fig 9: wider left-right gap (was 0.15)

# --- panel label positions (axes fraction) -----------------------------
PANEL_LABEL_POS = {
    "fig1": {"a": (0.03, 0.97), "b": (0.03, 0.97),
             "c": (0.03, 0.97), "d": (0.03, 0.97)},
    "fig2": {"a": (0.03, 0.97), "b": (0.03, 0.97),
             "c": (0.03, 0.97), "d": (0.03, 0.97)},
}

# --- legend positions ---------------------------------------------------
LEGEND_POS = {
    "fig1": {
        "a": dict(loc=(0.7, 0.01)),
        "b": dict(loc="best"),
        "c": dict(loc="best"),
        "d": dict(loc="lower right"),
    },
    "fig2": {
        "c": dict(loc="best"),
        "d": dict(loc="best"),
    },
}

# ----------------------------------------------------------------------
# 3. LOAD MAIN DATA (Sheet1)
# ----------------------------------------------------------------------
df = pd.read_excel(INPUT_FILE, sheet_name="Sheet1")
df.columns = [str(c).strip() for c in df.columns]

rename_map = {}
for c in df.columns:
    cl = c.lower()
    if cl == "o18":
        rename_map[c] = "d18O"
    elif cl == "d":
        rename_map[c] = "dD"
    elif "altitude" in cl:
        rename_map[c] = "Altitude"
    elif "temp" in cl:
        rename_map[c] = "Temp"
    elif cl == "ec":
        rename_map[c] = "EC"
    elif cl == "tds":
        rename_map[c] = "TDS"
    elif cl == "x":
        rename_map[c] = "X"
    elif cl == "y":
        rename_map[c] = "Y"
df = df.rename(columns=rename_map)

df_main = df[df["name"].notna()].copy()
df_main["name"] = df_main["name"].replace({"Rian": "Rain"})

style = {
    "spring": dict(color="tab:blue",   marker="o"),
    "qanat":  dict(color="tab:green",  marker="s"),
    "well":   dict(color="tab:brown",  marker="^"),
    "River":  dict(color="tab:cyan",   marker="D"),
    "Snow":   dict(color="tab:purple", marker="*"),
    "Rain":   dict(color="tab:orange", marker="v"),
}
group_order = ["spring", "qanat", "well", "River", "Snow", "Rain"]
group_order = [g for g in group_order if g in df_main["name"].unique()]

def disp(g):
    """Display name for a water-type key (capitalised)."""
    return DISPLAY_NAME.get(g, str(g).capitalize())

blue_tones = {
    "spring": "#1f77b4",
    "qanat":  "#6baed6",
    "well":   "#08519c",
    "River":  "#9ecae1",
    "Snow":   "#3182bd",
    "Rain":   "#4292c6",
}

# ----------------------------------------------------------------------
# 4. AXIS LABELS  (EDITOR FIXES: δ, superscript mass numbers, units)
# ----------------------------------------------------------------------
PERMIL = "\u2030"
D18O   = "\u03b4$^{18}$O"                                   # δ¹⁸O
DH     = "\u03b4$^{2}$H" if HYDROGEN_ISOTOPE_STYLE == "2H" else "\u03b4D"

LBL_D18O    = "%s (%s)" % (D18O, PERMIL)
LBL_DD      = "%s (%s)" % (DH, PERMIL)
LBL_DEXCESS = "d-excess = %s \u2212 8 \u00d7 %s (%s)" % (DH, D18O, PERMIL)   # × not *
LBL_ALT     = "Elevation (m a.s.l.)"
LBL_EC      = "EC (\u03bcS/cm)"                              # μS/cm
LBL_TEMP    = "Temperature (\u00b0C)"                        # °C

# ----------------------------------------------------------------------
# 5. HELPER FUNCTIONS
# ----------------------------------------------------------------------
def style_axis(ax):
    ax.tick_params(axis="both", labelsize=TICK_FONTSIZE)
    ax.xaxis.label.set_size(AXIS_LABEL_FONTSIZE)
    ax.yaxis.label.set_size(AXIS_LABEL_FONTSIZE)


def add_panel_label(ax, fig_key, panel_key):
    x, y = PANEL_LABEL_POS[fig_key][panel_key]
    ax.text(x, y, "(%s)" % panel_key, transform=ax.transAxes,
            fontsize=PANEL_LABEL_FONTSIZE, fontweight="bold",
            va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none", alpha=0.7))


def add_legend(ax, fig_key, panel_key, **extra_kwargs):
    cfg = LEGEND_POS.get(fig_key, {}).get(panel_key, dict(loc="best"))
    cfg = dict(cfg)
    cfg.setdefault("fontsize", LEGEND_FONTSIZE)
    cfg.update(extra_kwargs)
    ax.legend(**cfg)


def get_point_size(fig_key, panel_key):
    return POINT_SIZE.get(fig_key, {}).get(panel_key, 60)


def get_point_label_fontsize(fig_key, panel_key):
    return POINT_LABEL_FONTSIZE.get(fig_key, {}).get(panel_key, 10)


def add_point_labels(ax, x, y, labels, fig_key, panel_key):
    fontsize = get_point_label_fontsize(fig_key, panel_key)
    for xv, yv, lab in zip(x, y, labels):
        ax.annotate(str(lab), (xv, yv), textcoords="offset points",
                    xytext=POINT_LABEL_OFFSET, fontsize=fontsize)


def boxplot_compat(ax, data, labels, **kwargs):
    try:
        return ax.boxplot(data, tick_labels=labels, **kwargs)
    except TypeError:
        return ax.boxplot(data, labels=labels, **kwargs)


def color_boxplot_blue(bxp, groups):
    for patch, g in zip(bxp["boxes"], groups):
        patch.set_facecolor(blue_tones[g])
        patch.set_alpha(0.7)


def save_both(fig, basename):
    for ext in ("pdf", "png"):
        path = os.path.join(OUTPUT_DIR, "%s.%s" % (basename, ext))
        fig.savefig(path, dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
        print("Saved:", path)
    plt.close(fig)


# ----------------------------------------------------------------------
# 6. METEORIC WATER LINES
# ----------------------------------------------------------------------
def gmwl(x):
    return 8 * x + 10

precip = df_main[df_main["name"].isin(["Rain", "Snow"])]
lmwl_slope, lmwl_int = np.polyfit(precip["d18O"], precip["dD"], 1)

def lmwl(x):
    return lmwl_slope * x + lmwl_int

imwl_slope, imwl_int = None, None
try:
    imwl_df = pd.read_excel(INPUT_FILE, sheet_name="IMWL")
    imwl_df.columns = [str(c).strip() for c in imwl_df.columns]
    col_o18, col_d = None, None
    for c in imwl_df.columns:
        cleaned = re.sub(r"[^a-zA-Z0-9]", "", c).lower()
        if "18" in cleaned and col_o18 is None:
            col_o18 = c
        elif cleaned in ("d", "dd", "deltad") and col_d is None:
            col_d = c
    if col_o18 is not None and col_d is not None:
        x = imwl_df[col_o18].dropna().astype(float)
        y = imwl_df[col_d].dropna().astype(float)
        n = min(len(x), len(y))
        imwl_slope, imwl_int = np.polyfit(x.iloc[:n], y.iloc[:n], 1)
    else:
        print("Could not auto-detect columns in 'IMWL' sheet; IMWL line skipped.",
              list(imwl_df.columns))
except Exception as e:
    print("Note: 'IMWL' sheet not found or unreadable -> IMWL line skipped.", e)

def imwl(x):
    return imwl_slope * x + imwl_int

# ----------------------------------------------------------------------
# 7. d-excess
# ----------------------------------------------------------------------
df_main["d_excess"] = df_main["dD"] - 8 * df_main["d18O"]

# ----------------------------------------------------------------------
# FIGURE 8
# ----------------------------------------------------------------------
fig1, axes1 = plt.subplots(2, 2, figsize=(13, 11))

# (a) δ2H vs δ18O with meteoric water lines
ax = axes1[0, 0]
for g in group_order:
    sub = df_main[df_main["name"] == g]
    ax.scatter(sub["d18O"], sub["dD"], label=disp(g), s=get_point_size("fig1", "a"),
               edgecolor="k", linewidth=0.5, **style[g])
    add_point_labels(ax, sub["d18O"], sub["dD"], sub["label"], "fig1", "a")

x_range = np.linspace(df_main["d18O"].min() - 1, df_main["d18O"].max() + 1, 100)
ax.plot(x_range, gmwl(x_range), "k--", label="GMWL")
ax.plot(x_range, lmwl(x_range), "r-", label="LMWL")
if imwl_slope is not None:
    ax.plot(x_range, imwl(x_range), "g-.", label="IMWL")

ax.set_xlabel(LBL_D18O)
ax.set_ylabel(LBL_DD)
style_axis(ax)
add_panel_label(ax, "fig1", "a")
add_legend(ax, "fig1", "a")

# (b) δ18O vs Elevation
ax = axes1[0, 1]
for g in group_order:
    sub = df_main[df_main["name"] == g]
    ax.scatter(sub["d18O"], sub["Altitude"], label=disp(g), s=get_point_size("fig1", "b"),
               edgecolor="k", linewidth=0.5, **style[g])
    add_point_labels(ax, sub["d18O"], sub["Altitude"], sub["label"], "fig1", "b")

if len(precip) >= 2:
    p_slope, p_int = np.polyfit(precip["d18O"], precip["Altitude"], 1)
    xr = np.linspace(df_main["d18O"].min() - 1, df_main["d18O"].max() + 1, 100)
    ax.plot(xr, p_slope * xr + p_int, "r--", label="Precip. trend")

ax.set_xlabel(LBL_D18O)
ax.set_ylabel(LBL_ALT)
style_axis(ax)
add_panel_label(ax, "fig1", "b")
add_legend(ax, "fig1", "b")

# (c) d-excess vs δ18O
ax = axes1[1, 0]
for g in group_order:
    sub = df_main[df_main["name"] == g]
    ax.scatter(sub["d18O"], sub["d_excess"], label=disp(g), s=get_point_size("fig1", "c"),
               edgecolor="k", linewidth=0.5, **style[g])
    add_point_labels(ax, sub["d18O"], sub["d_excess"], sub["label"], "fig1", "c")

ax.axhline(10, color="k", linestyle="--", linewidth=1, label="GMWL d-excess = 10")
ax.set_xlabel(LBL_D18O)
ax.set_ylabel(LBL_DEXCESS)
style_axis(ax)
add_panel_label(ax, "fig1", "c")
add_legend(ax, "fig1", "c")

# (d) Spatial map
ax = axes1[1, 1]
df_xy = df_main.dropna(subset=["X", "Y"])

gdf = None
if not df_xy.empty:
    vmin, vmax = df_xy["d18O"].min(), df_xy["d18O"].max()
    try:
        import geopandas as gpd
        gdf = gpd.read_file(SHAPEFILE_PATH)
        minx, miny, maxx, maxy = gdf.total_bounds
    except Exception as e:
        print("Note: study-area shapefile not found/unreadable -> using data extent.", e)
        pad_x = (df_xy["X"].max() - df_xy["X"].min()) * 0.1
        pad_y = (df_xy["Y"].max() - df_xy["Y"].min()) * 0.1
        minx, maxx = df_xy["X"].min() - pad_x, df_xy["X"].max() + pad_x
        miny, maxy = df_xy["Y"].min() - pad_y, df_xy["Y"].max() + pad_y

    if gdf is not None:
        gdf.boundary.plot(ax=ax, color="black", linewidth=1.2, zorder=2)
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)

    sc = None
    for g in group_order:
        sub = df_xy[df_xy["name"] == g]
        if sub.empty:
            continue
        sc = ax.scatter(sub["X"], sub["Y"], c=sub["d18O"], cmap="viridis",
                        marker=style[g]["marker"], s=get_point_size("fig1", "d"),
                        edgecolor="k", linewidth=0.7,
                        vmin=vmin, vmax=vmax, label=disp(g), zorder=3)
        add_point_labels(ax, sub["X"], sub["Y"], sub["label"], "fig1", "d")

    cbar = fig1.colorbar(sc, ax=ax)
    cbar.set_label(LBL_D18O, fontsize=AXIS_LABEL_FONTSIZE)
    cbar.ax.tick_params(labelsize=TICK_FONTSIZE)

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    style_axis(ax)
    ax.set_xticks([])
    ax.set_yticks([])
    add_panel_label(ax, "fig1", "d")
    add_legend(ax, "fig1", "d")
    ax.set_aspect("equal", adjustable="datalim")
else:
    ax.text(0.5, 0.5, "No X/Y coordinates available", ha="center", va="center")
    add_panel_label(ax, "fig1", "d")

fig1.tight_layout()
fig1.subplots_adjust(wspace=FIG1_WSPACE, hspace=FIG1_HSPACE)
save_both(fig1, FIG8_BASENAME)

# ----------------------------------------------------------------------
# FIGURE 9
# ----------------------------------------------------------------------
fig2, axes2 = plt.subplots(2, 2, figsize=(13, 11))
group_labels = [disp(g) for g in group_order]

# (a) Boxplot of δ18O
ax = axes2[0, 0]
data_o18 = [df_main.loc[df_main["name"] == g, "d18O"] for g in group_order]
bxp_a = boxplot_compat(ax, data_o18, group_labels, showmeans=True, patch_artist=True)
color_boxplot_blue(bxp_a, group_order)
ax.set_ylabel(LBL_D18O)
style_axis(ax)
add_panel_label(ax, "fig2", "a")

# (b) Boxplot of δ2H
ax = axes2[0, 1]
data_d = [df_main.loc[df_main["name"] == g, "dD"] for g in group_order]
bxp_b = boxplot_compat(ax, data_d, group_labels, showmeans=True, patch_artist=True)
color_boxplot_blue(bxp_b, group_order)
ax.set_ylabel(LBL_DD)
style_axis(ax)
add_panel_label(ax, "fig2", "b")

# (c) EC vs δ18O
ax = axes2[1, 0]
for g in group_order:
    sub = df_main[df_main["name"] == g]
    ax.scatter(sub["d18O"], sub["EC"], label=disp(g), s=get_point_size("fig2", "c"),
               edgecolor="k", linewidth=0.5, **style[g])
    add_point_labels(ax, sub["d18O"], sub["EC"], sub["label"], "fig2", "c")

slope_c, int_c, r_c, p_c, se_c = stats.linregress(df_main["d18O"], df_main["EC"])
xr = np.linspace(df_main["d18O"].min(), df_main["d18O"].max(), 100)
ax.plot(xr, slope_c * xr + int_c, "k--", linewidth=1.5, label="Linear fit")

ax.set_xlabel(LBL_D18O)
ax.set_ylabel(LBL_EC)
style_axis(ax)
add_panel_label(ax, "fig2", "c")
add_legend(ax, "fig2", "c")

# (d) Temperature vs Elevation
ax = axes2[1, 1]
for g in group_order:
    sub = df_main[df_main["name"] == g]
    ax.scatter(sub["Altitude"], sub["Temp"], label=disp(g), s=get_point_size("fig2", "d"),
               edgecolor="k", linewidth=0.5, **style[g])
    add_point_labels(ax, sub["Altitude"], sub["Temp"], sub["label"], "fig2", "d")

slope_d, int_d, r_d, p_d, se_d = stats.linregress(df_main["Altitude"], df_main["Temp"])
xr = np.linspace(df_main["Altitude"].min(), df_main["Altitude"].max(), 100)
# EDITOR FIX 9d: R italic with upright superscript 2; °C/1000 m
ax.plot(xr, slope_d * xr + int_d, "k--", linewidth=1.5,
        label="Linear fit ($R^{2}$ = %.2f, %.1f \u00b0C/1000 m)"
              % (r_d ** 2, slope_d * 1000))

ax.set_xlabel(LBL_ALT)
ax.set_ylabel(LBL_TEMP)
style_axis(ax)
add_panel_label(ax, "fig2", "d")
add_legend(ax, "fig2", "d")

fig2.tight_layout()
fig2.subplots_adjust(wspace=FIG2_WSPACE, hspace=FIG2_HSPACE)
save_both(fig2, FIG9_BASENAME)
