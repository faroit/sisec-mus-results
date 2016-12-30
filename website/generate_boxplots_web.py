import pandas as pd
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
    fig_size = np.array([fig_width*4, fig_height*6])

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
    df = df[df.target_name == args.target]

    # get the list of estimate names and sort them
    estimate_names = sorted(df.estimate_name.unique().tolist())
    estimate_names += [estimate_names.pop(estimate_names.index("IBM"))]

    sns.set_style("darkgrid", {
        "axes.facecolor": "0.925",
        'axes.labelsize': 30,
        'font.size': 30,
        'legend.fontsize': 30,
        'xtick.labelsize': 30,
        'ytick.labelsize': 30,
    })

    f, axes = plt.subplots(4, 1, figsize=fig_size, sharex=True)

    for i, ax in enumerate(axes):
        df_measure = df[df.metric == measures[i]]

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

        # plt.setp(ax.get_xticklabels(), rotation=45, fontsize=19)

        lgd = ax.legend(
            loc='lower right',
            # bbox_to_anchor=(0.5, -0.22),
            bbox_transform=BlendedGenericTransform(
                f.transFigure, ax.transAxes
            ),
            ncol=2
        )

        ax.set_xlabel('')
        ax.set_ylabel(measures[i])

    f.set_tight_layout(True)
    f.savefig(
        args.target + ".png",
        bbox_inches='tight',
        dpi=100
    )
