import warnings

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import strax
import straxen
export, __all__ = strax.exporter()


@export
def plot_pmts(
        c, label='',
        figsize=None,
        xenon1t=False,
        show_tpc=True,
        extend='neither', vmin=None, vmax=None,
        **kwargs):
    """Plot the PMT arrays side-by-side, coloring the PMTS with c.

    :param c: Array of colors to use. Must have len() n_tpc_pmts
    :param label: Label for the color bar
    :param figsize: Figure size to use.
    :param extend: same as plt.colorbar(extend=...)
    :param vmin: Minimum of color scale
    :param vmax: maximum of color scale

    Other arguments are passed to plot_on_single_pmt_array.
    """
    if vmin is None:
        vmin = np.nanmin(c)
    if vmax is None:
        vmax = np.nanmax(c)
    if vmin == vmax:
        # Single-valued array passed
        vmax += 1
    if figsize is None:
        figsize = (11, 4) if xenon1t else (13, 5.5)

    f, axes = plt.subplots(1, 2, figsize=figsize)
    for array_i, array_name in enumerate(['top', 'bottom']):
        ax = axes[array_i]
        plt.sca(ax)
        plt.title(array_name.capitalize())

        plot_on_single_pmt_array(
            c,
            xenon1t=xenon1t,
            array_name=array_name,
            show_tpc=show_tpc,
            vmin=vmin, vmax=vmax,
            **kwargs)

    axes[1].yaxis.tick_right()
    axes[1].yaxis.set_label_position('right')

    plt.tight_layout()
    plt.subplots_adjust(wspace=0)
    plt.colorbar(ax=axes, extend=extend, label=label)



@export
def plot_on_single_pmt_array(
        c,
        array_name='top',
        xenon1t=False,
        r=straxen.tpc_r * 1.03,
        pmt_label_size=8,
        pmt_label_color='white',
        show_tpc=True,
        log_scale=False, vmin=None, vmax=None,
        **kwargs):
    """Plot one of the PMT arrays and color it by c.

    :param c: Array of colors to use. Must be len() of the number of TPC PMTs
    :param label: Label for the color bar
    :param pmt_label_size: Fontsize for the PMT number labels.
    Set to 0 to disable.
    :param pmt_label_color: Text color of the PMT number labels.
    :param log_scale: If True, use a logarithmic color scale
    :param extend: same as plt.colorbar(extend=...)
    :param vmin: Minimum of color scale
    :param vmax: maximum of color scale

    Other arguments are passed to plt.scatter.
    """
    if vmin is None:
        vmin = c.min()
    if vmax is None:
        vmax = c.max()

    pmt_positions = straxen.pmt_positions(xenon1t=xenon1t).to_records()

    ax = plt.gca()
    ax.set_aspect('equal')
    plt.xlim(-r, r)
    plt.ylim(-r, r)

    mask = pmt_positions['array'] == array_name
    pos = pmt_positions[mask]

    kwargs.setdefault('s', 280)
    result = plt.scatter(
        pos['x'],
        pos['y'],
        c=c[mask],
        vmin=vmin, vmax=vmax,
        norm=matplotlib.colors.LogNorm() if log_scale else None,
        **kwargs)

    if show_tpc:
        ax.set_facecolor('lightgrey')
        ax.add_artist(plt.Circle(
            (0, 0),
            straxen.tpc_r,
            edgecolor='k',
            facecolor='w',
            zorder=-5,
            linewidth=1))
    else:
        ax.set_axis_off()

    if pmt_label_size:
        for p in pos:
            plt.text(p['x'], p['y'], str(p['i']),
                     horizontalalignment='center',
                     verticalalignment='center',
                     fontsize=pmt_label_size,
                     color=pmt_label_color)
    return result


@export
def log_y(a=None, b=None, scalar_ticks=True, tick_at=None):
    """Make the y axis use a log scale from a to b"""
    plt.yscale('log')
    if a is not None:
        if b is None:
            a, b = a[0], a[-1]
        ax = plt.gca()
        plt.ylim(a, b)
        if scalar_ticks:
            ax.yaxis.set_major_formatter(
                matplotlib.ticker.FormatStrFormatter('%g'))
            ax.set_yticks(logticks(a, b, tick_at))


@export
def log_x(a=None, b=None, scalar_ticks=True, tick_at=None):
    """Make the x axis use a log scale from a to b"""
    plt.xscale('log')
    if a is not None:
        if b is None:
            a, b = a[0], a[-1]
        plt.xlim(a, b)
        ax = plt.gca()
        if scalar_ticks:
            ax.xaxis.set_major_formatter(
                matplotlib.ticker.FormatStrFormatter('%g'))
            ax.set_xticks(logticks(a, b, tick_at))


def logticks(tmin, tmax=None, tick_at=None):
    if tick_at is None:
        tick_at = (1, 2, 5, 10)
    a, b = np.log10([tmin, tmax])
    a = np.floor(a)
    b = np.ceil(b)
    ticks = np.sort(np.unique(np.outer(
        np.array(tick_at), 
        10.**np.arange(a, b)).ravel()))
    ticks = ticks[(tmin <= ticks) & (ticks <= tmax)]
    return ticks


@export
def quiet_tight_layout():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plt.tight_layout()
