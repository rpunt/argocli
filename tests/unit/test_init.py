# pylint: disable=attribute-defined-outside-init
"""
Unit tests for the module initialization.
"""

from unittest.mock import patch, MagicMock
import os

# Test the module's initialization by importing it
def test_module_init_in_ci():
    """Test that the module initializes correctly in CI environments."""
    # Set up CI environment
    with patch.dict(os.environ, {"CI": "true"}):
        # This import should not fail in CI environment
        import argocli

        # Verify the client was set up with test values
        assert hasattr(argocli, 'ARGO_CLIENT')

@patch('cac_core.credentialmanager.CredentialManager')
def test_module_init_with_env_vars(mock_credential_manager):
    """Test that the module uses environment variables correctly."""
    # Mock credential manager
    mock_instance = MagicMock()
    mock_instance.get_credential.return_value = "test-token"
    mock_credential_manager.return_value = mock_instance

    # Set environment variables
    test_env = {
        "ARGOCLI_SERVER": "https://custom-server.example.com",
        "ARGOCLI_NAMESPACE": "custom-namespace",
        "ARGOCLI_USERNAME": "custom-user"
    }

    with patch.dict(os.environ, test_env):
        # Reimport to test with environment variables
        import importlib
        import argocli
        importlib.reload(argocli)

        # Check that environment variables were used
        from argocli.core.client import ArgoClient
        assert isinstance(argocli.ARGO_CLIENT, ArgoClient)
        assert argocli.argo_server == "https://custom-server.example.com"
        assert argocli.argo_namespace == "custom-namespace"
        assert argocli.argo_username == "custom-user"
