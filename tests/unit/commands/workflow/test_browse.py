# pylint: disable=attribute-defined-outside-init
"""
Unit tests for workflow browse command.
"""

from unittest.mock import patch, MagicMock
import argparse

import requests

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

    @patch("webbrowser.open")
    def test_execute_workflow_not_found(self, mock_webbrowser_open):
        """A 404 from the client maps to a non-zero exit code and no browser open."""
        # Setup
        args = MagicMock()
        args.name = "non-existent-workflow"

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
        mock_webbrowser_open.assert_not_called()
