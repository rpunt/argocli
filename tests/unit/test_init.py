# pylint: disable=protected-access, import-outside-toplevel
"""
Integration tests for argocli module initialization.

Tests config loading, credential retrieval, lazy attribute access, and the
error paths in _initialize_client.
"""

import os

import pytest


class TestModuleInitialization:
    """Tests for lazy module initialization."""

    def test_initialize_success(self):
        """_initialize() sets up config and client state."""
        import argocli

        argocli._initialized = False
        argocli._module_state.clear()

        argocli._initialize()

        assert argocli._initialized is True
        assert "CONFIG" in argocli._module_state
        assert "ARGO_CLIENT" in argocli._module_state

        config = argocli._module_state["CONFIG"]
        assert config.get("server") == os.environ["ARGOCLI_SERVER"]
        assert config.get("namespace") == os.environ["ARGOCLI_NAMESPACE"]
        assert config.get("username") == os.environ["ARGOCLI_USERNAME"]

    def test_lazy_attribute_access(self):
        """Accessing CONFIG/ARGO_CLIENT triggers initialization."""
        import argocli
        from argocli.core.client import ArgoClient

        argocli._initialized = False
        argocli._module_state.clear()

        client = argocli.ARGO_CLIENT
        assert isinstance(client, ArgoClient)
        assert argocli._initialized is True

        config = argocli.CONFIG
        assert config.get("server") == os.environ["ARGOCLI_SERVER"]

    def test_invalid_attribute_access(self):
        """Accessing an unknown attribute raises AttributeError."""
        import argocli

        with pytest.raises(AttributeError, match="has no attribute 'INVALID_ATTR'"):
            _ = argocli.INVALID_ATTR

    def test_initialize_idempotent(self):
        """Calling _initialize() multiple times is safe."""
        import argocli

        argocli._initialize()
        argocli._initialize()

        assert argocli._initialized is True
        assert "ARGO_CLIENT" in argocli._module_state


class TestClientInitErrors:
    """Error paths in _initialize_client (missing credentials)."""

    @pytest.fixture
    def reset_client_state(self):
        """Force _initialize_client to re-run and clean up afterward."""
        import argocli

        argocli._module_state.pop("ARGO_CLIENT", None)
        argocli._initialized = False
        yield
        argocli._module_state.pop("ARGO_CLIENT", None)
        argocli._initialized = False

    def test_missing_token_exits(self, reset_client_state, monkeypatch):
        """No stored credential -> hard exit with a clear message."""
        import cac_core as cac
        import argocli

        monkeypatch.setattr(
            cac.credentialmanager.CredentialManager,
            "get_credential",
            lambda self, *a, **k: None,
        )
        with pytest.raises(SystemExit) as exc:
            argocli._initialize_client()
        assert exc.value.code == 1
