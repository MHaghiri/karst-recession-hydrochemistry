"""
Fig 10 - Combined Hydrochemical Process Figure (3 rows x 3 columns)
====================================================================
Panel layout:
  (a) Na+/Cl-               (b) Ca2+/Mg2+              (c) (Ca+Mg)/(HCO3+SO4)
  (d) HCO3-/Cl-             (e) SO4(2-)/Cl-            (f) Ion Exchange Index
  (g) d18O (recharge elev.) (h) d-excess               (i) WQI by sample (bar chart)

Revised for Hydrogeology Journal technical-editor comments (HYJO-D-26-00525R1):
  Fig 10  - one distance scale bar and one north arrow added (panel set by
            SCALEBAR_PANEL, default (a)).
          - ratio units "(meq)" -> "(equivalent ratio)".
  10a     - the reference mark on the colour bar is now ONE solid line.
            It was drawn dashed, and across a narrow colour bar a dashed line
            breaks into two short dashes, which read as a stray extra mark.
            (Style set by CBAR_REF_LINESTYLE.)
  10g/10h - text description labels set upright (non-italic).
  10h     - "GMWL d=10" text next to the colour bar removed.
  10i     - "Excellent" / "Good" (WQI class) labels enlarged (WQI_CLASS_LABEL_SIZE).
c:\Users\mhaghi2\Desktop\Article 9\github\create_repo.ps1
Other output changes:
  - Saved as Fig10.pdf (for submission) and Fig10.png, both at FIG_DPI.
  - Interpolated surfaces are rasterized inside the PDF so the file stays a
    sensible size; all text, lines, symbols and boundaries stay vector.

Data sources:
  - Coordinates (X, Y) from Isotope.xlsx (Sheet1)   [UTM, metres]
  - Major-ion + WHO-parameter chemistry from hydrochemical.xlsx
  - d18O / d2H from Isotope.xlsx (Sheet1)
  - Boundary from study_area.shp
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.font_manager as fm
from matplotlib.colors import Normalize
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from scipy.interpolate import RBFInterpolator

warnings.filterwarnings("ignore")

# Keep text as real text in the PDF (editable, scalable, never pixelated)
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"]  = 42

# ═══════════════════════════════════════════════════════════════════════
# USER SETTINGS
# ═══════════════════════════════════════════════════════════════════════

# ── File paths ────────────────────────────────────────────────────────
HYDROCHEM_XLSX = r"C:\Users\mhaghi2\Desktop\Article 9\data\hydrochemical\hydrochemical.xlsx"
ISOTOPE_XLSX   = r"c:\Users\mhaghi2\Desktop\Article 9\data\Isotop\Isotope.xlsx"
SHAPEFILE_PATH = r"c:\Users\mhaghi2\Desktop\Article 9\data\study_area.shp"
OUTPUT_DIR     = r"C:\Users\mhaghi2\Desktop\Article 9\map"
OUT_BASENAME   = "Fig10"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Figure / grid layout (3 rows x 3 cols) ────────────────────────────
NROWS, NCOLS  = 3, 3
PANEL_WIDTH   = 5
PANEL_HEIGHT  = 2.8
PANEL_HSPACE  = 0.05
PANEL_WSPACE  = 0.05
FIG_DPI       = 1000      # PNG resolution, and resolution of the rasterized
                          # interpolated surfaces inside the PDF

# ── Map margin inside each interpolated-surface panel ─────────────────
MAP_MARGIN_X        = 0.02
MAP_MARGIN_Y        = 0.06
USE_ASYMMETRIC_Y_MARGIN = False
MAP_MARGIN_Y_TOP    = 0.05
MAP_MARGIN_Y_BOTTOM = 0.05
AUTO_FIT_PANEL_ASPECT = False
AUTO_FIT_MIN_HEIGHT   = 2.5

# ── Colorbar dimensions (shared by all map panels) ────────────────────
CBAR_WIDTH    = 0.05
CBAR_HEIGHT   = 0.85
CBAR_PAD      = 0.02

# ── Colour-bar reference line (EDITOR FIX 10a) ────────────────────────
# Solid gives one continuous mark across the bar. "--" breaks into two short
# dashes on a narrow colour bar, which is what the editor saw.
CBAR_REF_LINESTYLE = "-"
CBAR_REF_LINEWIDTH = 2.0
CBAR_REF_COLOR     = "black"

# ── Interpolation ─────────────────────────────────────────────────────
INTERP_KERNEL   = "thin_plate_spline"
INTERP_GRID_RES = 200
INTERP_SMOOTH   = 0.0

# ── Symbology ─────────────────────────────────────────────────────────
MARKER_MAP = {
    "Spring": dict(marker="o", color="#1B8A1B", label="Spring"),
    "Qanat":  dict(marker="s", color="#1565C0", label="Qanat"),
    "Well":   dict(marker="^", color="#BF360C", label="Well"),
    "Other":  dict(marker="d", color="#616161", label="Other"),
}
POINT_SIZE          = 100
POINT_EDGE_COLOR    = "black"
POINT_EDGE_WIDTH    = 0.8
SHOW_POINT_LABELS   = True
POINT_LABEL_OFFSET  = (5, 5)

# ── Source classification ─────────────────────────────────────────────
N_SPRING = 11
N_QANAT  = 4
N_WELL   = 4

# ── Font sizes ────────────────────────────────────────────────────────
AXIS_LABEL_SIZE     = 12
TICK_SIZE           = 12
PANEL_LABEL_SIZE    = 16
CBAR_LABEL_SIZE     = 14
CBAR_TICK_SIZE      = 12
LEGEND_SIZE         = 16
POINT_LABEL_SIZE    = 10
DESCRIPTION_SIZE    = 10      # (g)/(h) explanatory text boxes
WQI_CLASS_LABEL_SIZE = 13     # EDITOR FIX 10i: "Excellent", "Good" ... (was 8)

# ── Spring / Qanat / Well marker legend (sits inside panel e) ─────────
# Narrowed so the box no longer runs past the sides of panel (e).
# To make it narrower still: lower LEGEND_FONT_SIZE or LEGEND_COL_SPACING.
LEGEND_X = 0.5
LEGEND_Y = 1.3
LEGEND_FONT_SIZE     = 13     # was 16 (LEGEND_SIZE)
LEGEND_MARKER_SCALE  = 1.1    # was 1.4
LEGEND_HANDLE_LENGTH = 1.0    # was 1.5
LEGEND_HANDLE_HEIGHT = 1.2    # was 1.5
LEGEND_HANDLE_TEXTPAD = 0.4   # gap between symbol and its word (default 0.8)
LEGEND_LABEL_SPACING = 0.8
LEGEND_COL_SPACING   = 0.9    # was 1.8 - gap between Spring / Qanat / Well
LEGEND_BORDER_PAD    = 0.5    # was 0.8

# ═══════════════════════════════════════════════════════════════════════
# SCALE BAR / NORTH ARROW  (EDITOR FIX: Fig 10, one of each)
# ═══════════════════════════════════════════════════════════════════════
SCALEBAR_PANEL       = "a"     # panel letter that receives the scale bar + north arrow
SCALEBAR_KM          = 20
MAP_UNITS_PER_KM     = 1000    # map units are metres (UTM)
SCALEBAR_LOC         = "lower right"
SCALEBAR_PAD         = 0.4
SCALEBAR_THICKNESS   = 0.015   # bar thickness as a fraction of the map height
SCALEBAR_FONT_SIZE   = 11
SCALEBAR_LABEL       = "%d km" % SCALEBAR_KM

NORTH_ARROW_XY       = (0.93, 0.90)   # arrow tip, axes fraction
NORTH_ARROW_LENGTH   = 0.18
NORTH_ARROW_FONT     = 14
NORTH_ARROW_WIDTH    = 2.5

# ── Ion-ratio panels (a)-(f)  (EDITOR FIX: "(meq)" -> "(equivalent ratio)") ──
RATIO_UNIT = "(equivalent ratio)"
RATIOS = [
    ("Na_Cl",        "Na$^{+}$/Cl$^{-}$\n%s" % RATIO_UNIT,                              "PuOr",     1.0, ""),
    ("Ca_Mg",        "Ca$^{2+}$/Mg$^{2+}$\n%s" % RATIO_UNIT,                            "BrBG",     1.0, ""),
    ("CaMg_HCO3SO4", "(Ca$^{2+}$+Mg$^{2+}$)/(HCO$_3^{-}$+SO$_4^{2-}$)\n%s" % RATIO_UNIT, "RdYlGn_r", 1.0, "1:1 carbonate"),
    ("HCO3_Cl",      "HCO$_3^{-}$/Cl$^{-}$\n%s" % RATIO_UNIT,                           "YlGnBu",   None, None),
    ("SO4_Cl",       "SO$_4^{2-}$/Cl$^{-}$\n%s" % RATIO_UNIT,                           "YlOrRd",   None, None),
    ("IonExch",      "Ion Exchange Index",                                               "coolwarm", 0.0, "no exchange"),
]

# ── Isotope panels (g)-(h) ─────────────────────────────────────────────
CMAP_D18O    = "viridis"
CMAP_DEXCESS = "cividis"

# ── WQI panel (i) — WHO (2017) standards: {param: (standard, weight)} ──
WHO = {
    "ph":   (8.5,  4),
    "tds":  (500,  5),
    "ec":   (1500, 4),
    "ca":   (75,   3),
    "mg":   (50,   3),
    "na":   (200,  2),
    "cl":   (250,  3),
    "so4":  (250,  4),
    "hco3": (500,  1),
}
PH_IDEAL = 7.0
WQI_CLASSES = [
    (0,   25,  "Excellent",  "#2166ac"),
    (25,  50,  "Good",       "#67a9cf"),
    (50,  75,  "Poor",       "#fddbc7"),
    (75,  100, "Very Poor",  "#ef8a62"),
    (100, 300, "Unsuitable", "#b2182b"),
]

MW = {"Ca": 40.078, "Mg": 24.305, "Na": 22.990, "K": 39.098,
      "Cl": 35.453, "SO4": 96.062, "HCO3": 61.016}
Z  = {"Ca": 2, "Mg": 2, "Na": 1, "K": 1, "Cl": 1, "SO4": 2, "HCO3": 1}
EPS = 1e-6

# ═══════════════════════════════════════════════════════════════════════
# DATA LOADING — HYDROCHEMISTRY
# ═══════════════════════════════════════════════════════════════════════

def normalise(s):
    return str(s).strip().lower().replace(" ", "").replace("+", "").replace("-", "")

raw = pd.read_excel(HYDROCHEM_XLSX, header=None)
ION_KEYWORDS = sorted(set(["ca", "mg", "na", "k", "cl", "so4", "hco3"]) | set(WHO.keys()))

def row_score(row):
    return sum(1 for v in row if isinstance(v, str) and any(k in v.lower() for k in ION_KEYWORDS))

header_row = max(range(min(5, len(raw))), key=lambda i: row_score(raw.iloc[i]))
raw_headers = raw.iloc[header_row].tolist()

filled, last = [], "col"
for v in raw_headers:
    if pd.isna(v) or str(v).strip() == "":
        filled.append(last)
    else:
        last = str(v).strip(); filled.append(last)

seen = {}; unique_headers = []
for hh in filled:
    hl = hh.lower(); seen[hl] = seen.get(hl, 0) + 1
    unique_headers.append(hh if seen[hl] == 1 else "%s_%d" % (hh, seen[hl]))

df_chem = raw.iloc[header_row + 1:].copy()
df_chem.columns = unique_headers
df_chem = df_chem.reset_index(drop=True)

name_col = df_chem.columns[0]
df_chem = df_chem[df_chem[name_col].notna()]
df_chem = df_chem[pd.to_numeric(df_chem[name_col], errors="coerce").isna()]
df_chem = df_chem[df_chem[name_col].astype(str).str.strip() != ""]
df_chem = df_chem.reset_index(drop=True)

norm_map = {c: normalise(c) for c in df_chem.columns}
sample_names = df_chem[name_col].astype(str).str.strip().unique()

ALL_TARGETS = sorted(set(["ca", "mg", "na", "k", "cl", "so4", "hco3"]) | set(WHO.keys()))

records = []
for sname in sample_names:
    sub = df_chem[df_chem[name_col].astype(str).str.strip() == sname]
    rec = {"sample": sname}
    for tgt in ALL_TARGETS:
        cols = [c for c, nrm in norm_map.items() if tgt in nrm]
        vals = []
        for c in cols:
            v = pd.to_numeric(sub[c], errors="coerce")
            vals.extend(v.dropna().tolist())
        rec[tgt] = np.mean(vals) if vals else np.nan
    records.append(rec)

df_ion = pd.DataFrame(records)

# ═══════════════════════════════════════════════════════════════════════
# DATA LOADING — COORDINATES + ISOTOPES
# ═══════════════════════════════════════════════════════════════════════

df_iso_raw = pd.read_excel(ISOTOPE_XLSX, sheet_name="Sheet1")
df_iso_raw.columns = [str(c).strip() for c in df_iso_raw.columns]

iso_rename = {}
for c in df_iso_raw.columns:
    cl = c.lower().replace(" ", "").replace("_", "")
    if cl == "x": iso_rename[c] = "X"
    elif cl == "y": iso_rename[c] = "Y"
    elif cl in ("o18", "d18o", "delta18o", "18o"): iso_rename[c] = "d18O"
    elif cl in ("d", "dd", "deltad", "deltah", "dh", "2h"): iso_rename[c] = "dD"
    elif cl in ("altitude", "elevation", "elev"): iso_rename[c] = "Altitude"
df_iso_raw = df_iso_raw.rename(columns=iso_rename)

df_iso_f = df_iso_raw[df_iso_raw["name"].isin(["spring", "qanat", "well"])].copy().reset_index(drop=True)
if len(df_iso_f) == len(sample_names):
    df_iso_f["sample"] = sample_names
else:
    print("[info] Isotope rows (%d) != hydrochem samples (%d); matching by source-type order."
          % (len(df_iso_f), len(sample_names)))
    df_iso_f["sample"] = range(len(df_iso_f))

df_coords = df_iso_f[["sample", "X", "Y"]].dropna(subset=["X", "Y"])

df_m = df_ion.merge(df_coords, on="sample", how="inner")
if df_m.empty:
    print("[warn] Name-based merge returned 0 rows. Trying positional merge...")
    df_coords_pos = df_coords.copy(); df_coords_pos["_idx"] = range(len(df_coords_pos))
    df_ion_pos = df_ion.copy(); df_ion_pos["_idx"] = range(len(df_ion_pos))
    df_m = df_ion_pos.merge(df_coords_pos[["_idx", "X", "Y"]], on="_idx", how="inner").drop(columns=["_idx"])
df_m = df_m.dropna(subset=["X", "Y"]).reset_index(drop=True)
print("[ok] %d samples with coordinates and chemistry" % len(df_m))

iso_cols_needed = [c for c in ["X", "Y", "d18O", "dD", "Altitude"] if c in df_iso_f.columns]
df_isotope = df_iso_f[["sample"] + iso_cols_needed].copy()
if "d18O" in df_isotope.columns and "dD" in df_isotope.columns:
    df_isotope = df_isotope.dropna(subset=["X", "Y", "d18O", "dD"]).reset_index(drop=True)
    df_isotope["d_excess"] = df_isotope["dD"] - 8 * df_isotope["d18O"]
else:
    print("[warn] d18O/dD columns not found in Isotope.xlsx; panels (g)-(h) will be skipped.")
    df_isotope = pd.DataFrame(columns=["sample", "X", "Y", "d18O", "dD", "d_excess"])

def classify_sources(df_in, sample_col="sample"):
    uq_s = list(pd.unique(df_in[sample_col]))
    ptype = {}
    for i, nm in enumerate(uq_s):
        if i < N_SPRING:
            ptype[nm] = "Spring"
        elif i < N_SPRING + N_QANAT:
            ptype[nm] = "Qanat"
        elif i < N_SPRING + N_QANAT + N_WELL:
            ptype[nm] = "Well"
        else:
            ptype[nm] = "Other"
    prefix = {"Spring": "S", "Qanat": "Q", "Well": "W", "Other": "O"}
    ctr = {}; lbl_map = {}
    for nm in uq_s:
        p = prefix[ptype[nm]]
        ctr[p] = ctr.get(p, 0) + 1
        lbl_map[nm] = "%s%d" % (p, ctr[p])
    df_in["source"] = df_in[sample_col].map(ptype)
    df_in["label"] = df_in[sample_col].map(lbl_map)
    return df_in

df_m = classify_sources(df_m)
if not df_isotope.empty:
    df_isotope = classify_sources(df_isotope)

# ── meq/L + ion ratios ─────────────────────────────────────────────────
for ion, key in [("Ca", "ca"), ("Mg", "mg"), ("Na", "na"), ("K", "k"),
                  ("Cl", "cl"), ("SO4", "so4"), ("HCO3", "hco3")]:
    df_m["%s_meq" % ion] = df_m[key] / MW[ion] * Z[ion]

df_m["Na_Cl"]        = df_m["Na_meq"] / (df_m["Cl_meq"] + EPS)
df_m["Ca_Mg"]        = df_m["Ca_meq"] / (df_m["Mg_meq"] + EPS)
df_m["CaMg_HCO3SO4"] = (df_m["Ca_meq"] + df_m["Mg_meq"]) / (df_m["HCO3_meq"] + df_m["SO4_meq"] + EPS)
df_m["HCO3_Cl"]      = df_m["HCO3_meq"] / (df_m["Cl_meq"] + EPS)
df_m["SO4_Cl"]       = df_m["SO4_meq"] / (df_m["Cl_meq"] + EPS)
_num = df_m["Na_meq"] + df_m["K_meq"] - df_m["Cl_meq"]
_den = _num + df_m["Ca_meq"] + df_m["Mg_meq"] - df_m["HCO3_meq"] - df_m["SO4_meq"]
df_m["IonExch"] = np.where(np.abs(_den) > EPS, _num / _den, 0)

# ── WQI ─────────────────────────────────────────────────────────────────
def compute_wqi(row):
    tw = 0; tqw = 0
    for param, (std, w) in WHO.items():
        val = row.get(param, np.nan)
        if pd.isna(val):
            continue
        qi = abs(val - PH_IDEAL) / abs(8.5 - PH_IDEAL) * 100 if param == "ph" else (val / std) * 100
        tqw += qi * w; tw += w
    return tqw / tw if tw > 0 else np.nan

df_m["WQI"] = df_m.apply(compute_wqi, axis=1)
if df_m["WQI"].notna().any():
    print("[ok] WQI range: %.1f - %.1f" % (df_m["WQI"].min(), df_m["WQI"].max()))

# ═══════════════════════════════════════════════════════════════════════
# SHAPEFILE
# ═══════════════════════════════════════════════════════════════════════

gdf = None
HAS_GDF = False
try:
    import geopandas as gpd
    from shapely.geometry import Point
    gdf = gpd.read_file(SHAPEFILE_PATH)
    minx, miny, maxx, maxy = gdf.total_bounds
    HAS_GDF = True
    print("[ok] Shapefile loaded: bounds = (%.0f, %.0f) - (%.0f, %.0f)" % (minx, miny, maxx, maxy))
except Exception as e:
    print("[warn] Shapefile not loaded (%s), using data extent" % e)
    pad_x = (df_m["X"].max() - df_m["X"].min()) * 0.15
    pad_y = (df_m["Y"].max() - df_m["Y"].min()) * 0.15
    minx = df_m["X"].min() - pad_x
    maxx = df_m["X"].max() + pad_x
    miny = df_m["Y"].min() - pad_y
    maxy = df_m["Y"].max() + pad_y

range_x = maxx - minx
range_y = maxy - miny

if USE_ASYMMETRIC_Y_MARGIN:
    view_miny = miny - range_y * MAP_MARGIN_Y_BOTTOM
    view_maxy = maxy + range_y * MAP_MARGIN_Y_TOP
else:
    view_miny = miny - range_y * MAP_MARGIN_Y
    view_maxy = maxy + range_y * MAP_MARGIN_Y

view_minx = minx - range_x * MAP_MARGIN_X
view_maxx = maxx + range_x * MAP_MARGIN_X
interp_bounds = (minx, maxx, miny, maxy)

_view_w = view_maxx - view_minx
_view_h = view_maxy - view_miny
_map_aspect = _view_h / _view_w if _view_w > 0 else 1.0

# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════

def interpolate_surface(x, y, z, bounds, res=INTERP_GRID_RES,
                         kernel=INTERP_KERNEL, smooth=INTERP_SMOOTH,
                         clip_gdf=None):
    pts = np.column_stack([x, y])
    rbf = RBFInterpolator(pts, z, kernel=kernel, smoothing=smooth)

    gx = np.linspace(bounds[0], bounds[1], res)
    gy = np.linspace(bounds[2], bounds[3], res)
    GX, GY = np.meshgrid(gx, gy)
    grid_pts = np.column_stack([GX.ravel(), GY.ravel()])
    GZ = rbf(grid_pts).reshape(GX.shape)

    if clip_gdf is not None:
        try:
            poly = clip_gdf.unary_union
            mask = np.array([poly.contains(Point(px, py))
                              for px, py in grid_pts]).reshape(GX.shape)
            GZ = np.where(mask, GZ, np.nan)
        except Exception:
            pass

    return GX, GY, GZ

def plot_sample_points(ax, dfs):
    for src, sty in MARKER_MAP.items():
        sub = dfs[dfs["source"] == src]
        if sub.empty:
            continue
        ax.scatter(sub["X"], sub["Y"], s=POINT_SIZE, marker=sty["marker"], c="white",
                   edgecolors=POINT_EDGE_COLOR, linewidths=POINT_EDGE_WIDTH,
                   label=sty["label"], zorder=4)
    if SHOW_POINT_LABELS:
        for _, row in dfs.iterrows():
            ax.annotate(row["label"], (row["X"], row["Y"]), xytext=POINT_LABEL_OFFSET,
                        textcoords="offset points", fontsize=POINT_LABEL_SIZE,
                        color="black", weight="bold", zorder=5)

def fmt_map_axes(ax, view_bounds):
    if HAS_GDF:
        gdf.boundary.plot(ax=ax, color="black", linewidth=1.4, zorder=2)
    ax.set_xlim(view_bounds[0], view_bounds[1])
    ax.set_ylim(view_bounds[2], view_bounds[3])
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xticks([]); ax.set_yticks([])

def add_cbar_ref_line(cbar, value):
    """Single continuous reference mark across the colour bar (FIX 10a)."""
    cbar.ax.axhline(value, color=CBAR_REF_COLOR, lw=CBAR_REF_LINEWIDTH,
                    ls=CBAR_REF_LINESTYLE)

def add_scale_bar(ax):
    length = SCALEBAR_KM * MAP_UNITS_PER_KM
    thickness = (ax.get_ylim()[1] - ax.get_ylim()[0]) * SCALEBAR_THICKNESS
    sb = AnchoredSizeBar(ax.transData, length, SCALEBAR_LABEL,
                         loc=SCALEBAR_LOC, pad=SCALEBAR_PAD,
                         color="black", frameon=False,
                         size_vertical=thickness, label_top=True,
                         fontproperties=fm.FontProperties(size=SCALEBAR_FONT_SIZE))
    sb.set_zorder(20)
    ax.add_artist(sb)

def add_north_arrow(ax):
    x, y = NORTH_ARROW_XY
    ax.annotate("", xy=(x, y), xytext=(x, y - NORTH_ARROW_LENGTH),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(facecolor="black", edgecolor="black",
                                width=NORTH_ARROW_WIDTH,
                                headwidth=NORTH_ARROW_WIDTH * 4,
                                headlength=NORTH_ARROW_WIDTH * 4),
                zorder=20)
    ax.text(x, y + 0.02, "N", transform=ax.transAxes, ha="center", va="bottom",
            fontsize=NORTH_ARROW_FONT, fontweight="bold", zorder=20)

# ═══════════════════════════════════════════════════════════════════════
# FIGURE — 3 x 3 GRID
# ═══════════════════════════════════════════════════════════════════════

if AUTO_FIT_PANEL_ASPECT and PANEL_WIDTH is not None:
    _fitted_height = max(AUTO_FIT_MIN_HEIGHT, PANEL_WIDTH * _map_aspect)
else:
    _fitted_height = PANEL_HEIGHT

row_heights = [
    _fitted_height if PANEL_HEIGHT is not None else 1,
    _fitted_height if PANEL_HEIGHT is not None else 1,
    max(_fitted_height, PANEL_HEIGHT) if PANEL_HEIGHT is not None else 1,
]

if PANEL_WIDTH is not None and PANEL_HEIGHT is not None:
    total_w = NCOLS * PANEL_WIDTH + (NCOLS - 1) * PANEL_WSPACE
    total_h = sum(row_heights) + (NROWS - 1) * PANEL_HSPACE
    fig_w = total_w + 2.0
    fig_h = total_h + 2.0
else:
    fig_w, fig_h = 18.0, 18.0

fig = plt.figure(figsize=(fig_w, fig_h), layout="constrained")
gs = gridspec.GridSpec(
    NROWS, NCOLS, figure=fig,
    width_ratios=[PANEL_WIDTH if PANEL_WIDTH is not None else 1] * NCOLS,
    height_ratios=row_heights,
)
fig.get_layout_engine().set(
    wspace=PANEL_WSPACE / (PANEL_WIDTH if PANEL_WIDTH is not None else 5),
    hspace=PANEL_HSPACE / (PANEL_HEIGHT if PANEL_HEIGHT is not None else 5),
    w_pad=0.06, h_pad=0.06,
)

fig.patch.set_facecolor("white")
axes = [fig.add_subplot(gs[r, c]) for r in range(NROWS) for c in range(NCOLS)]
panel_letters = [chr(ord("a") + i) for i in range(NROWS * NCOLS)]

def add_panel_label(ax, letter):
    ax.text(0.03, 0.95, "(%s)" % letter, transform=ax.transAxes,
            fontsize=PANEL_LABEL_SIZE, fontweight="bold", va="top", ha="left",
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=2),
            zorder=10)

# ─────────────────────────────────────────────────────────────────────
# PANELS (a)-(f): ion-ratio process maps
# ─────────────────────────────────────────────────────────────────────
for idx, (rkey, rtitle, cmap, ref_val, ref_lbl) in enumerate(RATIOS):
    ax = axes[idx]
    mask = df_m[rkey].notna() & np.isfinite(df_m[rkey])
    dfs = df_m[mask]

    if len(dfs) < 3:
        ax.text(0.5, 0.5, "Not enough data", ha="center", va="center",
                transform=ax.transAxes, fontsize=14)
        add_panel_label(ax, panel_letters[idx])
        continue

    z = dfs[rkey].values
    p5, p95 = np.percentile(z, 5), np.percentile(z, 95)
    rng = p95 - p5
    vmin = max(z.min(), p5 - 0.5 * rng)
    vmax = min(z.max(), p95 + 0.5 * rng)

    GX, GY, GZ = interpolate_surface(dfs["X"].values, dfs["Y"].values, z,
                                      interp_bounds, clip_gdf=gdf if HAS_GDF else None)
    im = ax.pcolormesh(GX, GY, GZ, cmap=cmap, shading="auto",
                       norm=Normalize(vmin=vmin, vmax=vmax), alpha=0.85,
                       zorder=1, rasterized=True)

    plot_sample_points(ax, dfs)
    fmt_map_axes(ax, (view_minx, view_maxx, view_miny, view_maxy))

    cbar = fig.colorbar(im, ax=ax, shrink=CBAR_HEIGHT, pad=CBAR_PAD, fraction=CBAR_WIDTH)
    cbar.set_label(rtitle, fontsize=CBAR_LABEL_SIZE)
    cbar.ax.tick_params(labelsize=CBAR_TICK_SIZE)
    if ref_val is not None and vmin <= ref_val <= vmax:
        add_cbar_ref_line(cbar, ref_val)
        if ref_lbl:
            cbar.ax.text(1.8, ref_val, ref_lbl, fontsize=CBAR_TICK_SIZE - 2, va="center",
                         transform=cbar.ax.get_yaxis_transform())

    add_panel_label(ax, panel_letters[idx])

# ─────────────────────────────────────────────────────────────────────
# PANELS (g)-(h): isotope maps
# ─────────────────────────────────────────────────────────────────────
ISO_START_IDX = 6

if not df_isotope.empty:
    x_i, y_i = df_isotope["X"].values, df_isotope["Y"].values

    # (g) d18O
    ax = axes[ISO_START_IDX]
    GX, GY, GZ1 = interpolate_surface(x_i, y_i, df_isotope["d18O"].values,
                                       interp_bounds, clip_gdf=gdf if HAS_GDF else None)
    im1 = ax.pcolormesh(GX, GY, GZ1, cmap=CMAP_D18O, shading="auto", alpha=0.85,
                        zorder=1, rasterized=True)
    plot_sample_points(ax, df_isotope)
    fmt_map_axes(ax, (view_minx, view_maxx, view_miny, view_maxy))
    cbar1 = fig.colorbar(im1, ax=ax, shrink=CBAR_HEIGHT, pad=CBAR_PAD, fraction=CBAR_WIDTH)
    cbar1.set_label("\u03b4$^{18}$O (\u2030)", fontsize=CBAR_LABEL_SIZE)
    cbar1.ax.tick_params(labelsize=CBAR_TICK_SIZE)
    # FIX 10g: description upright (style="normal")
    ax.text(0.02, 0.02, "More negative \u2192 higher\nrecharge elevation",
            transform=ax.transAxes, fontsize=DESCRIPTION_SIZE, style="normal",
            va="bottom", ha="left", bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))
    if "Altitude" in df_isotope.columns and df_isotope["Altitude"].notna().sum() >= 3:
        try:
            GX2, GY2, GZ_alt = interpolate_surface(x_i, y_i, df_isotope["Altitude"].values, interp_bounds)
            cs = ax.contour(GX2, GY2, GZ_alt, levels=6, colors="grey", linewidths=0.7,
                            linestyles=":", zorder=3)
            ax.clabel(cs, fmt="%d m", fontsize=POINT_LABEL_SIZE - 2, inline=True)
        except Exception:
            pass
    add_panel_label(ax, panel_letters[ISO_START_IDX])

    # (h) d-excess
    ax = axes[ISO_START_IDX + 1]
    GX, GY, GZ2 = interpolate_surface(x_i, y_i, df_isotope["d_excess"].values,
                                       interp_bounds, clip_gdf=gdf if HAS_GDF else None)
    im2 = ax.pcolormesh(GX, GY, GZ2, cmap=CMAP_DEXCESS, shading="auto", alpha=0.85,
                        zorder=1, rasterized=True)
    plot_sample_points(ax, df_isotope)
    fmt_map_axes(ax, (view_minx, view_maxx, view_miny, view_maxy))
    cbar2 = fig.colorbar(im2, ax=ax, shrink=CBAR_HEIGHT, pad=CBAR_PAD, fraction=CBAR_WIDTH)
    cbar2.set_label("d-excess (\u2030)", fontsize=CBAR_LABEL_SIZE)
    cbar2.ax.tick_params(labelsize=CBAR_TICK_SIZE)
    try:
        ax.contour(GX, GY, GZ2, levels=[10], colors="black", linewidths=1.5,
                   linestyles="--", zorder=2)
        d_lo, d_hi = np.nanmin(GZ2), np.nanmax(GZ2)
        if d_lo <= 10 <= d_hi:
            add_cbar_ref_line(cbar2, 10)
        # FIX 10h: "GMWL d=10" text next to the colour bar removed
    except Exception:
        pass
    # FIX 10h: description upright (style="normal")
    ax.text(0.02, 0.02, "d-excess > 10 \u2192 low humidity /\nsnowmelt recharge",
            transform=ax.transAxes, fontsize=DESCRIPTION_SIZE, style="normal",
            va="bottom", ha="left", bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))
    add_panel_label(ax, panel_letters[ISO_START_IDX + 1])
else:
    for offset in range(2):
        ax = axes[ISO_START_IDX + offset]
        ax.text(0.5, 0.5, "No isotope data\navailable", ha="center", va="center",
                transform=ax.transAxes, fontsize=14)
        add_panel_label(ax, panel_letters[ISO_START_IDX + offset])

# ─────────────────────────────────────────────────────────────────────
# PANEL (i): WQI horizontal bar chart
# ─────────────────────────────────────────────────────────────────────
WQI_IDX = 8
ax = axes[WQI_IDX]

dfs_wqi = df_m[df_m["WQI"].notna()].copy()
if len(dfs_wqi) >= 1:
    dfs_s = dfs_wqi.sort_values("WQI").reset_index(drop=True)
    bar_colors = [MARKER_MAP.get(r["source"], MARKER_MAP["Other"])["color"] for _, r in dfs_s.iterrows()]
    ax.barh(range(len(dfs_s)), dfs_s["WQI"].values, color=bar_colors,
            edgecolor="white", linewidth=0.5, height=0.7)
    ax.set_yticks(range(len(dfs_s)))
    ax.set_yticklabels(dfs_s["label"].values, fontsize=AXIS_LABEL_SIZE - 2)
    ax.set_xlabel("WQI", fontsize=AXIS_LABEL_SIZE)
    ax.tick_params(axis="x", labelsize=TICK_SIZE)
    ax.grid(axis="x", alpha=0.3)

    xlim = ax.get_xlim()
    for lo, hi, lbl, clr in WQI_CLASSES:
        ax.axvline(lo, color="grey", lw=0.5, ls=":")
        if lo < xlim[1]:
            ax.axvspan(lo, min(hi, xlim[1]), alpha=0.08, color=clr, zorder=0)
            mid = (lo + min(hi, xlim[1])) / 2
            # FIX 10i: class labels enlarged
            ax.text(mid, len(dfs_s) - 0.3, lbl, ha="center", va="top",
                    fontsize=WQI_CLASS_LABEL_SIZE, color=clr, weight="bold", rotation=90)
    ax.invert_yaxis()
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    wqi_handles = [Patch(facecolor=MARKER_MAP[s]["color"], edgecolor="white", label=s)
                  for s in ["Spring", "Qanat", "Well"] if s in dfs_wqi["source"].values]
    ax.legend(handles=wqi_handles, fontsize=LEGEND_SIZE - 4, loc="lower right", frameon=True)
else:
    ax.text(0.5, 0.5, "Not enough data\nfor WQI", ha="center", va="center",
            transform=ax.transAxes, fontsize=14)

add_panel_label(ax, panel_letters[WQI_IDX])

# ─────────────────────────────────────────────────────────────────────
# EDITOR FIX (Fig 10): one scale bar and one north arrow
# ─────────────────────────────────────────────────────────────────────
_sb_ax = axes[panel_letters.index(SCALEBAR_PANEL)]
fig.canvas.draw()   # settle layout and equal-aspect limits before sizing the bar
add_scale_bar(_sb_ax)
add_north_arrow(_sb_ax)

# ─────────────────────────────────────────────────────────────────────
# Shared bottom legend (sample-type markers)
# ─────────────────────────────────────────────────────────────────────
legend_handles = []
for src, sty in MARKER_MAP.items():
    if src in df_m["source"].values:
        legend_handles.append(
            Line2D([0], [0], marker=sty["marker"], color="w",
                  markerfacecolor="white", markeredgecolor="black",
                  markeredgewidth=1.2, markersize=10, label=sty["label"]))

_legend_anchor_ax = axes[(NROWS - 1) * NCOLS + NCOLS // 2]
fig.legend(handles=legend_handles, loc="upper center", ncol=len(legend_handles),
           fontsize=LEGEND_FONT_SIZE, frameon=True,
           markerscale=LEGEND_MARKER_SCALE,
           handlelength=LEGEND_HANDLE_LENGTH,
           handleheight=LEGEND_HANDLE_HEIGHT,
           handletextpad=LEGEND_HANDLE_TEXTPAD,
           labelspacing=LEGEND_LABEL_SPACING,
           columnspacing=LEGEND_COL_SPACING,
           borderpad=LEGEND_BORDER_PAD,
           bbox_to_anchor=(LEGEND_X, LEGEND_Y), bbox_transform=_legend_anchor_ax.transAxes)

# ═══════════════════════════════════════════════════════════════════════
# SAVE - PDF (for submission) and PNG
# ═══════════════════════════════════════════════════════════════════════
for ext in ("pdf", "png"):
    out_path = os.path.join(OUTPUT_DIR, "%s.%s" % (OUT_BASENAME, ext))
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
    print("[ok] saved -> %s" % out_path)
plt.close(fig)
