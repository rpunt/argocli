# pylint: disable=missing-module-docstring
"""
Pytest configuration for argocli tests.

Mocks are set up at module level so they take effect before argocli
initializes on first command instantiation.
"""

import os
from unittest.mock import patch

os.environ.setdefault("ARGOCLI_SERVER", "https://argo-server.example.com")
os.environ.setdefault("ARGOCLI_NAMESPACE", "test-namespace")
os.environ.setdefault("ARGOCLI_USERNAME", "test@example.com")

patch("keyring.get_password", return_value="fake-api-token").start()
patch("cac_core.updatechecker.check_package_for_updates").start()
