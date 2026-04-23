# ontology

This repo manages the ontologies that Dockstore uses to automatically categorize entries, and code that reproducibly generates them.

## Overview

Currently, we generate six ontologies with the following names and purposes:

* "operation": Operations that an entry performs (ex: "sequence quality control").
* "topic": Domains or fields of study (ex: "oncology").
* "input-data": Types of input data that an entry supports (ex: "sequence").
* "output-data": Types of output data that an entry generates (ex: "sequence statistics").
* "input-format": Input file formats that the entry supports (ex: "fastq").
* "output-format": Output file formats that the entry generates (ex: "BAM").

Currently, each of the above ontologies is derived from one of the four main subontologies of the [EDAM ontology](https://edamontology.org).

To convert the EDAM ontology to our six ontologies, we apply the following steps:

1. Download a recent tagged version of the EDAM OWL file (XML).
1. Convert the EDAM file to a simplified JSON representation (see below).  We use this simplified format in subsequent steps.
2. Map British spellings to American spellings.
3. Produce each of the target ontologies by extracting the appropriate hierarchy from the simplified-and-Americanized EDAM representation, then modifying ac necessary.

We represent processed EDAM and each target ontology in a simplified JSON format, as a list of objects, each of which represents an ontology DAG node.  Each node object has the following properties:

* "id": Unique human-readable node ID, consisting solely lowercase alphanumeric characters and dashes, in a form that can be used as the name of a corresponding Dockstore category.
* "label": Short term, similar to a title, that describes what the node represents.
* "definition": More detailed description of the node, up to several sentences long.
* "source": A representaton of the canonical origin of the node.  If the node was derived from EDAM, the canonical EDAM URL.
* "categorical": A boolean that indicates whether, during classification, the node should be represented by a Dockstore category.
* "parent_ids": A list of the IDs of this node's parents.

## Build

Run `build.sh` to generate the JSON file corresponding to each ontology.
