import os
import glob
import yaml
import pandas as pd
import scipy.io
import numpy as np
import difflib
import csv


def load_track_list():
    tracklist = ['']*101
    csv_file = 'tracklist.csv'
    with open(csv_file, 'rt') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        # skip header
        next(spamreader)
        for i, row in enumerate(spamreader):
            tracklist[int(row[0])] = str(row[1])
    return tracklist


class Data(object):
    def __init__(self):
        self.columns = [
            'track_id',
            'track_name',
            'target_name',
            'estimate_dir',
            'estimate_name',
            'SDR',
            'ISR',
            'SIR',
            'SAR',
            'sample',
            'subset'
        ]

        self.df = pd.DataFrame(columns=self.columns)
        self.tracklist = load_track_list()

    def row2series(self, **row_data):
        return pd.Series(row_data)

    def append(self, series):
        self.df = self.df.append(series, ignore_index=True)

    def to_pickle(self, filename):
        self.df.to_pickle(filename)

    def import_mat(self, filename, estimate_name=''):
        mat = scipy.io.loadmat(filename)
        mdata = mat['result']
        ndata = {n.title(): mdata[n][0, 0] for n in mdata.dtype.names}
        s = []

        for subset, subset_data in ndata.items():
            data = subset_data['results']
            for track in range(data.shape[1]):
                tdata = data[0, track][0, 0]
                for target in [
                    'vocals', 'drums', 'other', 'bass', 'accompaniment'
                ]:
                    frames = len(tdata[target][0]['sdr'][0][0])

                    has_nan_values = []
                    for metric in ['sdr', 'isr', 'sir', 'sar']:
                        score = tdata[target][0][metric][0][0]
                        has_nan_values.append(np.all(np.isnan(score)))

                    if any(has_nan_values):
                        # skip target
                        continue
                    else:
                        split_name = tdata['name'][0].split(' - ')
                        try:
                            track_id = int(split_name[0])
                        except ValueError:
                            # match closest track
                            match = difflib.get_close_matches(
                                str(tdata['name'][0]),
                                self.tracklist,
                                n=1
                            )
                            if match:
                                track_id = int(
                                    self.tracklist.index(match[0])
                                )
                        for frame in range(frames):
                            series = self.row2series(
                                track_id=track_id,
                                track_name=tdata['name'][0],
                                target_name=target,
                                estimate_dir=filename,
                                estimate_name=estimate_name,
                                SDR=tdata[target][0]['sdr'][0][0][frame],
                                ISR=tdata[target][0]['isr'][0][0][frame],
                                SIR=tdata[target][0]['sir'][0][0][frame],
                                SAR=tdata[target][0]['sar'][0][0][frame],
                                sample=frame,
                                subset=subset
                            )
                            s.append(series)
        self.append(s)


def add_supervised(row, metadata):
    return metadata[row['estimate_name']]['is_supervised']


def add_augmentation(row, metadata):
    return metadata[row['estimate_name']]['uses_augmentation']


def get_files():
    # traverse root directory, and list directories as dirs and files as files
    submissions_dir = "submissions"
    submissions = [
        name
        for name in os.listdir(submissions_dir)
        if os.path.isdir(submissions_dir)
    ]

    for submission in submissions:
        # list files in results
        results_dir = os.path.join(submissions_dir, submission, 'results')
        description_file = os.path.join(
            submissions_dir, submission, 'description.yml'
        )
        stream = open(description_file, 'r')
        metadata = yaml.load(stream)

        types = ('*.pandas', '*.mat')
        for ext in types:
            yield glob.glob(os.path.join(results_dir, ext)), metadata


def aggregrate(dsd):
    metadata_dict = {}
    for result_files, metadata in get_files():
        short_name = metadata['short']
        metadata_dict[metadata['short']] = metadata
        for result in result_files:
            if os.path.splitext(result)[1] == '.mat':
                data.import_mat(result, estimate_name=short_name)

    # add metadata
    data.df['is_supervised'] = \
        data.df.apply(
            lambda row: add_supervised(row, metadata_dict), axis=1
        )
    data.df['uses_augmentation'] = \
        data.df.apply(
            lambda row: add_augmentation(row, metadata_dict), axis=1
        )

if __name__ == '__main__':

    data = Data()
    aggregrate(data)
    # aggregate over each method and track, to remove the sample column
    # this results in less columns and should speed up the plotting
    data.df = data.df.groupby(
        ['estimate_name', 'track_id', 'target_name']
    ).mean().reset_index()
    data.to_pickle("sisec_mus_2017.pandas")
