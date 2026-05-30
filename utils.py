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

def qa(nodes):
    id_to_node = {node['id']: node for node in nodes}

    # Check duplicate IDs.
    if len(id_to_node) != len(nodes):
        seen, dups = set(), set()
        for node in nodes:
            (dups if node['id'] in seen else seen).add(node['id'])
        raise ValueError(f"Duplicate node IDs: {sorted(dups)}")

    # Check all parent IDs reference existing nodes.
    for node in nodes:
        for parent_id in node['parent_ids']:
            if parent_id not in id_to_node:
                raise ValueError(f"Node '{node['id']}' references nonexistent parent '{parent_id}'")

    # Check for cycles using recursive DFS.
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node['id']: WHITE for node in nodes}
    def dfs(node_id):
        color[node_id] = GRAY
        for parent_id in id_to_node[node_id]['parent_ids']:
            if color[parent_id] == GRAY:
                raise ValueError(f"Cycle detected: '{node_id}' -> '{parent_id}'")
            if color[parent_id] == WHITE:
                dfs(parent_id)
        color[node_id] = BLACK
    for node in nodes:
        if color[node['id']] == WHITE:
            dfs(node['id'])

    # Check that there is exactly one root (node with no parents). Given that all
    # parent IDs are valid and there are no cycles, every node must eventually reach
    # a parentless node via parent links, so one root implies a connected graph.
    roots = [node['id'] for node in nodes if not node['parent_ids']]
    if len(roots) != 1:
        raise ValueError(f"Expected one root node, found {len(roots)}: {sorted(roots)}")


def write_json(nodes, filename):
    qa(nodes)
    with open(filename, 'w') as f:
        json.dump(sort_by_id(nodes), f, indent=4)
    print(f"Wrote {len(nodes)} nodes to {filename}", file=sys.stderr)
