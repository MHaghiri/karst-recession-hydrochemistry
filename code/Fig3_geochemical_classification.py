"""
Fig 3 - Hydrogeochemical Classification
Panels: (a) Piper  (b) Durov  (c1/c2) Schoeller Wet/Dry  (d) Water Type

Revised for Hydrogeology Journal technical-editor comments (HYJO-D-26-00525R1):
  3a - axis titles no longer carry the "%" prefix (e.g. "Ca2+ + Mg2+")
  3b - water-type field labels set upright (non-italic)
     - horizontal axis title -> "Ca2+ (% of total cation equivalents)"
     - vertical   axis title -> "HCO3- (% of total anion equivalents)"
  3d - "3" and "4" set as subscripts in HCO3 and SO4
  Output written as both PDF (vector, for submission) and PNG, at DPI below.
"""
# ═══════════════════════════════════════════════════════════════════════════════
# USER SETTINGS  <- edit here
# ═══════════════════════════════════════════════════════════════════════════════
FIGURE_SIZE        = (22, 16)
FIGURE_DPI         = 1000          # applies to the PNG and to raster elements
SUPTITLE_SIZE      = 17

TICK_SIZE          = 15
LABEL_SIZE         = 15
PANEL_TITLE_SIZE   = 17
LEGEND_SIZE        = 13

LEG_B_XY   = (0.5, 0.6)
LEG_D_XY   = (0.1, 0.999)
LEG_D_NCOL = 1
LEG_WATERTYPE_LOC = 'upper right'

POINT_SIZE = 140

# Piper-specific font sizes (WQChartPy ticks/labels)
PIPER_TICK_SIZE  = 12
PIPER_LABEL_SIZE = 14

# ── Panel B (Durov) correlation line + point-label settings ───────────────────
SHOW_POINT_LABELS  = True
POINT_LABEL_SOURCE = 'symbol'   # 'symbol' -> S1, Q1, W1 ... | 'name' -> raw name
POINT_LABEL_SIZE   = 10
POINT_LABEL_COLOR  = 'black'
POINT_LABEL_OFFSET = (4, 4)

SHOW_CORR_LINE     = True
CORR_LINE_COLOR    = 'black'
CORR_LINE_STYLE    = '--'
CORR_LINE_WIDTH    = 1.5

# ── Output file names (saved into OUT_DIR, both formats) ─────────────────────
OUT_BASENAME = "Fig3"

LABEL_POSITIONS = {
    'piper':         {'x': 0.0,  'y': 0.98, 'text': 'a',  'fontsize': 20, 'weight': 'bold'},
    'durov':         {'x': 0.05, 'y': 0.95, 'text': 'b',  'fontsize': 20, 'weight': 'bold'},
    'schoeller_wet': {'x': 0.05, 'y': 0.95, 'text': 'c1', 'fontsize': 20, 'weight': 'bold'},
    'schoeller_dry': {'x': 0.05, 'y': 0.95, 'text': 'c2', 'fontsize': 20, 'weight': 'bold'},
    'watertype':     {'x': 0.05, 'y': 0.95, 'text': 'd',  'fontsize': 20, 'weight': 'bold'},
}
# ═══════════════════════════════════════════════════════════════════════════════

import os, sys, io, warnings, re
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
for hh in filled:
    hl = hh.lower(); seen[hl] = seen.get(hl, 0) + 1
    unique_headers.append(hh if seen[hl] == 1 else "%s_%d" % (hh, seen[hl]))

df_raw = raw.iloc[header_row + 1:].copy()
df_raw.columns = unique_headers
df_raw = df_raw.reset_index(drop=True)

def normalise(s):
    return str(s).strip().lower().replace(' ','').replace('+','').replace('-','') \
                 .replace('²','2').replace('2+','').replace('²⁺','')

norm_map = {c: normalise(c) for c in df_raw.columns}
name_col_raw = df_raw.columns[0]
TARGET = ['ca','mg','na','k','cl','so4','hco3','ec','tds','ph','temp']

