import os
import glob
import pytest
from cerberus import Validator
import yaml


@pytest.fixture
def schema():
    return {
        'method_name': {'type': 'string'},
        'authors': {'type': 'string'},
        'short': {'type': 'string', 'maxlength': 4},
        'affiliation': {'type': 'string'},
        'email': {'type': 'string'},
        'description': {'type': 'string'},
    }


@pytest.fixture
def submissions_dir():
    return "submissions"

submission_dirs = ["submissions"]


@pytest.fixture(params=[
    name
    for submission_dir in submission_dirs
    for name in os.listdir(submission_dir)
    if os.path.isdir(submission_dir)
])
def submission(request):
    return request.param


def test_results(submissions_dir, submission):
    # traverse root directory, and list directories as dirs and files as files
    # list files in results
    results_dir = os.path.join(submissions_dir, submission, 'results')
    assert os.path.isdir(results_dir)

    types = ('*.pandas', '*.mat')
    files_grabbed = []
    for ext in types:
        files_grabbed.extend(glob.glob(os.path.join(results_dir, ext)))

    assert len(files_grabbed) != 0


def test_descriptions(submissions_dir, submission, schema):
    v = Validator(schema)
    # traverse root directory, and list directories as dirs and files as files
    # list files in results
    description_file = os.path.join(
        submissions_dir, submission, 'description.yml'
    )

    stream = file(description_file, 'r')
    document = yaml.load(stream)
    assert v.validate(document), v.errors
