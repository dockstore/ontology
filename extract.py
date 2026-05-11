#!/usr/bin/env python3
"""Extract a file for each of the subontologies that we will use to automatically categorize Dockstore entries, using the simplified EDAM JSON representation as a base, and modifying as necessary."""

import json
import sys

def extract_subtree(nodes, root_id):
    id_to_node = {node['id']: node for node in nodes}
    def in_tree(node):
        if node['id'] == root_id:
            return True
        for parent in node['parent_ids']:
            parent_node = id_to_node.get(parent)
            if (parent_node and in_tree(parent_node)):
                return True
        return False
    return [node for node in nodes if in_tree(node)]

def remove_subtree(nodes, root_id):
    remove_ids = {node['id'] for node in extract_subtree(nodes, root_id)}
    return [{**node, 'parent_ids': [p for p in node['parent_ids'] if p not in remove_ids]} for node in nodes if node['id'] not in remove_ids]

def add_prefix_to_ids(nodes, prefix):
    return [{**node, 'id': prefix + node['id'], 'parent_ids': [prefix + p for p in node['parent_ids']]} for node in nodes]

def make_only_leaves_recommended_for_annotation(nodes):
    parent_ids = set()
    for node in nodes:
        parent_ids.update(node['parent_ids'])
    return [{**node, 'recommended_for_annotation': node['recommended_for_annotation'] and node['id'] not in parent_ids} for node in nodes]

def make_nodes_recommended_for_annotation(nodes, criteria):
    return [{**node, 'recommended_for_annotation': node['recommended_for_annotation'] or criteria(node)} for node in nodes]

def make_nodes_not_recommended_for_annotation(nodes, criteria):
    return [{**node, 'recommended_for_annotation': node['recommended_for_annotation'] and not criteria(node)} for node in nodes]

def sort_by_id(nodes):
    return sorted(nodes, key=lambda node: node['id'])

def get_generated_dir():
    if len(sys.argv) <= 1:
       print(f'Usage: {sys.argv[0]} <generated_dir>', file=sys.stderr)
       sys.exit(1)
    return sys.argv[1]

def write_json(nodes, filename):
    with open(filename, 'w') as f:
        json.dump(sort_by_id(nodes), f, indent=4)
    print(f"Wrote {len(nodes)} nodes to {filename}", file=sys.stderr)

generic_format_ids = {
    "format-csv",
    "format-dsv",
    "format-gzip-format",
    "format-html",
    "format-json",
    "format-json-ld",
    "format-mhtml",
    "format-n-quads",
    "format-n-triples",
    "format-notation3",
    "format-pickle",
    "format-plain-text-format-unformatted",
    "format-rdf-xml",
    "format-tar-format",
    "format-tsv",
    "format-turtle",
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


def main():
    generated_dir = get_generated_dir()
    nodes = json.load(sys.stdin)

    # Use the "operation" and "topic" subontologies verbatim.
    write_json(extract_subtree(nodes, 'operation'), f'{generated_dir}/operation.json')
    write_json(extract_subtree(nodes, 'topic'), f'{generated_dir}/topic.json')

    # Remove the "identifier" sub-branch of the "data" subontology,
    # then write versions of it for both inputs and outputs.
    data = remove_subtree(extract_subtree(nodes, 'data'), 'data-identifier')
    write_json(add_prefix_to_ids(data, 'input-'), f'{generated_dir}/input-data.json')
    write_json(add_prefix_to_ids(data, 'output-'), f'{generated_dir}/output-data.json')

    # Extract the format subontology.
    format = extract_subtree(nodes, 'format')
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
    # Write versions of the "format" subontology for both inputs and outputs.
    write_json(add_prefix_to_ids(format, 'input-'), f'{generated_dir}/input-format.json')
    write_json(add_prefix_to_ids(format, 'output-'), f'{generated_dir}/output-format.json')


if __name__ == '__main__':
    main()
