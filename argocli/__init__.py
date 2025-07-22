# pylint: disable=broad-except, line-too-long, fixme

"""
module docstring
"""

import os
import sys
from importlib import metadata
import cac_core as cac

# import yaml
# import keyring
import argocli.core.client as client

if sys.version_info < (3, 9):
    print("This project requires Python 3.9 or higher.", file=sys.stderr)
    sys.exit(1)

cac.updatechecker.check_package_for_updates(__name__)

try:
    __version__ = metadata.version(__package__)
except Exception:
    __version__ = "#N/A"

log = cac.logger.new(__name__)
log.debug("Initializing %s version %s", __name__, __version__)

# Initialize config with module name
# Environment variables with prefix ARGOCLI_ will automatically be loaded
CONFIG = cac.config.Config(__name__)

log.debug("user config path: %s", CONFIG.config_file)

# Check if we're running in a CI/test environment
IN_CI = os.environ.get('CI') == 'true' or 'PYTEST_CURRENT_TEST' in os.environ

# The cac_core Config automatically loads values from environment variables
# Environment variable pattern:
#   <MODULE_NAME_UPPERCASE>_<UPPERCASE_CONFIG_KEY>
# For example:
#   - ARGOCLI_SERVER for the "server" config option
#   - ARGOCLI_NAMESPACE for the "namespace" config option
#   - ARGOCLI_USERNAME for the "username" config option
#
# This allows us to override config values via environment variables without modifying the config file

# Get server configuration with fallback for CI environments
argo_server = CONFIG.get("server", "https://example.com" if IN_CI else "INVALID_DEFAULT")
if argo_server == "INVALID_DEFAULT":
    log.error("Invalid server in %s: %s", CONFIG.config_file, argo_server)
    sys.exit(1)

# Get namespace configuration with fallback for CI environments
argo_namespace = CONFIG.get("namespace", "default" if IN_CI else "INVALID_DEFAULT")
if argo_namespace == "INVALID_DEFAULT":
    log.error("Invalid namespace in %s: %s", CONFIG.config_file, argo_namespace)
    sys.exit(1)

# Get username configuration with fallback for CI environments
argo_username = CONFIG.get("username", "test-user" if IN_CI else "INVALID_DEFAULT")
if argo_username == "INVALID_DEFAULT":
    log.error("Invalid username in %s: %s", CONFIG.config_file, argo_username)
    sys.exit(1)

# In CI environment, use a dummy token for testing
if IN_CI:
    argo_api_token = "test-token-for-ci"
    log.info("Running in CI/test environment, using test credentials")
else:
    credentialmanager = cac.credentialmanager.CredentialManager(__name__)
    argo_api_token = credentialmanager.get_credential(
        argo_username,
        "Argo API key",
    )

    if not argo_api_token:
        # TODO: update the docs
        log.error(
            "API token not found for %s; see https://github.com/rpunt/%s/blob/main/README.md#authentication",
            argo_username,
            __name__.replace("_", "-"),
        )
        sys.exit(1)

ARGO_CLIENT = client.ArgoClient(argo_server, argo_namespace, argo_api_token)

__all__ = ["ARGO_CLIENT", "CONFIG", "log"]
