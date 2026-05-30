import json
import sys


def extract_subtree(nodes, root_id):
    id_to_node = {node['id']: node for node in nodes}
    def in_tree(node):
        if node['id'] == root_id:
            return True
        for parent in node['parent_ids']:
            parent_node = id_to_node.get(parent)
            if parent_node and in_tree(parent_node):
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
    if dups := {n['id'] for n in nodes_a} & {n['id'] for n in nodes_b}:
        raise ValueError(f"Duplicate node IDs: {dups}")
    return nodes_a + nodes_b

def write_json(nodes, filename):
    with open(filename, 'w') as f:
        json.dump(sort_by_id(nodes), f, indent=4)
    print(f"Wrote {len(nodes)} nodes to {filename}", file=sys.stderr)
