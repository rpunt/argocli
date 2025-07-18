#!/usr/bin/env python

"""
Base class for all Argo CLI commands.

This module provides a base class that all command actions should inherit from,
allowing for common functionality and arguments to be shared across different
command actions.
"""

import abc
from cac_core.command import Command
from argocli import CONFIG, ARGO_CLIENT, log


class ArgoCommand(Command):
    """
    Base class for all Argo CLI commands.

    This class defines common methods and properties that should be shared
    across all command actions, such as common arguments, authentication,
    and utility functions.
    """

    def __init__(self):
        """
        Initialize the command with a logger and Argo client.
        """
        super().__init__()
        self.log = log
        self.argo_client = ARGO_CLIENT
        self.config = CONFIG

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

    @abc.abstractmethod
    def execute(self, args):
        """
        Execute the command with the provided arguments.

        This method must be implemented by subclasses.

        Args:
            args: The parsed arguments
        """
        raise NotImplementedError("Command subclasses must implement execute()")
