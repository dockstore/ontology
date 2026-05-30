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

def load_json(path):
    with open(path) as f:
        return json.load(f)

def add_nodes(nodes_a, nodes_b):
    combined = nodes_a + nodes_b
    if dups := {n['id'] for n in nodes_a} & {n['id'] for n in nodes_b}:
        raise ValueError(f"Duplicate node IDs: {dups}")
    return combined

def get_generated_dir():
    if len(sys.argv) <= 1:
       print(f'Usage: {sys.argv[0]} <generated_dir>', file=sys.stderr)
       sys.exit(1)
    return sys.argv[1]

def write_json(nodes, filename):
    with open(filename, 'w') as f:
        json.dump(sort_by_id(nodes), f, indent=4)
    print(f"Wrote {len(nodes)} nodes to {filename}", file=sys.stderr)

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

def fix_operation(operation):
    # Add the AI-generated operation subontology nodes.
    operation = add_nodes(operation, load_json('additions/ai/operation.json'))
    return operation

def fix_topic(topic):
    # Unrecommend-for-annotation some nodes that represent very broad categories.
    topic = make_nodes_not_recommended_for_annotation(topic, lambda node: node['id'] in generic_topic_ids)
    # Add the AI-generated topic subontology nodes.
    topic = add_nodes(topic, load_json('additions/ai/topic.json'))
    return topic

def fix_data(data):
    # Remove the "identifier" sub-branch of the "data" subontology.
    data = remove_subtree(data, 'data-identifier')
    # Add the AI-generated data subontology nodes.
    data = add_nodes(data, load_json('additions/ai/data.json'))
    return data

def fix_format(format):
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
    # Add the AI-generated format subontology nodes.
    format = add_nodes(format, load_json('additions/ai/format.json'))
    return format


def main():
    generated_dir = get_generated_dir()
    nodes = json.load(sys.stdin)

    # Extract, fix, and write the operation subontology.
    operation = fix_operation(extract_subtree(nodes, 'operation'))
    write_json(operation, f'{generated_dir}/operation.json')

    # Extract, fix, and write the topic subontology.
    topic = fix_topic(extract_subtree(nodes, 'topic'))
    write_json(topic, f'{generated_dir}/topic.json')

    # Extract and fix the data subontology, then write versions of it for both inputs and outputs.
    data = fix_data(extract_subtree(nodes, 'data'))
    write_json(add_prefix_to_ids(data, 'input-'), f'{generated_dir}/input-data.json')
    write_json(add_prefix_to_ids(data, 'output-'), f'{generated_dir}/output-data.json')

    # Extract and fix the format subontology, then write versions of it for both inputs and outputs.
    format = fix_format(extract_subtree(nodes, 'format'))
    write_json(add_prefix_to_ids(format, 'input-'), f'{generated_dir}/input-format.json')
    write_json(add_prefix_to_ids(format, 'output-'), f'{generated_dir}/output-format.json')


if __name__ == '__main__':
    main()
