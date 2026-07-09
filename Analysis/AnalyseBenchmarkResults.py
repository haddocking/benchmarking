"""Analysis script dedicated to the HADDOCK3 + haddock-runner benchmarks.

Generates multiple-plots analysing different scenarios performances.
- Barplots: Standard best performing model among top X from all targets.
- Melquiplots: Per-target complex performances among top 200.
- Violinplots: Performance distribution among top X from all targets.

Please modify the Global variable: CAPRIEVAL_STEPS to suite your needs.
It is used to generate nice title to the caprieval steps.

Usage:
>python3 AnalyseBenchmarkResults.py <path/to/benchmark/dir/to/analyze/>

Expected input structure
-------------------------
<benchmark_results_dir>/
    <scenario_name>/
        <PDBid>/
            run1/
                <stage>_caprieval/
                    capri_ss.tsv

(scenario is the OUTER directory, PDBid the INNER one -- this matches the
directory layout currently produced by haddock-runner. The previous
`<PDBid>/<scenario_name>/run1/` layout is no longer supported.)
"""

import argparse
import glob
import json
import os
import re
import sys
import tarfile
import zipfile

from functools import partial
from pathlib import Path
from typing import Callable, Optional, Union

# Try to load external libraries
try:
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ModuleNotFoundError:
    sys.exit(
        "\n[ERROR]: Issue when loading the external libraries.\n\n"
        "This script is using `numpy` and `matplotlib` libraries.\n"
        "Please make sure they are accessible with current environment.\n"
        "(e.g.: >pip install numpy matplotlib)\n"
        )


__version__ = "1.2.0"  # July 2026
__author__ = ", ".join((
    "BonvinLab",
    "Computational Structural Biology group",
    "Utrecht University",
    "the Netherlands",
    "Europe",
    "Planet Earth",
    "Milky Way",
    ))
__dev__ = (
    "Victor G.P. Reys",
    "Shantanu Khatri",
    )


####################
# GLOBAL VARIABLES #
####################
# Define custom caprieval steps names
# NOTE: "Feel free to modify this `CAPRIEVAL_STEPS` dict content to fit your experiment"  # noqa : E501
# This dict must have:
#  as keys   -> Index of the caprieval stage (used to parse data)
#  as values -> Name to give to this stage (used as legends plots)
# NOTE: e.g.: for the following run: [topoaa, rigidbody, caprieval, seletop, caprieval.1, flexref, caprieval.2, emref, caprieval.3, clustfcc, seletopclusts, caprieval.4]  # noqa : E501
# CAPRIEVAL_STEPS = {
    # '02': 'rigidbody',
    # '04': 'seletop 200',
    # '06': 'flexref',
    # '08': 'emref',
    # '11': 'top 4 models per fcc clust',
    # }
CAPRIEVAL_STEPS = {
    '02': 'rigidbody',
    '04': 'seletop 200',
    '06': 'flexref',
    '08': 'emref',
    '11': 'top 4 models per fcc clust',
    }

# Set threshold of top X structures to take into account
TOP_X_THRESHOLDS = (1, 5, 10, 20, 50, 100, 200, 500, 1000, )
# Set number of entries to display in melquiplot
MELQUIPLOT_NB_ENTRIES = 200

# CAPRI performances classes
# NOTE: for each class, we define the lower and upper limit
ALL_PERFORMANCES_CLASSES = {
    "protein": {
        "irmsd": {
            "High": (0, 1),
            "Medium": (1, 2),
            "Acceptable": (2, 4),
            "Near-acceptable": (4, 6),
            "Low": (6, 99999),
            "Missing": (-2, -0.5),
            },
        "dockq": {
            "High": (0.8, 1),
            "Medium": (0.6, 0.8),
            "Acceptable": (0.5, 0.6),
            "Near-acceptable": (0.4, 0.5),
            "Low": (0, 0.4),
            "Missing": (-2, -0.5),
            },
        },
    "peptide": {
        "irmsd": {
            "High": (0, 0.5),
            "Medium": (0.5, 1),
            "Acceptable": (1, 2),
            "Near-acceptable": (2, 3),
            "Low": (3, 99999),
            "Missing": (-2, -0.5),
            },
        "dockq": {
            "High": (0.895, 1),
            "Medium": (0.71, 0.895),
            "Acceptable": (0.43, 0.71),
            "Near-acceptable": (0.35, 0.43),
            "Low": (0, 0.35),
            "Missing": (-2, -0.5),
            },
        },
    # FIXME: Optimize irmsd and dockq values for glycan
    "glycan": {
        "irmsd": {
            "High": (0, 0.5),
            "Medium": (0.5, 1),
            "Acceptable": (1, 2),
            "Near-acceptable": (2, 3),
            "Low": (3, 99999),
            "Missing": (-2, -0.5),
            },
        "dockq": {
            "High": (0.895, 1),
            "Medium": (0.71, 0.895),
            "Acceptable": (0.43, 0.71),
            "Near-acceptable": (0.35, 0.43),
            "Low": (0, 0.35),
            "Missing": (-2, -0.5),
            },
        "ilrmsd": {
            "High": (0, 1),
            "Medium": (1, 2),
            "Acceptable": (2, 3),
            "Near-acceptable": (3, 4),
            "Low": (4, 99999),
            "Missing": (-2, -0.5),
            },
        },
    }
PERFORMANCES_CLASSES = ALL_PERFORMANCES_CLASSES["protein"]

# Add color mapper
COLORS_MAPPER = {
    "High": "darkgreen",
    "Medium": "lightgreen",
    "Acceptable": "lightblue",
    "Near-acceptable": "gainsboro",
    "Low": "white",
    "Missing": "dimgrey",
    }

# Performance order
PERF_ORDER = (
    "High",
    "Medium",
    "Acceptable",
    "Near-acceptable",
    "Low",
    "Missing",
    )
# DPI of the generated figures
DPI = 400


####################
# DEFINE FUNCTIONS #
####################
def gen_graph(
        ax: plt.Axes,
        high: list,
        med: list,
        acc: list,
        nacc: list,
        low: list,
        miss: list,
        top: list,
        width: float = 0.5,
        percentage: bool = True,
        ) -> None:
    """Plot a barplot on the provided axis `ax`.

    Parameters
    ----------
    ax : `matplotlib.pyplot.Axes`
        The axis on which to draw the plot.
    high : list
        List containing number of `high performances` models
        for each threshold in `top`.
    med : list
        List containing number of `medium performances` models
        for each threshold in `top`.
    acc : list
        List containing number of `acceptable performances` models
        for each threshold in `top`.
    nacc : list
        List containing number of `near acceptable performances` models
        for each threshold in `top`.
    low : list
        List containing number of `low performances` models
        for each threshold in `top`.
    miss : list
        List containing number of missing model data
        for each threshold in `top`.
    top : list
        List of number of entries take into consideration.
    width : float
        Width of the bar to draw.
    percentage : bool
        If true, number of entries are converted into % sucess
    """
    # Performances mapper
    performances = {
        "High": high,
        "Medium": med,
        "Acceptable": acc,
        "Near-acceptable": nacc,
        "Low": low,
        "Missing": miss,
        }
    if percentage:
        # Compute total at each position
        indices_total: dict[int, int] = {}
        for label, counts in performances.items():
            for i, val in enumerate(counts):
                total = indices_total.setdefault(i, 0)
                indices_total[i] = total + val
        # Compute percentages
        percentage_perfs: dict[str, list[float]] = {}
        for label, counts in performances.items():
            for ind, val in enumerate(counts):
                try:
                    percent = 100 * val / indices_total[ind]
                except ZeroDivisionError:
                    percent = 0
                finally:
                    precent_list = percentage_perfs.setdefault(label, [])
                    precent_list.append(percent)
        performances = percentage_perfs
    # X labels
    tops = [f'Top{v}' for v in top]
    # initialize first bottom values with 0s
    bottom = np.zeros(len(high))

    # Loop over performances
    for label in PERF_ORDER:
        # point performances data
        perfs = performances[label]
        # draw bars
        ax.bar(
            tops,
            perfs,
            width,
            label=label,
            bottom=bottom,
            color=COLORS_MAPPER[label],
            )
        # increment bottom value
        bottom += perfs
    # New labels for percentage specific displaying
    if percentage:
        yticks = [0, 25, 50, 75, 100]
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticks)
        # Draw horizontal lines for better reading
        xlims = ax.get_xlim()
        xstart = np.floor(xlims[0])
        xend = np.ceil(xlims[1])
        for yposition in yticks[1:-1]:
            ax.plot(
                [xstart, xend],
                [yposition, yposition],
                linestyle="dashed",
                color="gray",
                alpha=0.7,
                )
    # Orient X labels
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
    ylabel = "Nb. entries" if not percentage else "% success rate"
    ax.set_ylabel(ylabel)