def find_cols(tgt):
    return [c for c, nrm in norm_map.items() if tgt in nrm]

ca_cols  = find_cols('ca')
n_seasons = max(1, len(ca_cols))
seasons  = []
for s_idx in range(n_seasons):
    sl    = ['Wet','Dry','S3','S4'][s_idx] if n_seasons > 1 else 'All'
    block = {'sample': df_raw[name_col_raw]}
    for tgt in TARGET:
        cands = find_cols(tgt)
        block[tgt] = pd.to_numeric(df_raw[cands[s_idx]], errors='coerce') if s_idx < len(cands) else np.nan
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

Ca_c='ca'; Mg_c='mg'; Na_c='na'; K_c='k'; Cl_c='cl'
SO4_c='so4'; HCO3_c='hco3'; EC_c='ec'; TDS_c='tds'; pH_c='ph'; T_c='temp'
mw = {'Ca':40.078,'Mg':24.305,'Na':22.990,'K':39.098,'Cl':35.453,'SO4':96.062,'HCO3':61.016}
z  = {'Ca':2,'Mg':2,'Na':1,'K':1,'Cl':1,'SO4':2,'HCO3':1}

def to_meq(col, ion): return df[col] / mw[ion] * z[ion]

Ca   = to_meq('ca','Ca');  Mg  = to_meq('mg','Mg')
Na   = to_meq('na','Na');  K   = to_meq('k','K')
Cl   = to_meq('cl','Cl');  SO4 = to_meq('so4','SO4'); HCO3 = to_meq('hco3','HCO3')
n    = len(df)
short_labels  = df['sample'].astype(str).values
season_labels = df['season'].astype(str).values

# ── Water-source classification ───────────────────────────────────────────────
N_SPRING = 11
N_QANAT  = 4
N_WELL   = 4

SOURCE_TYPE_OVERRIDE = {}

_unique_samples = list(pd.unique(df['sample'].astype(str)))
_positional_type = {}
for _idx, _name in enumerate(_unique_samples):
    if _idx < N_SPRING:
        _positional_type[_name] = 'Spring'
    elif _idx < N_SPRING + N_QANAT:
        _positional_type[_name] = 'Qanat'
    elif _idx < N_SPRING + N_QANAT + N_WELL:
        _positional_type[_name] = 'Well'
    else:
        _positional_type[_name] = 'Other'

def get_source_type(name):
    s = str(name).strip()
    if s in SOURCE_TYPE_OVERRIDE:
        return SOURCE_TYPE_OVERRIDE[s]
    su = s.upper()
    m = re.match(r'^([A-Z])\s*\d', su)
    if m:
        first = m.group(1)
        if first == 'S': return 'Spring'
        if first == 'Q': return 'Qanat'
        if first == 'W': return 'Well'
    return _positional_type.get(s, 'Other')

source_types = [get_source_type(nm) for nm in short_labels]
print("Source mapping (by order): %s" % _positional_type)

PREFIX_MAP = {'Spring': 'S', 'Qanat': 'Q', 'Well': 'W', 'Other': 'O'}
_type_counters = {}
SYMBOL_LABEL_MAP = {}
for _name in _unique_samples:
    _t = get_source_type(_name)
    _prefix = PREFIX_MAP.get(_t, 'X')
    _type_counters[_prefix] = _type_counters.get(_prefix, 0) + 1
    SYMBOL_LABEL_MAP[_name] = "%s%d" % (_prefix, _type_counters[_prefix])

print("Symbol labels: %s" % SYMBOL_LABEL_MAP)

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

def get_style(i):
    return STYLE_MAP.get((source_types[i], season_labels[i]), STYLE_MAP[('Other','Wet')])

def scatter_point(ax, x, y, i, size=None):
    st = get_style(i)
    s  = size if size else POINT_SIZE
    fc = st['color'] if st['filled'] else 'white'
    ax.scatter(x, y, c=[fc], s=s, marker=st['marker'],
               edgecolors=st['edgecolor'], linewidths=1.0, zorder=6, alpha=0.9)

