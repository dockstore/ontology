#!/usr/bin/env python3
"""Extract a file for each of the subontologies that we will use to automatically categorize Dockstore entries, using the simplified custom EDAM JSON representation as a base, and modifying as necessary."""

import json
import sys

def extract_subtree(nodes, root_id):
    id_to_node = {node['id']: node for node in nodes}
    children = {node['id']: [] for node in nodes}
    for node in nodes:
        for parent in node['parents']:
            if parent in children:
                children[parent].append(node['id'])

    in_subtree = set()
    queue = [root_id]
    while queue:
        current = queue.pop()
        if current in in_subtree:
            continue
        in_subtree.add(current)
        queue.extend(children.get(current, []))

    result = [node for node in nodes if node['id'] in in_subtree]
    id_set = in_subtree
    return [{**node, 'parents': [p for p in node['parents'] if p in id_set]} for node in result]


def remove_subtree(nodes, root_id):
    to_remove = {node['id'] for node in extract_subtree(nodes, root_id)}
    result = [node for node in nodes if node['id'] not in to_remove]
    return [{**node, 'parents': [p for p in node['parents'] if p not in to_remove]} for node in result]


def add_prefix(nodes, prefix):
    id_set = {node['id'] for node in nodes}
    return [{**node, 'id': prefix + node['id'], 'parents': [prefix + p for p in node['parents'] if p in id_set]} for node in nodes]


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
    with open('simplified.json') as f:
        nodes = json.load(f)

    write_json(extract_subtree(nodes, 'operation'), 'operation.json')
    write_json(extract_subtree(nodes, 'topic'), 'topic.json')

    data = remove_subtree(extract_subtree(nodes, 'data'), 'data-identifier')
    write_json(add_prefix(data, 'input-'), 'input-data.json')
    write_json(add_prefix(data, 'output-'), 'output-data.json')

    formats = make_only_leaves_categorical(extract_subtree(nodes, 'format'))
    write_json(add_prefix(formats, 'input-'), 'input-format.json')
    write_json(add_prefix(formats, 'output-'), 'output-format.json')


if __name__ == '__main__':
    main()
