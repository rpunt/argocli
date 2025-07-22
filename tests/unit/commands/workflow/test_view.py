# pylint: disable=attribute-defined-outside-init
"""
Unit tests for workflow view command.
"""

from unittest.mock import patch, MagicMock
import argparse

from argocli.commands.workflow.view import WorkflowView


class TestWorkflowView:
    """Tests for the WorkflowView class."""

    def setup_method(self):
        """Set up test environment before each test method."""
        self.command = WorkflowView()
        self.command.argo_client = MagicMock()

    def test_define_arguments(self):
        """Test argument definition."""
        parser = argparse.ArgumentParser()
        result = self.command.define_arguments(parser)
        assert result is not None

    @patch("cac_core.output.Output")
    def test_execute_with_json_output(self, mock_output_class):
        """Test viewing a workflow with JSON output."""
        # Setup
        args = MagicMock()
        args.name = "test-workflow"
        args.output = "json"

        # Mock client response
        workflow_data = {
            "metadata": {"name": "test-workflow"},
            "spec": {"entrypoint": "main"},
            "status": {"phase": "Running", "startedAt": "2023-01-01T00:00:00Z"}
        }
        self.command.argo_client.get_workflow.return_value = workflow_data

        # Mock output
        mock_output = MagicMock()
        mock_output_class.return_value = mock_output

        # Call the method
        self.command.execute(args)

        # Assertions
        self.command.argo_client.get_workflow.assert_called_once_with("test-workflow")
        mock_output_class.assert_called_once_with(args)
        mock_output.print_models.assert_called_once()

        # Verify that the full workflow data is passed to the output formatter
        model = mock_output.print_models.call_args[0][0]
        assert hasattr(model, "metadata")
        assert hasattr(model, "spec")
        assert hasattr(model, "status")

    @patch("cac_core.output.Output")
    def test_execute_with_table_output(self, mock_output_class):
        """Test viewing a workflow with table output."""
        # Setup
        args = MagicMock()
        args.name = "test-workflow"
        args.output = "table"

        # Mock client response
        workflow_data = {
            "metadata": {"name": "test-workflow"},
            "spec": {"entrypoint": "main"},
            "status": {
                "phase": "Running",
                "progress": "50%",
                "startedAt": "2023-01-01T00:00:00Z"
            }
        }
        self.command.argo_client.get_workflow.return_value = workflow_data

        # Mock output
        mock_output = MagicMock()
        mock_output_class.return_value = mock_output

        # Call the method
        self.command.execute(args)

        # Assertions
        self.command.argo_client.get_workflow.assert_called_once_with("test-workflow")
        mock_output_class.assert_called_once_with(args)
        mock_output.print_models.assert_called_once()

        # Verify that only the summary data is passed to the output formatter
        model = mock_output.print_models.call_args[0][0]
        assert model.name == "test-workflow"
        assert model.status == "Running"
        assert model.progress == "50%"
        assert model.started == "2023-01-01T00:00:00Z"
        assert model.finished is None

    @patch("builtins.print")
    def test_execute_workflow_not_found(self, mock_print):
        """Test execution when workflow is not found."""
        # Setup
        args = MagicMock()
        args.name = "non-existent-workflow"

        # Mock client response
        self.command.argo_client.get_workflow.return_value = None

        # Call the method
        self.command.execute(args)

        # Assertions
        self.command.argo_client.get_workflow.assert_called_once_with("non-existent-workflow")
        mock_print.assert_called_once_with("Workflow 'non-existent-workflow' not found.")