present_keys = set(zip(source_types, season_labels))
water_type_handles = []
for key in [('Spring','Wet'),('Spring','Dry'),('Qanat','Wet'),('Qanat','Dry'),('Well','Wet'),('Well','Dry')]:
    if key in present_keys:
        st = STYLE_MAP[key]
        fc = st['color'] if st['filled'] else 'white'
        water_type_handles.append(
            Line2D([0],[0], marker=st['marker'], color='w',
                   markerfacecolor=fc, markeredgecolor=st['edgecolor'],
                   markeredgewidth=1.2, markersize=9, label=st['label']))

# ── Schoeller individual sample styles ───────────────────────────────────────
SAMPLE_COLORS_LIST = [
    '#E67E22','#27AE60','#8E44AD','#1A5C96','#F39C12','#16A085',
    '#E74C3C','#2E86C1','#C0392B','#5DADE2','#884EA0','#17A589',
    '#D35400','#1A5276','#7F8C8D','#ABB2B9','#5D6D7E','#283747',
]
LINE_STYLES_LIST = ['-','--','-.', ':']
MARKERS_LIST     = ['o','s','^','D','v','p','*','h','8','P','d']

SAMPLE_STYLES = {}
for idx, sample in enumerate(df['sample'].unique()):
    SAMPLE_STYLES[sample] = {
        'color':  SAMPLE_COLORS_LIST[idx % len(SAMPLE_COLORS_LIST)],
        'lw':     1.5 + (idx % 3) * 0.3,
        'ls':     LINE_STYLES_LIST[idx % len(LINE_STYLES_LIST)],
        'marker': MARKERS_LIST[idx % len(MARKERS_LIST)],
        'ms':     6 + (idx % 3),
    }

sample_names = df['sample'].astype(str).values

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

print("Data loaded: %d samples" % n)
print("Source distribution: %s" % pd.Series(source_types).value_counts().to_dict())

plt.rcParams.update({'xtick.labelsize': TICK_SIZE, 'ytick.labelsize': TICK_SIZE})

def add_panel_label(ax, cfg):
    ax.text(cfg['x'], cfg['y'], cfg['text'],
            transform=ax.transAxes, ha='center', va='center',
            fontsize=cfg.get('fontsize',16), weight=cfg.get('weight','bold'),
            color=cfg.get('color','black'), zorder=100)

