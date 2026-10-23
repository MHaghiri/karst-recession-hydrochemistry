"""
Fig 6 - Saturation Index Analysis
Panels: (a1-a4) SI bar charts  (b) SI vs pH  (c) SIcalcite vs Temp  (d) SIcalcite vs SIdolomite

Revised for Hydrogeology Journal technical-editor comments (HYJO-D-26-00525R1):
  Fig 6  - "SI Calcite" / "SI Dolomite" -> SI with subscript mineral name
           (SI_calcite, SI_dolomite) on every axis, colour bar and label.
  Fig 6c - colour scale now spans only the plotted data range, so the full
           colour ramp is used (no empty range above the data).
         - colour scale bar title at the same size and style as the axis titles.
         - "r" in the trend-line legend is italic. The value is a Pearson
           correlation coefficient (np.corrcoef), not a regression R2, so "r"
           is the correct symbol.
  Fig 6d - "Both supersaturated" moved to the top-right corner (the direction
           of positive SI on both axes); "Both undersaturated" stays bottom-left.
         - "r" italic, as in 6c.
  Output written as both PDF (vector, for submission) and PNG.
"""
# ═══════════════════════════════════════════════════════════════════════════════
# USER SETTINGS  <- edit everything in this block
# ═══════════════════════════════════════════════════════════════════════════════

# ── Figure & font sizes ───────────────────────────────────────────────────────
FIGURE_SIZE         = (24, 18)
FIGURE_DPI          = 1000
SUPTITLE_SIZE       = 17
TICK_SIZE           = 18
LABEL_SIZE          = 20
PANEL_TITLE_SIZE    = 20
POINT_SIZE          = 240
ANNOTATION_SIZE     = 11
BAR_SAMPLE_SIZE     = 11
SI_ANNOT_SIZE       = 14

# ── Mineral SI labels (EDITOR FIX: subscript mineral names) ──────────────────
SI_LABEL = {
    'Calcite':  r'SI$_{\mathrm{calcite}}$',
    'Dolomite': r'SI$_{\mathrm{dolomite}}$',
    'Gypsum':   r'SI$_{\mathrm{gypsum}}$',
    'Halite':   r'SI$_{\mathrm{halite}}$',
}

# ── Spacing between the 4 main panels (outer grid) ───────────────────────────
OUTER_HSPACE        = 0.1
OUTER_WSPACE        = 0.1

# ── Spacing INSIDE Panel A (the 2x2 inner bar-chart grid) ────────────────────
PANEL_A_HSPACE      = 0.15
PANEL_A_WSPACE      = 0.18

# ── Legend sizes (font & marker) ─────────────────────────────────────────────
LEGEND_SIZE         = 14
LEGEND_MARKER_SCALE = 1.0
LEGEND_FRAME        = True
LEGEND_NCOL_B       = 1
LEGEND_NCOL_C       = 1
LEGEND_NCOL_D       = 1
LEGEND_NCOL_BOTTOM  = 1

# ── Panel label positions (x, y) in AXES fraction ────────────────────────────
LABEL_A1_XY        = (0.02, 0.97)
LABEL_A2_XY        = (0.02, 0.97)
LABEL_A3_XY        = (0.02, 0.97)
LABEL_A4_XY        = (0.02, 0.97)
LABEL_B_XY         = (0.02, 0.95)
LABEL_C_XY         = (0.02, 0.93)
LABEL_D_XY         = (0.02, 0.93)

# ── Panel B legend position ───────────────────────────────────────────────────
LEG_B_XY            = (0.02, 0.9)
LEG_B_LOC           = 'upper left'
LEG_B_ANCHOR        = 'upper left'

# ── Panel C legend position (inside panel) ────────────────────────────────────
LEG_C_XY            = (0.38, 0.75)
LEG_C_LOC           = 'upper right'
LEG_C_ANCHOR        = 'upper right'

# ── Panel D legend position ───────────────────────────────────────────────────
LEG_D_XY            = (0.94, 0.02)
LEG_D_LOC           = 'lower right'
LEG_D_ANCHOR        = 'lower right'

# ── Panel D: corner annotation text size ──────────────────────────────────────
PANEL_D_ANNOT_SIZE  = 16

