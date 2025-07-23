# pylint: disable=no-member, line-too-long

"""
Workflow browse module.

This module provides functionality to open Argo workflows in a web browser
for visualization and further interaction. It enables users to quickly access
the web UI for a specific workflow by name.
"""

import webbrowser
from argocli.commands.workflow import ArgoWorkflowCommand

class WorkflowBrowse(ArgoWorkflowCommand):
    """
    Command to open a workflow in the default web browser.

    This command fetches workflow information and constructs a URL to the
    Argo Workflows UI for the specified workflow. The workflow is then opened
    in the system's default web browser for visual inspection and interaction.
    """

    def define_arguments(self, parser):
        """
        Define command-specific arguments for the browse command.

        The browse command relies on the name argument defined in the parent class
        to identify which workflow to open in the browser.
        """
        super().define_arguments(parser)
        return parser

    def execute(self, args):
        """
        Execute the browse command to open the workflow in a web browser.

        This method:
        1. Retrieves the workflow information from the Argo API
        2. Constructs a URL to access the workflow in the Argo UI
        3. Opens the default web browser to display the workflow

        Args:
            args: Command-line arguments containing the workflow name
        """
        self.log.debug("Opening workflow %s in a browser", args.name)
        client = self.argo_client
        workflow = client.get_workflow(args.name)

        if not workflow:
            self.log.error("Workflow '%s' not found.", args.name)
            return

        # Open the workflow in the default web browser
        workflow_url = f"{client.server}/workflows/{client.namespace}/{workflow['metadata']['name']}"
        webbrowser.open(workflow_url)