def clear_plt() -> None:
    """Clear all previous instances/data generated by matplotlib."""
    plt.gca()
    plt.cla()
    plt.clf()


def gen_violin(
        ax: plt.Axes,
        perf_data: list,
        labels: list,
        metric: str = "",
        ) -> None:
    """Draw a violinplot on the axis.

    inspired from:
    https://matplotlib.org/stable/gallery/statistics/customized_violin.html

    Parameters
    ----------
    ax : `matplotlib.pyplot.Axes`
        The axis on which to draw the plot.
    perf_data : list
        List of performances values.
    labels : list
        List of labels (same order as `perf_data`).
    """
    # Draw it
    parts = ax.violinplot(
        perf_data,
        showmeans=False,
        showmedians=False,
        showextrema=False,
        )

    # Get color ramp
    nbcolors = 10 if len(perf_data) <= 10 else 20
    colorramp = mpl.colormaps[f'tab{nbcolors}']

    # Modify colors
    for vi, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colorramp((vi + 0.5) / nbcolors))
        pc.set_edgecolor('black')
        pc.set_alpha(1)
    quartile1, medians, quartile3 = np.percentile(
        perf_data,
        [25, 50, 75],
        axis=1,
        )
    whiskers = np.array([
        adjacent_values(sorted_array, q1, q3)
        for sorted_array, q1, q3 in zip(perf_data, quartile1, quartile3)
        ])
    whiskers_min, whiskers_max = whiskers[:, 0], whiskers[:, 1]
    inds = np.arange(1, len(medians) + 1)
    ax.scatter(inds, medians, marker='_', color='white', s=30, zorder=3)
    ax.vlines(inds, quartile1, quartile3, color='k', linestyle='-', lw=5)
    ax.vlines(inds, whiskers_min, whiskers_max, color='k', linestyle='-', lw=1)
    ax.set_ylabel(metric)

    # Set labels
    if labels:
        ax.set_xticks(list(range(1, len(labels) + 1)))
        ax.set_xticklabels(
            labels,
            rotation=40,
            ha='right',
            rotation_mode='anchor',
            )


def adjacent_values(
        vals: list[float],
        q1: float,
        q3: float,
        ) -> tuple[float, float]:
    """Find adjacent values.

    Inspired from:
    https://matplotlib.org/stable/gallery/statistics/customized_violin.html

    Parameters
    ----------
    vals : list
        List of values
    q1 : float
        Value of the first quartil
    q3 : float
        Value of the 3rd quartil

    Return
    ------
    lower_adjacent_value : float
        Closest true value under q1
    upper_adjacent_value : float
        Closest true value above q3
    """
    # Finds closest true value above q3
    upper_adjacent_value = q3 + (q3 - q1) * 1.5
    upper_adjacent_value = np.clip(upper_adjacent_value, q3, vals[-1])
    # Find closest true value under q1
    lower_adjacent_value = q1 - (q3 - q1) * 1.5
    lower_adjacent_value = np.clip(lower_adjacent_value, vals[0], q1)
    return lower_adjacent_value, upper_adjacent_value


def stage_name(cname: str) -> str:
    """Try to return the user defined stage name, or return default.

    Parameters
    ----------
    cname : str
        Index of the caprieval stage

    Returns
    -------
    name : str
        Name of the stage
    """
    try:
        name = CAPRIEVAL_STEPS[cname]
    except KeyError:
        name = f"{cname}_caprieval"
    return name


def gen_full_comparison_violins(
        scenars_perfs: dict,
        basepath: str = "./",
        title: str = "",
        metric: str = "",
        progress: bool = True,
        ) -> None:
    """Combine all scenarios caprieval within same plot.

    Parameters
    ----------
    scenars_perfs : dict
        Dictionary of all scenario stages performances.
    basepath : str
        Basepath where to write plot.
    title : str
        Title of the figure.
    """
    # Clear pervious instances of matplotlib
    clear_plt()
    # Compute number of rows (scenarios)
    scenars_order = sorted(scenars_perfs)
    nb_scenar = len(scenars_order)
    # Compute number of colums (capri steps)
    steps_order = sorted(scenars_perfs[scenars_order[0]])
    nb_steps = len(steps_order)
    # Get number of threshodls
    tops_order = sorted(
        scenars_perfs[scenars_order[0]][steps_order[0]]['values'],
        )
    nb_thresh = len(tops_order)
    # Compute total number of plots
    total_plots = nb_thresh * nb_steps

    # Initate figures / axis
    fig, axes = plt.subplots(
        figsize=((nb_steps * 4) + 1, (nb_thresh * 3) + 1),
        nrows=nb_thresh,
        ncols=nb_steps,
        sharey=True,
        sharex=True,
        squeeze=0,  # squeeze=0 allows to always return a 2d array
        )

    processed = 0
    # Loop over thresholds
    for ri, topx in enumerate(tops_order):
        # Loop over caprieval steps
        for ci, cname in enumerate(steps_order):
            processed += 1
            if progress:
                print(f"{100 * processed / total_plots:>6.2f} %", end="\r")
            # Point axis
            ax = axes[ri][ci]
            # Build sub-dt dict
            perf_data = [
                sorted(scenars_perfs[scenar][cname]['values'][topx])
                for scenar in scenars_order
                ]
            # Set labels on last row only
            labels = None
            if ri + 1 == nb_thresh:
                labels = [so.replace('scenario-', '') for so in scenars_order]
            # Write bars
            gen_violin(
                ax,
                perf_data,
                labels,
                metric=metric,
                )

    # Add columns titles
    pad = 5
    for ax, cname in zip(axes[0], steps_order):
        # Annotate column
        ax.annotate(
            stage_name(cname),
            xy=(0.5, 1),
            xytext=(0, pad),
            xycoords='axes fraction',
            textcoords='offset points',
            size='large',
            ha='center',
            va='baseline',
            )
    # Add rows titles
    for ax, topx in zip(axes[:, 0], tops_order):
        ax.annotate(
            f'Top {topx}',
            xy=(0, 0.5),
            xytext=(-ax.yaxis.labelpad - pad, 0),
            xycoords=ax.yaxis.label,
            textcoords='offset points',
            size='large',
            ha='right',
            va='center',
            )

    # Add figure title
    fig.suptitle(title, fontsize=16)

    # Get color ramp
    nbcolors = 10 if nb_scenar <= 10 else 20
    colorramp = mpl.colormaps[f'tab{nbcolors}']
    # Add bars legend
    fig.legend(
        [
            mpatches.FancyBboxPatch(
                (-0.025, -0.05), 0.05, 0.1, ec="none",
                boxstyle=mpatches.BoxStyle("Round", pad=0.02),
                color=colorramp((si + 0.5) / nbcolors),
                )
            for si, _perfclass in enumerate(scenars_order)
            ],
        [so.replace('scenario-', '') for so in scenars_order],
        loc='outside lower center',
        ncols=4,
        title="Scenarios",
        )

    plt.gca().set_ylim(bottom=0)

    # Adjust border to let annotations fit inside graph. The left margin
    # needs to hold both the y-axis label and the row-title annotations
    # (drawn at a small fixed point-offset from it). That fixed offset
    # becomes proportionally huge on narrow figures (e.g. a single caprieval
    # stage -> nb_steps=1), so scale the left fraction to preserve roughly
    # a constant absolute margin instead of leaving it fixed.
    fig_width_in = fig.get_size_inches()[0]
    left_margin = max(0.08, min(0.35, 1.3 / fig_width_in))
    fig.subplots_adjust(left=left_margin, top=0.95, bottom=0.12, right=0.98)

    # save figure
    plt.savefig(
        f"{basepath}_violins.png",
        format='png',
        dpi=DPI,
        bbox_inches='tight',
        pad_inches=0.3,
        )
    return


