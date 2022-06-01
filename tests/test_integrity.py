"""Data integrity tests."""

import re
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
DATE_RE = re.compile("^\\d{4}-\\d{2}-\\d{2}")


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
            pattern = bioregistry.get_pattern(path.stem)
            self.assertIsNotNone(pattern)
            pattern_re = re.compile(pattern)

            with self.subTest(name=path.name), path.open() as file:
                sep = "," if path.suffix == ".csv" else "\t"
                lines = (line.strip().split(sep) for line in file)
                header = next(lines)
                self.assertEqual(HEADER, header)
                for i, line in enumerate(lines, start=2):
                    with self.subTest(name=path.name, line=i):
                        self.assertEqual(N_COLUMNS, len(line))
                        old_id, date, new_id = line
                        if date:
                            self.assertRegex(date, DATE_RE)
                        self.assertRegex(old_id, pattern_re)
                        if new_id:
                            self.assertRegex(new_id, pattern_re)