# ═══════════════════════════════════════════════════════════════════════════════
# WQChartPy Piper geometry
# EDITOR FIX 3a: the axis titles below no longer carry a "%" prefix, so
# "%Ca2+ + %Mg2+" now reads "Ca2+ + Mg2+". The 0-100 tick values already
# make the percentage basis clear.
# ═══════════════════════════════════════════════════════════════════════════════
def wqchartpy_piper_background(ax, tick_size=PIPER_TICK_SIZE, label_size=PIPER_LABEL_SIZE):
    offset  = 0.10
    offsety = offset * np.tan(np.pi / 3.0)
    h       = 0.5 * np.tan(np.pi / 3.0)

    ltri_x = np.array([0, 0.5, 1, 0]); ltri_y = np.array([0, h, 0, 0])
    rtri_x = ltri_x + 2*offset + 1;    rtri_y = ltri_y
    dia_x  = np.array([0.5,1,1.5,1,0.5]) + offset
    dia_y  = h*np.array([1,2,1,0,1]) + offsety

    ax.plot(ltri_x, ltri_y, '-k', lw=1.0)
    ax.plot(rtri_x, rtri_y, '-k', lw=1.0)
    ax.plot(dia_x,  dia_y,  '-k', lw=1.0)

    interval = 0.2
    tl = ['0','20','40','60','80','100']
    for i, x in enumerate(np.linspace(0, 1, int(1/interval+1))):
        # left triangle grid + ticks
        ax.plot([x, x-x/2.0], [0, x/2.0*np.tan(np.pi/3)], 'k:', lw=1.0)
        if i in [1,2,3,4]:
            ax.text(x, -0.03, tl[-i-1], ha='center', va='center', fontsize=tick_size)
        ax.plot([x, (1-x)/2.0+x], [0, (1-x)/2.0*np.tan(np.pi/3)], 'k:', lw=1.0)
        if i in [1,2,3,4]:
            ax.text((1-x)/2.0+x+0.026, (1-x)/2.0*np.tan(np.pi/3)+0.015, tl[i],
                    ha='center', va='center', rotation=-60, fontsize=tick_size)
        ax.plot([x/2, 1-x/2], [x/2*np.tan(np.pi/3)]*2, 'k:', lw=1.0)
        if i in [1,2,3,4]:
            ax.text(x/2-0.026, x/2*np.tan(np.pi/3)+0.015, tl[i],
                    ha='center', va='center', rotation=60, fontsize=tick_size)

        # right triangle grid + ticks
        ax.plot([x+1+2*offset, x-x/2.0+1+2*offset], [0, x/2.0*np.tan(np.pi/3)], 'k:', lw=1.0)
        if i in [1,2,3,4]:
            ax.text(x+1+2*offset, -0.03, tl[i], ha='center', va='center', fontsize=tick_size)
        ax.plot([x+1+2*offset, (1-x)/2.0+x+1+2*offset], [0, (1-x)/2.0*np.tan(np.pi/3)], 'k:', lw=1.0)
        if i in [1,2,3,4]:
            ax.text((1-x)/2.0+x+1+2*offset+0.026, (1-x)/2.0*np.tan(np.pi/3)+0.015, tl[-i-1],
                    ha='center', va='center', rotation=-60, fontsize=tick_size)
        ax.plot([x/2+1+2*offset, 1-x/2+1+2*offset], [x/2*np.tan(np.pi/3)]*2, 'k:', lw=1.0)
        if i in [1,2,3,4]:
            ax.text(x/2+1+2*offset-0.026, x/2*np.tan(np.pi/3)+0.015, tl[-i-1],
                    ha='center', va='center', rotation=60, fontsize=tick_size)

        # diamond grid + ticks
        ax.plot([0.5+offset+0.5/(1/interval)*x/interval, 1+offset+0.5/(1/interval)*x/interval],
                [h+offsety+0.5/(1/interval)*x/interval*np.tan(np.pi/3),
                 offsety+0.5/(1/interval)*x/interval*np.tan(np.pi/3)], 'k:', lw=1.0)
        if i in [1,2,3,4]:
            ax.text(0.5+offset+0.5/(1/interval)*x/interval-0.026,
                    h+offsety+0.5/(1/interval)*x/interval*np.tan(np.pi/3)+0.015, tl[i],
                    ha='center', va='center', rotation=60, fontsize=tick_size)
            ax.text(1+offset+0.5/(1/interval)*x/interval+0.026,
                    offsety+0.5/(1/interval)*x/interval*np.tan(np.pi/3)-0.015, tl[-i-1],
                    ha='center', va='center', rotation=60, fontsize=tick_size)
        ax.plot([0.5+offset+0.5/(1/interval)*x/interval, 1+offset+0.5/(1/interval)*x/interval],
                [h+offsety-0.5/(1/interval)*x/interval*np.tan(np.pi/3),
                 2*h+offsety-0.5/(1/interval)*x/interval*np.tan(np.pi/3)], 'k:', lw=1.0)
        if i in [1,2,3,4]:
            ax.text(0.5+offset+0.5/(1/interval)*x/interval-0.026,
                    h+offsety-0.5/(1/interval)*x/interval*np.tan(np.pi/3)-0.015, tl[i],
                    ha='center', va='center', rotation=-60, fontsize=tick_size)
            ax.text(1+offset+0.5/(1/interval)*x/interval+0.026,
                    2*h+offsety-0.5/(1/interval)*x/interval*np.tan(np.pi/3)+0.015, tl[-i-1],
                    ha='center', va='center', rotation=-60, fontsize=tick_size)

    # ── Axis labels (FIX 3a: "%" prefixes removed) ──
    ax.text(0.5, -offset, 'Ca$^{2+}$', ha='center', va='center', fontsize=label_size)
    ax.text(1+2*offset+0.5, -offset, 'Cl$^{-}$', ha='center', va='center', fontsize=label_size)
    ax.text(0.25-offset*np.cos(np.pi/30), 0.25*np.tan(np.pi/3)+offset*np.sin(np.pi/30),
            'Mg$^{2+}$', ha='center', va='center', rotation=60, fontsize=label_size)
    ax.text(1.75+2*offset+offset*np.cos(np.pi/30), 0.25*np.tan(np.pi/3)+offset*np.sin(np.pi/30),
            'SO$_4^{2-}$', ha='center', va='center', rotation=-60, fontsize=label_size)
    ax.text(0.75+offset*np.cos(np.pi/30), 0.25*np.tan(np.pi/3)+offset*np.sin(np.pi/30),
            'Na$^+$ + K$^+$', ha='center', va='center', rotation=-60, fontsize=label_size)
    ax.text(1+2*offset+0.25-offset*np.cos(np.pi/30), 0.25*np.tan(np.pi/3)+offset*np.sin(np.pi/30),
            'HCO$_3^-$ + CO$_3^{2-}$', ha='center', va='center', rotation=60, fontsize=label_size)
    ax.text(0.5+offset+0.5*offset+offset*np.cos(np.pi/30),
            h+offsety+0.25*np.tan(np.pi/3)+offset*np.sin(np.pi/30),
            'SO$_4^{2-}$ + Cl$^-$', ha='center', va='center', rotation=60, fontsize=label_size)
    ax.text(1.5+offset-0.25+offset*np.cos(np.pi/30),
            h+offsety+0.25*np.tan(np.pi/3)+offset*np.sin(np.pi/30),
            'Ca$^{2+}$ + Mg$^{2+}$', ha='center', va='center', rotation=-60, fontsize=label_size)

    # Grey water-type shading (exact wqchartpy)
    g = (0.8, 0.8, 0.8)
    ax.fill([0.25,0.5,0.75,0.25], [h/2,0,h/2,h/2], color=g, zorder=0)
    ax.fill([1+2*offset+0.25,1+2*offset+0.5,1+2*offset+0.75,1+2*offset+0.25],
            [h/2,0,h/2,h/2], color=g, zorder=0)
    ax.fill([0.5+offset+0.25, 0.5+offset+0.25+0.5, 0.5+offset+0.25+0.25, 0.5+offset+0.25],
            [h+offsety-0.5*np.sin(np.pi/3), h+offsety-0.5*np.sin(np.pi/3), h+offsety,
             h+offsety-0.5*np.sin(np.pi/3)], color=g, zorder=0)
    ax.fill([0.5+offset+0.25, 0.5+offset+0.25+0.25, 0.5+offset+0.25+0.5, 0.5+offset+0.25],
            [h+offsety+0.5*np.sin(np.pi/3), h+offsety, h+offsety+0.5*np.sin(np.pi/3),
             h+offsety+0.5*np.sin(np.pi/3)], color=g, zorder=0)

    ax.set_xlim(-0.10, 2+2*offset+0.10)
    ax.set_ylim(-0.10, 2*h+offsety+0.10)
    return offset, h

