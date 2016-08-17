
import pandas as pd
import argparse
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import ols


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
       id_vars=['track_id', 'track_name', 'target_name', 'estimate_name', 'is_supervised'],
       value_vars=measures,
       var_name='metric',
       value_name='score'
    )

    # fetch track_id
    df[['track_id']] = df[['track_id']].apply(pd.to_numeric)
    df['subset'] = np.where(df['track_id'] >= 51, 'Dev', 'Test')

    # lets get to see how difficult the songs are in general
    df = df.query(
        'metric == "SDR" and target_name == "vocals" and subset == "Test"'
    )
    # ANOVA
    lm = ols('score ~ C(estimate_name) - 1', df).fit()
    print lm.summary()
    # table = sm.stats.anova_lm(lm, typ=2)
    # print table

    pc_table = sm.stats.multicomp.pairwise_tukeyhsd(
         df['score'], df['estimate_name'])

    print(pc_table)
