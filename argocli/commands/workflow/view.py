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

from datetime import datetime
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
        workflow = self.argo_client.get_workflow(args.name)

        # Create a printer for output
        printer = cac.output.Output(args)

        if args.output == "json":
            # For JSON output, use the full workflow data
            printer.print_models(cac.model.Model(workflow))
            return 0

        # Convert UTC timestamps to local time
        started_time = self._convert_to_local_time(workflow['status'].get('startedAt')) if 'startedAt' in workflow['status'] else None
        finished_time = self._convert_to_local_time(workflow['status'].get('finishedAt')) if 'finishedAt' in workflow['status'] else None

        # Start with the workflow base information
        models = [
            cac.model.Model(
                {
                    "name": workflow['metadata']['name'],
                    "status": workflow['status']['phase'],
                    "progress": workflow['status'].get('progress', 0),
                    "started": started_time,
                    "finished": finished_time,
                }
            )
        ]

        # If we have nodes, add the task information as additional table rows
        if 'nodes' in workflow['status']:
            running_tasks = []
            completed_tasks = []
            pending_tasks = []

            # Extract task information directly
            for _, node in workflow['status']['nodes'].items():
                if 'displayName' in node and node.get('type') != 'StepGroup' and node.get('type') != 'Steps':
                    if node.get('phase') == 'Running':
                        # Create a task model that looks like a workflow row but with task info
                        running_tasks.append({
                            'name': f"↪ {node.get('displayName', '')}",  # Indent to show it's a subtask
                            'status': f"Running ({node.get('type', '')})",
                            'progress': node.get('progress', ''),
                            'started': self._convert_to_local_time(node.get('startedAt', '')),
                            'finished': ''
                        })
                    elif node.get('phase') in ('Succeeded', 'Failed') and 'finishedAt' in node:
                        completed_tasks.append({
                            'name': f"↪ {node.get('displayName', '')}",
                            'status': f"{node.get('phase', '')} ({node.get('type', '')})",
                            'progress': node.get('progress', '100%') if node.get('phase') == 'Succeeded' else '',
                            'started': self._convert_to_local_time(node.get('startedAt', '')),
                            'finished': self._convert_to_local_time(node.get('finishedAt', ''))
                        })
                    elif node.get('phase') == 'Pending':
                        # Add pending tasks (not yet started)
                        pending_tasks.append({
                            'name': f"↪ {node.get('displayName', '')}",
                            'status': f"Pending ({node.get('type', '')})",
                            'progress': '0%',
                            'started': '-',
                            'finished': '-'
                        })

            # Add tasks to models list - order: completed, running, pending
            completed_tasks.sort(key=lambda x: x.get('finished', ''))
            running_tasks.sort(key=lambda x: x.get('started', ''))
            pending_tasks.sort(key=lambda x: x.get('name', ''))
            for task in [*completed_tasks, *running_tasks, *pending_tasks]:
                models.append(cac.model.Model(task))

        # Print all models as a single table
        printer.print_models(models)
        return 0

    def _convert_to_local_time(self, timestamp):
        """
        Convert a UTC ISO timestamp to local time.
        Returns a formatted string in the local timezone.
        """
        if not timestamp:
            return timestamp

        try:
            # Parse the ISO 8601 timestamp
            if timestamp.endswith('Z'):
                timestamp = timestamp.replace('Z', '+00:00')

            dt = datetime.fromisoformat(timestamp)

            # Convert to local time
            local_dt = dt.astimezone()

            # Format the datetime in a user-friendly way
            return local_dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error parsing timestamp: {str(e)}")
            # If there's any error parsing, return the original timestamp
            return timestamp
