#!/usr/bin/env python3
"""Adjust the EDAM ontology: modify subontology content and recommended-for-annotation flags."""

import json
import sys
from utils import (
    extract_subtree,
    make_nodes_not_recommended_for_annotation,
    make_nodes_recommended_for_annotation,
    make_only_leaves_recommended_for_annotation,
    remove_subtree,
)

generic_topic_ids = {
    "topic-bioinformatics",
    "topic-biology",
    "topic-biosciences",
    "topic-computational-biology",
    "topic-genetics",
    "topic-genomics",
    "topic-informatics",
    "topic-mathematics",
    "topic-omics",
    "topic-workflows"
}

generic_format_ids = {
    "format-configuration-file-format",
    "format-gzip-format",
    "format-html",
    "format-json",
    "format-json-ld",
    "format-mhtml",
    "format-pickle",
    "format-plain-text-format-unformatted",
    "format-tar-format",
    "format-xml",
    "format-yaml",
    "format-zip-format",
}

non_leaf_concrete_format_ids = {
    "format-bed6",
    "format-encode-peak-format",
    "format-fastq-illumina",
    "format-fastq-solexa",
    "format-gff2",
    "format-gff3",
    "format-hdf5",
    "format-mztab-m",
    "format-smiles",
    "format-vcf",
}


def adjust_operation(operation):
    return operation

def adjust_topic(topic):
    # Unrecommend-for-annotation some nodes that represent very broad categories.
    topic = make_nodes_not_recommended_for_annotation(topic, lambda node: node['id'] in generic_topic_ids)
    return topic

def adjust_data(data):
    # Remove the "identifier" sub-branch of the "data" subontology.
    data = remove_subtree(data, 'data-identifier')
    return data

def adjust_format(format):
    # In EDAM, generally, concrete formats are represented by leaf (terminal) nodes in the DAG.
    # Make only leaf nodes recommended-for-annotation.
    format = make_only_leaves_recommended_for_annotation(format)
    # There are a few non-leaf nodes that correspond to concrete formats.
    # Recommend them for annotation.
    format = make_nodes_recommended_for_annotation(format, lambda node: node['id'] in non_leaf_concrete_format_ids)
    # We probably don't want to categorize into "generic" formats (such as GZIP, JPG, TAR).
    # Unrecommend them for annotation.
    format = make_nodes_not_recommended_for_annotation(format, lambda node: node['id'] in generic_format_ids)
    # Children of 'format-pure' don't appear to be concrete formats.
    # Unrecommend them for annotation.
    pure_subtree_ids = [node['id'] for node in extract_subtree(format, 'format-pure')]
    format = make_nodes_not_recommended_for_annotation(format, lambda node: node['id'] in pure_subtree_ids)
    return format


def main():
    nodes = json.load(sys.stdin)

    operation = extract_subtree(nodes, 'operation')
    topic = extract_subtree(nodes, 'topic')
    data = extract_subtree(nodes, 'data')
    format = extract_subtree(nodes, 'format')

    core_ids = {node['id'] for node in operation + topic + data + format}
    other = [node for node in nodes if node['id'] not in core_ids]

    adjusted = adjust_operation(operation) + adjust_topic(topic) + adjust_data(data) + adjust_format(format) + other
    json.dump(adjusted, sys.stdout, indent=4)


if __name__ == '__main__':
    main()
