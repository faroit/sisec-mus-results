
import argparse
import json
import csv


def load_track_dict():
    tracklist = []
    csv_file = 'tracklist.csv'
    with open(csv_file, 'rt') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        # skip header
        next(spamreader)
        for i, row in enumerate(spamreader):
            values = {}
            values['id'] = int(row[0])
            values['name'] = row[1]
            values['genre'] = row[2]
            tracklist.append(values)
    return tracklist


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    tracklist = load_track_dict()
    sorted_list = sorted(tracklist, key=lambda x: x['id'])
    with open("tracklist.json", 'w') as f:
        json.dump(sorted_list, f)
