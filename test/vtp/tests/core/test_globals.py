import pytest

from vtp.core.common import Globals

from tests.utils import raises, raises_none


# --- Test data

## key, default, raises
GLOBALS_GET_TESTS = [
    (
        "ADDRESS_MAP_FILE",
        "address_map.yaml",
        raises_none(),
    ),
    (
        "BALLOT_FILE",
        "ballot.json",
        raises_none(),
    ),
    (
        "BALLOT_RECEIPT_ROWS",
        100,
        raises_none(),
    ),
    (
        "BIN_DIR",
        "src/vtp",
        raises_none(),
    ),
    (
        "BLANK_BALLOT_SUBDIR",
        "blank-ballots",
        raises_none(),
    ),
    (
        "CONFIG_FILE",
        "config.yaml",
        raises_none(),
    ),
    (
        "CONTEST_FILE",
        "contest.json",
        raises_none(),
    ),
    (
        "CONTEST_FILE_SUBDIR",
        "CVRs",
        raises_none(),
    ),
    (
        "RECEIPT_FILE",
        "receipt.csv",
        raises_none(),
    ),
    (
        "REQUIRED_GGO_ADDRESS_FIELDS",
        ["state", "town"],
        raises_none(),
    ),
    (
        "REQUIRED_NG_ADDRESS_FIELDS",
        ["street", "number"],
        raises_none(),
    ),
    (
        "ROOT_ELECTION_DATA_SUBDIR",
        "..",
        raises_none(),
    ),
    (
        "SHELL_TIMEOUT",
        15,
        raises_none(),
    ),
    (
        "INVALID_KEY",
        "No global key with this name",
        raises(KeyError, match = "INVALID_KEY"),
    ),
]


# --- Test cases

@pytest.mark.parametrize("key,default,raises", GLOBALS_GET_TESTS)
def test_globals_get(key, default, raises):
    with raises as ex:
        actual = Globals.get(key)
        expected = default
        assert(actual == expected)
