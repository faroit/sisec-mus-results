import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import numpy as np
import math
from matplotlib.transforms import BlendedGenericTransform
import matplotlib as mpl
import matplotlib.patches as mpatches


def discrete_cmap(N, base_cmap=None):
    """Create an N-bin discrete colormap from the specified input map"""

    # Note that if base_cmap is a string or None, you can simply do
    #    return plt.cm.get_cmap(base_cmap, N)
    # The following works for string, None, or a colormap instance:

    base = plt.cm.get_cmap(base_cmap)
    color_list = base(np.linspace(0, 1, N))
    cmap_name = base.name + str(N)
    color_tuples = map(tuple, color_list.tolist())
    return base.from_list(cmap_name, color_list, N), color_tuples


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'result_file',
        type=str,
        help='Pandas results'
    )

    args = parser.parse_args()

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['text.latex.unicode'] = 'True'

    sns.set()
    sns.set_context("paper")

    # Get this from LaTeX using \showthe\columnwidth
    fig_width_pt = 244.6937
    # Convert pt to inch
    inches_per_pt = 1.0 / 72.27
    # Aesthetic ratio
    golden_mean = (math.sqrt(5) - 1.0) / 2.0
    # width in inches
    fig_width = fig_width_pt * inches_per_pt
    # height in inches
    fig_height = fig_width * golden_mean
    fig_size = np.array([fig_width*6, fig_height*2])

    params = {
        'backend': 'ps',
        'axes.labelsize': 18,
        'font.size': 15,
        'legend.fontsize': 16,
        'xtick.labelsize': 15,
        'ytick.labelsize': 15,
        'text.usetex': True,
        'font.family': 'serif',
        'font.serif': 'ptmrr8re',
        'figure.figsize': fig_size
    }

    plt.rcParams.update(params)

    df = pd.read_pickle(args.result_file)

    measures = ['SDR', 'ISR', 'SIR', 'SAR']

    # reshape data
    df = pd.melt(
        df,
        id_vars=[
            'track_id',
            'track_name',
            'target_name',
            'estimate_name',
            'is_supervised'
        ],
        value_vars=measures,
        var_name='metric',
        value_name='score'
    )
    # fetch track_id
    df[['track_id']] = df[['track_id']].apply(pd.to_numeric)
    df['subset'] = np.where(df['track_id'] >= 51, 'Dev', 'Test')

    # show vocals/acc for now
    df = df[df.target_name.isin(['vocals', 'accompaniment'])].dropna()
    df = df[df.subset == 'Test'].dropna()

    # get the list of estimate names and sort them
    # estimate_names = sorted(df.estimate_name.unique().tolist())

    sns.set_style("darkgrid", {
        "axes.facecolor": "0.925",
        'text.usetex': True,
        'font.family': 'serif',
        'axes.labelsize': 16,
        'font.size': 16,
        'legend.fontsize': 15,
        'xtick.labelsize': 17,
        'ytick.labelsize': 17,
        'font.serif': 'ptmrr8re',
    })

    # sort by median of test score
    df_sort_by = df[(df.metric == "SDR") & (df.subset == "Test")]

    estimate_tuples = df_sort_by.score.groupby([df_sort_by.estimate_name, df_sort_by.is_supervised]).median().order().index.tolist()
    estimate_names, estimate_supervised = zip(*estimate_tuples)

    color_list, color_tuples = discrete_cmap(4, 'cubehelix_r')

    for measure in measures:

        df_measure = df[df.metric == measure]

        f, ax = plt.subplots(1, 1, figsize=fig_size)

        ax = sns.boxplot(
            'estimate_name',
            "score",
            "target_name",
            # hue_order=['Dev', 'Test'],
            data=df_measure,
            order=estimate_names,
            showmeans=False,
            notch=True,
            showfliers=False,
            width=0.75,
            ax=ax,
            palette="cubehelix_r"
        )

        plt.setp(ax.get_xticklabels(), fontsize=19)

        for i, (is_supervised, xtick) in enumerate(
            zip(estimate_supervised, ax.get_xticklabels())
        ):
            if is_supervised:
                box = ax.artists[i * 2]
                box.set(hatch='////', edgecolor='white', linewidth=0)
                box = ax.artists[i * 2 + 1]
                box.set(hatch='////', edgecolor='white', linewidth=0)
            else:
                box = ax.artists[i * 2]
                box.set(linewidth=0)
                box = ax.artists[i * 2 + 1]
                box.set(linewidth=0)

        ax.set_xlabel('')
        ax.set_ylabel(measure + ' in dB')
        ax.set_ylim([-10, 18.5])

        pv = mpatches.Patch(
            facecolor=color_tuples[1]
        )
        pa = mpatches.Patch(
            facecolor=color_tuples[2]
        )

        pu = mpatches.Patch(
            hatch='////', edgecolor='white', facecolor='black'
        )
        ps = mpatches.Patch(
            edgecolor='white', facecolor="black"
        )

        leg = plt.legend(
            [pv, pa, pu, ps],
            ['Vocals', 'Accompaniment', 'Unsupervised', 'Supervised'],
            ncol=2,
            loc='upper left',
            bbox_transform=BlendedGenericTransform(
                f.transFigure, ax.transAxes
            ),
        )

        ax.add_artist(leg)

        f.set_tight_layout(True)
        f.savefig(
            measure + ".pdf",
            bbox_inches='tight',
            dpi=300
        )
