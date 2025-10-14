"""Thin wrapper that delegates to the packaged CLI for backward compatibility."""
from scholarly.cli import main

if __name__ == "__main__":  # pragma: no cover
    main()
