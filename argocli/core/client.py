#!/usr/bin/env python
# pylint: disable=no-member

"""
Argo client module.
"""

import cac_core as cac
import requests

log = cac.logger.new(__name__)


class ArgoClient:
    """
    Argo client class.
    """

    def __init__(self, server, namespace, api_token=None):
        """
        Initialize the Argo client.

        Args:
            server: The Argo server
            username: The Argo username
            api_token: The Argo API token
        """
        self.server = server
        self.namespace = namespace
        self.api_token = api_token

    def get_workflow(self, name):
        """
        Get a workflow by name.

        Args:
            name: The name of the workflow

        Returns:
            The workflow object
        """
        log.debug("Getting workflow %s from server %s", name, self.server)
        response = requests.get(
            f"{self.server}/api/v1/workflows/{self.namespace}/{name}",
            headers={"Authorization": f"Bearer {self.api_token}"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            log.error("Failed to get workflow %s: %s %s", name, response.status_code, response.text)
            return None

    def list_workflows(self):
        """
        List all workflows in the namespace.

        Returns:
            A list of workflow objects
        """
        log.debug("Listing workflows from server %s", self.server)
        response = requests.get(
            f"{self.server}/api/v1/workflows/{self.namespace}",
            headers={"Authorization": f"Bearer {self.api_token}"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            log.error("Failed to list workflows: %s %s", response.status_code, response.text)
            return []
