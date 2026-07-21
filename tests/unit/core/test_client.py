# pylint: disable=attribute-defined-outside-init, unused-import
"""
Unit tests for the Argo client.
"""

from unittest.mock import patch, MagicMock

import pytest
import requests

from argocli.core.client import ArgoClient


class TestArgoClient:
    """Tests for the ArgoClient class."""

    def setup_method(self):
        """Set up test environment before each test method."""
        self.client = ArgoClient(
            server="https://argo-server.example.com",
            namespace="test-namespace",
            api_token="test-token",
        )

    @patch("argocli.core.client.requests.get")
    def test_get_workflow_success(self, mock_get):
        """Test successful workflow retrieval."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metadata": {"name": "test-workflow"},
            "status": {"phase": "Running"},
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.client.get_workflow("test-workflow")

        # Assertions
        assert result["metadata"]["name"] == "test-workflow"
        assert result["status"]["phase"] == "Running"
        url = "https://argo-server.example.com/api/v1/workflows/test-namespace/test-workflow"
        headers = {"Authorization": "Bearer test-token"}
        mock_get.assert_called_once_with(
            url, headers=headers, timeout=10
        )

    @patch("argocli.core.client.requests.get")
    def test_get_workflow_failure(self, mock_get):
        """A non-2xx response is raised, not swallowed."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response

        # Call the method
        with pytest.raises(requests.HTTPError):
            self.client.get_workflow("test-workflow")
        mock_get.assert_called_once()

    @patch("argocli.core.client.requests.get")
    def test_list_workflows_success(self, mock_get):
        """Test successful workflow listing."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"metadata": {"name": "workflow-1"}, "status": {"phase": "Running"}},
                {"metadata": {"name": "workflow-2"}, "status": {"phase": "Succeeded"}},
            ]
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.client.list_workflows()

        # Assertions
        assert len(result) == 2
        assert result[0]["metadata"]["name"] == "workflow-1"
        assert result[1]["metadata"]["name"] == "workflow-2"
        mock_get.assert_called_once_with(
            "https://argo-server.example.com/api/v1/workflows/test-namespace",
            headers={"Authorization": "Bearer test-token"},
            timeout=10,
        )

    @patch("argocli.core.client.requests.get")
    def test_list_workflows_empty(self, mock_get):
        """Test empty workflow listing."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        # Call the method
        result = self.client.list_workflows()

        # Assertions
        assert len(result) == 0
        mock_get.assert_called_once()

    @patch("argocli.core.client.requests.get")
    def test_list_workflows_failure(self, mock_get):
        """A non-2xx response is raised, not swallowed."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response

        # Call the method
        with pytest.raises(requests.HTTPError):
            self.client.list_workflows()
        mock_get.assert_called_once()