# ── Bottom figure legend (SI > 0 / SI < 0) ───────────────────────────────────
LEG_BOTTOM_XY       = (0.19, 0.38)
LEGEND_BOTTOM_SIZE  = 14

# ── Panel B: two-colour legend for Calcite vs Dolomite ───────────────────────
CAL_LEGEND_COLOR    = '#333333'
DOL_LEGEND_COLOR    = '#888888'
CAL_LEGEND_ALPHA    = 0.9
DOL_LEGEND_ALPHA    = 0.40

# ── Panel C colour bar (EDITOR FIX 6c) ───────────────────────────────────────
# None = fit the colour scale to the range of the PLOTTED points only, so the
# whole colour ramp is spent on the data. Set numbers to override, e.g. -15, -12.
CBAR_VMIN           = None
CBAR_VMAX           = None
CBAR_PAD_FRAC       = 0.02     # small margin added around the data range
CBAR_CMAP           = 'RdBu_r'
CBAR_TITLE_SIZE     = LABEL_SIZE   # same size as the axis titles
CBAR_TICK_SIZE      = TICK_SIZE    # same size as the axis tick labels

# ── Panel C: point sizes per source type ──────────────────────────────────────
POINT_SIZE_C_SPRING = 240
POINT_SIZE_C_QANAT  = 240
POINT_SIZE_C_WELL   = 240

# ── Panel B point labels ──────────────────────────────────────────────────────
SHOW_LABELS_B       = True
PANEL_B_LABEL_SIZE  = 11

# ── Axis domains (None = automatic) ──────────────────────────────────────────
PANEL_B_XLIM        = (6, 9)
PANEL_B_YLIM        = (-19, -10)
PANEL_C_XLIM        = (16, 28)
PANEL_C_YLIM        = (-15, -12)
PANEL_D_XLIM        = (-15, -12)
PANEL_D_YLIM        = (-19, -12)

# ── Correlation / trend lines for panels B, C, D ──────────────────────────────
SHOW_CORR_LINE_B      = True
SHOW_CORR_LINE_C      = True
SHOW_CORR_LINE_D      = True
CORR_LINE_COLOR_B_CAL = '#333333'
CORR_LINE_COLOR_B_DOL = '#888888'
CORR_LINE_COLOR_C     = '#000000'
CORR_LINE_COLOR_D     = '#000000'
CORR_LINE_STYLE       = '-'
CORR_LINE_WIDTH       = 1.8

# ── Output file name (saved into OUT_DIR, both formats) ──────────────────────
OUT_BASENAME        = "Fig6"

# ── Water-source classification ────────────────────────────────────────────────
N_SPRING            = 11
N_QANAT             = 4
N_WELL              = 4
SOURCE_TYPE_OVERRIDE = {}

# ═══════════════════════════════════════════════════════════════════════════════
#  END OF USER SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

import os, sys, io, re, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines
import matplotlib.colors as mcolors

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
warnings.filterwarnings('ignore')

# Keep text as real text in the PDF (editable, scalable, never pixelated)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype']  = 42

DATA_PATH = r"c:\Users\mhaghi2\Desktop\Article 9\data\hydrochemical\hydrochemical - Copy.xlsx"
OUT_DIR   = r"C:\Users\mhaghi2\Desktop\Article 9\map"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────
raw = pd.read_excel(DATA_PATH, header=None)
ION_KEYWORDS = ['ca','mg','na','cl','so4','hco3','ec','tds','ph','temp']
def row_score(row):
    return sum(1 for v in row if isinstance(v,str) and any(k in v.lower() for k in ION_KEYWORDS))
header_row = max(range(min(5,len(raw))), key=lambda i: row_score(raw.iloc[i]))
raw_headers = raw.iloc[header_row].tolist()
filled, last = [], 'col'
for v in raw_headers:
    if pd.isna(v) or str(v).strip()=='': filled.append(last)
    else: last=str(v).strip(); filled.append(last)
seen={}; unique_headers=[]
for h in filled:
    hl=h.lower(); seen[hl]=seen.get(hl,0)+1
    unique_headers.append(h if seen[hl]==1 else "%s_%d" % (h, seen[hl]))
