#!/usr/bin/env python3
"""Apply a series of definition corrections to the simplified EDAM JSON."""

import json
import sys

# (node-id, from-string, to-string)
ADJUSTMENTS = [

    # SPELLING AND GRAMMAR CORRECTIONS:
    # data subontology
    ("data-bibliography",                                   "scientic papers",                              "scientific papers"),
    ("data-cultivation-parameter",                          "Experimental determined",                      "Experimentally determined"),
    ("data-fate-map",                                       "that are significance to",                     "that are significant to"),
    ("data-geographic-location",                            "the isolaton of",                              "the isolation of"),
    ("data-helical-net",                                    "sequence sequence in a simple",                "sequence in a simple"),
    ("data-helical-wheel",                                  "sequence sequence looking",                    "sequence looking"),
    ("data-peptide-immunogenicity-data",                    "An report on allergenicity",                   "A report on allergenicity"),
    ("data-position-specific-scoring-matrix",               "is derived derived from",                      "is derived from"),
    ("data-protein-geometry-data",                          "planaraties etc.",                             "planarities etc."),
    ("data-protein-isoelectric-point",                      "of one proteins.",                             "of one protein."),
    ("data-protocol",                                       "about about how",                              "about how"),
    ("data-sequence-variations",                            "resulting large-scale",                        "resulting from large-scale"),
    ("data-sequence-version",                               "on an molecular",                              "on a molecular"),

    # format subontology
    ("format-cytoscape-input-file-format",                  "input file of gene expression",                "input file in which gene expression"),
    ("format-hmmer-profile-alignment-hmm-versus-sequences", "package for of an alignment",                  "package for an alignment"),
    ("format-individual-genetic-data-format",               "format for a metadata on",                     "format for metadata on"),
    ("format-latex",                                        "format for the LaTeX",                         "Format for the LaTeX"),
    ("format-mass-spectrometry-data-format",                "mass pectra and derived data, include peptide sequences", "mass spectra and derived data, including peptide sequences"),
    ("format-microarray-experiment-data-format",            "microarray experimental per se",               "microarray experiment per se"),
    ("format-nmredata",                                     "MReData is a text",                            "NMReData is a text"),
    ("format-nmrml",                                        "data. It is accompanies by",                   "data. It is accompanied by"),
    ("format-nrrd",                                         "Raw Rasta Data",                               "Raw Raster Data"),
    ("format-probam",                                       ". proBAM is an adaptation",                    "proBAM is an adaptation"),
    ("format-probed",                                       ". proBED is an adaptation",                    "proBED is an adaptation"),
    ("format-python-script",                                "scripts writtenin Python",                     "scripts written in Python"),
    ("format-trackdb",                                      "display charateristics.",                      "display characteristics."),
    ("format-wego",                                         "gene names and others GO IDs",                 "gene names and other GO IDs"),

    # operation subontology
    ("operation-active-site-prediction",                    "a substrate bind and catalyses",               "a substrate and catalyses"),
    ("operation-calculation",                               "a properly of a molecule",                     "a property of a molecule"),
    ("operation-expression-correlation-analysis",           "across across a variety",                      "across a variety"),
    ("operation-fold-recognition",                          "similarity to know structures",                 "similarity to known structures"),
    ("operation-gene-expression-qtl-analysis",              "to describe describe cis-",                    "to describe cis-"),
    ("operation-gene-functional-annotation",                "metaobolic pathways",                          "metabolic pathways"),
    ("operation-genome-alignment",                          "(tpyically huge)",                             "(typically huge)"),
    ("operation-mirna-expression-analysis",                 "naturally occurring plant and animal",         "naturally occurring in plant and animal"),
    ("operation-phylogenetic-reconstruction",               "from its leafes.",                             "from its leaves."),
    ("operation-probabilistic-data-generation",             "probibalistic model",                          "probabilistic model"),
    ("operation-protein-geometry-validation",               "planaraties etc. An example",                  "planarities etc. An example"),
    ("operation-rna-seq-quantification",                    "abundances durnig transcriptome",              "abundances during transcriptome"),
    ("operation-scaffolding",                               "typically typically contigs;",                 "typically contigs;"),
    ("operation-taxonomic-classification",                  "Classifiication (typically",                   "Classification (typically"),
    ("operation-variant-effect-prediction",                 "of strucural effects",                         "of structural effects"),

    # topic subontology
    ("topic-biochemistry",                                  "processes and that occur within",              "processes that occur within"),
    ("topic-biomarkers",                                    "and determinate treatment",                    "and determine treatment"),
    ("topic-biophysics",                                    "biological system.",                           "biological systems."),
    ("topic-chip-exo",                                      "immunoprecipitation-based exeperiment",        "immunoprecipitation-based experiment"),
    ("topic-chip-on-chip",                                  "high-throughput study protein-DNA",            "high-throughput study of protein-DNA"),
    ("topic-critical-care-medicine",                        "The multidisciplinary that cares",             "The multidisciplinary field that cares"),
    ("topic-data-acquisition",                              "by another other means",                       "by any other means"),
    ("topic-data-mining",                                   "and trasnsformation of",                       "and transformation of"),
    ("topic-drug-development",                              "lead compounds has",                           "lead compound has"),
    ("topic-environmental-sciences",                        "and it's effect on life",                      "and its effect on life"),
    ("topic-gene-and-protein-families",                     "encoded proteins.Primarily",                   "encoded proteins. Primarily"),
    ("topic-immunoinformatics",                             "immunoloogical questions",                     "immunological questions"),
    ("topic-metabolomics",                                  "they are involved, and",                       "they are involved in, and"),
    ("topic-microfluidics",                                 "Interdisplinary study",                        "Interdisciplinary study"),
    ("topic-nmr",                                           "the magenetic properties",                     "the magnetic properties"),
    ("topic-ophthalmology",                                 "and occular muscles",                          "and ocular muscles"),
    ("topic-personalised-medicine",                         "decisions, practices and are tailored",        "decisions and practices are tailored"),
    ("topic-public-health-and-epidemiology",                "the the patterns",                             "the patterns"),
    ("topic-systems-medicine",                              "an integrted whole",                           "an integrated whole"),
    ("topic-translational-medicine",                        "'translating' the output of basic",            "The practice of 'translating' the output of basic"),

    # DEFINITION IMPROVEMENTS
    ("topic-comparative-genomics",                          "of multiple genomes.",                          "of the genomes of multiple organisms."),
    ("data-electron-density-map",                           "X-ray crystallography data.",                  "The probability distribution of electrons within a molecule, derived from X-ray crystallography or cryo-EM data."),
]


def main():
    nodes = json.load(sys.stdin)

    corrections_by_id = {}
    for node_id, from_str, to_str in ADJUSTMENTS:
        corrections_by_id.setdefault(node_id, []).append((from_str, to_str))

    changed = 0
    for node in nodes:
        for from_str, to_str in corrections_by_id.get(node['id'], []):
            old_def = node['definition']
            new_def = old_def.replace(from_str, to_str)
            if new_def == old_def:
                print(f"Warning: no match for {node['id']!r}: {from_str!r}", file=sys.stderr)
            else:
                node['definition'] = new_def
                changed += 1

    print(f"Applied {changed} corrections.", file=sys.stderr)
    print(json.dumps(nodes, indent=4))


if __name__ == '__main__':
    main()
