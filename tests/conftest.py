# pylint: disable=missing-module-docstring
"""
Pytest configuration for argocli tests.
"""

# These imports will be installed when running pytest
# pylint: disable=import-error
from unittest.mock import MagicMock
import pytest

@pytest.fixture
def mock_config():
    """
    Mock configuration object for testing.
    """
    mock = MagicMock()
    mock.server = "https://argo-server.example.com"
    mock.namespace = "test-namespace"
    mock.username = "test-user"
    return mock

@pytest.fixture
def mock_logger():
    """
    Mock logger object for testing.
    """
    return MagicMock()
