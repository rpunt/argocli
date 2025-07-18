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
        log.debug(f"Getting workflow {name} from server {self.server}")
        response = requests.get(
            f"{self.server}/api/v1/workflows/{self.namespace}/{name}",
            headers={"Authorization": f"Bearer {self.api_token}"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            log.error(f"Failed to get workflow {name}: {response.status_code} {response.text}")
            return None
