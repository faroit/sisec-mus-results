import os
import glob
import dsdtools
import yaml


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

    data = dsdtools.evaluate.Data()
    aggregrate(data)
    # aggregate over each method and track, to remove the sample column
    # this results in less columns and should speed up the plotting
    data.df = data.df.groupby(
        ['estimate_name', 'track_id', 'target_name']
    ).mean().reset_index()
    data.to_pickle("out.pandas")
