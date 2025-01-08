"""Data integrity tests."""

import re
import unittest
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
                self.assertIsNotNone(
                    norm_stem,
                    msg=f"The Bioregistry does not contain an entry for {stem}. Please consider "
                    f"submitting a new prefix request at https://github.com/biopragmatics/bioregistry/"
                    f"issues/new?assignees=biopragmatics%2Fbioregistry-reviewers&labels=New%2CPrefix&"
                    f"template=new-prefix.yml&title=Add+prefix+%5B{stem}%5D.",
                )
                self.assertEqual(
                    norm_stem,
                    stem,
                    msg=f"The file name {path.name} is not normalized to the Bioregistry "
                    f"standard. Please rename this file to {norm_stem}.tsv",
                )

    def test_csv_integrity(self):
        """Test all files have the right columns."""
        for path in self.paths:
            prefix = path.stem
            pattern = bioregistry.get_pattern(prefix)
            self.assertIsNotNone(
                pattern,
                msg=f"The Bioregistry does not contain a regular expression pattern for validating identifiers "
                f"from {prefix}. Please consider submitting an issue on the Bioregistry to add one at "
                f"https://github.com/biopragmatics/bioregistry/issues/new?assignees=cthoyt&labels=Regex%2C"
                f"Update&template=update-regex.yml&title=Update+regular+expression+pattern+for+%5B{prefix}%5D.",
            )
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
                            self.fail(f"{path.name} had wrong number of columns on line {i}")
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