df_raw = raw.iloc[header_row+1:].copy()
df_raw.columns = unique_headers
df_raw = df_raw.reset_index(drop=True)
def normalise(s):
    return str(s).strip().lower().replace(' ','').replace('+','').replace('-','') \
                 .replace('²','2').replace('2+','').replace('²⁺','')
norm_map     = {c: normalise(c) for c in df_raw.columns}
name_col_raw = df_raw.columns[0]
TARGET = ['ca','mg','na','k','cl','so4','hco3','ec','tds','ph','temp']
def find_cols(tgt):
    return [c for c,nm in norm_map.items() if tgt in nm]
ca_cols   = find_cols('ca')
n_seasons = max(1, len(ca_cols))
seasons   = []
for s_idx in range(n_seasons):
    sl    = ['Wet','Dry','S3','S4'][s_idx] if n_seasons>1 else 'All'
    block = {'sample': df_raw[name_col_raw]}
    for tgt in TARGET:
        cands = find_cols(tgt)
        block[tgt] = pd.to_numeric(df_raw[cands[s_idx]], errors='coerce') \
                     if s_idx < len(cands) else np.nan
    bdf = pd.DataFrame(block); bdf['season'] = sl; seasons.append(bdf)
df = pd.concat(seasons, ignore_index=True)
df = df.dropna(subset=['ca','mg','na','k','cl','so4','hco3'], how='all')
df = df[pd.to_numeric(df['sample'], errors='coerce').isna()]
df = df[df['sample'].notna() & (df['sample'].astype(str).str.strip()!='')]
df = df.reset_index(drop=True)
for col in TARGET:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].median())

Ca_c='ca'; Mg_c='mg'; Na_c='na'; K_c='k'; Cl_c='cl'
SO4_c='so4'; HCO3_c='hco3'; TDS_c='tds'; pH_c='ph'; T_c='temp'
n             = len(df)
short_labels  = df['sample'].astype(str).values
season_labels = df['season'].astype(str).values

# ── Water-source classification ────────────────────────────────────────────────
_unique_samples  = list(pd.unique(df['sample'].astype(str)))
_positional_type = {}
for _idx, _name in enumerate(_unique_samples):
    if   _idx < N_SPRING:                    _positional_type[_name] = 'Spring'
    elif _idx < N_SPRING + N_QANAT:          _positional_type[_name] = 'Qanat'
    elif _idx < N_SPRING + N_QANAT + N_WELL: _positional_type[_name] = 'Well'
    else:                                     _positional_type[_name] = 'Other'

def get_source_type(name):
    s  = str(name).strip()
    if s in SOURCE_TYPE_OVERRIDE:
        return SOURCE_TYPE_OVERRIDE[s]
    su = s.upper()
    m  = re.match(r'^([A-Z])\s*\d', su)
    if m:
        f = m.group(1)
        if f == 'S': return 'Spring'
        if f == 'Q': return 'Qanat'
        if f == 'W': return 'Well'
    return _positional_type.get(s, 'Other')

source_types = [get_source_type(nm) for nm in short_labels]
is_plotted   = np.array([t != 'Other' for t in source_types])

# ── Sample-code labels (SW1, SD1, QW1 ...) ───────────────────────────────────
_type_prefix   = {'Spring':'S','Qanat':'Q','Well':'W','Other':'O'}
_season_letter = {'Wet':'W','Dry':'D','All':'A','S3':'3','S4':'4'}
_group_counters = {}
bar_labels = []
for i in range(n):
    src = source_types[i];  sea = season_labels[i];  key = (src, sea)
    _group_counters[key] = _group_counters.get(key, 0) + 1
    bar_labels.append("%s%s%d" % (_type_prefix.get(src,'O'),
                                  _season_letter.get(sea, sea[0].upper()),
                                  _group_counters[key]))

