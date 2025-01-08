"""Run this script to collate the data."""

import csv
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
HEADER = ["#prefix", "did", "when", "nextofkin", "contributor"]

# See https://mapping-commons.github.io/sssom/
SSSOM_PATH = ARTIFACTS.joinpath("tiwid.sssom.tsv")
SSSOM_HEADER = [
    "subject_id",
    "predicate_id",
    "object_id",
    "mapping_justification",
    "mapping_date",
    "author_id",
]

orcid_namespace = rdflib.Namespace("https://orcid.org/")

iao_namespace = rdflib.Namespace("http://purl.obolibrary.org/obo/IAO_")
replaced_by_uri = iao_namespace["0100001"]

ncbitaxon_namespace = rdflib.Namespace("http://purl.obolibrary.org/obo/NCBITaxon_")
human = ncbitaxon_namespace["9606"]

ontology_uri = URIRef(f"{URI_PATH_STEM}/{TTL_PATH.name}")


def main():
    """Collate all files together."""
    graph = rdflib.Graph()
    graph.bind("IAO", iao_namespace)
    graph.bind("orcid", orcid_namespace)
    graph.bind("ncbitaxon", ncbitaxon_namespace)
    graph.add((ontology_uri, RDF.type, OWL.Ontology))
    graph.add((ontology_uri, DCTERMS.title, Literal(TITLE)))
    graph.add((ontology_uri, FOAF.homepage, URIRef("https://github.com/bridgedb/tiwid")))
    graph.add((replaced_by_uri, RDF.type, OWL.AnnotationProperty))
    graph.add((replaced_by_uri, RDFS.label, Literal("term replaced by")))

    contributor_orcid_set: set[str] = set()
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
            reader = csv.DictReader(file, delimiter="\t")
            for record in reader:
                dead_id = record["#did"]
                when = record["when"]
                alt_id = record["nextofkin"]
                # this is a "get" because contributor is an optional column
                contributor_orcid = record.get("contributor", "")
                if contributor_orcid:
                    contributor_orcid_set.add(contributor_orcid)
                rows.append((path.stem, dead_id, when, alt_id, contributor_orcid))

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
                            contributor_orcid and f"orcid:{contributor_orcid}",
                        )
                    )

                    # The following generates RDF which is
                    # readily convertable to OWL
                    source = namespace[dead_id]
                    target = namespace[alt_id]
                    graph.add((source, replaced_by_uri, target))
                    graph.add((source, RDF.type, OWL.Class))
                    graph.add((target, RDF.type, OWL.Class))
                    if when or contributor_orcid:
                        axiom = rdflib.BNode()
                        graph.add((axiom, RDF.type, OWL.Axiom))
                        graph.add((axiom, OWL.annotatedSource, source))
                        graph.add((axiom, OWL.annotatedProperty, replaced_by_uri))
                        graph.add((axiom, OWL.annotatedTarget, target))
                        if when:
                            graph.add((axiom, DCTERMS.date, Literal(when, datatype=XSD.date)))
                        if contributor_orcid:
                            graph.add((axiom, DCTERMS.contributor, orcid_namespace[contributor_orcid]))

    graph.add((human, RDF.type, OWL.Class))
    graph.add((human, RDFS.label, Literal("human")))
    for contributor_orcid in contributor_orcid_set:
        graph.add((orcid_namespace[contributor_orcid], RDF.type, human))
        graph.add((ontology_uri, DCTERMS.contributor, orcid_namespace[contributor_orcid]))

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

    df = pd.DataFrame(rows, columns=["prefix", "dead_id", "date", "alternative_id", "contributor"])
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.histplot(data=df, y="prefix", ax=ax)
    ax.set_ylabel("")
    ax.set_xscale("log")
    ax.set_xlabel("Dead Identifiers")
    fig.tight_layout()
    fig.savefig(SUMMARY_SVG_PATH)


if __name__ == "__main__":
    main()
