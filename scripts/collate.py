"""Run this script to collate the data."""

from pathlib import Path

import bioregistry
import matplotlib.pyplot as plt
import pandas as pd
import rdflib
import seaborn as sns
from rdflib import DCTERMS, FOAF, OWL, RDF, RDFS, XSD, Literal, URIRef

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()
DATA = ROOT.joinpath("data")
ARTIFACTS = ROOT.joinpath("artifacts")
ARTIFACTS.mkdir(exist_ok=True, parents=True)
OUTPUT_PATH = ARTIFACTS.joinpath("collated.tsv")
TTL_PATH = ARTIFACTS.joinpath("tiwid.ttl")

TITLE = "This Is Where Identifiers Die"
URI_PATH_STEM = "https://github.com/bridgedb/tiwid/raw/refs/heads/main/artifacts"

SUMMARY_SVG_PATH = ARTIFACTS.joinpath("summary.svg")
HEADER = ["#prefix", "did", "when", "nextofkin"]

# See https://mapping-commons.github.io/sssom/
SSSOM_PATH = ARTIFACTS.joinpath("tiwid.sssom.tsv")
SSSOM_HEADER = [
    "subject_id",
    "predicate_id",
    "object_id",
    "mapping_justification",
    "mapping_date",
]

iao_namespace = rdflib.Namespace("http://purl.obolibrary.org/obo/IAO_")
replaced_by_uri = iao_namespace["0100001"]

ontology_uri = URIRef(f"{URI_PATH_STEM}/{TTL_PATH.name}")


def main():
    """Collate all files together."""
    graph = rdflib.Graph()
    graph.bind("IAO", iao_namespace)
    graph.add((ontology_uri, RDF.type, OWL.Ontology))
    graph.add((ontology_uri, DCTERMS.title, Literal(TITLE)))
    graph.add((ontology_uri, FOAF.homepage, URIRef("https://github.com/bridgedb/tiwid")))
    graph.add((replaced_by_uri, RDF.type, OWL.AnnotationProperty))
    graph.add((replaced_by_uri, RDFS.label, Literal("term replaced by")))

    rows = []
    sssom_rows = []
    sssom_prefixes = [("IAO", iao_namespace)]
    for path in DATA.glob("*.tsv"):
        prefix = bioregistry.get_preferred_prefix(path.stem) or path.stem

        uri_prefix = bioregistry.get_uri_prefix(prefix)
        if uri_prefix is None:
            raise ValueError

        namespace = rdflib.Namespace(uri_prefix)
        graph.namespace_manager.bind(prefix, namespace)
        sssom_prefixes.append((prefix, uri_prefix))

        with path.open() as file:
            _header = next(file)
            for line in file:
                dead_id, when, alt_id = line.strip("\n").split("\t")
                rows.append((path.stem, dead_id, when, alt_id))

                # If there's an explicitly defined alternate ID,
                # we can generate triples in SSSOM and RDF/OWL
                if alt_id:
                    sssom_rows.append(
                        (
                            f"{prefix}:{dead_id}",
                            "IAO:0100001",
                            f"{prefix}:{alt_id}",
                            "semapv:ManualMappingCuration",
                            when,
                        )
                    )

                    # The following generates RDF which is
                    # readily convertable to OWL
                    source = namespace[dead_id]
                    target = namespace[alt_id]
                    graph.add((source, replaced_by_uri, target))
                    graph.add((source, RDF.type, OWL.Class))
                    graph.add((target, RDF.type, OWL.Class))
                    if when:
                        axiom = rdflib.BNode()
                        graph.add((axiom, RDF.type, OWL.Axiom))
                        graph.add((axiom, OWL.annotatedSource, source))
                        graph.add((axiom, OWL.annotatedProperty, replaced_by_uri))
                        graph.add((axiom, OWL.annotatedTarget, target))
                        graph.add((axiom, DCTERMS.date, Literal(when, datatype=XSD.date)))

    graph.serialize(TTL_PATH)

    rows = sorted(rows)
    sssom_rows = sorted(sssom_rows)

    with OUTPUT_PATH.open("w") as file:
        print(*HEADER, sep="\t", file=file)
        for row in rows:
            print(*row, sep="\t", file=file)

    with SSSOM_PATH.open("w") as file:
        print(f"# mapping_set_id: {URI_PATH_STEM}/{SSSOM_PATH.name}", file=file)
        print(f"# mapping_set_description: {TITLE}", file=file)
        print(f"# license: https://creativecommons.org/publicdomain/zero/1.0/", file=file)
        print(f"# curie_map:", file=file)
        for prefix, uri_prefix in sorted(sssom_prefixes, key=lambda p: p[0].casefold()):
            print(f"#   {prefix}: {uri_prefix}", file=file)
        print(*SSSOM_HEADER, sep="\t", file=file)
        for row in sssom_rows:
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
