# pylint: disable=attribute-defined-outside-init
"""
Unit tests for workflow browse command.
"""

from unittest.mock import patch, MagicMock
import argparse

from argocli.commands.workflow.browse import WorkflowBrowse


class TestWorkflowBrowse:
    """Tests for the WorkflowBrowse class."""

    def setup_method(self):
        """Set up test environment before each test method."""
        self.command = WorkflowBrowse()
        self.command.argo_client = MagicMock()
        self.command.log = MagicMock()

    def test_define_arguments(self):
        """Test argument definition."""
        parser = argparse.ArgumentParser()
        result = self.command.define_arguments(parser)
        assert result is not None

    @patch("webbrowser.open")
    def test_execute_with_valid_workflow(self, mock_webbrowser_open):
        """Test opening a workflow in a browser when the workflow exists."""
        # Setup
        args = MagicMock()
        args.name = "test-workflow"

        # Mock client response
        workflow_data = {
            "metadata": {"name": "test-workflow"},
            "spec": {"entrypoint": "main"}
        }
        self.command.argo_client.get_workflow.return_value = workflow_data

        # Mock client properties
        self.command.argo_client.server = "https://argo-server.example.com"
        self.command.argo_client.namespace = "argo"

        # Call the method
        self.command.execute(args)

        # Assertions
        self.command.argo_client.get_workflow.assert_called_once_with("test-workflow")
        self.command.log.debug.assert_called_once()
        mock_webbrowser_open.assert_called_once_with(
            "https://argo-server.example.com/workflows/argo/test-workflow"
        )

    def test_execute_workflow_not_found(self):
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
        self.command.log.error.assert_called_once_with(
            "Workflow '%s' not found.", "non-existent-workflow"
        )
