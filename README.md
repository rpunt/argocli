# Argo CLI

A command-line interface for interacting with Argo.

This project uses [UV](https://github.com/astral-sh/uv) for dependency management.

## Installation

```bash
pip install argocli
```

## Authentication

On first-run, you'll be prompted for an Argo API token. This will be stored in your system credential store (e.g. Keychain on Mac OS) in an items called `argocli`.

## Configuration

On first-run, a configuration file will be generated at `~/.config/argocli/config.yaml`. In this file you'll need to replace the values of `server`, `namespace`, and `username` with appropriate values.

```yaml
server: https://your-argo-instance.server.tld
namespace: YOUR_PROJECT_NAMESPACE
username: your.email@example.com
```

## Usage

The Argo CLI follows a command-action pattern for all operations:

```bash
argocli <command> <action> [options]
```

### Global Options

- `--verbose`: Enable debug output
<!-- - `--output [table|json]`: Control output format (default table) -->
- `--help`: Show command help
<!-- --suppress-output: Hide command output -->
<!-- --version: Display version information -->

### Examples

#### Workflow Commands

Show the status of a workflow:

```bash
argocli workflow status -n WORKFLOW_NAME
```

## Development

### Setup Development Environment

```bash
# Install dependencies including dev dependencies
uv sync

# Activate the venv
source .venv/bin/activate

# Run tests
uv run pytest
```

Please note that tests are still WIP

### Project Structure

- `argocli/commands/` - Command implementations
  - `workflow/` - Workflow-related commands
- `argocli/cli/` - CLI entry point and argument parsing

### Adding New Commands

1. Create a new action module in the appropriate command directory.
2. Define a class that inherits from the command's base class.
3. Implement `define_arguments()` and `execute()` methods.
