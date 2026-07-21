# pylint: disable=broad-except, line-too-long

"""
Package initialization for the Argo CLI.

Discovery, argument parsing, shell completion, and dispatch are owned by the
shared ``cac_core`` framework (see ``main`` below). This module only supplies the
lazily-initialized ``CONFIG`` and ``ARGO_CLIENT`` singletons that commands
consume, plus the console-script entry point.
"""

import sys
from importlib import metadata
from typing import TYPE_CHECKING, cast

import cac_core as cac
from cac_core.cli import make_main

from argocli.core import client

if TYPE_CHECKING:
    # These module-level attributes are provided lazily via ``__getattr__``;
    # declare their types so consumers (and ``__all__``) see them statically.
    from cac_core.config import Config

    CONFIG: Config
    ARGO_CLIENT: client.ArgoClient

try:
    __version__ = metadata.version(__name__)
except Exception:
    __version__ = "#N/A"

log = cac.logger.new(__name__)

_initialized = False
_module_state: dict[str, object] = {}


def _initialize_config():
    """
    Load configuration and run first-run prompts.

    This is deliberately network-free: it only reads/writes the local config
    file and prompts on first run. It must remain cheap because it runs for
    every command during argument parsing (including ``--help``).
    """
    if "CONFIG" in _module_state:
        return

    log.debug("Initializing %s config version %s", __name__, __version__)

    config = cac.config.Config(__name__)
    log.debug("user config path: %s", config.config_file)

    # First-run setup: prompt for any keys still at their sentinel. ensure_keys
    # skips prompting during shell completion (argcomplete hijacks stdio, so an
    # interactive prompt would hang the shell); the sentinel is left in place and
    # every consumer treats it as "no value".
    config.ensure_keys(
        [
            ("server", "Enter your Argo server URL: ", True, None),
            ("namespace", "Enter your Argo namespace: ", True, None),
            ("username", "Enter your Argo username (email): ", True, None),
        ]
    )

    _module_state["CONFIG"] = config


def _initialize_client():
    """
    Connect to the Argo server.

    Requires config and credentials, so it is only invoked when a command
    actually needs the client (i.e. at execution time), not during argument
    parsing.
    """
    global _initialized  # pylint: disable=global-statement
    if "ARGO_CLIENT" in _module_state:
        return

    _initialize_config()
    config = cast(cac.config.Config, _module_state["CONFIG"])

    cac.updatechecker.check_package_for_updates(__name__)

    argo_server = config.get("server", "INVALID_DEFAULT")
    argo_namespace = config.get("namespace", "INVALID_DEFAULT")
    argo_username = config.get("username", "INVALID_DEFAULT")

    credentialmanager = cac.credentialmanager.CredentialManager(__name__)
    argo_api_token = credentialmanager.get_credential(argo_username, "Argo API key")
    if not argo_api_token:
        log.error(
            "API token not found for %s; see https://github.com/rpunt/%s/blob/main/README.md#authentication",
            argo_username,
            __name__.replace("_", "-"),
        )
        sys.exit(1)

    _module_state["ARGO_CLIENT"] = client.ArgoClient(
        argo_server, argo_namespace, argo_api_token
    )
    _initialized = True


def _initialize():
    """Fully initialize the module (config + client).

    Retained for backwards compatibility; new code should rely on lazy
    attribute access (``argocli.CONFIG`` / ``argocli.ARGO_CLIENT``).
    """
    _initialize_client()


def __getattr__(name):
    """Lazy initialization when accessing module-level attributes.

    Accessing ``CONFIG`` only loads the local config; accessing ``ARGO_CLIENT``
    additionally requires credentials. This keeps config-only consumers (e.g.
    argument defaults) from triggering credential lookups.
    """
    if name == "CONFIG":
        _initialize_config()
        return _module_state["CONFIG"]
    if name == "ARGO_CLIENT":
        _initialize_client()
        return _module_state["ARGO_CLIENT"]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Console-script entry point (see [project.scripts] -> ``argocli = argocli:main``).
# The framework owns discovery, argument parsing, completion, and dispatch; this
# module only supplies the package name, program name, and description.
main = make_main("argocli", "argocli", "Argo CLI tool")


__all__ = ["ARGO_CLIENT", "CONFIG", "log", "main", "_initialize"]
