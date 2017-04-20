import pandas as pd
import argparse
import os
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'filenames_file',
        type=str,
        help="""A csv file listing the filenames as given in the results file
        sisec_mus_2017_full.csv. Column name must be `filename`.""")

    args = parser.parse_args()

    # Only take unique filenames
    df = pd.read_csv(args.filenames_file)
    filenames = df['filename'].unique()

    directory = 'audio_downloads'
    if not os.path.exists(directory):
        os.makedirs(directory)

    url = "http://sisec17.audiolabs-erlangen.de/media/SISEC"

    for filename in filenames:

        tmp_url = '/'.join((url, filename))

        try:
            urlretrieve(tmp_url, '/'.join((directory, filename)))
        except:
            print('Error downloading {}'.format(tmp_url))