def gen_full_comparison_melquiplots(
        scenars_perfs: dict,
        perf_dtype: str = "irmsd",
        basepath: str = "./",
        progress: bool = True,
        ) -> str:
    """Generate multiple melquiplots for each scenario.

    Parameters
    ----------
    scenars_perfs : dict
        Dict containing performances for each scenario.
    perf_dtype : str, optional
        Model quality metric to use, by default "irmsd"
    title : str, optional
        Prefix to give to archive, by default "benchmark_melquis"
    basepath : str, optional
        Where to write the files, by default "./"

    Returns
    -------
    archive_path : str
        Path to the generated archive.zip
    """
    # Clear pervious instances of matplotlib
    clear_plt()

    # Set progression variables
    all_generated_melquis: list[str] = []
    processed = 0
    total_plots = len(scenars_perfs)

    # Loop over scenarios
    for scenar_name, scenar_perfs in scenars_perfs.items():
        processed += 1
        if progress:
            print(f"{100 * processed / total_plots:>6.2f} %", end="\r")
        # Generate melquiplot for this scenario
        scenar_melqui_path = make_scenar_melquiplots(
            scenar_perfs,
            perf_dtype=perf_dtype,
            title=scenar_name,
            basepath=basepath,
            )
        all_generated_melquis.append(scenar_melqui_path)

    # Generate archive of melqui plots
    archive_path = Path(f"{basepath}_melquiplots.zip")
    path = archive_path.parent
    archive_name = archive_path.name
    initdir = os.getcwd()
    os.chdir(path)
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for figure in all_generated_melquis:
            zipf.write(Path(figure).name)
    os.chdir(initdir)

    # Remove all original files
    for generated_melqui in all_generated_melquis:
        os.remove(generated_melqui)

    # Return archive path
    return archive_path


def make_scenar_melquiplots(
        scenar_perfs: dict,
        perf_dtype: str = "irmsd",
        title: str = "melquiplot",
        basepath: str = "./",
        ) -> str:
    """Generate multiples melquiplots for each Caprieval steps of a scenario.

    Parameters
    ----------
    scenar_perfs : dict
        Dict containing performances of a scenario.
    perf_dtype : str, optional
        Model quality metric to use, by default "irmsd"
    title : str, optional
        Title to the figure, by default "melquiplot"
    basepath : str, optional
        Where to write the files, by default "./"

    Returns
    -------
    figpath : str
        Path to the generated figure.
    """
    # Count nb_steps and entries
    steps = sorted(scenar_perfs)
    nb_rows = len(steps)
    nb_entries = len(scenar_perfs[steps[0]].keys())
    dtype_perf_classes = PERFORMANCES_CLASSES[perf_dtype]
    # Initate figures / axis
    fig, axes = plt.subplots(
        figsize=((nb_entries * 1) + 1, (nb_rows * 5) + 3),
        nrows=nb_rows,
        ncols=1,
        )
    if not isinstance(axes, np.ndarray):
        axes = [axes]

    # Loop over stages
    for si, (stage, stage_perfs) in enumerate(scenar_perfs.items()):
        # Point axis
        ax = axes[si]
        # Draw a melquiplot on this axis
        melquiplot(ax, stage_perfs, width=min(1, 5 / nb_entries))
        # Add title to graph
        ax.annotate(
            stage_name(stage),
            xy=(0.5, 1),
            xytext=(0, 5),
            xycoords='axes fraction',
            textcoords='offset points',
            size='large',
            ha='center',
            va='baseline',
            )
    # Add figure title
    fig.suptitle(title, fontsize=16)
    # Add Legend
    legend_data = [
        (
            plt.Rectangle((0, 0), 1, 1, fc=COLORS_MAPPER[perfclass]),
            rf'{perfclass} | {dtype_perf_classes[perfclass][0]} <= {perf_dtype.upper()} < {dtype_perf_classes[perfclass][1]}$\AA$',  # noqa : E501
            )
        for perfclass in PERF_ORDER
        ]
    legend_proxies, legend_labels = zip(*legend_data)
    # Add bars legend
    fig.legend(
        legend_proxies,
        legend_labels,
        loc='outside lower center',
        ncols=len(PERF_ORDER),
        title="performance classes",
        )

    # adjust border to let annotations fit inside graph
    fig.subplots_adjust(left=0.02, top=0.95, bottom=0.06, right=0.98)

    # save figure
    figpath = f"{basepath}_{title}_melquiplot.png"
    plt.savefig(
        figpath,
        format='png',
        dpi=DPI,
        bbox_inches='tight',
        pad_inches=0.3,
        )
    return figpath


def melquiplot(
        ax: plt.Axes,
        pdb_perfs: dict[str, list[str]],
        width: float = 0.3,
        ) -> None:
    """Draw a melquiplot on an sub-figure with provided input data.

    Parameters
    ----------
    ax : plt.Axes
        The axis on which to draw the Melquiplot
    pdb_perfs : dict[str, list[str]]
        Performances for each entry at a give stage.
    """
    width = 0.1
    max_stack_y = 0
    pdb_labels = sorted(pdb_perfs)
    stack_h_labels_pos: list[float] = []
    # Loop over each input entry
    for entry_index, pdb in enumerate(pdb_labels, start=0):
        # Point data
        perfs = pdb_perfs[pdb][MELQUIPLOT_NB_ENTRIES]
        x_coord = entry_index * width
        y_coord = 0
        # Loop over perfs
        for perf_label in perfs:
            # Draw a bar
            ax.bar(
                x_coord,
                2,
                align="edge",
                bottom=y_coord,
                color=COLORS_MAPPER[perf_label],
                width=width * 0.98,
                edgecolor='none',
                linewidth=0,
                )
            y_coord += 1

        max_stack_y = max(max_stack_y, y_coord)
        stack_h_labels_pos.append(x_coord + (width / 2))

    # Aesthetics
    ax.set_xlim((0, len(pdb_labels) * width))
    ax.set_ylim((0, max_stack_y))
    ax.set_ylabel('Energy Score Ranking (lower is better)')
    ax.set_xticks(stack_h_labels_pos)
    ax.set_xticklabels(pdb_labels, rotation=45, fontsize='small')
    ax.xaxis.set_ticks_position('none')


def melquiplot_original(
        ax: plt.Axes,
        pdb_perfs: dict[str, list[str]],
        ) -> None:
    """Draw a melquiplot on an sub-figure with provided input data.

    Parameters
    ----------
    ax : plt.Axes
        The axis on which to draw the Melquiplot
    pdb_perfs : dict[str, list[str]]
        Performances for each entry at a give stage.
    """
    max_stack_v = 0
    pdb_labels = sorted(pdb_perfs)
    stack_h_labels_pos: list[float] = []
    # Loop over each input entry
    for entry_index, pdb in enumerate(pdb_labels, start=1):
        # Point data
        perfs = pdb_perfs[pdb][MELQUIPLOT_NB_ENTRIES]
        stack_v = 0
        # Loop over perfs
        for perf_label in perfs:
            # Draw a bar
            ax.bar(
                entry_index - 0.5,
                2,
                bottom=stack_v,
                color=COLORS_MAPPER[perf_label],
                width=0.99,
                edgecolor='none',
                linewidth=0,
                )
            stack_v += 1

        max_stack_v = max(max_stack_v, stack_v)
        stack_h_labels_pos.append(entry_index - 0.501)

    # Aesthetics
    ax.set_xlim((0.05, len(pdb_labels) + 0.05))
    ax.set_ylim((0, max_stack_v))
    ax.set_ylabel('Energy Score Ranking (lower is better)')
    ax.set_xticks(stack_h_labels_pos)
    ax.set_xticklabels(pdb_labels, rotation=45, fontsize='small')
    ax.xaxis.set_ticks_position('none')


