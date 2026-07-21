"""Enable ``python -m argocli`` to invoke the CLI entry point."""

import sys

from argocli import main

if __name__ == "__main__":
    sys.exit(main())
