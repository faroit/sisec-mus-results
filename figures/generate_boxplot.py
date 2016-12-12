import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import numpy as np
import math
from matplotlib.transforms import BlendedGenericTransform
import matplotlib as mpl


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'result_file',
        type=str,
        help='Pandas results'
    )

    parser.add_argument(
        '--target',
        type=str,
        default='vocals'
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
    df = df[df.target_name == args.target].dropna()

    # get the list of estimate names and sort them
    estimate_names = sorted(df.estimate_name.unique().tolist())

    # bring IBM to the start position
    estimate_names.insert(0, estimate_names.pop(estimate_names.index('IBM')))

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

    for measure in measures:
        df_measure = df[df.metric == measure]
        f, ax = plt.subplots(1, 1, figsize=fig_size)

        ax = sns.boxplot(
            'estimate_name',
            "score",
            "subset",
            hue_order=['Dev', 'Test'],
            data=df_measure,
            order=estimate_names,
            showmeans=False,
            notch=True,
            showfliers=False,
            width=0.75,
            ax=ax
        )

        plt.setp(ax.get_xticklabels(), rotation=90)

        lgd = ax.legend(
            loc='upper right',
            # bbox_to_anchor=(0.5, -0.22),
            bbox_transform=BlendedGenericTransform(
                f.transFigure, ax.transAxes
            ),
            ncol=2
        )

        ax.set_xlabel('')
        ax.set_ylabel(measure)

        f.set_tight_layout(True)
        f.savefig(
            args.target + measure + ".pdf",
            bbox_inches='tight',
            dpi=300
        )
