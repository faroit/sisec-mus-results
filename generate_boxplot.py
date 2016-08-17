import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import numpy as np


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

    df = pd.read_pickle(args.result_file)

    measures = ['SDR', 'ISR', 'SIR', 'SAR']

    # reshape data
    df = pd.melt(
       df,
       id_vars=['track_id', 'track_name', 'target_name', 'estimate_name'],
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

    g = sns.FacetGrid(
        df,
        col="target_name",
        row="metric",
        sharex=False,
        sharey=False,
        legend_out=True,
        palette=sns.color_palette("viridis", 14)
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

    plt.show()
