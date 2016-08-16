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
    df = df.query('target_name == "vocals" or target_name == "accompaniment"')
    g = sns.FacetGrid(
        df,
        col="target_name",
        row="metric",
        col_order=['vocals', 'accompaniment'],
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
        showmeans=False,
        notch=True,
        showfliers=False,
    ).add_legend())

    plt.show()

    # lets get to see how difficult the songs are in general
    df = df.query(
        'metric == "SDR" and target_name == "vocals" and subset == "Test"'
    )

    sns.boxplot(
        'track_id',
        "score",
        data=df,
        showmeans=False,
        showfliers=False,
    )

    plt.show()