# ── Style map: source x season ────────────────────────────────────────────────
STYLE_MAP = {
    ('Spring','Wet'): dict(marker='o', color='#1B8A1B', edgecolor='#1B8A1B', filled=True,  label='Spring (Wet)'),
    ('Spring','Dry'): dict(marker='o', color='#1B8A1B', edgecolor='#1B8A1B', filled=False, label='Spring (Dry)'),
    ('Qanat', 'Wet'): dict(marker='s', color='#1565C0', edgecolor='#1565C0', filled=True,  label='Qanat (Wet)'),
    ('Qanat', 'Dry'): dict(marker='s', color='#1565C0', edgecolor='#1565C0', filled=False, label='Qanat (Dry)'),
    ('Well',  'Wet'): dict(marker='^', color='#BF360C', edgecolor='#BF360C', filled=True,  label='Well (Wet)'),
    ('Well',  'Dry'): dict(marker='^', color='#BF360C', edgecolor='#BF360C', filled=False, label='Well (Dry)'),
    ('Other', 'Wet'): dict(marker='d', color='#616161', edgecolor='#616161', filled=True,  label='_nolegend_'),
    ('Other', 'Dry'): dict(marker='d', color='#616161', edgecolor='#616161', filled=False, label='_nolegend_'),
    ('Spring','All'): dict(marker='o', color='#1B8A1B', edgecolor='#1B8A1B', filled=True,  label='Spring'),
    ('Qanat', 'All'): dict(marker='s', color='#1565C0', edgecolor='#1565C0', filled=True,  label='Qanat'),
    ('Well',  'All'): dict(marker='^', color='#BF360C', edgecolor='#BF360C', filled=True,  label='Well'),
    ('Other', 'All'): dict(marker='d', color='#616161', edgecolor='#616161', filled=True,  label='_nolegend_'),
}

_POINT_SIZE_C = {'Spring': POINT_SIZE_C_SPRING,
                 'Qanat':  POINT_SIZE_C_QANAT,
                 'Well':   POINT_SIZE_C_WELL,
                 'Other':  POINT_SIZE}

def get_style(i):
    key = (source_types[i], season_labels[i])
    return STYLE_MAP.get(key, STYLE_MAP.get(('Other','Wet'), {}))

def scatter_point(ax, x, y, i, size=None, alpha=0.9):
    if source_types[i] == 'Other':
        return
    st = get_style(i)
    s  = size if size else POINT_SIZE
    fc = st['color'] if st['filled'] else 'white'
    ax.scatter(x, y, c=[fc], s=s, marker=st['marker'],
               edgecolors=st['edgecolor'], linewidths=1.0, zorder=6, alpha=alpha)

def scatter_point_c(ax, x, y, i, si_val, cmap, norm):
    if source_types[i] == 'Other':
        return
    st    = get_style(i)
    s     = _POINT_SIZE_C.get(source_types[i], POINT_SIZE)
    color = cmap(norm(si_val))
    fc    = color if st['filled'] else 'white'
    ax.scatter(x, y, c=[fc], s=s, marker=st['marker'],
               edgecolors=[color], linewidths=1.2, zorder=6, alpha=0.9)

