#!/usr/bin/env python
# pylint: disable=no-member

"""
Argo client module.
"""

import cac_core as cac
import requests

log = cac.logger.new(__name__)


class ArgoClientError(Exception):
    """Raised for Argo API errors that are not plain HTTP failures."""


class ArgoClient:
    """
    Thin wrapper around the Argo Workflows REST API.

    Contract: every method returns the parsed response body on success or
    raises on failure (``requests.HTTPError`` for non-2xx responses,
    ``requests.RequestException`` for connection/timeout errors). Methods do not
    return sentinel values to signal failure; callers (the command layer) decide
    how to present errors and map them to exit codes.
    """

    def __init__(self, server, namespace, api_token=None):
        """
        Initialize the Argo client.

        Args:
            server: The Argo server
            namespace: The Argo namespace
            api_token: The Argo API token
        """
        self.server = server
        self.namespace = namespace
        self.api_token = api_token

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_token}"}

    def get_workflow(self, name):
        """
        Get a workflow by name.

        Args:
            name: The name of the workflow

        Returns:
            The workflow object

        Raises:
            requests.HTTPError: if the workflow cannot be retrieved (e.g. 404).
            requests.RequestException: on connection/timeout errors.
        """
        log.debug("Getting workflow %s from server %s", name, self.server)
        response = requests.get(
            f"{self.server}/api/v1/workflows/{self.namespace}/{name}",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def list_workflows(self):
        """
        List all workflows in the namespace.

        Returns:
            A list of workflow objects

        Raises:
            requests.HTTPError: if the list request fails.
            requests.RequestException: on connection/timeout errors.
        """
        log.debug("Listing workflows from server %s", self.server)
        response = requests.get(
            f"{self.server}/api/v1/workflows/{self.namespace}",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("items", [])
