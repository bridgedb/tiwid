"""Data integrity tests."""

import re
import unittest
from itertools import chain
from pathlib import Path

import bioregistry

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()
DATA = ROOT.joinpath("data")
HEADER = ["#did", "when", "nextofkin"]
N_COLUMNS = len(HEADER)
DATE_RE = re.compile("^\\d{4}-\\d{2}-\\d{2}")


class IntegrityTestCase(unittest.TestCase):
    """Data integrity tests."""

    def setUp(self) -> None:
        """Set up the test case by finding all CSV and TSV files."""
        self.paths = list(DATA.glob("*.tsv"))

    def test_path_names(self):
        """Check all file names use standard prefixes."""
        for path in self.paths:
            with self.subTest(name=path.name):
                stem = path.stem
                norm_stem = bioregistry.normalize_prefix(stem)
                self.assertEqual(
                    norm_stem, stem, msg=f"unnormalized file name: {path.name}"
                )

    def test_csv_integrity(self):
        """Test all files have the right columns."""
        for path in self.paths:
            prefix = path.stem
            pattern = bioregistry.get_pattern(prefix)
            self.assertIsNotNone(pattern)
            pattern_re = re.compile(pattern)

            with self.subTest(name=path.name), path.open() as file:
                header = next(file).strip("\n").split("\t")
                self.assertEqual(HEADER, header)
                for i, line in enumerate(file, start=2):
                    with self.subTest(name=path.name, line=i):
                        line = line.strip("\n")
                        self.assertEqual(
                            line.strip(" "),
                            line,
                            msg=f"{path.name} had trailing whitespace on line {i}",
                        )
                        try:
                            old_id, date, new_id = line.split("\t")
                        except ValueError:
                            self.fail(
                                f"{path.name} had wrong number of columns on line {i}"
                            )
                        if date:
                            self.assertRegex(date, DATE_RE)
                        self.assertRegex(
                            old_id,
                            pattern_re,
                            msg=f"{path.name} line {i} had invalid did",
                        )
                        if new_id:
                            self.assertRegex(
                                new_id,
                                pattern_re,
                                msg=f"{path.name} line {i} had invalid nextofkin",
                            )
