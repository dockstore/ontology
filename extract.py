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

    # Change the "format" subontology so that only the leaves are recommended for annotation,
    # then write versions of it for both inputs and outputs.
    format = make_only_leaves_recommended_for_annotation(extract_subtree(nodes, 'format'))
    write_json(add_prefix_to_ids(format, 'input-'), f'{generated_dir}/input-format.json')
    write_json(add_prefix_to_ids(format, 'output-'), f'{generated_dir}/output-format.json')


if __name__ == '__main__':
    main()
