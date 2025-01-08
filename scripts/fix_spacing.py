"""This script fixes trailing tabs in the data files."""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()
DATA = ROOT.joinpath("data")


def add_trailing_tabs(path: Path) -> None:
    """Add trailing tabs to the given file."""
    df = pd.read_csv(path, sep="\t", dtype=str)
    df.to_csv(path, sep="\t", index=False)


def main():
    """Add trailing tabs to all data files."""
    for path in DATA.glob("*.tsv"):
        add_trailing_tabs(path)


if __name__ == "__main__":
    main()
