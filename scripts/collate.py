"""Run this script to collate the data."""

from itertools import chain
from pathlib import Path

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()
DATA = ROOT.joinpath("data")
ARTIFACTS = ROOT.joinpath("artifacts")
ARTIFACTS.mkdir(exist_ok=True, parents=True)
OUTPUT_PATH = ARTIFACTS.joinpath("collated.tsv")
HEADER = ["#prefix", "did", "when", "nextofkin"]


def main():
    """Collate all files together."""
    rows = []
    for path in chain(DATA.glob("*.csv"), DATA.glob("*.tsv")):
        with path.open() as file:
            header = next(file)
            sep = "," if "," in header else "\t"
            for line in file:
                line = line.strip()
                if not line:  # TODO remove after instituting data integrity tests
                    continue
                dead_id, when, alt_id = line.split(sep)
                rows.append((path.stem, dead_id, when, alt_id))

    rows = sorted(rows)

    with OUTPUT_PATH.open("w") as file:
        print(*HEADER, sep="\t", file=file)
        for row in rows:
            print(*row, sep="\t", file=file)


if __name__ == "__main__":
    main()
