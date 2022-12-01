import pytest

from vtp.core.common import Shellout

from tests.utils import raises, raises_none


# --- Test data


# args, stdout, stderr
SHELLOUT_RUN_TESTS = [
    ( ["echo", 101], "101", "" ),
    ( ["echo", "1..2..3"], "1..2..3", "" )
]


# --- Test cases

# Notes:
#
# - PyTest captures all output. To test for 'Shellout' output use the 'capfd'
#   fixture's output and error, not the results of 'Shellout.run' (which will
#   always be None).
# - Parameters starting with '_' in test data but ignored by the test case.

@pytest.mark.parametrize("args,_output,_errors", SHELLOUT_RUN_TESTS)
def test_shellout_run_output(args, _output, _errors, capfd):
    # 'Shellout.run' discards output & errors by default
    assert Shellout.run(args).stdout == None
    actual = capfd.readouterr().out.rstrip()
    expected = _output
    assert(actual == expected)


@pytest.mark.parametrize("args,_output,_errors", SHELLOUT_RUN_TESTS)
def test_shellout_run_errors(args, _output, _errors, capfd):
    # 'Shellout.run' discards output & errors by default
    assert Shellout.run(args).stderr == None
    actual = capfd.readouterr().err.rstrip()
    expected = _errors
    assert(actual == expected)


@pytest.mark.parametrize("args,output,_errors", SHELLOUT_RUN_TESTS)
def test_shellout_run_with_io_output(args, output, _errors, capfd):
    Shellout.run(args, no_touch_stds = True)
    # Drop the trailing newline
    actual = capfd.readouterr().out.rstrip()
    expected = output
    assert(actual == expected)


@pytest.mark.parametrize("args,_output,errors", SHELLOUT_RUN_TESTS)
def test_shellout_run_with_io_errors(args, _output, errors, capfd):
    Shellout.run(args, no_touch_stds = True)
    # Drop the trailing newline
    actual = capfd.readouterr().err.rstrip()
    expected = errors
    assert(actual == expected)
