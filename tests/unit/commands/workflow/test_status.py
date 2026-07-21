# pylint: disable=attribute-defined-outside-init
"""
Unit tests for workflow status command.
"""

from unittest.mock import patch, MagicMock
import argparse

import requests

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

    def test_execute_workflow_not_found(self):
        """A 404 from the client maps to a non-zero exit code via run()."""
        # Setup
        args = MagicMock()
        args.name = "non-existent-workflow"
        self.command.log = MagicMock()

        # Mock client to raise a 404 like the real API
        response = MagicMock()
        response.status_code = 404
        self.command.argo_client.get_workflow.side_effect = requests.HTTPError(
            response=response
        )

        # run() wraps execute() and routes the error through handle_exception
        exit_code = self.command.run(args)

        # Assertions
        assert exit_code == 1
        self.command.argo_client.get_workflow.assert_called_once_with("non-existent-workflow")
        self.command.log.error.assert_called_once_with("Workflow not found.")
