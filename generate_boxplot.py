import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import numpy as np
import matplotlib as mpl
import math
from matplotlib.transforms import BlendedGenericTransform


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

    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['text.latex.unicode'] = 'True'

    sns.set()
    sns.set_context("paper")

    fig_width_pt = 244.6937  # Get this from LaTeX using \showthe\columnwidth
    inches_per_pt = 1.0 / 72.27               # Convert pt to inch
    golden_mean = (math.sqrt(5) - 1.0) / 2.0         # Aesthetic ratio
    fig_width = fig_width_pt * inches_per_pt  # width in inches
    fig_height = fig_width * golden_mean      # height in inches
    fig_size = np.array([fig_width*3.333, fig_height*1.5])

    params = {'backend': 'ps',
              'axes.labelsize': 14,
              'font.size': 16,
              'legend.fontsize': 14,
              'xtick.labelsize': 14,
              'ytick.labelsize': 14,
              'text.usetex': True,
              'font.family': 'serif',
              'figure.figsize': fig_size}

    plt.rcParams.update(params)

    df = pd.read_pickle(args.result_file)

    measures = ['SDR', 'ISR', 'SIR', 'SAR']

    # reshape data
    df = pd.melt(
       df,
       id_vars=['track_id', 'track_name', 'target_name', 'estimate_name', 'is_supervised'],
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

    sns.set()
    sns.set_context("paper")

    for measure in measures:
        df_measure = df[df.metric == measure]
        f, ax = plt.subplots(1, 1, figsize=fig_size)

        sns.boxplot(
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
            args.target + measure + ".eps",
            bbox_inches='tight',
            # bbox_extra_artists=(lgd,),
            dpi=300
        )
