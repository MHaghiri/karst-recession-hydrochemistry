"""
Fig 5 - Statistical Analysis
Layout:
  Row 1: (a) Correlation Heatmap  |  (b) PCA Biplot
  Row 2: (c) Hierarchical Cluster Dendrogram  (full width)
  Row 3: (d) Box Plots  |  (e) PCA Scree Plot

Revised for Hydrogeology Journal technical-editor comments (HYJO-D-26-00525R1):
  5a - colour scale bar title enlarged (CBAR_TITLE_SIZE) and "r" set italic
       ("Pearson r" -> "Pearson $r$")
  Output written as both PDF (vector, for submission) and PNG.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# USER SETTINGS  <- edit here
# ═══════════════════════════════════════════════════════════════════════════════

FIGURE_DPI        = 1000
SUPTITLE_SIZE     = 17
TICK_SIZE         = 16
LABEL_SIZE        = 18
PANEL_TITLE_SIZE  = 20
LEGEND_SIZE       = 14
POINT_SIZE        = 140
ANNOTATION_SIZE   = 11      # sample label size on PCA biplot
HEATMAP_NUM_SIZE  = 11      # numbers inside correlation matrix

# ── Panel a colour bar (EDITOR FIX 5a) ────────────────────────────────────────
CBAR_TITLE_SIZE   = 18      # colour scale bar title size (was matplotlib default ~10)
CBAR_TICK_SIZE    = 15      # colour scale bar tick value size
CBAR_TITLE        = 'Pearson $r$'   # "r" rendered italic via mathtext
CBAR_TITLE_PAD    = 14      # gap between the colour bar and its title

# ── Panel c (Dendrogram) x-axis settings ──────────────────────────────────────
DENDRO_LEAF_FONT_SIZE = 14

# ── Panel heights (inches) for each row ──────────────────────────────────────
ROW1_HEIGHT  = 5.5
ROW2_HEIGHT  = 4.5
ROW3_HEIGHT  = 4.5

# ── Panel widths (relative units) ────────────────────────────────────────────
ROW1_COL_LEFT   = 1.0
ROW1_COL_RIGHT  = 1.0
ROW3_COL_LEFT   = 1.6
ROW3_COL_RIGHT  = 1.0

# ── Spacing between panels ────────────────────────────────────────────────────
HSPACE = 0.6
WSPACE = 0.2

# ── PCA Biplot legend position (axes-fraction 0-1; None = auto) ──────────────
LEG_PCA_X  = 0.3
LEG_PCA_Y  = 0.65
LEG_PCA_HA = 'right'
LEG_PCA_VA = 'lower'

# ── Output file name (saved into OUT_DIR, both formats) ──────────────────────
OUT_BASENAME = "Fig5"

# ── Water-source classification ───────────────────────────────────────────────
N_SPRING = 11
N_QANAT  = 4
N_WELL   = 4
SOURCE_TYPE_OVERRIDE = {}

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
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import dendrogram, linkage

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
warnings.filterwarnings('ignore')

# Keep text as real text in the PDF (editable, scalable, never pixelated)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype']  = 42

DATA_PATH = r"C:\Users\mhaghi2\Desktop\Article 9\data\hydrochemical\hydrochemical.xlsx"
OUT_DIR   = r"C:\Users\mhaghi2\Desktop\Article 9\map"
os.makedirs(OUT_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════
raw = pd.read_excel(DATA_PATH, header=None)
ION_KEYWORDS = ['ca','mg','na','cl','so4','hco3','ec','tds','ph','temp']

def row_score(row):
    return sum(1 for v in row if isinstance(v, str) and any(k in v.lower() for k in ION_KEYWORDS))

header_row  = max(range(min(5, len(raw))), key=lambda i: row_score(raw.iloc[i]))
raw_headers = raw.iloc[header_row].tolist()
filled, last = [], 'col'
for v in raw_headers:
    if pd.isna(v) or str(v).strip() == '':
        filled.append(last)
    else:
        last = str(v).strip()
        filled.append(last)
seen = {}; unique_headers = []
for h in filled:
    hl = h.lower(); seen[hl] = seen.get(hl, 0) + 1
    unique_headers.append(h if seen[hl] == 1 else "%s_%d" % (h, seen[hl]))

df_raw = raw.iloc[header_row + 1:].copy()
df_raw.columns = unique_headers
df_raw = df_raw.reset_index(drop=True)

def normalise(s):
    return str(s).strip().lower().replace(' ','').replace('+','').replace('-','') \
                 .replace('²','2').replace('2+','').replace('²⁺','')

norm_map     = {c: normalise(c) for c in df_raw.columns}
name_col_raw = df_raw.columns[0]
TARGET       = ['ca','mg','na','k','cl','so4','hco3','ec','tds','ph','temp']

def find_cols(tgt):
    return [c for c, nn in norm_map.items() if tgt in nn]

ca_cols   = find_cols('ca')
n_seasons = max(1, len(ca_cols))
seasons   = []
for s_idx in range(n_seasons):
    sl    = ['Wet','Dry','S3','S4'][s_idx] if n_seasons > 1 else 'All'
    block = {'sample': df_raw[name_col_raw]}
    for tgt in TARGET:
        cands      = find_cols(tgt)
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

Ca_c='ca'; Mg_c='mg'; Na_c='na'; K_c='k'; Cl_c='cl'
SO4_c='so4'; HCO3_c='hco3'; EC_c='ec'; TDS_c='tds'
n = len(df)

short_labels  = df['sample'].astype(str).values
season_labels = df['season'].astype(str).values

# ═══════════════════════════════════════════════════════════════════════════════
# WATER-SOURCE CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════
_unique_samples  = list(pd.unique(df['sample'].astype(str)))
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
    m  = re.match(r'^([A-Z])\s*\d', su)
    if m:
        first = m.group(1)
        if first == 'S': return 'Spring'
        if first == 'Q': return 'Qanat'
        if first == 'W': return 'Well'
    return _positional_type.get(s, 'Other')

source_types = [get_source_type(nm) for nm in short_labels]

# ═══════════════════════════════════════════════════════════════════════════════
# COMPOUND LABELS:  SW1, SD1, QW1, QD1, WW1, WD1
# ═══════════════════════════════════════════════════════════════════════════════
def season_abbr(s):
    sl = str(s).strip().lower()
    if sl == 'wet': return 'W'
    if sl == 'dry': return 'D'
    return sl[0].upper() if sl else 'X'

src_prefix = {'Spring': 'S', 'Qanat': 'Q', 'Well': 'W', 'Other': 'O'}

compound_counter = {}
compound_labels  = []
for i in range(n):
    sp  = src_prefix.get(source_types[i], 'O')
    sa  = season_abbr(season_labels[i])
    key = (sp, sa)
    compound_counter[key] = compound_counter.get(key, 0) + 1
    compound_labels.append("%s%s%d" % (sp, sa, compound_counter[key]))
compound_labels = np.array(compound_labels)

# ═══════════════════════════════════════════════════════════════════════════════
# STYLE MAP  -  filled = Wet, open = Dry  |  shape/colour = source type
# ═══════════════════════════════════════════════════════════════════════════════
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
    return STYLE_MAP.get(
        (source_types[i], season_labels[i]),
        STYLE_MAP.get((source_types[i], 'Wet'), STYLE_MAP[('Other', 'Wet')])
    )

def scatter_point(ax, x, y, i, size=None):
    st = get_style(i)
    s  = size if size else POINT_SIZE
    fc = st['color'] if st['filled'] else 'white'
    ax.scatter(x, y, c=[fc], s=s, marker=st['marker'],
               edgecolors=st['edgecolor'], linewidths=1.0, zorder=6, alpha=0.9)

present_keys   = set(zip(source_types, season_labels))
legend_handles = []
for key, st in STYLE_MAP.items():
    if key in present_keys and key[0] != 'Other':
        fc = st['color'] if st['filled'] else 'white'
        legend_handles.append(
            Line2D([0], [0], marker=st['marker'], color='w',
                   markerfacecolor=fc, markeredgecolor=st['edgecolor'],
                   markersize=9, label=st['label'], linewidth=0)
        )

# ═══════════════════════════════════════════════════════════════════════════════
# PCA
# ═══════════════════════════════════════════════════════════════════════════════
stat_cols  = [c for c in [Ca_c,Mg_c,Na_c,K_c,Cl_c,SO4_c,HCO3_c,EC_c,TDS_c] if c in df.columns]
stat_nice  = {'ca':'Ca$^{2+}$','mg':'Mg$^{2+}$','na':'Na$^+$','k':'K$^+$','cl':'Cl$^-$',
              'so4':'SO$_4^{2-}$','hco3':'HCO$_3^-$','ec':'EC','tds':'TDS'}
data_stat  = df[stat_cols].copy()
nice_names = [stat_nice.get(c, c) for c in stat_cols]

scaler = StandardScaler()
Xs     = scaler.fit_transform(data_stat.dropna())
pca    = PCA(n_components=min(4, Xs.shape[1]))
scores = pca.fit_transform(Xs)
loads  = pca.components_.T
ev     = pca.explained_variance_ratio_ * 100

print("Data loaded: %d samples" % n)
print("Source-type counts:", {t: source_types.count(t) for t in ['Spring','Qanat','Well','Other']})
print("Sample compound labels (first 10):", compound_labels[:10].tolist())

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════
plt.rcParams.update({'xtick.labelsize': TICK_SIZE, 'ytick.labelsize': TICK_SIZE})

FIGURE_WIDTH  = max(ROW1_COL_LEFT + ROW1_COL_RIGHT,
                    ROW3_COL_LEFT  + ROW3_COL_RIGHT) * 6.5
FIGURE_HEIGHT = ROW1_HEIGHT + ROW2_HEIGHT + ROW3_HEIGHT

fig = plt.figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
fig.suptitle("", fontsize=SUPTITLE_SIZE, fontweight='bold', y=0.995)

top = fig.add_gridspec(1, 2,
                       width_ratios=[ROW1_COL_LEFT, ROW1_COL_RIGHT],
                       left=0.06, right=0.97,
                       top=1.0 - 0.04,
                       bottom=1.0 - 0.04 - ROW1_HEIGHT / FIGURE_HEIGHT,
                       wspace=WSPACE)

mid = fig.add_gridspec(1, 1,
                       left=0.06, right=0.97,
                       top=1.0 - 0.04 - ROW1_HEIGHT / FIGURE_HEIGHT - HSPACE * 0.1,
                       bottom=1.0 - 0.04 - ROW1_HEIGHT / FIGURE_HEIGHT
                             - HSPACE * 0.1 - ROW2_HEIGHT / FIGURE_HEIGHT)

bot = fig.add_gridspec(1, 2,
                       width_ratios=[ROW3_COL_LEFT, ROW3_COL_RIGHT],
                       left=0.06, right=0.97,
                       top=1.0 - 0.04 - ROW1_HEIGHT / FIGURE_HEIGHT
                           - HSPACE * 0.1 - ROW2_HEIGHT / FIGURE_HEIGHT - HSPACE * 0.1,
                       bottom=1.0 - 0.04 - ROW1_HEIGHT / FIGURE_HEIGHT
                           - HSPACE * 0.1 - ROW2_HEIGHT / FIGURE_HEIGHT
                           - HSPACE * 0.1 - ROW3_HEIGHT / FIGURE_HEIGHT,
                       wspace=WSPACE)

ax_heatmap = fig.add_subplot(top[0, 0])
ax_pca     = fig.add_subplot(top[0, 1])
ax_dendro  = fig.add_subplot(mid[0, 0])
ax_box     = fig.add_subplot(bot[0, 0])
ax_scree   = fig.add_subplot(bot[0, 1])

# ═══════════════════════════════════════════════════════════════════════════════
# (a) CORRELATION HEATMAP
# EDITOR FIX 5a: colour-bar title enlarged and "r" italic.
# ═══════════════════════════════════════════════════════════════════════════════
corr = data_stat.corr()
corr.index = corr.columns = nice_names
im = ax_heatmap.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)

cbar = plt.colorbar(im, ax=ax_heatmap, shrink=0.85)
cbar.set_label(CBAR_TITLE, fontsize=CBAR_TITLE_SIZE, labelpad=CBAR_TITLE_PAD)
cbar.ax.tick_params(labelsize=CBAR_TICK_SIZE)

ax_heatmap.set_xticks(range(len(nice_names)))
ax_heatmap.set_xticklabels(nice_names, rotation=45, ha='right', fontsize=TICK_SIZE)
ax_heatmap.set_yticks(range(len(nice_names)))
ax_heatmap.set_yticklabels(nice_names, fontsize=TICK_SIZE)
for i in range(len(nice_names)):
    for j in range(len(nice_names)):
        ax_heatmap.text(j, i, "%.2f" % corr.values[i, j],
                        ha='center', va='center', fontsize=HEATMAP_NUM_SIZE,
                        color='white' if abs(corr.values[i, j]) > 0.6 else 'black')
ax_heatmap.set_title('a', fontsize=PANEL_TITLE_SIZE, fontweight='bold')

# ═══════════════════════════════════════════════════════════════════════════════
# (b) PCA BIPLOT
# ═══════════════════════════════════════════════════════════════════════════════
for i in range(len(scores)):
    scatter_point(ax_pca, scores[i, 0], scores[i, 1], i)
    ax_pca.annotate(compound_labels[i],
                    (scores[i, 0] + 0.06, scores[i, 1] + 0.06),
                    fontsize=ANNOTATION_SIZE, alpha=0.75)

scale = (max(abs(scores[:, 0].max()), abs(scores[:, 1].max())) /
         max(abs(loads[:, 0]).max(), 1e-9) * 0.55)
for i, name in enumerate(nice_names[:len(loads)]):
    ax_pca.arrow(0, 0, loads[i, 0] * scale, loads[i, 1] * scale,
                 head_width=0.07, head_length=0.05,
                 fc='red', ec='red', lw=1.2, alpha=0.85)
    ax_pca.text(loads[i, 0] * scale * 1.13, loads[i, 1] * scale * 1.13,
                name, color='red', fontsize=TICK_SIZE, fontweight='bold')

ax_pca.axhline(0, color='grey', lw=0.8, ls='--')
ax_pca.axvline(0, color='grey', lw=0.8, ls='--')
ax_pca.set_xlabel('PC1 (%.1f%% variance)' % ev[0], fontsize=LABEL_SIZE)
ax_pca.set_ylabel('PC2 (%.1f%% variance)' % ev[1], fontsize=LABEL_SIZE)
ax_pca.set_title('b', fontsize=PANEL_TITLE_SIZE, fontweight='bold')
ax_pca.grid(alpha=0.25)

if LEG_PCA_X is None or LEG_PCA_Y is None:
    ax_pca.legend(handles=legend_handles, fontsize=LEGEND_SIZE, loc='best')
else:
    loc_str = "%s %s" % (LEG_PCA_VA, LEG_PCA_HA)
    ax_pca.legend(handles=legend_handles, fontsize=LEGEND_SIZE,
                  loc=loc_str,
                  bbox_to_anchor=(LEG_PCA_X, LEG_PCA_Y),
                  bbox_transform=ax_pca.transAxes)

# ═══════════════════════════════════════════════════════════════════════════════
# (c) DENDROGRAM
# ═══════════════════════════════════════════════════════════════════════════════
Xcl = scaler.fit_transform(data_stat.dropna())
lnk = linkage(Xcl, method='ward')
dendrogram(lnk, labels=compound_labels[:len(Xcl)], ax=ax_dendro,
           color_threshold=0.7 * max(lnk[:, 2]),
           leaf_rotation=90, leaf_font_size=DENDRO_LEAF_FONT_SIZE)
ax_dendro.set_ylabel('Ward Distance', fontsize=LABEL_SIZE)
ax_dendro.set_title('c', fontsize=PANEL_TITLE_SIZE, fontweight='bold')
ax_dendro.grid(axis='y', alpha=0.3)

# ═══════════════════════════════════════════════════════════════════════════════
# (d) BOX PLOTS
# ═══════════════════════════════════════════════════════════════════════════════
data_norm = pd.DataFrame(Xs, columns=nice_names)
bp = ax_box.boxplot([data_norm[c].dropna() for c in nice_names],
                    labels=nice_names, patch_artist=True, widths=0.55,
                    medianprops=dict(color='red', lw=2),
                    whiskerprops=dict(lw=1.2), capprops=dict(lw=1.2),
                    flierprops=dict(marker='o', ms=3, color='grey'))
colors_box = plt.cm.Set2(np.linspace(0, 1, len(nice_names)))
for patch, col in zip(bp['boxes'], colors_box):
    patch.set_facecolor(col); patch.set_alpha(0.75)
ax_box.axhline(0, color='k', lw=0.8, ls='--', alpha=0.5)
ax_box.set_ylabel('Standardised value (z-score)', fontsize=LABEL_SIZE)
ax_box.set_title('d', fontsize=PANEL_TITLE_SIZE, fontweight='bold')
ax_box.tick_params(axis='x', labelsize=TICK_SIZE)
ax_box.grid(axis='y', alpha=0.35)

# ═══════════════════════════════════════════════════════════════════════════════
# (e) PCA SCREE PLOT
# ═══════════════════════════════════════════════════════════════════════════════
pcs = ['PC%d' % (i+1) for i in range(len(ev))]
ax_scree.bar(pcs, ev, color='steelblue', edgecolor='k', alpha=0.85)
ax_scree.plot(pcs, np.cumsum(ev), 'ro-', lw=2, ms=7, label='Cumulative')
ax_scree.axhline(70, color='grey', ls='--', lw=1, alpha=0.6)
ax_scree.set_ylabel('Variance Explained (%)', fontsize=LABEL_SIZE)
ax_scree.set_title('e', fontsize=PANEL_TITLE_SIZE, fontweight='bold')
for i, v in enumerate(ev):
    ax_scree.text(i, v + 0.5, '%.1f%%' % v, ha='center', fontsize=TICK_SIZE - 1)
ax_scree.legend(fontsize=LEGEND_SIZE)
ax_scree.grid(alpha=0.3)

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE  -  PDF (vector, for submission) and PNG
# ═══════════════════════════════════════════════════════════════════════════════
for ext in ('pdf', 'png'):
    out_path = os.path.join(OUT_DIR, "%s.%s" % (OUT_BASENAME, ext))
    fig.savefig(out_path, dpi=FIGURE_DPI, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("  Saved -> %s" % out_path)
plt.close(fig)
