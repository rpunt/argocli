# pylint: disable=no-member, line-too-long

"""
Workflow list module.

This module provides functionality to list all Argo workflows with optional
filtering by name. The implementation supports fuzzy matching of workflow names,
allowing users to find workflows without knowing their exact names.
"""

import cac_core as cac
from argocli.commands.workflow import ArgoWorkflowCommand

class WorkflowList(ArgoWorkflowCommand):
    """
    Command to list all workflows.
    """

    def define_arguments(self, parser):
        """
        Define command-specific arguments for listing workflows.
        """
        # name argument is optional for listing workflows - used for filtering
        parser.add_argument(
            "-n",
            "--name",
            help="Filter workflows by name (fuzzy match)",
            required=False,
        )
        super().define_arguments(parser)
        return parser

    def execute(self, args):
        """
        Execute the command to check the workflow status.
        """
        client = self.argo_client
        workflows = client.list_workflows()
        if not workflows:
            print("No workflows found.")
            return

        models = []
        # Filter workflows if name is provided (fuzzy match)
        filter_name = args.name.lower() if args.name else None

        for wf in workflows:
            workflow_name = wf['metadata']['name']

            # If name filter is provided and doesn't match, skip this workflow
            if filter_name and filter_name not in workflow_name.lower():
                continue

            model = cac.model.Model(
                {
                    "name": workflow_name,
                    "status": wf['status']['phase'],
                    "progress": wf['status'].get('progress', 0),
                    "started": wf['status']['startedAt'] if 'startedAt' in wf['status'] else None,
                    "finished": wf['status']['finishedAt'] if 'finishedAt' in wf['status'] else None,
                }
            )
            models.append(model)

        if not models and filter_name:
            print(f"No workflows found matching '{args.name}'.")
            return

        printer = cac.output.Output(args)
        printer.print_models(models)
