
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

    # remove these tracks for the website for now
    df = df.query('track_id != 36 and track_id != 37 and track_id != 44 and track_id != 43')

    # aggregate over each method and track, to remove the sample column
    # this results in less columns and should speed up the plotting
    df = df.groupby(
        ['estimate_name', 'track_id', 'target_name']
    ).mean().reset_index()

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
    headers['subsets'] = ['Dev', 'Test']

    with open("headers.json", 'w') as f:
        json.dump(headers, f)

    # Encode names into IDs
    df['track_id'] = df['track_id'].astype(np.int16)
    df['is_dev'] = np.where(df['track_id'] >= 51, 0, 1)
    df['target_id'] = df['target_name'].astype('category').cat.codes
    df['method_id'] = df['estimate_name'].astype('category').cat.codes
    df['metric_id'] = df['metric'].astype('category').cat.codes

    # write out headers
    df.to_csv(
        path_or_buf="sisec_mus_2017.csv",
        sep=",",
        header=True,
        columns=[
            'track_id',
            'is_dev',
            'target_id',
            'method_id',
            'metric_id',
            'score'
        ],
        index=False,
        index_label=None
    )
