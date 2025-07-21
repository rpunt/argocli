#!/usr/bin/env python
# pylint: disable=line-too-long

"""
Main entry point for the Argo CLI tool.

This module provides the command-line interface for interacting with Argo Workflows.
It dynamically discovers commands and actions from the commands directory structure,
sets up appropriate argument parsers, and dispatches commands to their handlers.

The CLI follows a nested command pattern (e.g., 'argocli workflow list') and
supports automatic discovery of plugins and extensions without modifying this core file.
"""

import argparse
import importlib
import sys
import logging
import os

# import pkgutil
import cac_core as cac


def discover_commands():
    """
    Discover available commands by scanning the commands directory.

    Returns:
        list: A list of command names.
    """
    commands = []
    commands_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "commands")
    )

    # Check if the commands directory exists
    if not os.path.exists(commands_dir) or not os.path.isdir(commands_dir):
        return commands

    # Get all subdirectories (which are packages) in the commands directory
    for item in os.listdir(commands_dir):
        item_path = os.path.join(commands_dir, item)
        # Only consider directories that have an __init__.py file (Python packages)
        if (
            os.path.isdir(item_path)
            and os.path.exists(os.path.join(item_path, "__init__.py"))
            and item != "__pycache__"
        ):
            commands.append(item)

    return sorted(commands)


def discover_actions(command):
    """
    Discover available actions for a given command by scanning its directory.

    Args:
        command (str): The command name.

    Returns:
        list: A list of action names.
    """
    actions = []
    command_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "commands", command)
    )

    # Check if the command directory exists
    if not os.path.exists(command_dir) or not os.path.isdir(command_dir):
        return actions

    # Get all Python modules in the command directory
    for item in os.listdir(command_dir):
        # Skip __init__.py, __pycache__, and non-Python files
        if item == "__init__.py" or item == "__pycache__" or not item.endswith(".py"):
            continue

        # Extract action name (filename without .py extension)
        action = item[:-3]
        actions.append(action)

    return sorted(actions)


def show_command_help(command):
    """
    Show help for a specific command, listing all available actions.

    Args:
        command (str): The command to show help for
    """
    actions = discover_actions(command)
    print(f"\nAvailable actions for '{command}':")
    for action in sorted(actions):
        try:
            module_path = f"{__name__}.commands.{command}.{action}"
            module = importlib.import_module(module_path)
            doc = module.__doc__ or "No description available"
            doc = doc.strip().split("\n")[0]  # Get first line of docstring
            print(f"  {action.ljust(15)} - {doc}")
        except Exception:  # pylint: disable=broad-except
            print(f"  {action.ljust(15)} - No description available")


# def register_autocomplete(parser):
#     """Set up command autocompletion if supported environment"""
#     try:
#         import argcomplete
#         argcomplete.autocomplete(parser)
#     except ImportError:
#         # argcomplete is not installed, skip autocomplete setup
#         pass


def setup_logging(verbose: bool) -> logging.Logger:
    """Configure logging based on command line arguments"""
    log = cac.logger.new(__name__)
    if verbose:
        log.setLevel(logging.DEBUG)
    # if getattr(args, 'show_log_format', False):
    #     print(f"Log format: {cac.logger.get_formatter_string()}")
    #     sys.exit(0)
    return log


def main():
    """
    Entry point for the Argo CLI tool.

    This function sets up the argument parser with nested commands, and dynamically
    loads and executes the appropriate module and action based on user input.
    """
    log = cac.logger.new(__name__)

    # Create parent parser for global arguments
    parent_parser = argparse.ArgumentParser(add_help=False)

    # Main parser that inherits from parent
    parser = argparse.ArgumentParser(
        prog="argocli", description="Argo CLI tool", parents=[parent_parser]
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Discover available commands by scanning the commands directory
    commands = discover_commands()
    log.debug("Discovered commands: %s", commands)

    # Dictionary to map command names to their subparsers
    command_subparsers = {}

    # Set up command structure based on discovered commands
    for command in commands:
        command_parser = subparsers.add_parser(
            command,
            help=f"{command.capitalize()}-related commands",
            parents=[parent_parser],
        )
        command_subparsers[command] = command_parser.add_subparsers(
            dest="action", required=True
        )

    # Add all available action parsers up front by scanning directories
    for command, subparser in command_subparsers.items():
        actions = discover_actions(command)
        log.debug("Discovered actions for %s: %s", command, actions)

        for action in actions:
            try:
                # Load the module and class for this action
                module_path = f"argocli.commands.{command}.{action}"
                module = importlib.import_module(module_path)

                class_name = f"{command.capitalize()}{action.capitalize()}"
                action_class = getattr(module, class_name, None)

                if action_class is None:
                    log.warning(
                        "Class '%s' not found in module '%s'", class_name, module_path
                    )
                    continue

                # Instantiate the action class
                action_instance = action_class()

                # Create parser for this action and let the action define its arguments
                action_parser = subparser.add_parser(
                    action, help=f"{action} {command}", parents=[parent_parser]
                )
                action_instance.define_arguments(action_parser)

                # Store the class for later execution
                action_parser.set_defaults(action_class=action_class)

            except ModuleNotFoundError:
                log.warning("Command module '%s' not found", module_path)
            except Exception as e:  # pylint: disable=broad-except
                log.warning("Error setting up %s %s: %s", command, action, e)

    # # Add autocomplete setup
    # register_autocomplete(parser)

    # Parse arguments
    args = parser.parse_args()

    log = setup_logging(args.verbose)
    # log = setup_logging(False)
    log.debug("Parsed arguments: %s", args)

    # Add to main function, after argument parsing but before execution
    if args.command is None:
        parser.print_help()
        print("\nAvailable commands:")
        for cmd in sorted(commands):
            print(f"  {cmd}")
        sys.exit(1)

    # Execute the appropriate action
    try:
        # Get the action class from the parser defaults
        action_class = getattr(args, "action_class", None)

        if action_class is None:
            log.error("No handler found for %s %s", args.command, args.action)
            sys.exit(1)

        # Instantiate and execute
        if callable(action_class):
            action_instance = action_class()
        else:
            log.error("Invalid action class for %s %s", args.command, args.action)
            sys.exit(1)

        log.debug("Executing action: %s %s", args.command, args.action)
        action_instance.execute(args)

    except Exception as e:  # pylint: disable=broad-except
        log.error("Error executing command: %s", e)


if __name__ == "__main__":
    main()
