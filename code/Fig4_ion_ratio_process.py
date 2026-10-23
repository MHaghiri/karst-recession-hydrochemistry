"""
Fig 4 - Ion Ratio & Process Plots
Panels: (a) Gibbs-Cations (b) Gibbs-Anions (c-j) bivariate plots (k) CAI-1 (l) CAI-2

Revised for Hydrogeology Journal technical-editor comments (HYJO-D-26-00525R1):

  COMMENT 1 - "reverse exchange / direct exchange labels are unclear and how
               they relate to the bars is unclear due to overlapping of
               sub-figure labels k and l - please reposition the sub-figure
               letter labels to the top left"
    -> Panel letters moved OUTSIDE each axis, to the top-left corner above the
       frame, for every panel (a-l), so nothing can overlap panel content.
    -> The free-text "+= Reverse exchange / -= Direct exchange" note in (k)/(l)
       is replaced by a proper colour legend keyed to the bars themselves:
       red bar = CAI > 0 = reverse ion exchange, blue bar = CAI < 0 = direct.

  COMMENT 2 - "Some graphs contain a legend for the 1:1 line and others don't.
               Some graphs contain an additional line (trend line?), please make
               this consistent between graphs, and make it clear which line is
               which"
    -> Every scatter panel (a-j) now carries its own line legend naming each
       line that is drawn on it. The 1:1 line is drawn on panels (c-g, i, j);
       panels (a), (b) and (h) show the trend line only.
    -> Line styles are now fixed and distinct: 1:1 solid grey,
       linear trend dashed black.

Output written as both PDF (vector, for submission) and PNG.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# USER SETTINGS  <- edit here
# ═══════════════════════════════════════════════════════════════════════════════
FIGURE_SIZE         = (26, 18)
FIGURE_DPI          = 1000

# 1 ── Panel spacing
HSPACE              = 0.26   # vertical space between rows (raised: labels now sit above each panel)
WSPACE              = 0.22   # horizontal space between columns

# 2 ── Panel letter labels  (FIX 1: now OUTSIDE the axes, top-left)
PANEL_LABEL_SIZE    = 20
PANEL_LABEL_X       = -0.02   # axes fraction; negative = left of the y-axis
PANEL_LABEL_Y       = 1.04    # axes fraction; >1 = above the top frame
PANEL_LABEL_VA      = 'bottom'
PANEL_LABEL_HA      = 'right'

# 4 ── Water-source legend placed inside panel (e)
LEG_SIZE            = 14
LEG_LOC             = 'upper left'
LEG_BBOX            = (0.02, 0.92)   # None = use LEG_LOC

# 4b ── Line legend shown on every scatter panel (FIX 2)
LINE_LEG_SIZE       = 11
LINE_LEG_LOC        = 'lower right'

# 4c ── CAI bar legend (FIX 1)
CAI_LEG_SIZE        = 11
CAI_LEG_LOC         = 'upper right'

# 5 ── Axis label & tick sizes
LABEL_SIZE          = 14
TICK_SIZE           = 13

# General
POINT_SIZE          = 160

# ── Point (sample-code) labels on scatter panels a-j ──────────────────────────
SHOW_POINT_LABELS   = True
POINT_LABEL_SIZE    = 10
POINT_LABEL_COLOR   = 'black'
POINT_LABEL_OFFSET  = (4, 4)

# ── Line styling (FIX 2: fixed, distinct, and named in every legend) ──────────
SHOW_CORR_LINE      = True
CORR_LINE_COLOR     = 'black'
CORR_LINE_STYLE     = '--'
CORR_LINE_WIDTH     = 1.4
CORR_LINE_LABEL     = 'Linear trend'

REF_LINE_COLOR      = '#555555'
REF_LINE_STYLE      = '-'
REF_LINE_WIDTH      = 1.4

# ── Output file name (saved into OUT_DIR, both formats) ──────────────────────
OUT_BASENAME        = "Fig4"

# ── Water-source classification ───────────────────────────────────────────────
N_SPRING = 11
N_QANAT  = 4
N_WELL   = 4
SOURCE_TYPE_OVERRIDE = {}

# 6 ── Style map: (source_type, season) -> appearance
STYLE_MAP = {
    ('Spring', 'Wet'): dict(marker='o', color='#1B8A1B', edgecolor='#1B8A1B', filled=True,  label='Spring (Wet)'),
    ('Spring', 'Dry'): dict(marker='o', color='#1B8A1B', edgecolor='#1B8A1B', filled=False, label='Spring (Dry)'),
    ('Qanat',  'Wet'): dict(marker='s', color='#1565C0', edgecolor='#1565C0', filled=True,  label='Qanat (Wet)'),
    ('Qanat',  'Dry'): dict(marker='s', color='#1565C0', edgecolor='#1565C0', filled=False, label='Qanat (Dry)'),
    ('Well',   'Wet'): dict(marker='^', color='#BF360C', edgecolor='#BF360C', filled=True,  label='Well (Wet)'),
    ('Well',   'Dry'): dict(marker='^', color='#BF360C', edgecolor='#BF360C', filled=False, label='Well (Dry)'),
    ('Other',  'Wet'): dict(marker='d', color='#616161', edgecolor='#616161', filled=True,  label='Other (Wet)'),
    ('Other',  'Dry'): dict(marker='d', color='#616161', edgecolor='#616161', filled=False, label='Other (Dry)'),
}

# CAI bar colours (FIX 1: these are now explained in a legend, not free text)
CAI_POS_COLOR = '#e74c3c'   # CAI > 0  -> reverse ion exchange
CAI_NEG_COLOR = '#3498db'   # CAI < 0  -> direct ion exchange

# ═══════════════════════════════════════════════════════════════════════════════

import os, sys, io, re, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
warnings.filterwarnings('ignore')

# Keep text as real text in the PDF (editable, scalable, never pixelated)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype']  = 42

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_PATH = r"C:\Users\mhaghi2\Desktop\Article 9\data\hydrochemical\hydrochemical.xlsx"
OUT_DIR   = r"C:\Users\mhaghi2\Desktop\Article 9\map"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────
raw = pd.read_excel(DATA_PATH, header=None)
ION_KEYWORDS = ['ca','mg','na','cl','so4','hco3','ec','tds','ph','temp']
def row_score(row):
    return sum(1 for v in row if isinstance(v, str) and any(k in v.lower() for k in ION_KEYWORDS))
header_row = max(range(min(5, len(raw))), key=lambda i: row_score(raw.iloc[i]))
raw_headers = raw.iloc[header_row].tolist()
filled, last = [], 'col'
for v in raw_headers:
    if pd.isna(v) or str(v).strip() == '':
        filled.append(last)
    else:
        last = str(v).strip(); filled.append(last)
seen = {}; unique_headers = []
for h in filled:
    hl = h.lower(); seen[hl] = seen.get(hl, 0) + 1
    unique_headers.append(h if seen[hl] == 1 else "%s_%d" % (h, seen[hl]))
df_raw = raw.iloc[header_row+1:].copy()
df_raw.columns = unique_headers
df_raw = df_raw.reset_index(drop=True)

def normalise(s):
    return str(s).strip().lower().replace(' ','').replace('+','').replace('-','') \
                 .replace('²','2').replace('2+','')
norm_map     = {c: normalise(c) for c in df_raw.columns}
name_col_raw = df_raw.columns[0]
TARGET = ['ca','mg','na','k','cl','so4','hco3','ec','tds','ph','temp']

def find_cols(tgt):
    return [c for c, nn in norm_map.items() if tgt in nn]

ca_cols   = find_cols('ca')
n_seasons = max(1, len(ca_cols))
seasons   = []
for s_idx in range(n_seasons):
    sl    = ['Wet','Dry','S3','S4'][s_idx] if n_seasons > 1 else 'All'
    block = {'sample': df_raw[name_col_raw]}
    for tgt in TARGET:
        cands = find_cols(tgt)
        block[tgt] = pd.to_numeric(df_raw[cands[s_idx]], errors='coerce') \
                     if s_idx < len(cands) else np.nan
    bdf = pd.DataFrame(block); bdf['season'] = sl; seasons.append(bdf)
df = pd.concat(seasons, ignore_index=True)
df = df.dropna(subset=['ca','mg','na','k','cl','so4','hco3'], how='all')
df = df[pd.to_numeric(df['sample'], errors='coerce').isna()]
df = df[df['sample'].notna() & (df['sample'].astype(str).str.strip() != '')]
df = df.reset_index(drop=True)
for col in TARGET:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].median())

# ── meq/L conversion ──────────────────────────────────────────────────────────
mw = {'Ca':40.078,'Mg':24.305,'Na':22.990,'K':39.098,'Cl':35.453,'SO4':96.062,'HCO3':61.016}
z  = {'Ca':2,'Mg':2,'Na':1,'K':1,'Cl':1,'SO4':2,'HCO3':1}
def to_meq(col, ion): return df[col] / mw[ion] * z[ion]
Ca   = to_meq('ca','Ca');  Mg  = to_meq('mg','Mg')
Na   = to_meq('na','Na');  K   = to_meq('k','K')
Cl   = to_meq('cl','Cl'); SO4  = to_meq('so4','SO4'); HCO3 = to_meq('hco3','HCO3')

n             = len(df)
short_labels  = df['sample'].astype(str).values
season_labels = df['season'].astype(str).values

TDS_v     = df['tds'].values if 'tds' in df.columns else \
            (df['ca']+df['mg']+df['na']+df['k']+df['cl']+df['so4']+df['hco3']).values
ratio_cat = df['na'].values / (df['na'].values + df['ca'].values + 1e-9)
ratio_an  = df['cl'].values / (df['cl'].values + df['hco3'].values + 1e-9)
CAI1 = (Cl - (Na+K)) / (Cl + 1e-12)
CAI2 = (Cl - (Na+K)) / (SO4 + HCO3 + Cl + 1e-12)

# ── Water-source classification ───────────────────────────────────────────────
_unique_samples  = list(pd.unique(df['sample'].astype(str)))
_positional_type = {}
for _idx, _name in enumerate(_unique_samples):
    if   _idx < N_SPRING:
        _positional_type[_name] = 'Spring'
    elif _idx < N_SPRING + N_QANAT:
        _positional_type[_name] = 'Qanat'
    elif _idx < N_SPRING + N_QANAT + N_WELL:
        _positional_type[_name] = 'Well'
    else:
        _positional_type[_name] = 'Other'

def get_source_type(name):
    s  = str(name).strip()
    if s in SOURCE_TYPE_OVERRIDE:
        return SOURCE_TYPE_OVERRIDE[s]
    su = s.upper()
    m  = re.match(r'^([A-Z])\s*\d', su)
    if m:
        first = m.group(1)
        if first == 'S': return 'Spring'
        if first == 'Q': return 'Qanat'
        if first == 'W': return 'Well'
    return _positional_type.get(s, 'Other')

source_types = [get_source_type(nm) for nm in short_labels]

PREFIX_MAP = {'Spring': 'S', 'Qanat': 'Q', 'Well': 'W', 'Other': 'O'}
_type_counter = {}
cai_xlabels = []
for st in source_types:
    prefix = PREFIX_MAP.get(st, 'O')
    _type_counter[prefix] = _type_counter.get(prefix, 0) + 1
    cai_xlabels.append("%s%d" % (prefix, _type_counter[prefix]))

# ── Style helpers ─────────────────────────────────────────────────────────────
def get_style(i):
    key = (source_types[i], season_labels[i])
    return STYLE_MAP.get(key,
           STYLE_MAP.get((source_types[i], 'Wet'),
           STYLE_MAP[('Other', 'Wet')]))

def scatter_point(ax, x, y, i, size=None):
    st = get_style(i)
    s  = size if size else POINT_SIZE
    fc = st['color'] if st['filled'] else 'white'
    ax.scatter(x, y, c=[fc], s=s, marker=st['marker'],
               edgecolors=st['edgecolor'], linewidths=1.0, zorder=6, alpha=0.9)

def add_point_labels(ax, xv, yv):
    if not SHOW_POINT_LABELS:
        return
    xv = np.asarray(xv, dtype=float)
    yv = np.asarray(yv, dtype=float)
    for i in range(n):
        ax.annotate(cai_xlabels[i], (xv[i], yv[i]),
                    xytext=POINT_LABEL_OFFSET, textcoords='offset points',
                    fontsize=POINT_LABEL_SIZE, color=POINT_LABEL_COLOR, zorder=7)

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 2 - line drawing helpers.
# Each returns a legend handle (or None), so every panel can build a legend
# naming exactly the lines it actually shows.
# ═══════════════════════════════════════════════════════════════════════════════

def add_corr_line(ax, xv, yv):
    """Dashed black linear trend line. Returns its legend handle."""
    if not SHOW_CORR_LINE:
        return None
    xv = np.asarray(xv, dtype=float)
    yv = np.asarray(yv, dtype=float)
    mask = np.isfinite(xv) & np.isfinite(yv)
    if mask.sum() < 2:
        return None
    slope, intercept = np.polyfit(xv[mask], yv[mask], 1)
    x_line = np.array([xv[mask].min(), xv[mask].max()])
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, color=CORR_LINE_COLOR, linestyle=CORR_LINE_STYLE,
            lw=CORR_LINE_WIDTH, zorder=5)
    return Line2D([], [], color=CORR_LINE_COLOR, linestyle=CORR_LINE_STYLE,
                  lw=CORR_LINE_WIDTH, label=CORR_LINE_LABEL)

def add_ref_line(ax, xv, yv, kind):
    """Solid grey reference line: '1:1' (equal) or '1:-1' (reverse exchange)."""
    if kind is None:
        return None
    xv = np.asarray(xv, dtype=float)
    yv = np.asarray(yv, dtype=float)
    if kind == '1:1':
        mn = min(xv.min(), yv.min()) * 0.9
        mx = max(xv.max(), yv.max()) * 1.1
        ax.plot([mn, mx], [mn, mx], color=REF_LINE_COLOR,
                linestyle=REF_LINE_STYLE, lw=REF_LINE_WIDTH, zorder=4)
        lbl = '1:1 line'
    elif kind == '1:-1':
        mx = max(abs(xv).max(), abs(yv).max()) * 1.1
        ax.plot([-mx, mx], [mx, -mx], color=REF_LINE_COLOR,
                linestyle=REF_LINE_STYLE, lw=REF_LINE_WIDTH, zorder=4)
        lbl = '1:$-$1 line'
    else:
        return None
    return Line2D([], [], color=REF_LINE_COLOR, linestyle=REF_LINE_STYLE,
                  lw=REF_LINE_WIDTH, label=lbl)

# ── Water-source legend handles ───────────────────────────────────────────────
legend_handles = []
preferred_order = [
    ('Spring','Wet'), ('Spring','Dry'),
    ('Qanat', 'Wet'), ('Qanat', 'Dry'),
    ('Well',  'Wet'), ('Well',  'Dry'),
    ('Other', 'Wet'), ('Other', 'Dry'),
]
present_keys = set(zip(source_types, season_labels))
for key in preferred_order:
    if key in present_keys:
        st = STYLE_MAP.get(key, STYLE_MAP[('Other','Wet')])
        fc = st['color'] if st['filled'] else 'white'
        legend_handles.append(
            Line2D([], [], marker=st['marker'], color='w',
                   markerfacecolor=fc, markeredgecolor=st['edgecolor'],
                   markeredgewidth=1.0, markersize=10, label=st['label'])
        )

# ── General helpers ───────────────────────────────────────────────────────────
def save(fig, basename):
    """Write the figure as PDF (vector, for submission) and PNG."""
    pdf_path = os.path.join(OUT_DIR, basename + ".pdf")
    png_path = os.path.join(OUT_DIR, basename + ".png")
    fig.savefig(pdf_path, dpi=FIGURE_DPI, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("  Saved -> %s" % pdf_path)
    fig.savefig(png_path, dpi=FIGURE_DPI, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("  Saved -> %s" % png_path)
    plt.close(fig)

plt.rcParams.update({
    'xtick.labelsize': TICK_SIZE,
    'ytick.labelsize': TICK_SIZE,
})
print("Data loaded: %d samples" % n)

def add_panel_label(ax, letter):
    """FIX 1: panel letter sits outside the axes, top-left, so it cannot
    overlap any plotted content or annotation."""
    ax.text(PANEL_LABEL_X, PANEL_LABEL_Y, '(%s)' % letter,
            transform=ax.transAxes,
            fontsize=PANEL_LABEL_SIZE, fontweight='bold',
            va=PANEL_LABEL_VA, ha=PANEL_LABEL_HA, zorder=10,
            clip_on=False)

def sp(x, y, xl, yl, ax, refkind='1:1'):
    """Generic bivariate panel with point labels, a reference line and a trend
    line, plus a legend naming whichever lines were drawn (FIX 2)."""
    xv = np.asarray(x, dtype=float)
    yv = np.asarray(y, dtype=float)
    for i in range(n):
        scatter_point(ax, xv[i], yv[i], i)
    add_point_labels(ax, xv, yv)

    line_handles = []
    h_ref  = add_ref_line(ax, xv, yv, refkind)
    if h_ref is not None:
        line_handles.append(h_ref)
    h_corr = add_corr_line(ax, xv, yv)
    if h_corr is not None:
        line_handles.append(h_corr)

    if line_handles:
        ax.legend(handles=line_handles, fontsize=LINE_LEG_SIZE,
                  loc=LINE_LEG_LOC, framealpha=0.85)

    ax.set_xlabel(xl, fontsize=LABEL_SIZE)
    ax.set_ylabel(yl, fontsize=LABEL_SIZE)
    ax.grid(alpha=0.3)
    return line_handles

# ═══════════════════════════════════════════════════════════════════════════════
# Build figure
# ═══════════════════════════════════════════════════════════════════════════════
fig2 = plt.figure(figsize=FIGURE_SIZE)
gs2  = gridspec.GridSpec(3, 4, figure=fig2, hspace=HSPACE, wspace=WSPACE)

# ── Row 1 ─────────────────────────────────────────────────────────────────────

# (a) Gibbs - Cations   [no reference line: axes are not comparable]
ax_a = fig2.add_subplot(gs2[0, 0])
for i in range(n):
    scatter_point(ax_a, ratio_cat[i], TDS_v[i], i)
add_point_labels(ax_a, ratio_cat, TDS_v)
h_a = add_corr_line(ax_a, ratio_cat, TDS_v)
ax_a.set_yscale('log')
ax_a.set_xlabel('Na$^+$/(Na$^+$+Ca$^{2+}$)', fontsize=LABEL_SIZE)
ax_a.set_ylabel('TDS (mg/L)', fontsize=LABEL_SIZE)
for txt, xy in [('Precipitation',   (0.50, TDS_v.min()*1.5)),
                ('Rock Weathering', (0.45, np.median(TDS_v))),
                ('Evaporation',     (0.85, TDS_v.max()*0.7))]:
    ax_a.text(xy[0], xy[1], txt, fontsize=TICK_SIZE-2,
              color='grey', ha='center', style='normal')
ax_a.grid(alpha=0.3)
if h_a is not None:
    ax_a.legend(handles=[h_a], fontsize=LINE_LEG_SIZE,
                loc=LINE_LEG_LOC, framealpha=0.85)
add_panel_label(ax_a, 'a')

# (b) Gibbs - Anions    [no reference line: axes are not comparable]
ax_b = fig2.add_subplot(gs2[0, 1])
for i in range(n):
    scatter_point(ax_b, ratio_an[i], TDS_v[i], i)
add_point_labels(ax_b, ratio_an, TDS_v)
h_b = add_corr_line(ax_b, ratio_an, TDS_v)
ax_b.set_yscale('log')
ax_b.set_xlabel('Cl$^-$/(Cl$^-$+HCO$_3^-$)', fontsize=LABEL_SIZE)
ax_b.set_ylabel('TDS (mg/L)', fontsize=LABEL_SIZE)
ax_b.grid(alpha=0.3)
if h_b is not None:
    ax_b.legend(handles=[h_b], fontsize=LINE_LEG_SIZE,
                loc=LINE_LEG_LOC, framealpha=0.85)
add_panel_label(ax_b, 'b')

# (c) Carbonate vs Evaporite
ax_c = fig2.add_subplot(gs2[0, 2])
sp(Ca+Mg, HCO3+SO4,
   'Ca$^{2+}$+Mg$^{2+}$ (meq/L)', 'HCO$_3^-$+SO$_4^{2-}$ (meq/L)',
   ax_c, refkind='1:1')
add_panel_label(ax_c, 'c')

# (d) Calcite vs Dolomite
ax_d = fig2.add_subplot(gs2[0, 3])
sp(Ca, Mg, 'Ca$^{2+}$ (meq/L)', 'Mg$^{2+}$ (meq/L)', ax_d, refkind='1:1')
add_panel_label(ax_d, 'd')

# ── Row 2 ─────────────────────────────────────────────────────────────────────

# (e) Gypsum Dissolution  <- water-source legend placed here
ax_e = fig2.add_subplot(gs2[1, 0])
line_h_e = sp(Ca, SO4, 'Ca$^{2+}$ (meq/L)', 'SO$_4^{2-}$ (meq/L)',
              ax_e, refkind='1:1')
# keep the line legend (added by sp) and add the water-source legend separately
if LEG_BBOX is not None:
    leg_src = ax_e.legend(handles=legend_handles, fontsize=LEG_SIZE,
                          bbox_to_anchor=LEG_BBOX, loc='upper left',
                          framealpha=0.85, borderpad=0.6)
else:
    leg_src = ax_e.legend(handles=legend_handles, fontsize=LEG_SIZE,
                          loc=LEG_LOC, framealpha=0.85, borderpad=0.6)
if line_h_e:
    ax_e.add_artist(leg_src)
    ax_e.legend(handles=line_h_e, fontsize=LINE_LEG_SIZE,
                loc=LINE_LEG_LOC, framealpha=0.85)
add_panel_label(ax_e, 'e')

# (f) Halite / Cation Exchange
ax_f = fig2.add_subplot(gs2[1, 1])
sp(Na, Cl, 'Na$^+$ (meq/L)', 'Cl$^-$ (meq/L)', ax_f, refkind='1:1')
add_panel_label(ax_f, 'f')

# (g) Cation Exchange
ax_g = fig2.add_subplot(gs2[1, 2])
sp(Ca+Mg, Na+K,
   'Ca$^{2+}$+Mg$^{2+}$ (meq/L)', 'Na$^+$+K$^+$ (meq/L)',
   ax_g, refkind='1:1')
add_panel_label(ax_g, 'g')

# (h) Reverse Cation Exchange  [original format: no reference line]
ax_h = fig2.add_subplot(gs2[1, 3])
sp(Na+K-Cl, Ca+Mg-HCO3-SO4,
   '(Na$^+$+K$^+$)$-$Cl$^-$ (meq/L)',
   '(Ca$^{2+}$+Mg$^{2+}$)$-$(HCO$_3^-$+SO$_4^{2-}$)',
   ax_h, refkind=None)
add_panel_label(ax_h, 'h')

# ── Row 3 ─────────────────────────────────────────────────────────────────────

# (i) Carbonate Weathering
ax_i = fig2.add_subplot(gs2[2, 0])
sp(HCO3, Ca, 'HCO$_3^-$ (meq/L)', 'Ca$^{2+}$ (meq/L)', ax_i, refkind='1:1')
add_panel_label(ax_i, 'i')

# (j) Chloro-Alkaline Indicator
ax_j = fig2.add_subplot(gs2[2, 1])
sp(Cl+SO4, HCO3, 'Cl$^-$+SO$_4^{2-}$ (meq/L)', 'HCO$_3^-$ (meq/L)',
   ax_j, refkind='1:1')
add_panel_label(ax_j, 'j')

# ── (k) CAI-1  and  (l) CAI-2 ────────────────────────────────────────────────
# FIX 1: the free-text exchange note is replaced by a colour legend tied to the
# bars, and the panel letters now sit outside the axes.
cai_legend_handles = [
    mpatches.Patch(facecolor=CAI_POS_COLOR, edgecolor='k', linewidth=0.3,
                   label='CAI > 0: reverse ion exchange'),
    mpatches.Patch(facecolor=CAI_NEG_COLOR, edgecolor='k', linewidth=0.3,
                   label='CAI < 0: direct ion exchange'),
]

for ax, cai, letter in [
    (fig2.add_subplot(gs2[2, 2]), CAI1, 'k'),
    (fig2.add_subplot(gs2[2, 3]), CAI2, 'l'),
]:
    bar_colors = [CAI_POS_COLOR if v > 0 else CAI_NEG_COLOR for v in cai]
    ax.bar(range(n), cai, color=bar_colors, edgecolor='k', lw=0.3, width=0.8)
    ax.axhline(0, color='k', lw=1.5, ls='--')

    ax.set_xticks(range(n))
    ax.set_xticklabels(cai_xlabels, rotation=90, fontsize=TICK_SIZE - 1)

    ax.set_xlabel('Sample', fontsize=LABEL_SIZE)
    ax.set_ylabel('CAI-1' if letter == 'k' else 'CAI-2', fontsize=LABEL_SIZE)
    ax.grid(axis='y', alpha=0.3)

    # headroom so the legend does not sit on top of the tallest bars
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin, ymax + (ymax - ymin) * 0.22)

    ax.legend(handles=cai_legend_handles, fontsize=CAI_LEG_SIZE,
              loc=CAI_LEG_LOC, framealpha=0.9)
    add_panel_label(ax, letter)

# ── Save ──────────────────────────────────────────────────────────────────────
save(fig2, OUT_BASENAME)
