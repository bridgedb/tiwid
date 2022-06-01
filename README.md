# This is where identifiers die

This project collects identifiers that are, for some reason, no longer pointing to active records
in the corresponding database. As such, these identifiers should no longer be used. By collecting
them in a machine readable way, we can make it easier to automate the detection of dead identifiers
in data curation workflows.

If you use this data, please cite: 

[![DOI](https://zenodo.org/badge/334110717.svg)](https://zenodo.org/badge/latestdoi/334110717)

## Data

The data in the `data` folder is structured like as follows. Filenames follow the namespace of
the resources as defined by identifiers.org and used in compact identifiers. The content of
the file is a comma-separated values file with one or more columns:

* did: the dead identifier
* when: when the identifier stopped being used
* nextofkin: the identifier that replaces the identifier (for some reason)

This model is incomplete and volatile, but applies to Release 1.

A collation of all curations can be found in [`artifacts/collated.tsv`](artifacts/collated.tsv).
