# pylint: disable=line-too-long, attribute-defined-outside-init
"""
Unit tests for workflow list command.
"""

from unittest.mock import patch, MagicMock
import argparse

from argocli.commands.workflow.list import WorkflowList


class TestWorkflowList:
    """Tests for the WorkflowList class."""

    def setup_method(self):
        """Set up test environment before each test method."""
        self.command = WorkflowList()
        self.command.argo_client = MagicMock()

    def test_define_arguments(self):
        """Test argument definition."""
        parser = argparse.ArgumentParser()
        result = self.command.define_arguments(parser)
        assert result is not None

        # Parse arguments to see if the name argument is correctly defined
        args = parser.parse_args([])
        assert hasattr(args, "name")
        assert args.name is None

        # Test with name argument
        args = parser.parse_args(["--name", "test-workflow"])
        assert args.name == "test-workflow"

    @patch("cac_core.output.Output")
    def test_execute_list_all(self, mock_output_class):
        """Test listing all workflows."""
        # Setup
        args = MagicMock()
        args.name = None

        # Mock client response
        workflows = [
            {"metadata": {"name": "workflow-1"}, "status": {"phase": "Running", "progress": "50%", "startedAt": "2023-01-01T00:00:00Z"}},
            {"metadata": {"name": "workflow-2"}, "status": {"phase": "Succeeded", "progress": "100%", "startedAt": "2023-01-01T00:00:00Z", "finishedAt": "2023-01-01T01:00:00Z"}}
        ]
        self.command.argo_client.list_workflows.return_value = workflows

        # Mock output
        mock_output = MagicMock()
        mock_output_class.return_value = mock_output

        # Call the method
        self.command.execute(args)

        # Assertions
        self.command.argo_client.list_workflows.assert_called_once()
        mock_output_class.assert_called_once_with(args)
        mock_output.print_models.assert_called_once()

        # Check that all workflows are included
        models = mock_output.print_models.call_args[0][0]
        assert len(models) == 2
        assert models[0].name == "workflow-1"
        assert models[1].name == "workflow-2"

    @patch("cac_core.output.Output")
    def test_execute_filtered_list(self, mock_output_class):
        """Test listing workflows with a name filter."""
        # Setup
        args = MagicMock()
        args.name = "flow-1"

        # Mock client response
        workflows = [
            {"metadata": {"name": "workflow-1"}, "status": {"phase": "Running", "progress": "50%", "startedAt": "2023-01-01T00:00:00Z"}},
            {"metadata": {"name": "workflow-2"}, "status": {"phase": "Succeeded", "progress": "100%", "startedAt": "2023-01-01T00:00:00Z", "finishedAt": "2023-01-01T01:00:00Z"}}
        ]
        self.command.argo_client.list_workflows.return_value = workflows

        # Mock output
        mock_output = MagicMock()
        mock_output_class.return_value = mock_output

        # Call the method
        self.command.execute(args)

        # Assertions
        mock_output.print_models.assert_called_once()

        # Check that only filtered workflows are included
        models = mock_output.print_models.call_args[0][0]
        assert len(models) == 1
        assert models[0].name == "workflow-1"

    def test_execute_no_workflows(self):
        """Test execution when no workflows are found."""
        # Setup
        args = MagicMock()
        args.name = None
        self.command.log = MagicMock()

        # Mock client response
        self.command.argo_client.list_workflows.return_value = []

        # Call the method
        self.command.execute(args)

        # Assertions
        self.command.argo_client.list_workflows.assert_called_once()
        self.command.log.info.assert_called_once_with("No workflows found.")

    def test_execute_no_matching_workflows(self):
        """Test execution when no workflows match the filter."""
        # Setup
        args = MagicMock()
        args.name = "nonexistent"
        self.command.log = MagicMock()

        # Mock client response
        workflows = [
            {"metadata": {"name": "workflow-1"}, "status": {"phase": "Running"}},
            {"metadata": {"name": "workflow-2"}, "status": {"phase": "Succeeded"}}
        ]
        self.command.argo_client.list_workflows.return_value = workflows

        # Call the method
        self.command.execute(args)

        # Assertions
        self.command.argo_client.list_workflows.assert_called_once()
        self.command.log.info.assert_called_once_with(
            "No workflows found matching '%s'.", "nonexistent"
        )
