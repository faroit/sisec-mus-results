
import pandas as pd
import argparse
import numpy as np
import json


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
       id_vars=['track_id', 'target_name', 'estimate_name'],
       value_vars=measures,
       var_name='metric',
       value_name='score'
    )

    headers = {}
    headers['methods'] = list(
        df['estimate_name'].astype('category').cat.categories
    )
    headers['metrics'] = list(
        df['metric'].astype('category').cat.categories
    )
    headers['targets'] = list(
        df['target_name'].astype('category').cat.categories
    )
    with open("headers.json", 'w') as f:
        json.dump(headers, f)

    # fetch track_id
    df[['track_id']] = df[['track_id']].astype(np.int16)
    df['target_name'] = df['target_name'].astype('category').cat.codes
    df['estimate_name'] = df['estimate_name'].astype('category').cat.codes
    df['metric'] = df['metric'].astype('category').cat.codes

    df.to_csv(
        path_or_buf="out.csv",
        sep=",",
        header=True,
        index=False,
        index_label=None
    )
