# pylint: disable=missing-module-docstring
"""
Pytest configuration for argocli tests.

Env defaults are set at module level, and credential/update-check patches are
started by a session-scoped autouse fixture. Because argocli initializes
lazily (only on first command instantiation), the fixture runs early enough to
be in effect, while still allowing the patches to be stopped cleanly at the end
of the session.
"""

import os
from unittest.mock import patch

import pytest

os.environ.setdefault("ARGOCLI_SERVER", "https://argo-server.example.com")
os.environ.setdefault("ARGOCLI_NAMESPACE", "test-namespace")
os.environ.setdefault("ARGOCLI_USERNAME", "test@example.com")


@pytest.fixture(autouse=True, scope="session")
def _global_mocks():
    """Patch credential lookup and the update checker for the whole session."""
    patchers = [
        patch("keyring.get_password", return_value="fake-api-token"),
        patch("cac_core.updatechecker.check_package_for_updates"),
    ]
    for p in patchers:
        p.start()
    yield
    for p in patchers:
        p.stop()
