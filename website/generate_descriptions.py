
import argparse
import json
import os
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
        description_file = os.path.join(
            submissions_dir, submission, 'description.yml'
        )
        stream = open(description_file, 'r')
        metadata = yaml.load(stream)

        yield metadata

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    metadata_list = []

    for metadata in get_files():
        metadata_list.append(metadata)

    sorted_list = sorted(metadata_list, key=lambda x: x['short'])
    with open("metadata.json", 'w') as f:
        json.dump(sorted_list, f)
