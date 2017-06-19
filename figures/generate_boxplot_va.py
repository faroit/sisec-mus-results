import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import numpy as np
import math
from matplotlib.transforms import BlendedGenericTransform
import matplotlib as mpl
from matplotlib import gridspec


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
    fig_size = np.array([fig_width*5, fig_height*2])

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

    # get 2 discrete colors used for the labels (4 because of b/w)
    color_list, color_tuples = discrete_cmap(4, 'cubehelix_r')

    for measure in measures:
        f = plt.figure(figsize=fig_size)
        gs = gridspec.GridSpec(1, 3, width_ratios=[8, 15, 1])

        # create an unsupervised methods and a supervised methods axis
        ax_u = plt.subplot(gs[0])
        ax_s = plt.subplot(gs[1], sharey=ax_u)
        ax_i = plt.subplot(gs[2], sharey=ax_u)

        df_u = df[(df.metric == measure) & ~df.is_supervised]
        df_s = df[(df.metric == measure) & df.is_supervised & (df.estimate_name != 'IBM')]
        df_i = df[(df.metric == measure) & df.is_supervised & (df.estimate_name == 'IBM')]

        # sort by median of test score
        df_u_sort_by = df_u[
            (df_u.metric == measure) &
            (df_u.subset == "Test") &
            (df_u.target_name == "vocals")
        ]

        estimate_names_u = df_u_sort_by.score.groupby(
            df_u_sort_by.estimate_name
        ).median().order().index.tolist()

        ax_u = sns.boxplot(
            'estimate_name',
            "score",
            "target_name",
            # hue_order=['Dev', 'Test'],
            data=df_u,
            order=estimate_names_u,
            showmeans=False,
            notch=True,
            showfliers=False,
            width=0.75,
            ax=ax_u,
            palette="cubehelix_r"
        )

        df_u.groupby(df_u.target_name).score.mean().vocals

        # sort by median of test score
        df_s_sort_by = df_s[
            (df_s.metric == measure) &
            (df_s.subset == "Test") &
            (df_s.target_name == "vocals")
        ]
        estimate_names_s = df_s_sort_by.score.groupby(
            df_s_sort_by.estimate_name
        ).median().order().index.tolist()

        ax_s = sns.boxplot(
            'estimate_name',
            "score",
            "target_name",
            # hue_order=['Dev', 'Test'],
            data=df_s,
            order=estimate_names_s,
            showmeans=False,
            notch=True,
            showfliers=False,
            width=0.75,
            ax=ax_s,
            palette="cubehelix_r"
        )

        ax_i = sns.boxplot(
            'estimate_name',
            "score",
            "target_name",
            # hue_order=['Dev', 'Test'],
            data=df_i,
            showmeans=False,
            notch=True,
            showfliers=False,
            width=0.75,
            ax=ax_i,
            palette="cubehelix_r"
        )

        if measure == 'SDR':
            ax_u.set_ylim([-9,  18.5])

        if measure == 'SIR':
            ax_u.set_ylim([-10,  28])

        if measure == 'SAR':
            ax_u.set_ylim([-5,  25])

        ax_u.legend_.remove()
        ax_i.legend_.remove()
        ax_s.legend_.remove()

        # get labels and handles from ax1
        h, l = ax_u.get_legend_handles_labels()

        plt.figlegend(
            h, l,
            loc='upper center', ncol=2, labelspacing=0.,
            bbox_to_anchor=(0.5, 1.15),
            bbox_transform=BlendedGenericTransform(
                f.transFigure, ax_u.transAxes
            )
        )

        ax_u.axhline(
            y=df_u.groupby(df_u.target_name).score.median().vocals,
            color=color_tuples[1],
            linestyle='dashed',
            linewidth=2
        )

        ax_u.axhline(
            y=df_u.groupby(df_u.target_name).score.median().accompaniment,
            color=color_tuples[2],
            linestyle='dashed',
            linewidth=2
        )

        ax_s.axhline(
            y=df_s.groupby(df_s.target_name).score.median().vocals,
            color=color_tuples[1],
            linestyle='dashed',
            linewidth=2
        )

        ax_s.axhline(
            y=df_s.groupby(df_s.target_name).score.median().accompaniment,
            color=color_tuples[2],
            linestyle='dashed',
            linewidth=2
        )

        ax_i.axhline(
            y=df_i.groupby(df_i.target_name).score.median().vocals,
            color=color_tuples[1],
            linestyle='dashed',
            linewidth=2
        )

        ax_i.axhline(
            y=df_i.groupby(df_i.target_name).score.median().accompaniment,
            color=color_tuples[2],
            linestyle='dashed',
            linewidth=2
        )

        ax_u.set_xlabel('')
        ax_s.set_xlabel('')
        ax_i.set_xlabel('')

        ax_s.set_ylabel('')
        ax_i.set_ylabel('')

        plt.setp(ax_s.get_yticklabels(), visible=False)
        plt.setp(ax_i.get_yticklabels(), visible=False)

        ax_u.set_ylabel(measure + ' in dB')

        f.set_tight_layout(True)
        f.savefig(
            measure + ".pdf",
            bbox_inches='tight',
            dpi=300
        )
