#!/usr/bin/env python
# pylint: disable=protected-access
"""
Base module for all issue-related commands.

This module defines the base ArgoCommand class that all issue-related
action classes should inherit from.
"""

import abc
from argocli.commands.command import ArgoCommand


class ArgoWorkflowCommand(ArgoCommand):
    """
    Base class for all workflow-related actions.

    This class defines common methods and properties that should be shared
    across all workflow actions, such as workflow-specific arguments and utilities.
    """

    @abc.abstractmethod
    def define_arguments(self, parser):
        """
        Define arguments specific to this command.

        Args:
            parser: The argument parser to add arguments to

        Returns:
            The parser with arguments added
        """
        super().define_arguments(parser)
        # Add workflow-specific common arguments
        has_name = any(action.dest == "name" for action in parser._actions)
        if not has_name:
            parser.add_argument(
                "-n",
                "--name",
                help="Workflow name",
                required=True,
            )
        return parser

    @abc.abstractmethod
    def execute(self, args):
        """
        Execute the command with the given arguments.

        Args:
            args: The parsed arguments

        Returns:
            The result of the command execution
        """
        raise NotImplementedError("Subclasses must implement execute()")
