import os
import glob
import dsdtools
import yaml


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
    for result_files, metadata in get_files():
        for result in result_files:
            if os.path.splitext(result)[1] == '.mat':
                short_name = metadata['short']
                data.import_mat(result, estimate_name=short_name)


if __name__ == '__main__':

    data = dsdtools.evaluate.Data()
    aggregrate(data)
    data.to_pickle("out.pandas")