def wqchartpy_piper_coords(meqL, offset, h):
    """Exact wqchartpy coordinate transform. meqL cols: Ca,Mg,Na,K,HCO3,CO3,Cl,SO4."""
    sumcat = np.sum(meqL[:, 0:4], axis=1)
    suman  = np.sum(meqL[:, 4:8], axis=1)
    cat = np.zeros((meqL.shape[0], 3)); an = np.zeros((meqL.shape[0], 3))
    cat[:, 0] = meqL[:, 0] / sumcat                  # Ca
    cat[:, 1] = meqL[:, 1] / sumcat                  # Mg
    cat[:, 2] = (meqL[:, 2] + meqL[:, 3]) / sumcat   # Na+K
    an[:, 0]  = (meqL[:, 4] + meqL[:, 5]) / suman    # HCO3+CO3
    an[:, 2]  = meqL[:, 6] / suman                   # Cl
    an[:, 1]  = meqL[:, 7] / suman                   # SO4
    cat_x = 0.5 * (2 * cat[:, 2] + cat[:, 1])
    cat_y = h * cat[:, 1]
    an_x  = 1 + 2*offset + 0.5 * (2 * an[:, 2] + an[:, 1])
    an_y  = h * an[:, 1]
    d_x = an_y / (4 * h) + 0.5 * an_x - cat_y / (4 * h) + 0.5 * cat_x
    d_y = 0.5 * an_y + h * an_x + 0.5 * cat_y - h * cat_x
    return cat_x, cat_y, an_x, an_y, d_x, d_y

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE LAYOUT  2x2
# ═══════════════════════════════════════════════════════════════════════════════
fig1 = plt.figure(figsize=FIGURE_SIZE)
gs1  = gridspec.GridSpec(2, 2, figure=fig1, hspace=0.17, wspace=0.15)

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL A - Piper diagram
# ═══════════════════════════════════════════════════════════════════════════════
ax_pip = fig1.add_subplot(gs1[0, 0], aspect='equal', frameon=False, xticks=[], yticks=[])
add_panel_label(ax_pip, LABEL_POSITIONS['piper'])

