"""Data integrity tests."""

import unittest
from itertools import chain
from pathlib import Path

import bioregistry

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()
DATA = ROOT.joinpath("data")
EXTENSION = "csv"
HEADER = ["#did", "when", "nextofkin"]
N_COLUMNS = len(HEADER)


class IntegrityTestCase(unittest.TestCase):
    """Data integrity tests."""

    def setUp(self) -> None:
        """Set up the test case by finding all CSV and TSV files."""
        self.paths = list(
            chain(
                DATA.glob("*.csv"),
                DATA.glob("*.tsv"),
            )
        )

    def test_path_names(self):
        """Check all file names use standard prefixes."""
        for path in self.paths:
            with self.subTest(name=path.name):
                stem = path.stem
                norm_stem = bioregistry.normalize_prefix(stem)
                self.assertEqual(norm_stem, stem, msg="unnormalized file name: path")

    def test_csv_integrity(self):
        """Test all files have the right columns."""
        for path in self.paths:
            with self.subTest(name=path.name), path.open() as file:
                sep = "," if path.suffix == ".csv" else "\t"
                lines = (line.strip().split(sep) for line in file)
                header = next(lines)
                self.assertEqual(HEADER, header)
                for line in lines:
                    self.assertEqual(N_COLUMNS, len(line))