def gen_full_comparison_barplots(
        scenars_perfs: dict,
        basepath: str = "./",
        title: str = "",
        progress: bool = True,
        no_percentage: bool = False,
        ) -> None:
    """Combine all scenarios caprieval within same plot.

    Parameters
    ----------
    scenars_perfs : dict
        Dictionary of all scenario stages performances.
    basepath : str
        Basepath where to write plot.
    title : str
        Title of the figure.
    """
    # Clear pervious instances of matplotlib
    clear_plt()
    # Compute number of rows
    rows_order = sorted(scenars_perfs)
    nb_rows = len(rows_order)
    # Compute number of colums
    cols_order = sorted(scenars_perfs[rows_order[0]])
    nb_cols = len(cols_order)
    # Compute total number of plots
    total_plots = nb_rows * nb_cols
    processed = 0

    # Initate figures / axis
    fig, axes = plt.subplots(
        figsize=((nb_cols * 4) + 1, (nb_rows * 3) + 4),
        nrows=nb_rows, ncols=nb_cols,
        )

    # Loop over rows
    for ri, rname in enumerate(rows_order):
        # Point row axe(s)
        if len(rows_order) == 1:
            axr = axes
        else:
            axr = axes[ri]
        for ci, cname in enumerate(cols_order):
            # Display progression
            processed += 1
            if progress:
                print(f"{100 * processed / total_plots:>6.2f} %", end="\r")
            # Point column axe(s)
            if len(cols_order) == 1:
                ax = axr
            else:
                ax = axr[ci]
            # Point data
            perf_data = scenars_perfs[rname][cname]['classes']
            # Get sorted entreis
            topx = sorted(perf_data)
            # attribute perf classes at each topX model
            high = [perf_data[top]['High'] for top in topx]
            med = [perf_data[top]['Medium'] for top in topx]
            acc = [perf_data[top]['Acceptable'] for top in topx]
            nacc = [perf_data[top]['Near-acceptable'] for top in topx]
            low = [perf_data[top]['Low'] for top in topx]
            miss = [perf_data[top]['Missing'] for top in topx]
            # Write bars
            gen_graph(
                ax,
                high,
                med,
                acc,
                nacc,
                low,
                miss,
                topx,
                percentage=not no_percentage,
                )

    # Set padding between two plots
    pad = 5  # NOTE: nicely hardcoded !

    # Search for first row
    if len(rows_order) == 1:
        first_row = axes
    else:
        first_row = axes[0]
    if not isinstance(first_row, np.ndarray):
        first_row = [first_row]

    # Add columns titles
    for ax, cname in zip(first_row, cols_order):
        # Add column name
        ax.annotate(
            stage_name(cname),
            xy=(0.5, 1),
            xytext=(0, pad),
            xycoords='axes fraction',
            textcoords='offset points',
            size='large',
            ha='center',
            va='baseline',
            )

    # Find all first row columns
    if len(rows_order) == 1:
        axrows = [axes]
    else:
        axrows = axes
    if len(cols_order) == 1:
        axrows_firstcols = axrows
    else:
        axrows_firstcols = [ax[0] for ax in axrows]

    # Add rows titles
    for ax, rname in zip(axrows_firstcols, rows_order):
        ax.annotate(
            rname.replace('scenario-', ''),
            xy=(0, 0.5),
            xytext=(-ax.yaxis.labelpad - pad, 0),
            xycoords=ax.yaxis.label,
            textcoords='offset points',
            size='large',
            ha='right',
            va='center',
            )

    # Add figure title
    fig.suptitle(title, fontsize=16)

    # Add bars legend
    fig.legend(
        [mpatches.FancyBboxPatch(
            (-0.025, -0.05), 0.05, 0.1, ec="none",
            boxstyle=mpatches.BoxStyle("Round", pad=0.02),
            color=COLORS_MAPPER[perfclass],
            )
         for perfclass in PERF_ORDER],
        PERF_ORDER,
        loc='outside lower center',
        ncols=len(PERF_ORDER),
        title="performance classes",
        )

    # Adjust border to let annotations fit inside graph. Same reasoning as
    # in `gen_full_comparison_violins`: scale the left margin so a narrow
    # figure (e.g. a single caprieval stage -> nb_cols=1) still has enough
    # absolute room for the y-axis label and row-title annotations, instead
    # of clipping them.
    fig_width_in = fig.get_size_inches()[0]
    left_margin = max(0.15, min(0.35, 1.3 / fig_width_in))
    fig.subplots_adjust(left=left_margin, top=0.9, bottom=0.15, right=0.98)

    # Save figure
    plt.savefig(
        f"{basepath}_capribarpolots.png",
        format='png',
        dpi=DPI,
        bbox_inches='tight',
        pad_inches=0.3,
        )
    return


def get_pdb_entries(basepath: str) -> list:
    """Retrieve list of immediate subdirectory names.

    Generic directory lister -- reused both to list scenario names at the
    top level of the benchmark directory, and to list PDBid/target names
    inside each scenario directory. Kept its original name for API
    stability, even though it's no longer PDBid-specific.

    Parameters
    ----------
    basepath : str
        Path to a directory whose immediate subdirectories should be listed.

    Return
    ------
    entries : list
        List of subdirectory names found directly under `basepath`.
    """
    entries = [
        pdbid_path.stem
        for pdbid_path in Path(basepath).glob("*/")
        if pdbid_path.is_dir()
        ]
    return entries


def _find_scenario_data_dir(
        candidate_path: str,
        _max_depth: int = 3,
        ) -> Optional[str]:
    """Find the directory that actually holds `<PDBid>/run1/` entries.

    Checks whether `candidate_path` directly contains one or more
    ``<PDBid>/run1/`` subdirectories. If not, and `candidate_path` has
    exactly one subdirectory, recurses into that single subdirectory (up to
    `_max_depth` levels) to transparently see through extra wrapper
    directories -- e.g. a scenario directory that ended up nested one level
    too deep, such as ``<scenario>/<scenario>/<PDBid>/run1/`` instead of
    ``<scenario>/<PDBid>/run1/``. Only drills down when there is a single,
    unambiguous subdirectory to descend into, so it won't misfire on
    directories that hold unrelated clutter (e.g. output files).

    Parameters
    ----------
    candidate_path : str
        Directory to inspect (should end with '/').
    _max_depth : int
        Maximum number of wrapper levels to look through.

    Return
    ------
    resolved : Optional[str]
        Path to the directory directly containing `<PDBid>/run1/` entries,
        or None if none could be found within `_max_depth` levels.
    """
    for entry in Path(candidate_path).glob("*/"):
        if entry.is_dir() and (entry / "run1").is_dir():
            return candidate_path
    if _max_depth <= 0:
        return None
    subdirs = [entry for entry in Path(candidate_path).glob("*/") if entry.is_dir()]
    if len(subdirs) == 1:
        return _find_scenario_data_dir(
            f"{subdirs[0]}/",
            _max_depth=_max_depth - 1,
            )
    return None


def _looks_like_scenario_dir(scenario_path: str) -> bool:
    """Heuristic check for whether a directory is a real scenario dir.

    A genuine scenario directory (as produced by haddock-runner) contains
    at least one ``<PDBid>/run1/`` subdirectory, possibly behind a single
    extra wrapper level (see `_find_scenario_data_dir`). This is used to
    filter out unrelated top-level clutter that can end up alongside the
    scenario directories -- most commonly a previous analysis output
    directory (e.g. `Analysis/`) left inside the benchmark directory, or
    stray/hidden directories -- so they aren't mistaken for scenarios.

    Parameters
    ----------
    scenario_path : str
        Candidate scenario directory path (should end with '/').

    Return
    ------
    bool
        True if a `<PDBid>/run1/` pattern is found inside `scenario_path`,
        directly or behind a single unambiguous wrapper level.
    """
    return _find_scenario_data_dir(scenario_path) is not None


def _resolve_scenario_dir(basepath: str, scenario: str) -> str:
    """Resolve a scenario name to its actual data directory on disk.

    Normally this is simply ``{basepath}{scenario}/``. However, some
    benchmark directories end up with an extra wrapper level in between
    (e.g. produced by manual reorganisation), such as::

        <basepath>/<scenario>/<scenario_or_other_wrapper>/<PDBid>/run1/

    instead of the expected::

        <basepath>/<scenario>/<PDBid>/run1/

    This transparently drills down through such wrapper levels via
    `_find_scenario_data_dir`.

    Parameters
    ----------
    basepath : str
        Root directory containing scenario directories.
    scenario : str
        Scenario name.

    Return
    ------
    resolved : str
        Path to the directory that actually contains `<PDBid>/run1/`
        subdirectories for this scenario (or the original, unresolved
        candidate if no unambiguous wrapper level could be found -- in
        which case downstream existence checks will raise a clear error).
    """
    candidate = f"{basepath}{scenario}/"
    resolved = _find_scenario_data_dir(candidate)
    return resolved if resolved is not None else candidate


def get_scenario_entries(basepath: str) -> list:
    """Retrieve list of scenario directory names at the top of `basepath`.

    Like `get_pdb_entries`, but filters out any top-level directory that
    doesn't actually look like a scenario directory (see
    `_looks_like_scenario_dir`). This protects against stray directories
    such as a leftover `Analysis/` output folder, hidden directories, etc.
    being mistaken for scenarios.

    Parameters
    ----------
    basepath : str
        Path to the benchmark directory to analyse.

    Return
    ------
    scenarios : list
        List of directory names under `basepath` that look like real
        scenario directories.
    """
    scenarios = [
        name for name in get_pdb_entries(basepath)
        if _looks_like_scenario_dir(f'{basepath}{name}/')
        ]
    return scenarios


def scenario_name_2_threshold(scenar_name: str) -> float:
    """Gather threshold value from scenario name.

    NOTE: function used for CPORT-ARCTIC3D-BM5 benchmark

    Parameters
    ----------
    scenar_name : str
        Name of a scenario.

    Return
    ------
    threshold : float
        CPORT threshold value used in this scenario.
    """
    # Get last part of scenario name
    str_thresh = scenar_name.split('-')[-1]
    # Replace underscore by a dot
    dot_thresh = str_thresh.replace('_', '.')
    # Cast it to float
    threshold = float(dot_thresh)
    return threshold


