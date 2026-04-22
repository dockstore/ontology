#!/usr/bin/env python3
"""Extract a file for each of the subontologies that we will use to automatically categorize Dockstore entries, using the simplified custom EDAM JSON representation as a base, and modifying as necessary."""

import json
import sys

def extract_subtree(nodes, root_id):
    id_to_node = {node['id']: node for node in nodes}
    def in_tree(node):
        if node['id'] == root_id:
            return True
        for parent in node['parents']:
            parent_node = id_to_node.get(parent)
            if (parent_node and in_tree(parent_node)):
                return True
        return False
    return [node for node in nodes if in_tree(node)]

def remove_subtree(nodes, root_id):
    remove_ids = {node['id'] for node in extract_subtree(nodes, root_id)}
    return [{**node, 'parents': [p for p in node['parents'] if p not in remove_ids]} for node in nodes if node['id'] not in remove_ids]

def add_prefix(nodes, prefix):
    return [{**node, 'id': prefix + node['id'], 'parents': [prefix + p for p in node['parents']]} for node in nodes]

def make_only_leaves_categorical(nodes):
    has_children = set()
    id_set = {node['id'] for node in nodes}
    for node in nodes:
        for parent in node['parents']:
            if parent in id_set:
                has_children.add(parent)
    return [{**node, 'categorical': node['categorical'] and node['id'] not in has_children} for node in nodes]


def write_json(nodes, filename):
    with open(filename, 'w') as f:
        json.dump(nodes, f, indent=4)
    print(f"Wrote {len(nodes)} nodes to {filename}", file=sys.stderr)


def main():
    nodes = json.load(sys.stdin)

    write_json(extract_subtree(nodes, 'operation'), 'operation.json')
    write_json(extract_subtree(nodes, 'topic'), 'topic.json')

    data = remove_subtree(extract_subtree(nodes, 'data'), 'data-identifier')
    write_json(add_prefix(data, 'input-'), 'input-data.json')
    write_json(add_prefix(data, 'output-'), 'output-data.json')

    format = make_only_leaves_categorical(extract_subtree(nodes, 'format'))
    write_json(add_prefix(format, 'input-'), 'input-format.json')
    write_json(add_prefix(format, 'output-'), 'output-format.json')


if __name__ == '__main__':
    main()
