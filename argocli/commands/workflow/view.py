# pylint: disable=no-member, line-too-long

"""
Workflow view module.

This module provides functionality to view detailed information about a specific
Argo workflow. It fetches workflow data and displays either a formatted summary
or the complete JSON representation based on the output format requested.

The view command requires a workflow name and displays information such as
status, progress, and timestamps for the workflow execution.
"""

import cac_core as cac
from argocli.commands.workflow import ArgoWorkflowCommand

class WorkflowView(ArgoWorkflowCommand):
    """
    Command to view the details of a workflow.
    """

    def define_arguments(self, parser):
        """
        Define command-specific arguments for viewing workflow details.
        """
        super().define_arguments(parser)
        return parser

    def execute(self, args):
        """
        Execute the command to check the workflow status.
        """
        client = self.argo_client
        workflow = client.get_workflow(args.name)
        if not workflow:
            print(f"Workflow '{args.name}' not found.")
            return
        if args.output == "json":
            model = cac.model.Model(workflow)
        else:
            model = cac.model.Model(
                {
                    "name": workflow['metadata']['name'],
                    "status": workflow['status']['phase'],
                    "progress": workflow['status'].get('progress', 0),
                    "started": workflow['status']['startedAt'] if 'startedAt' in workflow['status'] else None,
                    "finished": workflow['status']['finishedAt'] if 'finishedAt' in workflow['status'] else None,
                }
            )

        printer = cac.output.Output(args)
        printer.print_models(model)
