"""Run this script to collate the data."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()
DATA = ROOT.joinpath("data")
ARTIFACTS = ROOT.joinpath("artifacts")
ARTIFACTS.mkdir(exist_ok=True, parents=True)
OUTPUT_PATH = ARTIFACTS.joinpath("collated.tsv")
SUMMARY_SVG_PATH = ARTIFACTS.joinpath("summary.svg")
HEADER = ["#prefix", "did", "when", "nextofkin"]


def main():
    """Collate all files together."""
    rows = []
    for path in DATA.glob("*.tsv"):
        with path.open() as file:
            _header = next(file)
            for line in file:
                dead_id, when, alt_id = line.strip("\n").split("\t")
                rows.append((path.stem, dead_id, when, alt_id))

    rows = sorted(rows)

    with OUTPUT_PATH.open("w") as file:
        print(*HEADER, sep="\t", file=file)
        for row in rows:
            print(*row, sep="\t", file=file)

    df = pd.DataFrame(rows, columns=["prefix", "dead_id", "date", "alternative_id"])
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.histplot(data=df, y="prefix", ax=ax)
    ax.set_ylabel("")
    ax.set_xscale("log")
    ax.set_xlabel("Dead Identifiers")
    fig.tight_layout()
    fig.savefig(SUMMARY_SVG_PATH)


if __name__ == "__main__":
    main()
