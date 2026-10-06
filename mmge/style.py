"""Plotting conventions shared by all figures: palettes, labels and CDF helpers."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap

MODELS = ['htessel', 'jules', 'mhm', 'pcrglobwb']
MODEL_LABEL = {'htessel': 'HTESSEL', 'jules': 'JULES', 'mhm': 'mHM', 'pcrglobwb': 'PCR-GLOBWB'}
FORCINGS = ['em_earth', 'era5land', 'mswep', 'w5e5']
FORCING_LABEL = {'era5land': 'ERA5-Land', 'em_earth': 'EM-Earth', 'mswep': 'MSWEP', 'w5e5': 'W5E5'}

# Categorical palettes, validated for colour-vision-deficiency safety with four series.
# Models and forcings use two distinct hue families (not tints of one another) so a reader
# does not read "blue" in one figure and "blue" in another as the same meaning.
PALETTE_MODELS = ['#2a78d6', '#eb6834', '#1baf7a', '#4a3aa7']
PALETTE_FORCINGS = ['#c99a2e', '#00a3a3', '#d6336c', '#2f6b2f']
GRIDLINE_COLOR = '#e1e0d9'

plt.rcParams.update({'xtick.direction': 'in', 'ytick.direction': 'in'})


def sort_cdf(x):
    """Sorted values and their empirical cumulative probabilities."""
    x = np.sort(np.asarray(x, dtype=float))
    return x, np.arange(len(x)) / len(x)


def plot_cdf(data, ax=None, labels=None, palette=PALETTE_MODELS, xlim=None, ylim=None,
             xlabel='KGE [-]', ylabel='CDF [-]', linewidth=1.5, line_styles=None, vline=None):
    """Plot the empirical CDF of every column of a DataFrame on one axis (NaNs dropped)."""
    ax = ax or plt.gca()
    labels = list(data.columns) if labels is None else labels
    line_styles = line_styles or ['-'] * data.shape[1]
    for i, col in enumerate(data.columns):
        values = data[col].dropna().values
        ax.plot(*sort_cdf(values), label=labels[i], linewidth=linewidth,
                color=palette[i % len(palette)], linestyle=line_styles[i])
    if xlim is not None:
        ax.set_xlim(xlim)
    ax.set_ylim(ylim if ylim is not None else [0, 1])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if vline is not None:
        ax.axvline(vline, color='0.4', linewidth=0.8, linestyle='--')
    return ax


def style_region_grid(fig, axes, nrows=2, ncols=3):
    """Shared styling for the 2x3 regional panel grids: gridlines, shared labels, one legend."""
    last = nrows * ncols - 1
    for i, ax in enumerate(axes):
        row, col = divmod(i, ncols)
        ax.grid(True, color=GRIDLINE_COLOR, linewidth=0.7, alpha=0.8, zorder=0)
        ax.set_axisbelow(True)
        if col != 0:
            ax.set_ylabel('')
        if row != nrows - 1:
            ax.set_xlabel('')
            ax.tick_params(axis='x', labelbottom=False)
        else:
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')
        legend = ax.get_legend()
        if legend is not None and i != last:
            legend.remove()
    fig.subplots_adjust(hspace=0.15, wspace=0.08)


def two_slope_discrete_cmap(vmin, vmax, vcenter=0.0, bin_width=0.1, cmap_name='RdYlBu_r'):
    """Discrete, two-slope diverging colormap + norm + boundaries for a signed
    quantity (e.g. a correlation) whose neutral value `vcenter` need not be
    the midpoint of [vmin, vmax]. `vcenter` always lands exactly on the base
    colormap's own midpoint; each side gets independent `bin_width`-wide bins
    drawn from only that half of the base colormap."""
    if not (vmin < vcenter < vmax):
        raise ValueError('vcenter must be strictly between vmin and vmax.')
    n_neg = max(1, round((vcenter - vmin) / bin_width))
    n_pos = max(1, round((vmax - vcenter) / bin_width))
    neg_boundaries = np.linspace(vmin, vcenter, n_neg + 1)
    pos_boundaries = np.linspace(vcenter, vmax, n_pos + 1)
    boundaries = np.concatenate([neg_boundaries, pos_boundaries[1:]])
    base = plt.get_cmap(cmap_name, 256)
    neg_colors = base(np.linspace(0.0, 0.5, n_neg, endpoint=False))
    pos_colors = base(np.linspace(0.5, 1.0, n_pos))
    cmap = ListedColormap(np.vstack([neg_colors, pos_colors]))
    norm = BoundaryNorm(boundaries, cmap.N)
    return cmap, norm, boundaries


def two_slope_discrete_cmap_with_band(vmin, vmax, vcenter=0.0, bin_width=0.1, cmap_name='BrBG',
                                       neutral_half_width=0.0):
    """Like `two_slope_discrete_cmap`, but carves out one explicit bin
    spanning [vcenter - neutral_half_width, vcenter + neutral_half_width]
    and colours it pure white -- a neutral BAND rather than a knife-edge
    centre value. Used for the elasticity figures, whose "unremarkable"
    value (elasticity = 1) needs a visible tolerance band around it, not a
    single boundary line. `neutral_half_width=0` reproduces
    `two_slope_discrete_cmap`'s own point-centred behaviour exactly."""
    if not (vmin < vcenter < vmax):
        raise ValueError('vcenter must be strictly between vmin and vmax.')
    if neutral_half_width < 0:
        raise ValueError('neutral_half_width must be >= 0.')
    neg_edge = vcenter - neutral_half_width
    pos_edge = vcenter + neutral_half_width
    if not (vmin < neg_edge and pos_edge < vmax):
        raise ValueError('neutral_half_width must leave room inside vmin/vmax.')

    n_neg = max(1, round((neg_edge - vmin) / bin_width))
    n_pos = max(1, round((vmax - pos_edge) / bin_width))
    neg_boundaries = np.linspace(vmin, neg_edge, n_neg + 1)
    pos_boundaries = np.linspace(pos_edge, vmax, n_pos + 1)
    base = plt.get_cmap(cmap_name, 256)
    if neutral_half_width > 0:
        boundaries = np.concatenate([neg_boundaries, pos_boundaries])
        neg_colors = base(np.linspace(0.0, 0.5, n_neg, endpoint=False))
        neutral_color = base(np.array([0.5]))
        pos_colors = base(np.linspace(0.5, 1.0, n_pos + 1)[1:])
        cmap = ListedColormap(np.vstack([neg_colors, neutral_color, pos_colors]))
    else:
        boundaries = np.concatenate([neg_boundaries, pos_boundaries[1:]])
        neg_colors = base(np.linspace(0.0, 0.5, n_neg, endpoint=False))
        pos_colors = base(np.linspace(0.5, 1.0, n_pos))
        cmap = ListedColormap(np.vstack([neg_colors, pos_colors]))
    norm = BoundaryNorm(boundaries, cmap.N)
    return cmap, norm, boundaries


