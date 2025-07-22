# pylint: disable=attribute-defined-outside-init
"""
Unit tests for workflow status command.
"""

from unittest.mock import patch, MagicMock
import argparse

from argocli.commands.workflow.status import WorkflowStatus


class TestWorkflowStatus:
    """Tests for the WorkflowStatus class."""

    def setup_method(self):
        """Set up test environment before each test method."""
        self.command = WorkflowStatus()
        self.command.argo_client = MagicMock()

    def test_define_arguments(self):
        """Test argument definition."""
        parser = argparse.ArgumentParser()
        result = self.command.define_arguments(parser)
        assert result is not None

    @patch("cac_core.output.Output")
    def test_execute_success(self, mock_output_class):
        """Test successful command execution."""
        # Setup
        args = MagicMock()
        args.name = "test-workflow"

        # Mock client response
        self.command.argo_client.get_workflow.return_value = {
            "metadata": {"name": "test-workflow"},
            "status": {"phase": "Running"}
        }

        # Mock output
        mock_output = MagicMock()
        mock_output_class.return_value = mock_output

        # Call the method
        self.command.execute(args)

        # Assertions
        self.command.argo_client.get_workflow.assert_called_once_with("test-workflow")
        mock_output_class.assert_called_once_with(args)
        mock_output.print_models.assert_called_once()

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