def get_caprieval_stages(
        basepath: str,
        read_from_archive: bool = False,
        ) -> list[str]:
    """Retrieve all caprieval stages inside a haddock3 run.

    Parameters
    ----------
    basepath : str
        Path to a haddock3 run directory `rundir`.
    read_from_archive : bool, optional
        When set to True, performs the search of capri_ss.tsv files from the
        analysis archive instead of the run directory, by default False

    Return
    ------
    caprieval_stages : list
        List of caprieval module indexes
    """
    if not read_from_archive:
        caprieval_paths = glob.glob(f'{basepath}*caprieval/')
    else:
        # Read members from the archive and retrieve capri_ss file paths
        with tarfile.open(basepath, "r:gz") as tarin:
            caprieval_paths = [
                fp.name for fp in tarin.getmembers()
                if re.search(r"\d+_caprieval_analysis\/capri_ss\.tsv", fp.name)
            ]
    # Gather only the stages IDs of the caprieval modules
    caprieval_stages = [
        hd3_module_2_stage(caprip.split('/')[-2])
        for caprip in caprieval_paths
        ]
    return caprieval_stages


def hd3_module_2_stage(indexed_modulename: str) -> str:
    """Split a haddock3 module name and retrieve it id.

    Parameters
    ----------
    indexed_modulename : str
        Directory name of an indexed haddock3 module name.


    Return
    ------
    stage : str
        Index of the haddock3 module.
    """
    stage = indexed_modulename.split('_')[0]
    return stage


def _make_run_path(scenario_basepath: str, pdbid: str) -> str:
    """Return the haddock3 run directory path.

    Parameters
    ----------
    scenario_basepath : str
        Path to the scenario's own directory (already resolved -- may be
        ``{basepath}{scenario}/`` in multi-scenario mode, or just
        ``{basepath}`` itself in single-scenario mode).
    pdbid : str
        Target/PDBid name.
    """
    return f"{scenario_basepath}{pdbid}/run1/"


def _make_archive_path(scenario_basepath: str, pdbid: str) -> str:
    """Return the haddock3 run analysis archive path.

    Parameters
    ----------
    scenario_basepath : str
        Path to the scenario's own directory (already resolved).
    pdbid : str
        Target/PDBid name.
    """
    return f"{scenario_basepath}{pdbid}/run1_analysis.tgz"


def map_data(
        basepath: str,
        subset_scenarios: Optional[list[str]] = None,
        read_from_archive: bool = False,
        ) -> dict[str, dict[str, dict[str, dict[str, Union[str, list[str, str]]]]]]:
    """Map data in one analysis dict to accessit easily.

    Expects the benchmark directory to be laid out as produced by
    haddock-runner::

        <basepath>/<scenario_name>/<PDBid>/run1/<stage>_caprieval/capri_ss.tsv

    i.e. scenario is the outer directory and PDBid the inner one. This
    holds whether `basepath` contains a single scenario directory or
    several -- there is no special-casing, the code below just handles
    however many scenario directories are found.

    Parameters
    ----------
    basepath : str
        Path to the root directory containing one or more scenario
        directories.
    subset_scenarios : Optional[list[str]]
        List of scenario names on which to perform the analysis.
    read_from_archive : bool, optional
        When set to True, performs the search of capri_ss.tsv files from the
        analysis archive instead of the run directory, by default False

    Return
    ------
    dtmap : dict[str, dict[str, dict[str, dict[str, str]]]]
        Dictionary mapping scenarios/pdbids to caprieval tsv paths.
        Structure:
        {"scenario_id":
            {"caprieval_stage":
                {"PDBid":
                    {"complexe_id": "path/to/caprieval_ss.tsv",
                     ...,
                    }
                }
            }
        }
    """
    # Initiate mapper
    dtmap: dict[str, dict[str, dict[str, dict[str, Union[str, list[str, str]]]]]] = {}

    # `basepath` is always the root containing one or more scenario
    # directories -- this naturally handles both a single scenario and
    # multiple scenarios without any special-casing, since the loops below
    # just iterate over however many scenarios are found.
    if subset_scenarios:
        all_scenarios = subset_scenarios
    else:
        # Scenarios are the top-level directories of basepath (filtered to
        # exclude stray/unrelated directories, e.g. a leftover `Analysis/`
        # output folder sitting inside the benchmark directory).
        all_scenarios = sorted(get_scenario_entries(basepath))
    assert all_scenarios, (
        f"[ERROR] no scenario directories found directly under `{basepath}`. "
        "Expected layout is `<basepath>/<scenario_name>/<PDBid>/run1/` -- "
        "this applies whether there is one scenario or several."
        )

    def scenario_dir(scenario: str) -> str:
        """Resolve a scenario name to its actual directory on disk."""
        return _resolve_scenario_dir(basepath, scenario)

    # pdbids are gathered per scenario, deduplicated across all scenarios.
    pdbids_set: set[str] = set()
    for scenario in all_scenarios:
        pdbids_set.update(get_pdb_entries(scenario_dir(scenario)))
    pdbids = sorted(pdbids_set)
    assert pdbids, (
        f"[ERROR] no target/PDBid directories found under any scenario in "
        f"`{basepath}`."
        )

    # Make sure all pdbs have all scenarios
    for scenario in all_scenarios:
        for pdbid in pdbids:
            # Default behavior
            if not read_from_archive:
                scenar_rundir = _make_run_path(scenario_dir(scenario), pdbid)
                assert os.path.exists(scenar_rundir), \
                    (
                        f"[ERROR] could not find scenario `{scenario}` "
                        f"directory for entry `{pdbid}` at: {scenar_rundir}"
                    )
            # Case where we need to search data in the archive
            else:
                analysis_archive = _make_archive_path(scenario_dir(scenario), pdbid)
                assert os.path.exists(analysis_archive), \
                    (
                        f"[ERROR] could not find scenario `{scenario}` "
                        f"archive for entry `{pdbid}` at: {analysis_archive}"
                    )

    all_caprieval_stages = []
    # Add scenario data to data maper
    for scenario in all_scenarios:
        # Loop over pdb ids
        for pdbid in pdbids:
            if not read_from_archive:
                # Generate scenario basepath
                scenario_bp = _make_run_path(scenario_dir(scenario), pdbid)
            else:
                scenario_bp = _make_archive_path(scenario_dir(scenario), pdbid)
            # Retrieve caprieval stages
            caprieval_stages = get_caprieval_stages(
                scenario_bp,
                read_from_archive=read_from_archive,
                )
            all_caprieval_stages += caprieval_stages
    all_caprieval_stages = sorted(list(set(all_caprieval_stages)))
    assert all_caprieval_stages, (
        f"[ERROR] no caprieval stages found anywhere under `{basepath}`."
        )

    # Make sure all stages are computed for all pdb in all scenarios...
    for scenario in all_scenarios:
        for pdbid in pdbids:
            archive_path = _make_archive_path(scenario_dir(scenario), pdbid)
            if read_from_archive:
                tararchive = tarfile.open(archive_path, "r:gz")
            for stage in all_caprieval_stages:
                if not read_from_archive:
                    # Build caprieval tsv filepath
                    caprieval_tsv_path = f"{_make_run_path(scenario_dir(scenario), pdbid)}{stage}_caprieval/capri_ss.tsv"  # noqa : E501
                    assert os.path.exists(caprieval_tsv_path), \
                        (
                            f"[ERROR] could not access CAPRIEVAL results file at: "
                            f"{caprieval_tsv_path}\n- Stage {stage}\n- Scenario "
                            f"`{scenario}`\n- Target `{pdbid}`"
                        )
                else:
                    expected_capriss_fpath = f"run1_analysis/{stage}_caprieval_analysis/capri_ss.tsv"
                    found_file = False
                    try:
                        _tarinfo = tararchive.getmember(expected_capriss_fpath)
                        found_file = True
                    except KeyError:
                        assert found_file == True, \
                            (
                            f"[ERROR] could not access CAPRIEVAL results file at: "
                            f"{expected_capriss_fpath}\n"
                            f"  - Stage {stage}\n"
                            f"  - Scenario `{scenario}`\n"
                            f"  - Target `{pdbid}`"
                            )
            if read_from_archive:
                tararchive.close()

    # Gather all data
    for scenario in all_scenarios:
        dtmap[scenario] = {}
        for stage in all_caprieval_stages:
            dtmap[scenario][stage] = {}
            for pdbid in pdbids:
                if not read_from_archive:
                    # Build caprieval tsv filepath
                    caprieval_tsv_path = f"{_make_run_path(scenario_dir(scenario), pdbid)}{stage}_caprieval/capri_ss.tsv"  # noqa : E501
                else:
                    caprieval_tsv_path = [
                        _make_archive_path(scenario_dir(scenario), pdbid),
                        f"run1_analysis/{stage}_caprieval_analysis/capri_ss.tsv",
                    ]
                # Hold datapath
                dtmap[scenario][stage][pdbid] = caprieval_tsv_path

    return dtmap


