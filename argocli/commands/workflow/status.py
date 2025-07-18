# pylint: disable=no-member

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
        # print(f"Checking status for workflow: {args.name}")
        client = self.argo_client
        workflow_status = client.get_workflow(args.name)
        print(
            workflow_status["status"]["phase"]
            if workflow_status
            else "Workflow not found or error occurred."
        )