def extended_discrete_cmap(cmap, boundaries, extend='min'):
    """Discrete colormap and norm over `boundaries` with extra colour(s) for values outside
    the range. Colours are sampled evenly from `cmap`, the first (and/or last) being used
    for the out-of-range extension, so the in-range bins take the remaining colours."""
    from matplotlib.colors import from_levels_and_colors
    n_ext = {'neither': 0, 'min': 1, 'max': 1, 'both': 2}[extend]
    n_colors = len(boundaries) - 1 + n_ext
    colors = cmap(np.linspace(0, 1, n_colors))
    return from_levels_and_colors(boundaries, colors, extend=extend)


def discrete_map_colours(field, cmap, boundaries):
    """Colormap and norm for drawing `field` in discrete bins given by `boundaries`.
    Values beyond the first/last boundary get their own extension colour, chosen from
    the data, and the in-range bins take the remaining colours sampled evenly from
    `cmap`. Returns keyword arguments for DataArray.plot / pcolormesh."""
    data = np.asarray(field, dtype=float)
    below = bool(np.nanmin(data) < boundaries[0])
    above = bool(np.nanmax(data) > boundaries[-1])
    extend = {(False, False): 'neither', (True, False): 'min',
              (False, True): 'max', (True, True): 'both'}[(below, above)]
    cmap, norm = extended_discrete_cmap(cmap, boundaries, extend=extend)
    return {'cmap': cmap, 'norm': norm}


def savefig(fig, name):
    """Save a figure as PNG (300 dpi) and PDF under output/figures/. Gridded map layers
    are rasterised in the PDF to keep file sizes small."""
    from matplotlib.collections import QuadMesh
    from mmge.paths import FIG_DIR
    for ax in fig.axes:
        for artist in ax.collections:
            if isinstance(artist, QuadMesh):
                artist.set_rasterized(True)
    for ext in ('png', 'pdf'):
        fig.savefig(FIG_DIR / f'{name}.{ext}', dpi=300, bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)
    print(f'Saved output/figures/{name}.png/.pdf')


def round_half_away(x, ndigits=2):
    """Round half away from zero (e.g. -0.225 -> -0.23), as printed in the manuscript tables."""
    from decimal import Decimal, ROUND_HALF_UP
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return x
    q = Decimal(1).scaleb(-ndigits)
    value = float(Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP))
    return 0.0 if value == 0 else value


def round_frame(df, ndigits=2):
    """Apply round_half_away to every numeric column of a DataFrame (or a Series)."""
    import pandas as pd
    if isinstance(df, pd.Series):
        return df.map(lambda v: round_half_away(v, ndigits))
    out = df.copy()
    for col in out.select_dtypes('number').columns:
        out[col] = out[col].map(lambda v: round_half_away(v, ndigits))
    return out


def colorbar(fig, mappable, boundaries, extend=None, **kwargs):
    """Colourbar for a discrete map over `boundaries`. With an extension, the outermost
    bin(s) are drawn as the triangular end(s), so the rectangular part spans the inner
    boundaries. `extend` defaults to the extension of the mappable's colormap."""
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import BoundaryNorm, ListedColormap
    boundaries = np.asarray(boundaries, dtype=float)
    if extend is None:
        extend = getattr(mappable.cmap, 'colorbar_extend', 'neither') or 'neither'
    centres = 0.5 * (boundaries[:-1] + boundaries[1:])
    colours = mappable.cmap(mappable.norm(centres))
    lo = 1 if extend in ('min', 'both') else 0
    hi = len(centres) - (1 if extend in ('max', 'both') else 0)
    cmap = ListedColormap(colours[lo:hi])
    if lo:
        cmap.set_under(colours[0])
    if hi < len(centres):
        cmap.set_over(colours[-1])
    inner = boundaries[lo:len(boundaries) - (len(centres) - hi)]
    sm = ScalarMappable(norm=BoundaryNorm(inner, cmap.N), cmap=cmap)
    ticks = kwargs.pop('ticks', None)
    if ticks is not None:
        ticks = [t for t in np.atleast_1d(ticks) if inner[0] - 1e-9 <= t <= inner[-1] + 1e-9]
    return fig.colorbar(sm, extend=extend, ticks=ticks, **kwargs)