def analyse_scenario(
        scenario_dt: dict,
        _entries_thresholds: list,
        sort_dtype: str = "haddock-score",
        perf_dtype: str = "irmsd",
        read_from_archive: bool = False,
        ) -> tuple[dict[str, dict], dict[str, dict]]:
    """Process the analysis of a scenario.

    Parameters
    ----------
    scenario_dt : dict
        Dictionary of scenario data containing
        - as keys; index of the caprieval stage
        - as values; Dictionary mapping pdbid to caprieval files
    entries_thresholds : list
        List of entries theshold to take into consideration.
    sort_dtype : str
        Key used to sort data.
    perf_dtype : str
        Key used to define performance.
    read_from_archive : bool, optional
        When set to True, performs the search of capri_ss.tsv files from the
        analysis archive instead of the run directory, by default False

    Return
    ------
    scenario_stages_perfs : dict
        Dictionary of stage performances, containing
        - as keys; index of the caprieval stage
        - as values; best performing values and classes at each threshold
    """
    if not MELQUIPLOT_NB_ENTRIES in _entries_thresholds:
        entries_thresholds = [e for e in _entries_thresholds]
        entries_thresholds.append(MELQUIPLOT_NB_ENTRIES)
    else:
        entries_thresholds = _entries_thresholds

    # Initiate all stages performances holder
    scenario_stages_perfs = {}
    scenario_stages_pdb_perfs = {}
    # Loop over caprieval data
    for stage, stage_perfs_mapper in scenario_dt.items():
        # Initiate stage performance holder
        pdb_best_perfs = {}
        pdb_perfs = {}
        # Loop over pdbs
        for pdbid, caprieval_filepath in stage_perfs_mapper.items():
            # Gather performances
            best_perfs_h, top_x_perfs = analyse_caprieval_performances(
                caprieval_filepath,
                entries_thresholds,
                sort_dtype=sort_dtype,
                perf_dtype=perf_dtype,
                read_from_archive=read_from_archive,
                )
            # Hold best performances
            pdb_best_perfs[pdbid] = best_perfs_h
            # Hold top X perf classes
            pdb_perfs[pdbid] = {
                topx: [perf_to_class(v, dtype=perf_dtype) for v in perfs]
                for topx, perfs in top_x_perfs.items()
                }

        # Summerize all pdb best performances
        stage_best_perfs = {
            n: [pdb_perf[n] for pdb_perf in pdb_best_perfs.values()]
            for n in entries_thresholds
            }
        # Transform performances values to classes
        stage_class_perfs = {
            n: perfs_to_classes(perfs, dtype=perf_dtype)
            for n, perfs in stage_best_perfs.items()
            }

        # Hold stage performances
        scenario_stages_perfs[stage] = {
            "values": stage_best_perfs,
            "classes": stage_class_perfs,
            }
        scenario_stages_pdb_perfs[stage] = pdb_perfs

    return scenario_stages_perfs, scenario_stages_pdb_perfs


def perfs_to_classes(
        perfs: list,
        dtype: str = "irmsd",
        ) -> dict:
    """Convert performances values into classes.

    Parameters
    ----------
    perfs : list
        List of performance values.
    dtype : str
        Type of the performance.

    Return
    ------
    perfs_classes : dict
        Dictionary holding
        - as keys; names of the classes
        - as values; number of entries falling in this classe
    """
    # Count classes in perfs
    perfs_classes_list = [
        perf_to_class(v, dtype=dtype)
        for v in perfs
        ]
    perfs_classes = {
        cls: perfs_classes_list.count(cls)
        for cls in PERFORMANCES_CLASSES[dtype].keys()
        }
    return perfs_classes


def perf_to_class(value: float, dtype: str = "irmsd") -> str:
    """Cast a performance value into a performance class.

    Parameters
    ----------
    value : float
        Performance value.
    dtype : str
        Name of the data type.

    Return
    ------
    cls : str
        Corresponding class
    """
    # Get dt types classes boundaries
    classes_dt_map = PERFORMANCES_CLASSES[dtype]
    # Get comparison function
    comparison_func = dtype_to_boundary_function(dtype)
    for cls, (lowb, highb) in classes_dt_map.items():
        if comparison_func(lowb, highb, value):
            return cls
    # In case it is not found, return "Missing"
    return PERF_ORDER[-1]


def dtype_to_boundary_function(dtype: str) -> Callable:
    """Get function to make a comparison between two boundaries.

    Parameters
    ----------
    dtype : str
        Name of the data type.

    Return
    ------
    _function : function
        Function used to make a comparison.
    """
    def _include_higher(lowb: float, highb: float, value: float) -> bool:
        return lowb < value <= highb
    def _include_lower(lowb: float, highb: float, value: float) -> bool:
        return lowb <= value < highb
    _function = _include_higher if get_reverse_bool(dtype) else _include_lower
    return _function


def analyse_caprieval_performances(
        capireval_fpath: Union[str, list[str, str]],
        entries_thresholds: list,
        sort_dtype: str = "haddock-score",
        perf_dtype: str = "irmsd",
        read_from_archive: bool = False,
        ) -> tuple[dict[int, float], dict[int, list[float]]]:
    """Analyse a CAPRIeval step performances.

    Parameters
    ----------
    capireval_fpath : Union[str, list[str, str]]
        Path to the caprival file to analyse.
    entries_thresholds : list
        List of entries theshold to take into consideration.
    sort_dtype : str
        Key used to sort data.
    perf_dtype : str
        Key used to define performance.
    read_from_archive : bool, optional
        When set to True, performs the search of capri_ss.tsv files from the
        analysis archive instead of the run directory, by default False

    Return
    ------
    best_perfs_h : dict
        Dictionary holder best performances at each threshold.
    """
    # Load caprieval data
    caprieval_data = load_caprieval_data(capireval_fpath, read_from_archive)
    # Sort entries by perf value
    sorted_complexes = sorted(
        caprieval_data,
        key=lambda k: caprieval_data[k][sort_dtype],
        reverse=get_reverse_bool(sort_dtype),
        )

    # Get performances taking into account increasing number of entries
    best_perfs_h = {
        nb_entries: best_perfs(
            caprieval_data,
            sorted_complexes,
            dtype=perf_dtype,
            n=nb_entries,
            )
        for nb_entries in entries_thresholds
        }
    # Gather top X performances
    top_x_perfs = {
        nb_entries: [
            caprieval_data[entry][perf_dtype]
            for entry in sorted_complexes[:nb_entries]
            ]
        for nb_entries in entries_thresholds
        }

    # Return performances
    return best_perfs_h, top_x_perfs


def best_perfs(
        caprieval_data: dict,
        order: list,
        dtype: str = 'irmsd',
        n: int = 1,
        tolerance: float = 6,
        ) -> float:
    """Obtain best performing value.

    Parameters
    ----------
    caprieval_data : dict
        Dictionary holding performances data for each complexes.
    order : list
        Ordered set of keys in `caprieval_data`.
    dtype : str
        Name of the performance key to take into consideration.
    n : int
        Number of entries to take into consideration.
    tolerance : float
        Percentage of tolerated difference between number of accessible
        entries `len(order)` and number of queried `n` entries.

    Return
    ------
    best_perfomance : float
        Best performing value.
    """
    # Check if length of order << n
    # if (len(order) + (len(order) * tolerance / 100)) < n:
    #     return -1

    # Obtain list of all performances
    all_perfs = [caprieval_data[entry][dtype] for entry in order[:n]]
    # Get best function
    best_function = dtype_to_best_function(dtype)
    # Get best performing value
    best_perfomance = best_function(all_perfs)
    return best_perfomance


def dtype_to_best_function(dtype: str) -> Callable:
    """Get best function.

    Parameters
    ----------
    dttype : str
        Name of the data type.

    Return
    ------
    _function : function
        Function used to identify best score within list of values.
    """
    _function = max if get_reverse_bool(dtype) else min
    return _function


def get_reverse_bool(dt_type: str) -> bool:
    """Check sorting order.

    Parameters
    ----------
    dt_type : str
        Name of the data type.

    Return
    ------
    _reversed : bool
        Weather or not the ordering should be reversed.
    """
    _reversed = True if dt_type in ('fnat', 'dockq', ) else False
    return _reversed


