"""Run this script to collate the data."""

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
    for path in DATA.glob("*.tsv"):
        with path.open() as file:
            _header = next(file)
            for line in file:
                dead_id, when, alt_id = line.strip().split("\t")
                rows.append((path.stem, dead_id, when, alt_id))

    rows = sorted(rows)

    with OUTPUT_PATH.open("w") as file:
        print(*HEADER, sep="\t", file=file)
        for row in rows:
            print(*row, sep="\t", file=file)


if __name__ == "__main__":
    main()
