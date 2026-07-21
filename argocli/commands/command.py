#!/usr/bin/env python

"""
Base class for all Argo CLI commands.

This module provides a base class that all command actions should inherit from,
allowing for common functionality and arguments to be shared across different
command actions.
"""

import abc
from typing import Optional

import requests
from cac_core.command import Command

import argocli
from argocli import log
from argocli.core.client import ArgoClient, ArgoClientError


class ArgoCommand(Command):
    """
    Base class for all Argo CLI commands.

    This class defines common methods and properties that should be shared
    across all command actions, such as common arguments, authentication,
    and utility functions.
    """

    def __init__(self):
        """
        Initialize the command with a logger and configuration.

        Configuration is loaded eagerly (it is network-free and needed for
        argument defaults), but the Argo client is resolved lazily on first
        access via the ``argo_client`` property so that argument parsing and
        ``--help`` do not require credentials.
        """
        super().__init__()
        self.log = log
        self.config = argocli.CONFIG
        self._argo_client: Optional[ArgoClient] = None

    @property
    def argo_client(self) -> ArgoClient:
        """The Argo client, resolved on first access."""
        if self._argo_client is None:
            self._argo_client = argocli.ARGO_CLIENT
        return self._argo_client

    @argo_client.setter
    def argo_client(self, value: ArgoClient) -> None:
        self._argo_client = value

    @abc.abstractmethod
    def define_arguments(self, parser):
        """
        Define command-specific arguments.

        This method must be implemented by subclasses to add
        command-specific arguments to the parser.

        Args:
            parser: The argument parser to add arguments to

        Returns:
            The updated argument parser
        """
        super().define_arguments(parser)
        return parser

    def handle_exception(self, exc):
        """
        Give Argo API errors a friendly message; defer the rest to the base.

        A 404 from the Argo API means the requested workflow does not exist;
        other HTTP/connection errors get a concise message. Everything else
        falls back to the base template (logged with a traceback under
        ``--verbose``).

        Args:
            exc: The exception raised by ``execute()``.

        Returns:
            int: A non-zero exit code.
        """
        if isinstance(exc, ArgoClientError):
            self.log.error("%s", exc)
            return 1
        if isinstance(exc, requests.HTTPError):
            status = exc.response.status_code if exc.response is not None else "?"
            if status == 404:
                self.log.error("Workflow not found.")
            else:
                self.log.error("Argo API request failed: %s", exc)
            return 1
        if isinstance(exc, requests.RequestException):
            self.log.error("Could not reach the Argo server: %s", exc)
            return 1
        return super().handle_exception(exc)

    @abc.abstractmethod
    def execute(self, args):
        """
        Perform the command's work.

        Subclasses implement this as straight-line logic. Errors raised by the
        Argo client propagate to ``run()``, which logs them and returns a
        non-zero exit code, so ``execute()`` does not need to wrap client calls
        in try/except. Return ``None``/``0`` on success, or a non-zero int for
        command-specific validation failures.

        Args:
            args: The parsed arguments

        Returns:
            Optional[int]: ``None``/``0`` on success, non-zero on failure.
        """
        raise NotImplementedError("Command subclasses must implement execute()")
