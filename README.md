# ontology

This repo manages the ontologies that Dockstore uses to automatically categorize entries, and code that we use to reproducibly generate them.

## Overview

Currently, we generate six ontologies with the following names and purposes:

* "operation": Operations that an entry performs (ex: "sequence quality control").
* "topic": Domains or fields of study (ex: "oncology").
* "input-data": Types of input data that an entry supports (ex: "sequence").
* "output-data": Types of output data that an entry generates (ex: "sequence statistics").
* "input-format": Input file formats that the entry supports (ex: "fastq").
* "output-format": Output file formats that the entry generates (ex: "BAM").

Currently, each of the above ontologies is derived primarily from one of the four main subontologies of the [EDAM ontology](https://edamontology.org).

## Build

Run `build.sh` to generate the JSON file corresponding to each ontology.