meqL = np.column_stack([
    Ca.values, Mg.values, Na.values, K.values,
    HCO3.values, np.zeros(n), Cl.values, SO4.values
])

p_offset, p_h = wqchartpy_piper_background(ax_pip)
cat_x, cat_y, an_x, an_y, d_x, d_y = wqchartpy_piper_coords(meqL, p_offset, p_h)

for i in range(n):
    scatter_point(ax_pip, cat_x[i], cat_y[i], i)
    scatter_point(ax_pip, an_x[i],  an_y[i],  i)
    scatter_point(ax_pip, d_x[i],   d_y[i],   i)

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL B - Durov diagram
# EDITOR FIX 3b: axis titles reworded; water-type field labels set upright.
# ═══════════════════════════════════════════════════════════════════════════════
ax_dur = fig1.add_subplot(gs1[0, 1])
add_panel_label(ax_dur, LABEL_POSITIONS['durov'])

sumcat = Ca.values + Mg.values + Na.values + K.values + 1e-12
suman  = HCO3.values + Cl.values + SO4.values + 1e-12
f_Ca_pct   = Ca.values   / sumcat * 100
f_HCO3_pct = HCO3.values / suman  * 100

for i in range(n):
    scatter_point(ax_dur, f_Ca_pct[i], f_HCO3_pct[i], i)

corr_line_handle = None
if SHOW_CORR_LINE:
    mask_valid = np.isfinite(f_Ca_pct) & np.isfinite(f_HCO3_pct)
    if mask_valid.sum() > 1:
        slope, intercept = np.polyfit(f_Ca_pct[mask_valid], f_HCO3_pct[mask_valid], 1)
        r_val = np.corrcoef(f_Ca_pct[mask_valid], f_HCO3_pct[mask_valid])[0, 1]
        x_line = np.array([f_Ca_pct[mask_valid].min(), f_Ca_pct[mask_valid].max()])
        y_line = slope * x_line + intercept
        corr_line_handle, = ax_dur.plot(
            x_line, y_line,
            color=CORR_LINE_COLOR, linestyle=CORR_LINE_STYLE, lw=CORR_LINE_WIDTH,
            zorder=5, label='Trend'
        )

if SHOW_POINT_LABELS:
    for i in range(n):
        if POINT_LABEL_SOURCE == 'symbol':
            lbl_text = SYMBOL_LABEL_MAP.get(short_labels[i], str(short_labels[i]))
        else:
            lbl_text = str(short_labels[i])
        ax_dur.annotate(
            lbl_text,
            (f_Ca_pct[i], f_HCO3_pct[i]),
            xytext=POINT_LABEL_OFFSET, textcoords='offset points',
            fontsize=POINT_LABEL_SIZE, color=POINT_LABEL_COLOR, zorder=7
        )