def load_caprieval_data(
        tsvpath: Union[str, list[str, str]],
        read_from_archive: bool,
        sep: str = "\t",
        ) -> dict[str, dict[str, float]]:
    """Load caprieval data as dict.

    Parameters
    ----------
    tsvpath : str
        Path to the caprieval_ss.tsv file.
    read_from_archive : bool, optional
        When set to True, performs the search of capri_ss.tsv files from the
        analysis archive instead of the run directory, by default False
    sep : str
        String used to separate data in the file.

    Return
    ------
    data : dict[str, dict[str, float]]
        Dictionary holding data for each complexes.
    """
    data: dict[str, dict[str, float]] = {}
    # Read file content
    if not read_from_archive:
        with open(tsvpath, "r") as filin:
            file_content = filin.read()
    else:
        # Unpack archive name and tsv filepath
        archive_path, _tsv_fpath = tsvpath
        # Open archive
        tarin = tarfile.open(archive_path, "r:gz")
        # Extract desired file
        tar_tsv = tarin.extractfile(_tsv_fpath)
        # Read it
        file_content = tar_tsv.read().decode("utf-8")
        # Close archive
        tarin.close()

    # Loop over file lines
    for i, _ in enumerate(file_content.split("\n")):
        # Split the line
        s_ = _.strip().split(sep)
        # Gather header names
        if i == 0:
            header = s_
            continue
        if _.strip() == "":
            continue
        # Load data
        complex_name = s_[header.index('model')]
        complex_dt_str = {
            'rank': s_[header.index('caprieval_rank')],
            'haddock-score': s_[header.index('score')],
            'irmsd': s_[header.index('irmsd')],
            'lrmsd': s_[header.index('lrmsd')],
            'fnat': s_[header.index('fnat')],
            'ilrmsd': s_[header.index('ilrmsd')],
            'dockq': s_[header.index('dockq')],
            }
        # Cast all values to float
        complex_dt = {
            k: float(v)
            for k, v in complex_dt_str.items()
            }
        # Hold this guy
        data[complex_name] = complex_dt
    return data