def add_corr_line(ax, x, y, color='k', ls='-', lw=1.5, zorder=5):
    """Linear trend line through (x, y); returns (Line2D, Pearson r)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2:
        return None, np.nan
    xv, yv = x[mask], y[mask]
    slope, intercept = np.polyfit(xv, yv, 1)
    r  = np.corrcoef(xv, yv)[0, 1]
    xs = np.linspace(xv.min(), xv.max(), 100)
    line, = ax.plot(xs, slope * xs + intercept, color=color, ls=ls, lw=lw, zorder=zorder)
    return line, r

# ── Legend handles (Spring / Qanat / Well only) ───────────────────────────────
_present_keys = set(zip(source_types, season_labels))
style_handles = []
_seen_labels  = set()
_key_order    = [
    ('Spring','Wet'),('Spring','Dry'),
    ('Qanat', 'Wet'),('Qanat', 'Dry'),
    ('Well',  'Wet'),('Well',  'Dry'),
    ('Spring','All'),('Qanat', 'All'),('Well','All'),
]
for key in _key_order:
    if key in _present_keys and key in STYLE_MAP:
        st  = STYLE_MAP[key]
        lbl = st['label']
        if lbl.startswith('_') or lbl in _seen_labels:
            continue
        fc = st['color'] if st['filled'] else 'white'
        h  = plt.scatter([], [], marker=st['marker'], c=[fc],
                         edgecolors=st['edgecolor'], linewidths=1.0,
                         s=POINT_SIZE*LEGEND_MARKER_SCALE, label=lbl)
        style_handles.append(h)
        _seen_labels.add(lbl)

def save(fig, basename):
    """Write the figure as PDF (vector, for submission) and PNG."""
    for ext in ('pdf', 'png'):
        path = os.path.join(OUT_DIR, "%s.%s" % (basename, ext))
        fig.savefig(path, dpi=FIGURE_DPI, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        print("  Saved -> %s" % path)
    plt.close(fig)

plt.rcParams.update({'xtick.labelsize': TICK_SIZE, 'ytick.labelsize': TICK_SIZE})
print("Data loaded: %d samples" % n)

def _panel_label(ax, text, xy):
    ax.text(xy[0], xy[1], text, transform=ax.transAxes,
            fontsize=PANEL_TITLE_SIZE, fontweight='bold', va='top', ha='left')

def _leg(ax, handles, loc=None, xy=None, anchor='upper left', ncol=1):
    kw = dict(fontsize=LEGEND_SIZE, frameon=LEGEND_FRAME, ncol=ncol,
              markerscale=LEGEND_MARKER_SCALE)
    if xy is not None:
        ax.legend(handles=handles, bbox_to_anchor=xy, loc=anchor, **kw)
    elif loc is not None:
        ax.legend(handles=handles, loc=loc, **kw)
    else:
        ax.legend(handles=handles, **kw)

# ── Thermodynamic calculations ────────────────────────────────────────────────
pH_v  = df[pH_c].values.astype(float)
T_v   = df[T_c].values.astype(float)
TDS_v = df[TDS_c].values if TDS_c in df.columns else \
        (df[Ca_c]+df[Mg_c]+df[Na_c]+df[Cl_c]+df[SO4_c]+df[HCO3_c]).values

def pKsp_calcite(T):
    K=T+273.15; return 171.9065+0.077993*K-2839.319/K-71.595*np.log10(K)
def pKsp_dolomite(T):
    K=T+273.15; return 21.838-9.4371e-3*K-5.5*np.log10(K)
def pK2_carbonic(T):
    K=T+273.15; return 107.8871+0.03252849*K-5151.79/K-38.92561*np.log10(K)+563713.9/K**2
def gamma(zv, I):
    return 10**(-0.5115*zv**2*(np.sqrt(I)/(1+np.sqrt(I))-0.3*I))

IS   = np.clip(2.5e-5*TDS_v, 1e-6, 1)
gCa  = gMg = gCO3 = gamma(2, IS)
gNa  = gCl = gHCO3 = gamma(1, IS)
gSO4 = gamma(2, IS)
Ca_mol   = df[Ca_c].values/40.078;   Mg_mol  = df[Mg_c].values/24.305
HCO3_mol = df[HCO3_c].values/61.016; SO4_mol = df[SO4_c].values/96.062
Na_mol   = df[Na_c].values/22.990;   Cl_mol  = df[Cl_c].values/35.453
K2       = 10**(-pK2_carbonic(T_v))
CO3_mol  = K2 * HCO3_mol / (10**(-pH_v) + 1e-30)

SI_cal = np.log10(gCa*Ca_mol*gCO3*CO3_mol / (10**pKsp_calcite(T_v)))
SI_dol = np.log10(gCa*Ca_mol*gMg*Mg_mol*(gCO3*CO3_mol)**2 / (10**pKsp_dolomite(T_v)))
SI_gyp = np.log10(gCa*Ca_mol*gSO4*SO4_mol / 10**(-4.58))
SI_hal = np.log10(gNa*Na_mol*gCl*Cl_mol   / 10**(-1.57))

# ═══════════════════════════════════════════════════════════════════════════════
# Figure layout
# ═══════════════════════════════════════════════════════════════════════════════
fig4 = plt.figure(figsize=FIGURE_SIZE)
fig4.suptitle("", fontsize=SUPTITLE_SIZE, fontweight='bold', y=0.99)
gs4  = gridspec.GridSpec(2, 2, figure=fig4,
                          hspace=OUTER_HSPACE, wspace=OUTER_WSPACE)

# ── Panel A: SI bar charts, y-axis titled with the subscripted SI name ───────
inner = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs4[0, 0],
                                          hspace=PANEL_A_HSPACE, wspace=PANEL_A_WSPACE)
_minerals          = [('Calcite', SI_cal), ('Dolomite', SI_dol),
                      ('Gypsum',  SI_gyp), ('Halite',   SI_hal)]
_a_label_positions = [LABEL_A1_XY, LABEL_A2_XY, LABEL_A3_XY, LABEL_A4_XY]

for idx, (mineral, si) in enumerate(_minerals):
    axi   = fig4.add_subplot(inner[idx // 2, idx % 2])
    bar_c = ['#e74c3c' if v > 0 else '#3498db' for v in si]
    axi.bar(range(n), si, color=bar_c, edgecolor='k', lw=0.25, width=0.8)
    axi.axhline(0, color='k', lw=1.2, ls='--')
    axi.set_xticks(range(n))
    axi.set_xticklabels(bar_labels, rotation=90, fontsize=BAR_SAMPLE_SIZE)
    axi.set_ylabel(SI_LABEL[mineral], fontsize=LABEL_SIZE - 1)
    axi.grid(axis='y', alpha=0.3)
    ymax = max(abs(si)) * 1.1 if max(abs(si)) > 0 else 1
    axi.set_ylim(-ymax * 1.18, ymax * 1.18)
    axi.text(n * 0.97,  ymax * 0.38, 'Supersaturated', ha='right',
             fontsize=SI_ANNOT_SIZE, color='#c0392b', style='italic')
    axi.text(n * 0.97, -ymax * 0.38, 'Undersaturated', ha='right',
             fontsize=SI_ANNOT_SIZE, color='#2980b9', style='italic')
    _panel_label(axi, '(a%d)' % (idx+1), _a_label_positions[idx])

# ── Panel B: SI vs pH ─────────────────────────────────────────────────────────
ax4b = fig4.add_subplot(gs4[0, 1])
for i in range(n):
    scatter_point(ax4b, pH_v[i], SI_cal[i], i, size=POINT_SIZE,     alpha=CAL_LEGEND_ALPHA)
    scatter_point(ax4b, pH_v[i], SI_dol[i], i, size=POINT_SIZE*0.6, alpha=DOL_LEGEND_ALPHA)

if SHOW_LABELS_B:
    for i in range(n):
        if source_types[i] != 'Other':
            ax4b.annotate(bar_labels[i], (pH_v[i]+0.01, SI_cal[i]+0.01),
                          fontsize=PANEL_B_LABEL_SIZE, alpha=0.75)
            ax4b.annotate(bar_labels[i], (pH_v[i]+0.01, SI_dol[i]+0.01),
                          fontsize=PANEL_B_LABEL_SIZE, alpha=0.75)

ax4b.axhline(0, color='r', lw=1.5, ls='--')
ax4b.set_xlabel('pH', fontsize=LABEL_SIZE)
ax4b.set_ylabel('SI', fontsize=LABEL_SIZE)
ax4b.grid(alpha=0.3)
if PANEL_B_XLIM is not None: ax4b.set_xlim(PANEL_B_XLIM)
if PANEL_B_YLIM is not None: ax4b.set_ylim(PANEL_B_YLIM)
_panel_label(ax4b, '(b)', LABEL_B_XY)

corr_handles_b = []
if SHOW_CORR_LINE_B:
    line_b_cal, r_b_cal = add_corr_line(ax4b, pH_v, SI_cal,
                                         color=CORR_LINE_COLOR_B_CAL,
                                         ls=CORR_LINE_STYLE, lw=CORR_LINE_WIDTH)
    if line_b_cal is not None:
        line_b_cal.set_label(r'%s trend ($r$ = %.2f)' % (SI_LABEL['Calcite'], r_b_cal))
        corr_handles_b.append(line_b_cal)
    line_b_dol, r_b_dol = add_corr_line(ax4b, pH_v, SI_dol,
                                         color=CORR_LINE_COLOR_B_DOL,
                                         ls=CORR_LINE_STYLE, lw=CORR_LINE_WIDTH)
    if line_b_dol is not None:
        line_b_dol.set_label(r'%s trend ($r$ = %.2f)' % (SI_LABEL['Dolomite'], r_b_dol))
        corr_handles_b.append(line_b_dol)

cal_handles, dol_handles = [], []
for st_h in style_handles:
    lbl = st_h.get_label()
    fc  = st_h.get_facecolor()[0]
    mk  = st_h.get_paths()[0]
    cal_handles.append(plt.scatter([], [], marker=mk, c=[fc],
                                    edgecolors=CAL_LEGEND_COLOR, linewidths=1.2,
                                    s=POINT_SIZE*LEGEND_MARKER_SCALE,
                                    alpha=CAL_LEGEND_ALPHA,
                                    label='%s - %s' % (lbl, SI_LABEL['Calcite'])))
    dol_handles.append(plt.scatter([], [], marker=mk, c=[fc],
                                    edgecolors=DOL_LEGEND_COLOR, linewidths=1.2,
                                    s=POINT_SIZE*0.6*LEGEND_MARKER_SCALE,
                                    alpha=DOL_LEGEND_ALPHA,
                                    label='%s - %s' % (lbl, SI_LABEL['Dolomite'])))
equil_h = mlines.Line2D([], [], color='r', lw=1.5, ls='--', label='Equilibrium (SI = 0)')
_leg(ax4b, cal_handles + dol_handles + [equil_h] + corr_handles_b,
     loc=LEG_B_LOC, xy=LEG_B_XY, anchor=LEG_B_ANCHOR, ncol=LEGEND_NCOL_B)

# ── Panel C: SIcalcite vs Temperature ────────────────────────────────────────
ax4c = fig4.add_subplot(gs4[1, 0])

# FIX 6c: colour scale fitted to the plotted points only (Other excluded),
# so no part of the colour ramp is wasted on values that do not occur.
si_plotted = SI_cal[is_plotted & np.isfinite(SI_cal)]
d_lo, d_hi = float(np.min(si_plotted)), float(np.max(si_plotted))
pad  = (d_hi - d_lo) * CBAR_PAD_FRAC
vmin = CBAR_VMIN if CBAR_VMIN is not None else d_lo - pad
vmax = CBAR_VMAX if CBAR_VMAX is not None else d_hi + pad
print("Panel c colour scale: %.2f to %.2f (data %.2f to %.2f)" % (vmin, vmax, d_lo, d_hi))

cmap_c = plt.get_cmap(CBAR_CMAP)
norm_c = mcolors.Normalize(vmin=vmin, vmax=vmax)

for i in range(n):
    scatter_point_c(ax4c, T_v[i], SI_cal[i], i, SI_cal[i], cmap_c, norm_c)

sm = plt.cm.ScalarMappable(cmap=cmap_c, norm=norm_c)
sm.set_array([])
cbar_c = plt.colorbar(sm, ax=ax4c, shrink=0.85)
# FIX 6c: colour bar title same size and style as the axis titles
cbar_c.set_label(SI_LABEL['Calcite'], fontsize=CBAR_TITLE_SIZE)
cbar_c.ax.tick_params(labelsize=CBAR_TICK_SIZE)

for i in range(n):
    if source_types[i] != 'Other':
        ax4c.annotate(bar_labels[i], (T_v[i]+0.05, SI_cal[i]+0.02),
                      fontsize=ANNOTATION_SIZE, alpha=0.75)
ax4c.axhline(0, color='k', lw=1.5, ls='--')
ax4c.set_xlabel('Temperature (°C)', fontsize=LABEL_SIZE)
ax4c.set_ylabel(SI_LABEL['Calcite'], fontsize=LABEL_SIZE)
ax4c.grid(alpha=0.3)
if PANEL_C_XLIM is not None: ax4c.set_xlim(PANEL_C_XLIM)
if PANEL_C_YLIM is not None: ax4c.set_ylim(PANEL_C_YLIM)
_panel_label(ax4c, '(c)', LABEL_C_XY)

corr_handle_c = []
if SHOW_CORR_LINE_C:
    line_c, r_c = add_corr_line(ax4c, T_v, SI_cal,
                                 color=CORR_LINE_COLOR_C,
                                 ls=CORR_LINE_STYLE, lw=CORR_LINE_WIDTH)
    if line_c is not None:
        # FIX 6c: "r" italic (Pearson correlation coefficient)
        line_c.set_label(r'Trend ($r$ = %.2f)' % r_c)
        corr_handle_c.append(line_c)

c_shape_handles = []
_c_shape_keys = [('Spring','Wet'),('Qanat','Wet'),('Well','Wet'),
                 ('Spring','All'),('Qanat','All'),('Well','All')]
_c_seen = set()
for key in _c_shape_keys:
    if key in _present_keys and key in STYLE_MAP:
        st  = STYLE_MAP[key]
        src = key[0]
        if src in _c_seen:
            continue
        h = plt.scatter([], [], marker=st['marker'], c=['#888888'],
                        edgecolors=st['edgecolor'], linewidths=1.2,
                        s=POINT_SIZE_C_SPRING * LEGEND_MARKER_SCALE,
                        label=src)
        c_shape_handles.append(h)
        _c_seen.add(src)

equil_c = mlines.Line2D([], [], color='k', lw=1.5, ls='--', label='Equilibrium (SI = 0)')
_leg(ax4c, c_shape_handles + [equil_c] + corr_handle_c,
     loc=LEG_C_LOC, xy=LEG_C_XY, anchor=LEG_C_ANCHOR, ncol=LEGEND_NCOL_C)

# ── Panel D: SIcalcite vs SIdolomite ─────────────────────────────────────────
ax4d = fig4.add_subplot(gs4[1, 1])
for i in range(n):
    scatter_point(ax4d, SI_cal[i], SI_dol[i], i)
    if source_types[i] != 'Other':
        ax4d.annotate(bar_labels[i], (SI_cal[i]+0.02, SI_dol[i]+0.02),
                      fontsize=ANNOTATION_SIZE)
ax4d.axhline(0, color='grey', lw=1, ls='--')
ax4d.axvline(0, color='grey', lw=1, ls='--')
ax4d.set_xlabel(SI_LABEL['Calcite'],  fontsize=LABEL_SIZE)
ax4d.set_ylabel(SI_LABEL['Dolomite'], fontsize=LABEL_SIZE)
if PANEL_D_XLIM is not None: ax4d.set_xlim(PANEL_D_XLIM)
if PANEL_D_YLIM is not None: ax4d.set_ylim(PANEL_D_YLIM)

# FIX 6d: "Both supersaturated" to the top-right (positive SI on both axes);
# "Both undersaturated" stays bottom-left (negative SI on both axes).
ax4d.text(0.97, 0.97, 'Both supersaturated', transform=ax4d.transAxes,
          fontsize=PANEL_D_ANNOT_SIZE, color='#c0392b', va='top', ha='right')
ax4d.text(0.03, 0.03, 'Both undersaturated', transform=ax4d.transAxes,
          fontsize=PANEL_D_ANNOT_SIZE, color='#2980b9', va='bottom', ha='left')
ax4d.grid(alpha=0.3)
_panel_label(ax4d, '(d)', LABEL_D_XY)

corr_handle_d = []
if SHOW_CORR_LINE_D:
    line_d, r_d = add_corr_line(ax4d, SI_cal, SI_dol,
                                 color=CORR_LINE_COLOR_D,
                                 ls=CORR_LINE_STYLE, lw=CORR_LINE_WIDTH)
    if line_d is not None:
        # FIX 6d: "r" italic (Pearson correlation coefficient)
        line_d.set_label(r'Trend ($r$ = %.2f)' % r_d)
        corr_handle_d.append(line_d)

_leg(ax4d, style_handles + corr_handle_d,
     loc=LEG_D_LOC, xy=LEG_D_XY, anchor=LEG_D_ANCHOR, ncol=LEGEND_NCOL_D)

# ── Bottom legend: bar colour key ─────────────────────────────────────────────
red_p = mpatches.Patch(color='#e74c3c', label='SI > 0  Supersaturated')
blu_p = mpatches.Patch(color='#3498db', label='SI < 0  Undersaturated')
fig4.legend(handles=[red_p, blu_p], loc='lower center',
            ncol=LEGEND_NCOL_BOTTOM, fontsize=LEGEND_BOTTOM_SIZE,
            bbox_to_anchor=LEG_BOTTOM_XY, frameon=LEGEND_FRAME)

save(fig4, OUT_BASENAME)
