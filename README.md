# Argo CLI

A command-line interface for interacting with Argo.

This project uses [UV](https://github.com/astral-sh/uv) for dependency management.

## Installation

```bash
pip install argocli
```

## Authentication

On first-run, you'll be prompted for an Argo API token. This will be stored in your system credential store (e.g. Keychain on Mac OS) in an item called `argocli`.

## Configuration

On first-run, a configuration file will be generated at `~/.config/argocli/config.yaml`. In this file you'll need to replace the values of `server`, `namespace`, and `username` with appropriate values.

```yaml
server: https://your-argo-instance.server.tld
namespace: YOUR_PROJECT_NAMESPACE
username: your.email@example.com
```

### Environment Variables

You can also override configuration values using environment variables. The naming pattern is:

```bash
ARGOCLI_<UPPERCASE_CONFIG_KEY>
```

For example:

- `ARGOCLI_SERVER` overrides the `server` config option
- `ARGOCLI_NAMESPACE` overrides the `namespace` config option
- `ARGOCLI_USERNAME` overrides the `username` config option

This is useful for CI/CD pipelines or for switching between different Argo instances without modifying the config file.

## Usage

The Argo CLI follows a command-action pattern for all operations:

```bash
argocli <command> <action> [options]
```

### Available Commands

| Command | Action | Description |
|---------|--------|-------------|
| workflow | status | Show the status of a specific workflow |
| workflow | list | List all workflows with optional name filtering |
| workflow | view | View detailed information about a specific workflow |

### Global Options

- `--verbose`: Enable debug output
- `--output [table|json]`: Control output format (default: table)
- `--help`: Show command help
<!-- --suppress-output: Hide command output -->
<!-- --version: Display version information -->

### Examples

#### Workflow Commands

Show the status of a workflow:

```bash
argocli workflow status -n WORKFLOW_NAME
```

List all workflows:

```bash
argocli workflow list
```

Filter workflows by name (fuzzy match):

```bash
argocli workflow list -n cron
```

List workflows with JSON output:

```bash
argocli workflow list --output json
```

View detailed information about a specific workflow:

```bash
argocli workflow view -n WORKFLOW_NAME
```

View workflow information in JSON format (this will dump the entire workflow object, which is useful for further API work):

```bash
argocli workflow view -n WORKFLOW_NAME --output json
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

# Run tests with coverage report
uv run pytest --cov=argocli --cov-report=term
```

### Testing

The project uses pytest for unit testing. Tests are organized in a structure that mirrors the main codebase:

- `tests/unit/` - Unit tests
  - `commands/` - Tests for command implementations
    - `workflow/` - Tests for workflow-related commands
  - `core/` - Tests for core functionality

To run specific tests:

```bash
# Run tests in a specific file
pytest tests/unit/core/test_client.py

# Run a specific test class
pytest tests/unit/commands/workflow/test_list.py::TestWorkflowList

# Run a specific test method
pytest tests/unit/commands/workflow/test_list.py::TestWorkflowList::test_execute_filtered_list
```

### Project Structure

- `argocli/commands/` - Command implementations
  - `workflow/` - Workflow-related commands
- `argocli/cli/` - CLI entry point and argument parsing
- `tests/` - Test directory

### Adding New Commands

1. Create a new action module in the appropriate command directory.
2. Define a class that inherits from the command's base class.
3. Implement `define_arguments()` and `execute()` methods.
