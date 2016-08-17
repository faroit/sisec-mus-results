import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import numpy as np
import matplotlib as mpl
import math


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

    plt.rc('text', usetex=False)

    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['text.latex.unicode'] = 'False'

    sns.set()
    sns.set_context("paper")
    sns.set_style(
        "white", {
            "font.family":
            "serif", 'font.serif':
            'ptmrr8re'
        }
    )

    fig_width_pt = 244.6937  # Get this from LaTeX using \showthe\columnwidth
    inches_per_pt = 1.0 / 72.27               # Convert pt to inch
    golden_mean = (math.sqrt(5) - 1.0) / 2.0         # Aesthetic ratio
    fig_width = fig_width_pt * inches_per_pt  # width in inches
    fig_height = fig_width * golden_mean      # height in inches
    fig_size = np.array([fig_width*2.5, fig_height*1.5])

    params = {'backend': 'ps',
              'axes.labelsize': 14,
              'font.size': 14,
              'legend.fontsize': 12,
              'xtick.labelsize': 12,
              'ytick.labelsize': 12,
              'text.usetex': False,
              'font.family': 'serif',
              'font.serif': 'ptmrr8re',
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
    df = df[df.target_name == args.target]

    # get the list of estimate names and sort them
    estimate_names = sorted(df.estimate_name.unique().tolist())
    # bring IBM to the start position
    estimate_names.insert(0, estimate_names.pop(estimate_names.index('IBM')))

    sns.set()
    sns.set_context("paper")
    g = sns.FacetGrid(
        df,
        col="target_name",
        row="metric",
        sharex=False,
        sharey=False,
        legend_out=True,
        palette=sns.color_palette("viridis", 14),
        aspect=3.3
    )
    g = (g.map(
        sns.boxplot,
        'estimate_name',
        "score",
        "subset",
        hue_order=['Dev', 'Test'],
        order=estimate_names,
        showmeans=False,
        notch=True,
        showfliers=False,
        width=0.75
    ).add_legend())

    plt.savefig(
        args.target + ".eps",
        bbox_inches='tight',
        # bbox_extra_artists=(lgd,),
        dpi=300
    )
