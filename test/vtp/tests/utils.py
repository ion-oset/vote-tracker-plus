"""Utility functions for tests.

"""

import contextlib
import json
import os

# Use the backport of 'importlib.resources' where possible because it maintains
# backward compatibility strictly.
try:
    import importlib_resources
except ImportError:
    import importlib.resources as importlib_resources
    if not hasattr(importlib_resources, "files"):
        raise ImportError("module 'importlib.resources' has no attribute 'files'")

import pytest

# --- Uniform declarations for whether tests raise an exception

raises = pytest.raises
raises_none = contextlib.nullcontext


# --- Loading test data from 'tests.resources'

def get_test_data_path(file):
    """Location of test data file, as a path.

    Parameters:
        file: Sub-path of the test file, rooted in the test data path.

    Returns:
        Path to the data file.
    """
    path, file = os.path.split(file)
    package = "tests.resources"
    if path:
        assert not os.path.isabs(path), \
            f"Path to file must be relative (to test data root: {package})"
        sub_package = path.replace("/", ".")
        package = f"{package}.{sub_package}"
    path = importlib_resources.files(package).joinpath(file)
    return path


def load_test_data(file):
    """Load test files from the test data package.

    Parameters:
        file: Sub-path of the test file, rooted in the test data path.

    Returns:
        Test data found at path.
    """
    path = get_test_data_path(file)
    with path.open() as input:
        data = input.read()
        return data


def load_test_json(file):
    """Load JSON files from the test data package.

    Parameters:
        file: Sub-path of the test file, rooted in the test data path.

    Returns:
        Test data found at path.
    """
    text = load_test_data(file)
    data = json.loads(text)
    return data
