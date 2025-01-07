[![Tests](https://github.com/bridgedb/tiwid/actions/workflows/qa.yml/badge.svg)](https://github.com/bridgedb/tiwid/actions/workflows/qa.yml)
[![DOI](https://zenodo.org/badge/334110717.svg)](https://zenodo.org/badge/latestdoi/334110717)

# This is where identifiers die

This project collects identifiers that are, for some reason, no longer pointing to active records
in the corresponding database. As such, these identifiers should no longer be used. By collecting
them in a machine-readable way, we can make it easier to automate the detection of dead identifiers
in data curation workflows.

The following is a short summary of the contents of this resource:

![](artifacts/summary.svg)

## Data

The data in the `data` folder is structured like as follows. Filenames follow the namespace of
the resources as defined by the Bioregistry and used in compact URIs. The content of
the file is a comma-separated values file with one or more columns:

* `#did`: the dead identifier
* `when`: when the identifier stopped being used
* `nextofkin`: the identifier that replaces the identifier (for some reason)

This model is incomplete and volatile, but applies to Release 1.

## Outputs

Automatically generated artifacts can be found in the [`artifacts`](artifacts) folder.

| Format | File                                         | Description                                                                                                                                                                                 |
|--------|----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| TSV    | [collated.tsv](artifacts/collated.tsv)       | A collated version of all TSV in the [data/](data) folder                                                                                                                                   |
| SSSOM  | [tiwid.sssom.tsv](artifacts/tiwid.sssom.tsv) | An output in the [Simple Standard for Sharing Ontological Mappings (SSSOM)](https://mapping-commons.github.io/sssom/) format                                                                |
| RDF    | [tiwid.ttl](artifacts/tiwid.ttl)             | An output in RDF, serialized with Turtle. This file can be readily converted to an OWL ontology with [ROBOT](https://robot.obolibrary.org/) with `robot convert -i tiwid.ttl -o tiwid.owl`. |

## Tests

Run tests using `tox` with the following commands in the shell:

```shell
$ pip install tox
$ tox
```

The tests are also run using GitHub Actions following all commits to the main branch
and pull requests to the main branch.
