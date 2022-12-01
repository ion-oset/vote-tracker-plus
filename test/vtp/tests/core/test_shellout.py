import pytest

import sys

from vtp.core.common import Shellout

from tests.utils import raises, raises_none


# --- Test data

# Notes
# - All these tests use 'echo' because it will exist where Bash does, and
#   can't fail (the way 'ls' could if it was run with a non-existent path),
# - Doing this right needs mocks of file paths.

# TODO:
# - Actual stderr tests
# - Test 'Shellout.changed_cwd'
# - Test 'Shellout.changed_branch'
# - Test 'Shellout.cvr_parse_git_log_output'

# args, kwargs, stdout, stderr
SHELLOUT_RUN_TESTS = [
    (
        [ "echo", "1..2..3" ],
        {},
        "1..2..3",
        "",
    ),
    (
        [ "echo", 101 ] ,
        {},
        "101",
        ""
    ),
    (
        [ "echo", "1..2..3" ],
        { "no_touch_stds": False },
        "1..2..3",
        ""
    ),
    (
        [ "echo", "1..2..3" ],
        { "no_touch_stds": True },
        "1..2..3",
        ""
    ),
    (
        [ "echo", "1..2..3" ],
        { "verbosity": 2 },
        "",
        ""
    ),
    # 'stdout' == None is the default, so sys.stdout is used
    (
        [ "echo", "1..2..3" ],
        { "stdout": None, "verbosity": 2 },
        "1..2..3",
        ""
    ),
    # This fails because sys.stdout is not a file descriptor, and not because
    # the expected output is wrong. This is an artifact of using 'capfd' instead
    # of 'capsys' in the test.
    pytest.param(
        [ "echo", "1..2..3" ],
        { "stdout": sys.stdout, "verbosity": 2 },
        "1..2..3",
        "",
        marks = pytest.mark.xfail
    ),
]


# --- Test cases

# Notes:
#
# - PyTest captures all output. To test for 'Shellout' output use the 'capfd'
#   fixture's output and error, not the results of 'Shellout.run' (which will
#   always be None).
# - 'capfd' doesn't allow passing streams to output and errors (need 'capsys'
#   for that), which makes it hard to write to stderr instead of stdout.
# - Parameters starting with '_' in test data but ignored by the test case.

@pytest.mark.parametrize("args,kwargs,output,_errors", SHELLOUT_RUN_TESTS)
def test_shellout_run_output(args, kwargs, output, _errors, capfd):
    Shellout.run(args, **kwargs).stdout == None
    # Drop any trailing newline
    actual = capfd.readouterr().out.rstrip()
    expected = output
    assert(actual == expected)


@pytest.mark.parametrize("args,kwargs,_output,errors", SHELLOUT_RUN_TESTS)
def test_shellout_run_errors(args, kwargs, _output, errors, capfd):
    assert Shellout.run(args, **kwargs).stderr == None
    # Drop any trailing newline
    actual = capfd.readouterr().err.rstrip()
    expected = errors
    assert(actual == expected)