def write_json(data: dict, path: str) -> None:
    """Write a json file containing data.

    Parameters
    ----------
    data : dict / list
        The data to be dumped in the file.
    path : str
        Path to the file to write.
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def load_json(path: str) -> Union[dict, list]:
    """Load a json file.

    Parameters
    ----------
    path : str
        Path to the .json file to load.

    Return
    ------
    data : dict or list
        Python loaded data within file
    """
    with open(path, "r") as fin:
        data = json.load(fin)
    return data


def get_data_mapper(
        basepath: str,
        overwrite: bool = False,
        outpath: str = "",
        subset_scenarios: Optional[list[str]] = None,
        read_from_archive: bool = False,
        ) -> dict:
    """Retrieve or generate data mapper.

    Parameters
    ----------
    basepath : str
        Path to the benchmark directory to analyse
    overwrite : bool
        Weather or not an existing benchmark_mapper be overwritten.
        If False, existing benchmark_mapper will be returned.
    outpath : str
        Base path where to write data
    subset_scenarios : Optional[list[str]]
        List of scenario names on which to perform the analysis.
    read_from_archive : bool, optional
        When set to True, performs the search of capri_ss.tsv files from the
        analysis archive instead of the run directory, by default False

    Return
    ------
    dtmapper : dict
        Dictionary mapping scenarios/pdbids to caprieval tsv paths.
    """
    # Name of the mapper
    mapper_fpath = f"{outpath}_benchmark_mapper.json"
    # Check for no overwrites
    if not overwrite and os.path.exists(mapper_fpath):
        dtmapper = load_json(mapper_fpath)
        return dtmapper

    # Gather data mapper
    dtmapper = map_data(
        basepath,
        subset_scenarios=subset_scenarios,
        read_from_archive=read_from_archive,
        )
    # Write it
    write_json(dtmapper, mapper_fpath)
    # Return data
    return dtmapper


def gen_outputdir(outputdir: str) -> None:
    """Make sure output directory is created.

    Parameters
    ----------
    outputdir : str
        Path to directory where to store the results
    """
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)


def set_output_path(
        benchmark_directory: str,
        outputpath: str,
        label: Optional[str] = None,
        ) -> tuple[str, str]:
    """Initiate output paths and directory.

    Parameters
    ----------
    benchmark_directory : str
        Path to the benchmark directory to analyse
    outputpath : str
        Path to directory where to store the results
    label : Optional[str]
        Custom name to use for output filenames and plot titles instead of
        the benchmark directory's basename (e.g. useful when the directory
        is named something generic like `test-analysis`).

    Return
    ------
    basename : str
        Name used to prefix output files / title the plots.
    base_outputpath : str
        Base path where to write data
    """
    # Initiate output directory
    gen_outputdir(outputpath)
    # Get basename of analysis, or use the user-provided label if given
    basename = label if label else os.path.basename(os.path.dirname(benchmark_directory))
    # Generate baseoutput path
    base_outputpath = f'{outputpath}{basename}'
    return basename, base_outputpath


def _vprint(silence: bool, msg: str) -> None:
    """Print on screen

    Parameters
    ----------
    msg : str
        Message to print
    silence : bool
        If true, do not print
    """
    if not silence:
        print(msg)


#################
# Main function #
#################
def main(
        benchmark_directory: str,
        outputpath: str = 'Analysis/',
        scenarios: Optional[list[str]] = None,
        metric: str = "irmsd",
        silent: bool = False,
        no_percentage: bool = False,
        no_capriplots: bool = False,
        no_violinplots: bool = False,
        no_melquiplots: bool = False,
        read_from_archive: bool = False,
        label: Optional[str] = None,
        per_scenario_plots: bool = False,
        ) -> None:
    """Run the analysis procedure.

    Parameters
    ----------
    benchmark_directory : str
        Path to the benchmark directory to analyse
    outputpath : str
        Path to directory where to store the results
    scenarios : Optional[list[str]]
        List of scenario names on which to perform the analysis.
    metric : str, optional
        Quality metric to be used for the analysis, by default "irmsd"
    silent : bool, optional
        Set the STDOUT silent or not, by default False
    no_percentage : bool, optional
        If set to True, the values will be reported by
        number of docking runs, by default False
    no_capriplots : bool, optional
        Do not generate the usual CAPRI model quality bar plots,
        by default False
    no_violinplots : bool, optional
        Do not generate the violin plots, by default False
    no_melquiplots : bool, optional
        Do not generate the melquiplots, by default False
    read_from_archive : bool, optional
        When set to True, performs the search of capri_ss.tsv files from the
        analysis archive instead of the run directory, by default False
    label : Optional[str], optional
        Custom name to use for output filenames and plot titles instead of
        the benchmark directory's basename, by default None
    per_scenario_plots : bool, optional
        In addition to the single combined comparison bar/violin plot
        (which already shows every scenario as its own row), also
        generate a standalone bar/violin plot for each individual
        scenario, by default False
    """
    # Pre-setting the STDOUT print function
    vprint = partial(_vprint, silent)

    # Initiate output paths
    basename, base_outputpath = set_output_path(
        benchmark_directory,
        outputpath,
        label=label,
        )
    vprint(f"Setting the output directory path: `{outputpath}`")

    # Gather data mapper
    vprint(f"- Searching for data in `{benchmark_directory}`")
    dtmapper = get_data_mapper(
        benchmark_directory,
        overwrite=True,
        outpath=base_outputpath,
        subset_scenarios=scenarios,
        read_from_archive=read_from_archive,
        )

    # Initiate all scenarios perforamces mapper
    vprint(
        f"- Loading data from `{benchmark_directory}` "
        f"for {len(dtmapper)} scenario(s): {', '.join(dtmapper)}"
        )
    all_scenar_perfs: dict[str, dict] = {}
    all_scenar_melquis: dict[str, dict] = {}
    # Loop over scenario
    for scenar_name, scenario_dt in dtmapper.items():
        # Analyse this scenario
        scenar_best_perfs, scenar_pdb_perfs = analyse_scenario(
            scenario_dt,
            TOP_X_THRESHOLDS,
            sort_dtype='haddock-score',
            perf_dtype=metric,
            read_from_archive=read_from_archive,
            )
        # Hold perforamnces
        all_scenar_perfs[scenar_name] = scenar_best_perfs
        all_scenar_melquis[scenar_name] = scenar_pdb_perfs

    # Write data as json
    write_json(all_scenar_perfs, f"{base_outputpath}_performances.json")

    # Build a nicer plot title than the bare basename (e.g. instead of just
    # `test-analysis`, show `Benchmark Output: test-analysis`).
    plot_title = f"Benchmark Output: {basename}"

    # Draw general graph
    if not no_capriplots:
        vprint("- Generating Bar plots")
        gen_full_comparison_barplots(
            all_scenar_perfs,
            basepath=base_outputpath,
            title=plot_title,
            progress=not silent,
            no_percentage=no_percentage,
            )

    if not no_violinplots:
        vprint("- Generating Violin plots")
        gen_full_comparison_violins(
            all_scenar_perfs,
            basepath=base_outputpath,
            title=plot_title,
            metric=metric,
            progress=not silent,
            )

    if not no_melquiplots:
       vprint("- Generating Melqui plots")
       gen_full_comparison_melquiplots(
            all_scenar_melquis,
            perf_dtype=metric,
            basepath=base_outputpath,
            progress=not silent,
            )

    # Draw per-scenario graphs, so each scenario also gets its own
    # standalone bar/violin plot, not just the combined comparison figure.
    # Skipped when there's only a single scenario overall, since in that
    # case the combined plot and the per-scenario plot would be identical
    # (redundant duplicate file).
    if per_scenario_plots and len(all_scenar_perfs) > 1:
        for scenar_name, scenar_perfs in all_scenar_perfs.items():
            scenar_outputpath = f"{base_outputpath}_{scenar_name}"
            scenar_title = f"{plot_title} - {scenar_name}"
            if not no_capriplots:
                vprint(f"- Generating Bar plot for scenario `{scenar_name}`")
                gen_full_comparison_barplots(
                    {scenar_name: scenar_perfs},
                    basepath=scenar_outputpath,
                    title=scenar_title,
                    progress=not silent,
                    no_percentage=no_percentage,
                    )
            if not no_violinplots:
                vprint(f"- Generating Violin plot for scenario `{scenar_name}`")
                gen_full_comparison_violins(
                    {scenar_name: scenar_perfs},
                    basepath=scenar_outputpath,
                    title=scenar_title,
                    metric=metric,
                    progress=not silent,
                    )


###################################
# COMMAND LINE ARGUMENTS HANDLERS #
###################################
def must_end_with_slash(dirpath: str) -> str:
    """Make sure a directory paths is terminating by '/'.

    NOTE: only appends the slash if `dirpath` already exists as a
    directory. Suitable for `benchmark_directory`, which must already
    exist. NOT suitable for an output path that hasn't been created yet
    -- use `ensure_trailing_slash` for that instead, otherwise the missing
    slash causes output filenames to get mashed together with whatever
    prefix follows (e.g. `AnalysisHADDOCK24_ab_initio_...` instead of
    `Analysis/HADDOCK24_ab_initio_...`), and can leave output files
    sitting loose inside the benchmark directory itself.

    Parameters
    ----------
    dirpath : str
        Path to a directory
    """
    if dirpath[-1] != '/' and Path(dirpath).is_dir():
        dirpath += '/'
    return dirpath


def ensure_trailing_slash(dirpath: str) -> str:
    """Unconditionally make sure a path ends with '/'.

    Unlike `must_end_with_slash`, this does not require the path to
    already exist -- appropriate for output directories, which are
    created later via `gen_outputdir`.

    Parameters
    ----------
    dirpath : str
        Path to a directory (existing or not).
    """
    if not dirpath.endswith('/'):
        dirpath += '/'
    return dirpath


def parse_cmd_line() -> argparse.Namespace:
    """Parse command line argument.

    Return
    ------
    args : argparse.Namespace
        Object holding validated arguments.
    """
    global DPI, PERFORMANCES_CLASSES
    # Load command line arguments
    args = _get_cmd_line_args()
    # Convert directory paths
    args.benchmark_directory = must_end_with_slash(args.benchmark_directory)
    # Default output path (when -o/--output_path isn't given) lives INSIDE
    # the benchmark directory itself (e.g. `<benchmark_directory>/Analysis/`),
    # not relative to wherever the script happens to be run from. If the
    # user explicitly passes -o, that value is used as-is (relative to cwd,
    # or absolute).
    if args.output_path is None:
        args.output_path = f"{args.benchmark_directory}Analysis"
    args.output_path = ensure_trailing_slash(args.output_path)
    # Set global variables
    DPI = args.dpi
    PERFORMANCES_CLASSES = ALL_PERFORMANCES_CLASSES[args.type]
    # Check that directory exist
    if not os.path.exists(args.benchmark_directory):
        sys.exit(
            f'INPUT ERROR: path to directory to analyse '
            f'"{args.benchmark_directory}" not found!'
            )
    return args


def _get_cmd_line_args() -> argparse.Namespace:
    """Define and parse the command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Analyse a HADDOCK3 + haddock-runner benchmark. Expects "
            "<benchmark_directory>/<scenario_name>/<PDBid>/run1/ layout "
            "(one or more scenarios). Generates a combined bar plot, "
            "violin plot, per-scenario melquiplots (zipped), and a JSON "
            "summary, written by default to Analysis/ inside the "
            "benchmark directory."
            ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    parser.add_argument(
        "benchmark_directory",
        help=(
            "Path to directory "
            "where benchmark was performed by haddock-runner"
            ),
        type=str,
        )
    parser.add_argument(
        "-o",
        "--output_path",
        help=(
            "Directory where to write output files. Defaults to "
            "`Analysis/` inside the benchmark directory itself."
            ),
        required=False,
        default=None,
        type=str,
        )
    parser.add_argument(
        '-l',
        '--label',
        help=(
            "Custom name to use for output filenames and plot titles, "
            "instead of the benchmark directory's basename (useful when "
            "the directory is named something generic, e.g. `test-analysis`)."
            ),
        required=False,
        default=None,
        type=str,
        )
    parser.add_argument(
        "-m",
        "--metric",
        help="Performance metric to track.",
        required=False,
        default="irmsd",
        choices=("irmsd", "dockq", ),
        type=str,
        )
    parser.add_argument(
        '-s',
        '--scenario',
        help="Name(s) of a specific scenario(s) to analyze. Can be multiple of them, separated by space. By default, all scenarios will be analysed together.",
        required=False,
        default=None,
        nargs="+",
        type=str,
        )
    parser.add_argument(
        '-t',
        '--type',
        help="Type of analysis to be conducted.",
        required=False,
        default="protein",
        choices=("protein", "peptide", "glycan", ),
        type=str,
        )
    parser.add_argument(
        '-d',
        '--dpi',
        help="DPI of the generated figures.",
        required=False,
        default=400,
        type=int,
        )
    parser.add_argument(
        '--no-capriplots',
        help="Do not generate CAPRI plots",
        action="store_true",
        default=False,
        )
    parser.add_argument(
        '--no-violinplots',
        help="Do not generate violin plots",
        action="store_true",
        default=False,
        )
    parser.add_argument(
        '--no-melquiplots',
        help="Do not generate melqui plots",
        action="store_true",
        default=False,
        )
    parser.add_argument(
        '--per-scenario-plots',
        help=(
            "In addition to the single combined comparison plot "
            "(all scenarios as rows in one bar/violin plot), also "
            "generate a separate standalone bar/violin plot for each "
            "individual scenario. Off by default."
            ),
        action="store_true",
        default=False,
        )
    parser.add_argument(
        '-n',
        '--no-percentage',
        help="Display number of structures instead of percentages",
        action="store_true",
        default=False,
        )
    parser.add_argument(
        '-a',
        '--from-archive',
        help=(
            "Perfoms the analysis directly from a haddock3 analysis archived runs. "
            "This option is ment to be used when haddock3 is launched with "
            "`gen_archive = true`, therefore searching for capri_ss.tsv files "
            "directly from the archive."
            ),
        action="store_true",
        default=False,
        )
    parser.add_argument(
        '-q',
        '--quiet',
        help="Silences prints",
        action="store_true",
        default=False,
        )
    args = parser.parse_args()
    return args


def welcome_msg(silent: bool) -> None:
    """Print welcome message

    Parameters
    ----------
    silent : bool
        If true, do not print
    """
    msg = (
        f"{'#' * 80}\n"
        "#   Haddock-runner haddock3 analysis script\n"
        f"#   Version: {__version__}\n"
        f"#   Author:  {__author__}\n"
        f"#   Devs:    {', '.join(__dev__)}\n"
        f"{'#' * 80}\n"
    )
    _vprint(silent, msg)


############################
# COMMAND LINE ENTRY POINT #
############################
def maincli() -> None:
    """CLI entry point."""
    args = parse_cmd_line()
    welcome_msg(args.quiet)
    main(
        args.benchmark_directory,
        outputpath=args.output_path,
        scenarios=args.scenario,
        metric=args.metric,
        silent=args.quiet,
        no_percentage=args.no_percentage,
        no_capriplots=args.no_capriplots,
        no_violinplots=args.no_violinplots,
        no_melquiplots=args.no_melquiplots,
        read_from_archive=args.from_archive,
        label=args.label,
        per_scenario_plots=args.per_scenario_plots,
        )


if __name__ == "__main__":
    maincli()