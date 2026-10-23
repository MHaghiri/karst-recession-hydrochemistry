"""
Fig 7 - Combined Hydrochemical Maps
===================================
Panel layout (4 rows x 3 cols):
  (a) Ca2+    (b) Mg2+    (c) Na+
  (d) K+      (e) Cl-     (f) SO4 2-
  (g) HCO3-   (h) TDS     (i) Hydrochemical facies map
  (j) EC wet  (k) EC dry  (l) Delta EC (dry - wet)

Revised for Hydrogeology Journal technical-editor comments (HYJO-D-26-00525R1):
  Fig 7  - one distance scale bar and one north arrow added, on panel (j) only.
           Size, position and text are set in the SCALE BAR / NORTH ARROW block.
  Fig 7i - "Water type" legend re-anchored by its BOTTOM edge just inside the
           map frame, so it now grows upward and no longer crosses the map
           perimeter. Nudge with FACIES_LEGEND_OFFSETS["water_type"].

Other output changes:
  - Saved as Fig7.pdf (for submission) and Fig7.png, both at FIG_DPI.
  - The interpolated surfaces are rasterized inside the PDF. Without this every
    one of the 1000 x 1000 grid cells in each of 11 maps is written as a vector
    shape, which makes the PDF enormous and very slow to open. Text, lines,
    symbols, boundaries, the scale bar and north arrow all stay vector.

Data sources:
  - Coordinates (X, Y) from Isotope.xlsx (Sheet1)  [UTM, metres]
  - Chemistry from hydrochemical.xlsx
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
import matplotlib.patches as mpatches
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path as MPath
from matplotlib.lines import Line2D
from matplotlib.colors import Normalize, TwoSlopeNorm
from scipy.interpolate import RBFInterpolator
from scipy.spatial import Voronoi

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
OUT_BASENAME   = "Fig7"

os.makedirs(OUTPUT_DIR, exist_ok=True)

USE_HYDROCHEM_COORDS = False

# ── Figure / grid layout ──────────────────────────────────────────────
NROWS, NCOLS  = 4, 3
PANEL_WIDTH   = 5
PANEL_HEIGHT  = 3.5
PANEL_HSPACE  = 1.0
PANEL_WSPACE  = 4
FIG_DPI       = 1000       # PNG resolution, and resolution of the rasterized
                           # interpolated surfaces inside the PDF

# ── Map margin inside each ion panel (fraction of data range) ────────
MAP_MARGIN_X  = 0.02
MAP_MARGIN_Y  = 0.02

# ── Colorbar dimensions ───────────────────────────────────────────────
CBAR_WIDTH    = 0.05
CBAR_HEIGHT   = 0.85
CBAR_PAD      = 0.02

# ── Colormaps ─────────────────────────────────────────────────────────
CMAP_CHOICE = 5
CMAP_OPTIONS = {1: "RdYlBu_r", 2: "Spectral_r", 3: "YlOrRd", 4: "viridis", 5: "plasma"}
CMAP = CMAP_OPTIONS[CMAP_CHOICE]
EC_CMAP_CONC = "YlOrRd"
EC_CMAP_DIFF = "RdBu_r"
EC_PARAM_LABEL = "EC (\u03bcS/cm)"

# ── Interpolation ─────────────────────────────────────────────────────
INTERP_KERNEL   = "thin_plate_spline"
INTERP_GRID_RES = 1000
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

# ── Ions for the 8 concentration panels ───────────────────────────────
IONS = [
    ("ca",   "Ca\u00b2\u207a",  "mg/L"),
    ("mg",   "Mg\u00b2\u207a",  "mg/L"),
    ("na",   "Na\u207a",        "mg/L"),
    ("k",    "K\u207a",         "mg/L"),
    ("cl",   "Cl\u207b",        "mg/L"),
    ("so4",  "SO\u2084\u00b2\u207b", "mg/L"),
    ("hco3", "HCO\u2083\u207b", "mg/L"),
    ("tds",  "TDS",             "mg/L"),
]

# ── Font sizes ────────────────────────────────────────────────────────
AXIS_LABEL_SIZE     = 12
TICK_SIZE           = 12
PANEL_LABEL_SIZE    = 18
CBAR_LABEL_SIZE     = 14
CBAR_TICK_SIZE      = 12
LEGEND_SIZE         = 16
POINT_LABEL_SIZE    = 10

# ── Shared bottom legend ────────────────────────────────────────────
LEGEND_X = 0.5
LEGEND_Y = 0.16

# ═══════════════════════════════════════════════════════════════════════
# SCALE BAR / NORTH ARROW  (EDITOR FIX: Fig 7, one of each, panel j)
# ═══════════════════════════════════════════════════════════════════════
SCALEBAR_PANEL       = "j"     # panel letter that receives the scale bar + north arrow
MAP_UNITS_PER_KM     = 1000    # map units are metres (UTM)

# Standard alternating black/white scale bar, labelled 0 ... SCALEBAR_KM km
SCALEBAR_KM          = 20      # total length of the bar in km
SCALEBAR_SEGMENTS    = 4       # number of alternating black/white blocks
SCALEBAR_LABEL_EVERY = 2       # label every n-th block boundary (0, 10, 20 km)
SCALEBAR_X0          = 0.04    # left end of the bar, axes fraction
SCALEBAR_Y0          = 0.07    # bottom of the bar, axes fraction
SCALEBAR_THICKNESS   = 0.035   # bar height, axes fraction
SCALEBAR_FONT_SIZE   = 14
SCALEBAR_LINE_WIDTH  = 1.2

# Standard north arrow: split arrowhead (left half black, right half white)
# with "N" above. Everything stays inside the panel frame.
NORTH_ARROW_X        = 0.91    # centre of the arrow, axes fraction
NORTH_ARROW_TIP_Y    = 0.80    # tip of the arrow, axes fraction (keep < ~0.85)
NORTH_ARROW_HEIGHT   = 0.20    # arrow height, axes fraction
NORTH_ARROW_HALF_W   = 0.035   # half-width of the arrow base, axes fraction
NORTH_ARROW_FONT     = 16      # size of the "N"
NORTH_ARROW_GAP      = 0.015   # gap between tip and "N", axes fraction

# ── Facies-panel settings (panel "i") ─────────────────────────────────
FACIES_COLORS = {
    "Ca-HCO3": "#4393c3", "Ca-SO4": "#92c5de", "Ca-Cl": "#d1e5f0",
    "Mg-HCO3": "#66c2a5", "Mg-SO4": "#abdda4", "Mg-Cl": "#e6f598",
    "Na-K-HCO3": "#f46d43", "Na-K-SO4": "#fdae61", "Na-K-Cl": "#fee08b",
}
PIE_CAT = {"Ca": "#1f78b4", "Mg": "#33a02c", "Na+K": "#e31a1c"}
PIE_AN  = {"HCO3": "#a6cee3", "SO4": "#b2df8a", "Cl": "#fb9a99"}

FACIES_TEXT_SIZES = {
    "legend_title": 11,
    "legend_text": 12,
    "sample_label": 8,
    "axis_label": 8,
}
FACIES_POINT_SIZES = {
    "sample_marker": 8,
    "legend_marker": 8,
    "bar_edge_width": 0.4,
}
FACIES_BAR_W = 0.020
FACIES_BAR_H = 0.020
FACIES_BAR_OFFSET_X = 0.6
FACIES_BAR_OFFSET_Y = 0.3

# EDITOR FIX 7i: the "Water type" legend is anchored by its LOWER-LEFT
# corner (FACIES_LEGEND_LOCS below) and grows upward. y = -0.01 puts its
# bottom level with the "Bar chart" and "Sample type" legends. Raise y to
# move it up, lower it to move it down; change x to slide it left/right.
FACIES_LEGEND_OFFSETS = {
    "water_type":  (0.70, -0.01),   # level with the other two legends
    "bar_chart":   (0.00, -0.01),
    "sample_type": (0.65, -0.01),
}
FACIES_LEGEND_LOCS = {
    "water_type":  "lower left",
    "bar_chart":   "lower left",
    "sample_type": "lower right",
}
FACIES_FRAME_SETTINGS = {
    "map_frame": True, "map_frame_color": "black", "map_frame_width": 2,
    "legend_frames": True, "legend_frame_color": "black", "legend_frame_width": 1,
    "legend_facecolor": "white", "legend_alpha": 0.85,
}

MW = {"Ca": 40.078, "Mg": 24.305, "Na": 22.990, "K": 39.098,
      "Cl": 35.453, "SO4": 96.062, "HCO3": 61.016}
Z  = {"Ca": 2, "Mg": 2, "Na": 1, "K": 1, "Cl": 1, "SO4": 2, "HCO3": 1}

# ═══════════════════════════════════════════════════════════════════════
# DATA LOADING - CHEMISTRY
# ═══════════════════════════════════════════════════════════════════════

raw = pd.read_excel(HYDROCHEM_XLSX, header=None)
ION_KEYWORDS = ["ca", "mg", "na", "k", "cl", "so4", "hco3", "ec", "tds", "ph", "temp"]

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

def normalise(s):
    return str(s).strip().lower().replace(" ", "").replace("+", "").replace("-", "") \
                 .replace("\u00b2", "2").replace("2+", "").replace("\u00b2\u207a", "")

norm_map = {c: normalise(c) for c in df_chem.columns}

def find_col(tgt):
    for c, nrm in norm_map.items():
        if tgt in nrm:
            return c
    return None

sample_names = df_chem[name_col].astype(str).str.strip().unique()

records = []
for sname in sample_names:
    sub = df_chem[df_chem[name_col].astype(str).str.strip() == sname]
    rec = {"sample": sname}
    for tgt, _, _ in IONS:
        cols = [c for c, nrm in norm_map.items() if tgt in nrm]
        vals = []
        for c in cols:
            v = pd.to_numeric(sub[c], errors="coerce")
            vals.extend(v.dropna().tolist())
        rec[tgt] = np.mean(vals) if vals else np.nan
    ec_cols = [c for c, nrm in norm_map.items() if "ec" in nrm]
    for si, stag in enumerate(["wet", "dry"]):
        if si < len(ec_cols):
            v = pd.to_numeric(sub[ec_cols[si]], errors="coerce").dropna()
            rec["ec_%s" % stag] = v.mean() if len(v) else np.nan
        else:
            rec["ec_%s" % stag] = np.nan
    if ec_cols:
        all_v = pd.to_numeric(sub[ec_cols[0]], errors="coerce").dropna()
        rec["ec"] = all_v.mean() if len(all_v) else np.nan
    else:
        rec["ec"] = np.nan
    records.append(rec)

df_ion = pd.DataFrame(records)
for stag in ["wet", "dry"]:
    col = "ec_%s" % stag
    if df_ion[col].isna().all():
        df_ion[col] = df_ion["ec"]

# ═══════════════════════════════════════════════════════════════════════
# DATA LOADING - COORDINATES
# ═══════════════════════════════════════════════════════════════════════

if USE_HYDROCHEM_COORDS:
    x_col = find_col("x")
    y_col = find_col("y")
    if x_col and y_col:
        coords = []
        for sname in sample_names:
            sub = df_chem[df_chem[name_col].astype(str).str.strip() == sname]
            xv = pd.to_numeric(sub[x_col], errors="coerce").dropna()
            yv = pd.to_numeric(sub[y_col], errors="coerce").dropna()
            coords.append({
                "sample": sname,
                "X": xv.iloc[0] if len(xv) else np.nan,
                "Y": yv.iloc[0] if len(yv) else np.nan,
            })
        df_coords = pd.DataFrame(coords)
    else:
        print("[warn] X/Y columns not found in hydrochemical file; falling back to isotope file")
        USE_HYDROCHEM_COORDS = False

if not USE_HYDROCHEM_COORDS:
    df_iso = pd.read_excel(ISOTOPE_XLSX, sheet_name="Sheet1")
    df_iso.columns = [str(c).strip() for c in df_iso.columns]
    rename = {}
    for c in df_iso.columns:
        cl = c.lower()
        if cl == "x": rename[c] = "X"
        elif cl == "y": rename[c] = "Y"
    df_iso = df_iso.rename(columns=rename)

    label_col_iso = None
    for c in df_iso.columns:
        cl = c.lower()
        if cl in ("label", "sample", "sample_name", "samplename", "id"):
            label_col_iso = c
            break

    if label_col_iso:
        df_iso["_match"] = df_iso[label_col_iso].astype(str).str.strip()
    else:
        df_iso_filtered = df_iso[df_iso["name"].isin(["spring", "qanat", "well"])].copy()
        if len(df_iso_filtered) == len(sample_names):
            df_iso_filtered["_match"] = sample_names
        else:
            print("[info] Isotope rows (%d) != hydrochem samples (%d)"
                  % (len(df_iso_filtered), len(sample_names)))
            print("       Will attempt to match by source-type order.")
            df_iso_filtered["_match"] = range(len(df_iso_filtered))
        df_iso = df_iso_filtered

    df_coords = df_iso[["_match", "X", "Y"]].rename(columns={"_match": "sample"}).dropna(subset=["X", "Y"])

df_merged = df_ion.merge(df_coords, on="sample", how="inner")

if df_merged.empty:
    print("[warn] Name-based merge returned 0 rows. Trying positional merge...")
    df_coords_pos = df_coords.copy()
    df_coords_pos["_idx"] = range(len(df_coords_pos))
    df_ion_pos = df_ion.copy()
    df_ion_pos["_idx"] = range(len(df_ion_pos))
    df_merged = df_ion_pos.merge(df_coords_pos[["_idx", "X", "Y"]], on="_idx", how="inner")
    df_merged = df_merged.drop(columns=["_idx"])

df_merged = df_merged.dropna(subset=["X", "Y"])
print("[ok] %d samples with coordinates and chemistry" % len(df_merged))

# ── Source / label classification ─────────────────────────────────────
unique_samples = list(pd.unique(df_merged["sample"]))
positional_type = {}
for idx, nm in enumerate(unique_samples):
    if idx < N_SPRING:
        positional_type[nm] = "Spring"
    elif idx < N_SPRING + N_QANAT:
        positional_type[nm] = "Qanat"
    elif idx < N_SPRING + N_QANAT + N_WELL:
        positional_type[nm] = "Well"
    else:
        positional_type[nm] = "Other"

PREFIX = {"Spring": "S", "Qanat": "Q", "Well": "W", "Other": "O"}
type_counters = {}
symbol_map = {}
for nm in unique_samples:
    t = positional_type[nm]
    p = PREFIX[t]
    type_counters[p] = type_counters.get(p, 0) + 1
    symbol_map[nm] = "%s%d" % (p, type_counters[p])

df_merged["source"] = df_merged["sample"].map(positional_type)
df_merged["label"]  = df_merged["sample"].map(symbol_map)

# ── meq/L + facies classification (panel "i") ─────────────────────────
for ion, key in [("Ca", "ca"), ("Mg", "mg"), ("Na", "na"), ("K", "k"),
                  ("Cl", "cl"), ("SO4", "so4"), ("HCO3", "hco3")]:
    df_merged["%s_meq" % ion] = df_merged[key] / MW[ion] * Z[ion]
df_merged["NaK_meq"] = df_merged["Na_meq"] + df_merged["K_meq"]
_cat = df_merged["Ca_meq"] + df_merged["Mg_meq"] + df_merged["NaK_meq"] + 1e-12
_an  = df_merged["HCO3_meq"] + df_merged["SO4_meq"] + df_merged["Cl_meq"] + 1e-12
df_merged["Ca_pct"]   = df_merged["Ca_meq"] / _cat * 100
df_merged["Mg_pct"]   = df_merged["Mg_meq"] / _cat * 100
df_merged["NaK_pct"]  = df_merged["NaK_meq"] / _cat * 100
df_merged["HCO3_pct"] = df_merged["HCO3_meq"] / _an * 100
df_merged["SO4_pct"]  = df_merged["SO4_meq"] / _an * 100
df_merged["Cl_pct"]   = df_merged["Cl_meq"] / _an * 100

def classify_facies(row):
    cats = {"Ca": row["Ca_pct"], "Mg": row["Mg_pct"], "Na-K": row["NaK_pct"]}
    ans  = {"HCO3": row["HCO3_pct"], "SO4": row["SO4_pct"], "Cl": row["Cl_pct"]}
    return "%s-%s" % (max(cats, key=cats.get), max(ans, key=ans.get))

df_merged["facies"] = df_merged.apply(classify_facies, axis=1)

df_m = df_merged

# ═══════════════════════════════════════════════════════════════════════
# SHAPEFILE
# ═══════════════════════════════════════════════════════════════════════

gdf = None
HAS_GDF = False
try:
    import geopandas as gpd
    from shapely.ops import unary_union
    from shapely.geometry import Point
    gdf = gpd.read_file(SHAPEFILE_PATH)
    minx, miny, maxx, maxy = gdf.total_bounds
    HAS_GDF = True
    print("[ok] Shapefile loaded: bounds = (%.0f, %.0f) - (%.0f, %.0f)" % (minx, miny, maxx, maxy))
except Exception as e:
    print("[warn] Shapefile not loaded (%s), using data extent" % e)
    pad_x = (df_merged["X"].max() - df_merged["X"].min()) * 0.15
    pad_y = (df_merged["Y"].max() - df_merged["Y"].min()) * 0.15
    minx = df_merged["X"].min() - pad_x
    maxx = df_merged["X"].max() + pad_x
    miny = df_merged["Y"].min() - pad_y
    maxy = df_merged["Y"].max() + pad_y

range_x = maxx - minx
range_y = maxy - miny
view_minx = minx - range_x * MAP_MARGIN_X
view_maxx = maxx + range_x * MAP_MARGIN_X
view_miny = miny - range_y * MAP_MARGIN_Y
view_maxy = maxy + range_y * MAP_MARGIN_Y

def geom_to_path(geom):
    """Convert a shapely geometry to a matplotlib Path (for clipping)."""
    if geom.geom_type == "Polygon":
        coords = list(geom.exterior.coords)
        codes = [MPath.MOVETO] + [MPath.LINETO] * (len(coords) - 2) + [MPath.CLOSEPOLY]
        verts = list(coords)
        for interior in geom.interiors:
            ic = list(interior.coords)
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(ic) - 2) + [MPath.CLOSEPOLY]
            verts += ic
        return MPath(verts, codes)
    elif geom.geom_type in ("MultiPolygon", "GeometryCollection"):
        sub_paths = [geom_to_path(g) for g in geom.geoms if hasattr(g, "exterior")]
        verts, codes = [], []
        for p in sub_paths:
            verts.extend(p.vertices); codes.extend(p.codes)
        return MPath(verts, codes)
    return None

# ═══════════════════════════════════════════════════════════════════════
# INTERPOLATION HELPER
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

# ═══════════════════════════════════════════════════════════════════════
# SCALE BAR + NORTH ARROW HELPERS  (EDITOR FIX: Fig 7)
# ═══════════════════════════════════════════════════════════════════════

def add_scale_bar(ax):
    """Standard cartographic scale bar: alternating black/white blocks drawn
    in true map units (metres), labelled 0 ... SCALEBAR_KM km above the bar.
    Call after fig.canvas.draw() so the equal-aspect limits are final."""
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    w, h = xmax - xmin, ymax - ymin

    x0 = xmin + SCALEBAR_X0 * w
    y0 = ymin + SCALEBAR_Y0 * h
    bar_h = SCALEBAR_THICKNESS * h
    seg = SCALEBAR_KM * MAP_UNITS_PER_KM / float(SCALEBAR_SEGMENTS)

    for k in range(SCALEBAR_SEGMENTS):
        ax.add_patch(Rectangle((x0 + k * seg, y0), seg, bar_h,
                               facecolor="black" if k % 2 == 0 else "white",
                               edgecolor="black", linewidth=SCALEBAR_LINE_WIDTH,
                               zorder=20, clip_on=False))

    km_per_seg = SCALEBAR_KM / float(SCALEBAR_SEGMENTS)
    for k in range(0, SCALEBAR_SEGMENTS + 1, SCALEBAR_LABEL_EVERY):
        ax.text(x0 + k * seg, y0 + bar_h * 1.4, "%g" % (k * km_per_seg),
                ha="center", va="bottom", fontsize=SCALEBAR_FONT_SIZE,
                zorder=20, clip_on=False)
    # unit to the right of the bar, so it does not crowd the last number
    ax.text(x0 + SCALEBAR_SEGMENTS * seg + 0.015 * w, y0 + bar_h / 2.0, "km",
            ha="left", va="center", fontsize=SCALEBAR_FONT_SIZE,
            zorder=20, clip_on=False)

def add_north_arrow(ax):
    """Standard north arrow: split arrowhead (left half black, right half
    white, black outline) with a bold 'N' above. Drawn in axes fraction so it
    always stays inside the panel frame."""
    x   = NORTH_ARROW_X
    tip = NORTH_ARROW_TIP_Y
    hgt = NORTH_ARROW_HEIGHT
    hw  = NORTH_ARROW_HALF_W
    notch = tip - 0.70 * hgt      # inner point of the arrow base

    left_half  = [(x, tip), (x - hw, tip - hgt), (x, notch)]
    right_half = [(x, tip), (x + hw, tip - hgt), (x, notch)]
    ax.add_patch(mpatches.Polygon(left_half, closed=True, transform=ax.transAxes,
                                  facecolor="black", edgecolor="black",
                                  linewidth=1.2, zorder=20))
    ax.add_patch(mpatches.Polygon(right_half, closed=True, transform=ax.transAxes,
                                  facecolor="white", edgecolor="black",
                                  linewidth=1.2, zorder=20))
    ax.text(x, tip + NORTH_ARROW_GAP, "N", transform=ax.transAxes,
            ha="center", va="bottom",
            fontsize=NORTH_ARROW_FONT, fontweight="bold", zorder=20)

# ═══════════════════════════════════════════════════════════════════════
# FIGURE
# ═══════════════════════════════════════════════════════════════════════

if PANEL_WIDTH is not None and PANEL_HEIGHT is not None:
    total_w = NCOLS * PANEL_WIDTH + (NCOLS - 1) * PANEL_WSPACE
    total_h = NROWS * PANEL_HEIGHT + (NROWS - 1) * PANEL_HSPACE
    fig_w = total_w + 2.0
    fig_h = total_h + 2.0
    fig = plt.figure(figsize=(fig_w, fig_h))
    gs = gridspec.GridSpec(
        NROWS, NCOLS, figure=fig,
        width_ratios=[PANEL_WIDTH] * NCOLS,
        height_ratios=[PANEL_HEIGHT] * NROWS,
        hspace=PANEL_HSPACE / total_h,
        wspace=PANEL_WSPACE / total_w,
    )
else:
    fig = plt.figure(figsize=(20, 20))
    gs = gridspec.GridSpec(NROWS, NCOLS, figure=fig, hspace=PANEL_HSPACE, wspace=PANEL_WSPACE)

fig.patch.set_facecolor("white")
axes = [fig.add_subplot(gs[r, c]) for r in range(NROWS) for c in range(NCOLS)]
panel_letters = [chr(ord("a") + i) for i in range(NROWS * NCOLS)]

def add_panel_label(ax, letter):
    ax.text(0.03, 0.95, "(%s)" % letter, transform=ax.transAxes,
            fontsize=PANEL_LABEL_SIZE, fontweight="bold", va="top", ha="left",
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=2),
            zorder=10)

interp_bounds = (minx, maxx, miny, maxy)

# ─────────────────────────────────────────────────────────────────────
# PANELS (a)-(h): 8 ion concentration maps
# ─────────────────────────────────────────────────────────────────────
for idx, (ion_key, ion_title, ion_unit) in enumerate(IONS):
    ax = axes[idx]
    mask = df_merged[ion_key].notna() & np.isfinite(df_merged[ion_key])
    dfs = df_merged[mask]

    if len(dfs) < 3:
        ax.text(0.5, 0.5, "Not enough data\nfor %s" % ion_title,
                ha="center", va="center", transform=ax.transAxes, fontsize=14)
        add_panel_label(ax, panel_letters[idx])
        continue

    x = dfs["X"].values
    y = dfs["Y"].values
    z = dfs[ion_key].values

    GX, GY, GZ = interpolate_surface(x, y, z, interp_bounds, clip_gdf=gdf if HAS_GDF else None)

    im = ax.pcolormesh(GX, GY, GZ, cmap=CMAP, shading="auto",
                        norm=Normalize(vmin=np.nanmin(GZ), vmax=np.nanmax(GZ)),
                        alpha=0.85, zorder=1, rasterized=True)

    if HAS_GDF:
        gdf.boundary.plot(ax=ax, color="black", linewidth=1.4, zorder=2)

    for src, sty in MARKER_MAP.items():
        sub = dfs[dfs["source"] == src]
        if sub.empty:
            continue
        ax.scatter(sub["X"], sub["Y"], s=POINT_SIZE,
                   marker=sty["marker"], c="white",
                   edgecolors=POINT_EDGE_COLOR, linewidths=POINT_EDGE_WIDTH,
                   label=sty["label"], zorder=4)

    if SHOW_POINT_LABELS:
        for _, row in dfs.iterrows():
            ax.annotate(row["label"], (row["X"], row["Y"]),
                        xytext=POINT_LABEL_OFFSET, textcoords="offset points",
                        fontsize=POINT_LABEL_SIZE, color="black", weight="bold",
                        zorder=5)

    cbar = fig.colorbar(im, ax=ax, shrink=CBAR_HEIGHT, pad=CBAR_PAD, fraction=CBAR_WIDTH)
    cbar.set_label("%s (%s)" % (ion_title, ion_unit), fontsize=CBAR_LABEL_SIZE)
    cbar.ax.tick_params(labelsize=CBAR_TICK_SIZE)

    ax.set_xlim(view_minx, view_maxx)
    ax.set_ylim(view_miny, view_maxy)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xticks([])
    ax.set_yticks([])

    add_panel_label(ax, panel_letters[idx])

# ─────────────────────────────────────────────────────────────────────
# PANEL (i): hydrochemical facies map
# ─────────────────────────────────────────────────────────────────────
FACIES_IDX = 8
ax = axes[FACIES_IDX]

bx = maxx - minx
by = maxy - miny
pts = df_m[["X", "Y"]].values
mirror = np.vstack([pts, pts + [2 * bx, 0], pts - [2 * bx, 0],
                     pts + [0, 2 * by], pts - [0, 2 * by]])
vor = Voronoi(mirror)
for i in range(len(df_m)):
    reg = vor.regions[vor.point_region[i]]
    if -1 in reg or len(reg) == 0:
        continue
    poly = vor.vertices[reg]
    ax.fill(*zip(*poly), alpha=0.30,
            color=FACIES_COLORS.get(df_m.iloc[i]["facies"], "#cccccc"), zorder=0)
    ax.plot(*zip(*np.vstack([poly, poly[0]])), color="grey", lw=0.5, alpha=0.6, zorder=1)

if HAS_GDF:
    gdf.boundary.plot(ax=ax, color="black", linewidth=2.0, zorder=5)
    union_geom = unary_union(gdf.geometry)
    clip_path_geom = geom_to_path(union_geom)
    if clip_path_geom is not None:
        clip_patch = PathPatch(clip_path_geom, transform=ax.transData)
        for artist in ax.get_children():
            try:
                artist.set_clip_path(clip_patch)
            except Exception:
                pass

ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)
ax.set_aspect("equal", "datalim")
ax.set_xticks([]); ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

if FACIES_FRAME_SETTINGS["map_frame"]:
    fig.canvas.draw()
    bbox = ax.get_position()
    frame = Rectangle((bbox.x0, bbox.y0), bbox.width, bbox.height,
                       fill=False, edgecolor=FACIES_FRAME_SETTINGS["map_frame_color"],
                       linewidth=FACIES_FRAME_SETTINGS["map_frame_width"],
                       transform=fig.transFigure, zorder=100)
    fig.patches.append(frame)

for _, row in df_m.iterrows():
    mk = MARKER_MAP.get(row["source"], MARKER_MAP["Other"])
    ax.plot(row["X"], row["Y"], marker=mk["marker"], color=mk["color"],
            ms=FACIES_POINT_SIZES["sample_marker"], zorder=8, mec="white", mew=0.6)

fig.canvas.draw()

for _, row in df_m.iterrows():
    xf, yf = ax.transData.transform((row["X"], row["Y"]))
    xf, yf = fig.transFigure.inverted().transform((xf, yf))

    xf_bar = xf + FACIES_BAR_W * FACIES_BAR_OFFSET_X
    yf_bar = yf + FACIES_BAR_H * FACIES_BAR_OFFSET_Y

    if (xf_bar < 0.02 or yf_bar < 0.02 or
            xf_bar + FACIES_BAR_W > 0.98 or yf_bar + FACIES_BAR_H > 0.98):
        continue

    inax = fig.add_axes([xf_bar, yf_bar, FACIES_BAR_W, FACIES_BAR_H])

    cat_vals = [row["Ca_pct"], row["Mg_pct"], row["NaK_pct"]]
    an_vals  = [row["HCO3_pct"], row["SO4_pct"], row["Cl_pct"]]
    cat_colors = [PIE_CAT["Ca"], PIE_CAT["Mg"], PIE_CAT["Na+K"]]
    an_colors  = [PIE_AN["HCO3"], PIE_AN["SO4"], PIE_AN["Cl"]]

    left = 0
    for val, col in zip(cat_vals, cat_colors):
        inax.barh(1, val, left=left, color=col, height=0.7,
                  edgecolor="white", linewidth=FACIES_POINT_SIZES["bar_edge_width"])
        left += val
    left = 0
    for val, col in zip(an_vals, an_colors):
        inax.barh(0, val, left=left, color=col, height=0.7,
                  edgecolor="white", linewidth=FACIES_POINT_SIZES["bar_edge_width"])
        left += val

    inax.set_xlim(0, 100)
    inax.set_ylim(-0.5, 1.5)
    inax.set_yticks([0, 1])
    inax.set_yticklabels(["An", "Cat"], fontsize=FACIES_TEXT_SIZES["axis_label"], color="#333")
    inax.set_xticks([])
    inax.tick_params(axis="y", length=0, pad=1)
    for spine in ["top", "right", "bottom"]:
        inax.spines[spine].set_visible(False)
    inax.spines["left"].set_linewidth(0.4)
    inax.patch.set_alpha(0.0)

    fig.add_artist(Line2D([xf, xf_bar], [yf, yf_bar], transform=fig.transFigure,
                           color="gray", lw=0.5, zorder=3, alpha=0.6))

for _, row in df_m.iterrows():
    ax.annotate(row["label"], (row["X"], row["Y"]), xytext=(-8, -8),
                textcoords="offset points", fontsize=FACIES_TEXT_SIZES["sample_label"],
                weight="bold", zorder=10, color="#222")

fh = [mpatches.Patch(facecolor=FACIES_COLORS.get(ft, "#ccc"), alpha=0.6,
                     edgecolor="grey", label=ft) for ft in sorted(df_m["facies"].unique())]
cat_handles = [mpatches.Patch(facecolor=c, label=k) for k, c in PIE_CAT.items()]
an_handles  = [mpatches.Patch(facecolor=c, label=k) for k, c in PIE_AN.items()]
facies_marker_handles = [
    Line2D([0], [0], marker=v["marker"], color=v["color"], ms=FACIES_POINT_SIZES["legend_marker"],
           ls="none", label=k, mec="white", mew=0.6)
    for k, v in MARKER_MAP.items() if k != "Other"
]

_lf_kwargs = dict(
    fontsize=FACIES_TEXT_SIZES["legend_text"], title_fontsize=FACIES_TEXT_SIZES["legend_title"],
    framealpha=FACIES_FRAME_SETTINGS["legend_alpha"] if FACIES_FRAME_SETTINGS["legend_frames"] else 0.0,
    edgecolor=FACIES_FRAME_SETTINGS["legend_frame_color"] if FACIES_FRAME_SETTINGS["legend_frames"] else "none",
    facecolor=FACIES_FRAME_SETTINGS["legend_facecolor"] if FACIES_FRAME_SETTINGS["legend_frames"] else "none",
    fancybox=False,
)

# FIX 7i: anchored by its lower-left corner, inside the frame, growing upward
l1 = ax.legend(handles=fh, title="Water type", loc=FACIES_LEGEND_LOCS["water_type"],
               bbox_to_anchor=FACIES_LEGEND_OFFSETS["water_type"], **_lf_kwargs)
if FACIES_FRAME_SETTINGS["legend_frames"]:
    l1.get_frame().set_linewidth(FACIES_FRAME_SETTINGS["legend_frame_width"])
l1.set_zorder(30)
ax.add_artist(l1)

l2 = ax.legend(handles=cat_handles + an_handles, title="Bar chart",
               loc=FACIES_LEGEND_LOCS["bar_chart"],
               bbox_to_anchor=FACIES_LEGEND_OFFSETS["bar_chart"], ncol=2, **_lf_kwargs)
if FACIES_FRAME_SETTINGS["legend_frames"]:
    l2.get_frame().set_linewidth(FACIES_FRAME_SETTINGS["legend_frame_width"])
ax.add_artist(l2)

l3 = ax.legend(handles=facies_marker_handles, title="Sample type",
               loc=FACIES_LEGEND_LOCS["sample_type"],
               bbox_to_anchor=FACIES_LEGEND_OFFSETS["sample_type"], **_lf_kwargs)
if FACIES_FRAME_SETTINGS["legend_frames"]:
    l3.get_frame().set_linewidth(FACIES_FRAME_SETTINGS["legend_frame_width"])

add_panel_label(ax, panel_letters[FACIES_IDX])

# ─────────────────────────────────────────────────────────────────────
# PANELS (j)-(l): EC seasonal comparison
# ─────────────────────────────────────────────────────────────────────
EC_START_IDX = 9

def plot_ec_points(ax, dfs):
    for _, row in dfs.iterrows():
        mk = MARKER_MAP.get(row["source"], MARKER_MAP["Other"])["marker"]
        ax.scatter(row["X"], row["Y"], s=POINT_SIZE, marker=mk, c="white",
                   edgecolors=POINT_EDGE_COLOR, linewidths=POINT_EDGE_WIDTH, zorder=4)
        if SHOW_POINT_LABELS:
            ax.annotate(row["label"], (row["X"], row["Y"]), xytext=POINT_LABEL_OFFSET,
                        textcoords="offset points", fontsize=POINT_LABEL_SIZE,
                        weight="bold", zorder=5)

def fmt_ec_axes(ax):
    if HAS_GDF:
        gdf.boundary.plot(ax=ax, color="black", linewidth=1.4, zorder=2)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect("equal", "datalim")
    ax.set_xticks([]); ax.set_yticks([])

ec_mask = df_m["ec_wet"].notna() & df_m["ec_dry"].notna()
dfs_ec = df_m[ec_mask].copy()

if len(dfs_ec) >= 3:
    vmin = min(dfs_ec["ec_wet"].min(), dfs_ec["ec_dry"].min())
    vmax = max(dfs_ec["ec_wet"].max(), dfs_ec["ec_dry"].max())

    for offset, (col, lbl) in enumerate([("ec_wet", "Wet Season"), ("ec_dry", "Dry Season")]):
        ax = axes[EC_START_IDX + offset]
        GX, GY, GZ = interpolate_surface(dfs_ec["X"].values, dfs_ec["Y"].values,
                                          dfs_ec[col].values, interp_bounds,
                                          clip_gdf=gdf if HAS_GDF else None)
        im = ax.pcolormesh(GX, GY, GZ, cmap=EC_CMAP_CONC, shading="auto",
                           norm=Normalize(vmin=vmin, vmax=vmax), alpha=0.85,
                           zorder=1, rasterized=True)
        plot_ec_points(ax, dfs_ec)
        fmt_ec_axes(ax)
        cbar = fig.colorbar(im, ax=ax, shrink=CBAR_HEIGHT, pad=CBAR_PAD, fraction=CBAR_WIDTH)
        cbar.set_label(EC_PARAM_LABEL, fontsize=CBAR_LABEL_SIZE)
        cbar.ax.tick_params(labelsize=CBAR_TICK_SIZE)
        add_panel_label(ax, panel_letters[EC_START_IDX + offset])

    ax = axes[EC_START_IDX + 2]
    dfs_ec["_diff"] = dfs_ec["ec_dry"] - dfs_ec["ec_wet"]
    GX, GY, GZ_d = interpolate_surface(dfs_ec["X"].values, dfs_ec["Y"].values,
                                        dfs_ec["_diff"].values, interp_bounds,
                                        clip_gdf=gdf if HAS_GDF else None)
    dmax = max(abs(np.nanmin(GZ_d)), abs(np.nanmax(GZ_d)))
    dmax = dmax if dmax > 0 else 1
    im_d = ax.pcolormesh(GX, GY, GZ_d, cmap=EC_CMAP_DIFF, shading="auto",
                         norm=TwoSlopeNorm(vmin=-dmax, vcenter=0, vmax=dmax),
                         alpha=0.85, zorder=1, rasterized=True)
    plot_ec_points(ax, dfs_ec)
    fmt_ec_axes(ax)
    cbar = fig.colorbar(im_d, ax=ax, shrink=CBAR_HEIGHT, pad=CBAR_PAD, fraction=CBAR_WIDTH)
    cbar.set_label("\u0394 %s" % EC_PARAM_LABEL, fontsize=CBAR_LABEL_SIZE)
    cbar.ax.tick_params(labelsize=CBAR_TICK_SIZE)
    add_panel_label(ax, panel_letters[EC_START_IDX + 2])
else:
    for offset in range(3):
        ax = axes[EC_START_IDX + offset]
        ax.text(0.5, 0.5, "Not enough seasonal\nEC data", ha="center", va="center",
                transform=ax.transAxes, fontsize=14)
        add_panel_label(ax, panel_letters[EC_START_IDX + offset])

# ─────────────────────────────────────────────────────────────────────
# EDITOR FIX (Fig 7): one scale bar and one north arrow, on panel (j)
# ─────────────────────────────────────────────────────────────────────
_sb_idx = panel_letters.index(SCALEBAR_PANEL)
fig.canvas.draw()   # settle the equal-aspect limits before sizing the bar
add_scale_bar(axes[_sb_idx])
add_north_arrow(axes[_sb_idx])

# ─────────────────────────────────────────────────────────────────────
# Hide unused panels
# ─────────────────────────────────────────────────────────────────────
for j in range(12, NROWS * NCOLS):
    axes[j].set_visible(False)

# ─────────────────────────────────────────────────────────────────────
# Shared bottom legend (sample-type markers)
# ─────────────────────────────────────────────────────────────────────
legend_handles = []
for src, sty in MARKER_MAP.items():
    if src in df_merged["source"].values:
        legend_handles.append(
            Line2D([0], [0], marker=sty["marker"], color="w",
                   markerfacecolor="white", markeredgecolor="black",
                   markeredgewidth=1.2, markersize=10, label=sty["label"]))

_last_used_idx = max(idx for idx in range(NROWS * NCOLS) if axes[idx].get_visible())
_legend_anchor_ax = axes[_last_used_idx - (_last_used_idx % NCOLS) + NCOLS // 2]
fig.legend(handles=legend_handles, loc="upper center", ncol=len(legend_handles),
           fontsize=LEGEND_SIZE, frameon=True,
           bbox_to_anchor=(LEGEND_X, LEGEND_Y), bbox_transform=_legend_anchor_ax.transAxes)

# ═══════════════════════════════════════════════════════════════════════
# SAVE - PDF (for submission) and PNG
# ═══════════════════════════════════════════════════════════════════════
for ext in ("pdf", "png"):
    out_path = os.path.join(OUTPUT_DIR, "%s.%s" % (OUT_BASENAME, ext))
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
    print("[ok] saved -> %s" % out_path)
plt.close(fig)
