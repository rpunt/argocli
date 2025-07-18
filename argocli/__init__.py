# pylint: disable=broad-except, line-too-long

"""
module docstring
"""

# import os
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

CONFIG = cac.config.Config(__name__)

log.debug("user config path: %s", CONFIG.config_file)

# TODO: prompt user for server and username if not set
argo_server = CONFIG.get("server", "INVALID_DEFAULT") #.replace("https://", "")
if argo_server == "INVALID_DEFAULT":
    log.error("Invalid server in %s: %s", CONFIG.config_file, argo_server)
    sys.exit(1)

argo_namespace = CONFIG.get("namespace", "INVALID_DEFAULT")
if argo_namespace == "INVALID_DEFAULT":
    log.error("Invalid namespace in %s: %s", CONFIG.config_file, argo_namespace)
    sys.exit(1)

argo_username = CONFIG.get("username", "INVALID_DEFAULT")
if argo_username == "INVALID_DEFAULT":
    log.error("Invalid username in %s: %s", CONFIG.config_file, argo_username)
    sys.exit(1)

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