# FIX 3b: axis titles as requested by the editor
ax_dur.set_xlabel('Ca$^{2+}$ (% of total cation equivalents)', fontsize=LABEL_SIZE)
ax_dur.set_ylabel('HCO$_3^-$ (% of total anion equivalents)', fontsize=LABEL_SIZE)
ax_dur.grid(alpha=0.3)

xlim = ax_dur.get_xlim(); ylim = ax_dur.get_ylim()
cx   = (xlim[0]+xlim[1])/2;  cy = (ylim[0]+ylim[1])/2
ax_dur.axhline(cy, color='grey', lw=0.9, ls='--', alpha=0.5)
ax_dur.axvline(cx, color='grey', lw=0.9, ls='--', alpha=0.5)

# FIX 3b: water-type field labels now upright (style='normal' instead of 'italic')
for tx, ty, lbl in [(0.17,0.88,'Ca-HCO$_3$'), (0.70,0.88,'Mixed-HCO$_3$'),
                     (0.17,0.10,'Ca-SO$_4$/Cl'),(0.70,0.10,'Na-Cl')]:
    ax_dur.text(tx, ty, lbl, transform=ax_dur.transAxes,
                fontsize=LABEL_SIZE-1, color='dimgrey', ha='center', style='normal')

legend_handles_b = list(water_type_handles)
if corr_line_handle is not None:
    legend_handles_b = legend_handles_b + [corr_line_handle]

ax_dur.legend(handles=legend_handles_b, fontsize=LEGEND_SIZE,
              bbox_to_anchor=LEG_B_XY, loc='upper left',
              title='Water source type', title_fontsize=LEGEND_SIZE,
              framealpha=0.9, ncol=2)

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL C - Schoeller
# ═══════════════════════════════════════════════════════════════════════════════
gs1c   = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs1[1, 0], hspace=0.15)
ax_schW = fig1.add_subplot(gs1c[0, 0])
ax_schD = fig1.add_subplot(gs1c[1, 0])
add_panel_label(ax_schW, LABEL_POSITIONS['schoeller_wet'])
add_panel_label(ax_schD, LABEL_POSITIONS['schoeller_dry'])

ion_series  = [Ca, Mg, Na, K, Cl, SO4, HCO3]
ion_lbl_sch = ['Ca$^{2+}$','Mg$^{2+}$','Na$^+$','K$^+$','Cl$^-$','SO$_4^{2-}$','HCO$_3^-$']
x_pos = list(range(len(ion_lbl_sch)))

all_meq  = pd.concat(ion_series)
pos_vals = all_meq[all_meq > 0]
ymin_s   = pos_vals.min() * 0.3 if len(pos_vals) else 1e-4
ymax_s   = all_meq.max()  * 3.0

wet_mask = np.array(season_labels) == 'Wet'
dry_mask = np.array(season_labels) == 'Dry'
if not wet_mask.any(): wet_mask = np.ones(n, dtype=bool)
if not dry_mask.any(): dry_mask = np.ones(n, dtype=bool)

all_schoeller_handles = []
seen_for_legend = set()

