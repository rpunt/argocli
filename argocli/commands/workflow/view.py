# pylint: disable=no-member, line-too-long, broad-except

"""
Workflow view module.

This module provides functionality to view detailed information about a specific
Argo workflow. It fetches workflow data and displays either a formatted summary
or the complete JSON representation based on the output format requested.

The view command requires a workflow name and displays information such as
status, progress, and timestamps for the workflow execution.

For workflows in the "Running" state, it also displays information about
the currently running tasks, including their names, types, and start times.
This helps users track the progress of ongoing workflows more effectively.
"""

import cac_core as cac
from argocli.commands.workflow import ArgoWorkflowCommand

class WorkflowView(ArgoWorkflowCommand):
    """
    Command to view the details of a workflow.

    Displays general workflow information including status, progress, and timestamps.
    For running workflows, shows details of currently executing tasks.
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

        # Basic workflow information for all outputs
        model_data = {
            "name": workflow['metadata']['name'],
            "status": workflow['status']['phase'],
            "progress": workflow['status'].get('progress', 0),
            "started": workflow['status']['startedAt'] if 'startedAt' in workflow['status'] else None,
            "finished": workflow['status']['finishedAt'] if 'finishedAt' in workflow['status'] else None,
        }

        # Create a printer for output
        printer = cac.output.Output(args)

        try:
            if args.output == "json":
                # For JSON output, use the full workflow data
                model = cac.model.Model(workflow)
                printer.print_models(model)
            else:
                # For other formats, prepare models with workflow and task information
                models = []

                # Start with the workflow base information
                models.append(cac.model.Model(model_data))

                # If we have nodes, add the task information as additional table rows
                if 'nodes' in workflow['status']:
                    running_tasks = []
                    completed_tasks = []

                    # Extract task information directly
                    for _, node in workflow['status']['nodes'].items():
                        if 'displayName' in node and node.get('type') != 'StepGroup' and node.get('type') != 'Steps':
                            if node.get('phase') == 'Running':
                                # Create a task model that looks like a workflow row but with task info
                                task_model = {
                                    'name': f"↪ {node.get('displayName', '')}",  # Indent to show it's a subtask
                                    'status': f"Running ({node.get('type', '')})",
                                    'progress': node.get('progress', ''),
                                    'started': node.get('startedAt', ''),
                                    'finished': ''
                                }
                                running_tasks.append(task_model)
                            elif node.get('phase') in ('Succeeded', 'Failed') and 'finishedAt' in node:
                                # Add only recent completions (we'll sort and limit later)
                                task_model = {
                                    'name': f"↪ {node.get('displayName', '')}",
                                    'status': f"{node.get('phase', '')} ({node.get('type', '')})",
                                    'progress': node.get('progress', '100%') if node.get('phase') == 'Succeeded' else '',
                                    'started': node.get('startedAt', ''),
                                    'finished': node.get('finishedAt', '')
                                }
                                completed_tasks.append(task_model)

                    # Sort tasks
                    if running_tasks:
                        running_tasks.sort(key=lambda x: x.get('started', ''))
                        # Add all running tasks to the models list
                        for task in running_tasks:
                            models.append(cac.model.Model(task))

                    if completed_tasks:
                        # Sort by finished time (most recent first) and take only the 3 most recent
                        completed_tasks.sort(key=lambda x: x.get('finished', ''), reverse=True)
                        for task in completed_tasks[:3]:  # Show only 3 most recent
                            models.append(cac.model.Model(task))

                # Print all models as a single table
                printer.print_models(models)

        except Exception as e:
            # If there's an error, log it but don't crash
            print(f"Warning: Error displaying detailed workflow information: {str(e)}")

            # Create a simple model with just the basic information if we haven't printed it yet
            if args.output == "json":
                basic_model = cac.model.Model({
                    "name": workflow['metadata']['name'],
                    "status": workflow['status']['phase'],
                    "progress": workflow['status'].get('progress', 0),
                    "started": workflow['status']['startedAt'] if 'startedAt' in workflow['status'] else None,
                    "finished": workflow['status']['finishedAt'] if 'finishedAt' in workflow['status'] else None,
                })
                printer.print_models(basic_model)
