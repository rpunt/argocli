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

        # Verify that the summary data is passed to the output formatter
        models = mock_output.print_models.call_args[0][0]
        assert isinstance(models, list)
        assert len(models) >= 1

        # Check the first model (workflow info)
        workflow_model = models[0]
        assert workflow_model.name == "test-workflow"
        assert workflow_model.status == "Running"
        assert workflow_model.progress == "50%"
        assert workflow_model.started == "2023-01-01T00:00:00Z"
        assert workflow_model.finished is None

    @patch("cac_core.output.Output")
    def test_execute_with_running_tasks(self, mock_output_class):
        """Test viewing a workflow with running tasks."""
        # Setup
        args = MagicMock()
        args.name = "test-workflow"
        args.output = "table"

        # Mock client response with running nodes
        workflow_data = {
            "metadata": {"name": "test-workflow"},
            "spec": {"entrypoint": "main"},
            "status": {
                "phase": "Running",
                "progress": "50%",
                "startedAt": "2023-01-01T00:00:00Z",
                "nodes": {
                    "node1": {
                        "id": "node1",
                        "name": "task-1",
                        "displayName": "running-task-1",
                        "type": "Pod",
                        "phase": "Running",
                        "startedAt": "2023-01-01T00:05:00Z"
                    },
                    "node2": {
                        "id": "node2",
                        "name": "task-2",
                        "displayName": "completed-task",
                        "type": "Pod",
                        "phase": "Succeeded",
                        "startedAt": "2023-01-01T00:01:00Z",
                        "finishedAt": "2023-01-01T00:03:00Z"
                    }
                }
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

        # Verify the model list contains workflow and task data
        models = mock_output.print_models.call_args[0][0]
        assert isinstance(models, list)
        assert len(models) >= 3  # Should include workflow info, running task, and completed task

        # Check first model (workflow info)
        workflow_model = models[0]
        assert workflow_model.name == "test-workflow"
        assert workflow_model.status == "Running"

        # Check for running task
        found_running_task = False
        found_completed_task = False

        for model in models[1:]:  # Skip the workflow model
            if "running-task-1" in model.name:
                found_running_task = True
                assert "Running" in model.status
            elif "completed-task" in model.name:
                found_completed_task = True
                assert "Succeeded" in model.status

        assert found_running_task, "Running task not found in models"
        assert found_completed_task, "Completed task not found in models"

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