def draw_schoeller_individual(ax, mask, title):
    global all_schoeller_handles
    idx = np.where(mask)[0]
    for i in idx:
        sname = sample_names[i]
        vals  = [float(s.iloc[i]) for s in ion_series]
        st    = SAMPLE_STYLES.get(sname, {'color':'#888','lw':1.5,'ls':'-','marker':'o','ms':6})
        ax.plot(x_pos, vals,
                color=st['color'], lw=st['lw'], ls=st['ls'],
                marker=st['marker'], ms=st['ms'],
                markerfacecolor='white', markeredgewidth=1.0,
                alpha=0.7, zorder=4)
        if sname not in seen_for_legend:
            all_schoeller_handles.append(
                Line2D([], [], color=st['color'], lw=st['lw'], ls=st['ls'],
                       marker=st['marker'], ms=st['ms'],
                       markerfacecolor='white', markeredgewidth=1.0,
                       label=sname))
            seen_for_legend.add(sname)

    mean_v = [float(np.mean([ion_series[j].iloc[i] for i in idx])) for j in range(7)]
    ax.plot(x_pos, mean_v, color='black', lw=2.8, marker='D', ms=8, zorder=8)

    ax.set_yscale('log'); ax.set_ylim(ymin_s, ymax_s)
    ax.set_xticks(x_pos); ax.set_xticklabels(ion_lbl_sch, fontsize=TICK_SIZE, rotation=30, ha='right')
    ax.set_ylabel('Concentration (meq/L)', fontsize=LABEL_SIZE)
    ax.set_title(title, fontsize=PANEL_TITLE_SIZE-1, fontweight='bold')
    ax.grid(True, which='both', alpha=0.3)

draw_schoeller_individual(ax_schW, wet_mask, 'Wet Season')
draw_schoeller_individual(ax_schD, dry_mask, 'Dry Season')

all_schoeller_handles.append(
    Line2D([], [], color='black', lw=2.8, marker='D', ms=8, label='Mean'))

ax_schW.set_xticklabels([])

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL D - Water Type bar  +  Schoeller sample legend
# EDITOR FIX 3d: "3" and "4" are now subscripts in HCO3 and SO4.
# ═══════════════════════════════════════════════════════════════════════════════
ax_wt = fig1.add_subplot(gs1[1, 1])
add_panel_label(ax_wt, LABEL_POSITIONS['watertype'])

def classify(i):
    dom_cat = int(np.argmax([Ca.iloc[i], Mg.iloc[i], Na.iloc[i]+K.iloc[i]]))
    dom_an  = int(np.argmax([HCO3.iloc[i], SO4.iloc[i], Cl.iloc[i]]))
    return "%s-%s" % (['Ca','Mg','Na-K'][dom_cat], ['HCO3','SO4','Cl'][dom_an])

def prettify_watertype(label):
    """Plain water-type code -> mathtext with subscripted 3 and 4."""
    out = str(label)
    out = out.replace('HCO3', 'HCO$_3$')
    out = out.replace('SO4',  'SO$_4$')
    return out

wt       = [classify(i) for i in range(n)]
wt_s     = pd.DataFrame({'type': wt, 'season': season_labels})
wt_pivot = wt_s.groupby(['type','season']).size().unstack(fill_value=0)

season_color_map = {'Wet':'#2196F3','Dry':'#FF5722'}
bar_colors = [season_color_map.get(c,'#888') for c in wt_pivot.columns]

wt_pivot.plot(kind='bar', ax=ax_wt, color=bar_colors, edgecolor='k', lw=0.7)
ax_wt.set_xlabel('Water Type', fontsize=LABEL_SIZE)
ax_wt.set_ylabel('Number of Samples', fontsize=LABEL_SIZE)

# FIX 3d: re-label the x-axis categories with proper subscripts
ax_wt.set_xticklabels([prettify_watertype(t.get_text()) for t in ax_wt.get_xticklabels()])

ax_wt.tick_params(axis='x', rotation=20, labelsize=TICK_SIZE)
ax_wt.tick_params(axis='y', labelsize=TICK_SIZE)
ax_wt.grid(axis='y', alpha=0.4)

for bar in ax_wt.patches:
    h_b = bar.get_height()
    if h_b > 0:
        ax_wt.text(bar.get_x()+bar.get_width()/2, h_b+0.1, str(int(h_b)),
                   ha='center', va='bottom', fontsize=TICK_SIZE)

ax_wt.legend(handles=all_schoeller_handles,
             fontsize=LEGEND_SIZE,
             bbox_to_anchor=LEG_D_XY,
             loc='upper left',
             ncol=LEG_D_NCOL,
             title='Schoeller samples',
             title_fontsize=LEGEND_SIZE,
             framealpha=0.9)

save(fig1, OUT_BASENAME)
