# pylint: disable=no-member

"""
Workflow status module.

This module provides functionality to check the current status of a specific
Argo workflow. It retrieves the workflow by name and displays its execution phase
(e.g., Running, Succeeded, Failed, Error).

This command requires a workflow name parameter and returns a simple status output
that can be easily used in scripts or monitoring.
"""

import cac_core as cac
from argocli.commands.workflow import ArgoWorkflowCommand

class WorkflowStatus(ArgoWorkflowCommand):
    """
    Command to check the status of a workflow.
    """

    def define_arguments(self, parser):
        """
        Define command-specific arguments for checking workflow status.
        """
        super().define_arguments(parser)
        return parser

    def execute(self, args):
        """
        Execute the command to check the workflow status.
        """
        workflow = self.argo_client.get_workflow(args.name)

        model = cac.model.Model(
            {
                "name": workflow["metadata"]["name"],
                "status": workflow["status"]["phase"],
            }
        )

        printer = cac.output.Output(args)
        printer.print_models(model)
        return 0
