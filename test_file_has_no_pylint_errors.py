"""pylint dynamic pytest wrapper"""


import glob
import subprocess
import json
import pytest

LOCATION = '.'
ANALYSIS_FILES = glob.glob(f'{LOCATION}/**/*.py', recursive=True)
@pytest.mark.parametrize('filepath', ANALYSIS_FILES)
def test_file_has_no_pylint_errors(filepath):
    """validate that there are zero pylint warnings against a python file"""
    print(f'creating tests for file {filepath}')

    proc = subprocess.Popen(
        f"pylint {filepath} -f json --persistent=n --score=y",
        stdout=subprocess.PIPE,
        shell=True,
    )

    (out, _err) = proc.communicate()

    lint_json = json.loads(out) if out and  out.strip() else []
    # pylint: disable=C1801
    assert len(lint_json) == 0
