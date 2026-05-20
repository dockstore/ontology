#!/usr/bin/env python3
"""Normalize an AI-generated ontology JSON file: fix unicode, derive id from label, set source to "ai"."""

import json
import re
import sys

REPLACEMENTS = [
    ('—', '-'),   # em-dash
    ('–', '-'),   # en-dash
    ('′', "'"),   # prime
]


def normalize_str(s):
    for old, new in REPLACEMENTS:
        s = s.replace(old, new)
    return s


def normalize_value(v):
    if isinstance(v, str):
        return normalize_str(v)
    if isinstance(v, list):
        return [normalize_value(item) for item in v]
    return v


def to_id(subontology, label):
    slug = re.sub('-+', '-', re.sub('[^a-z0-9]+', '-', label.lower())).strip('-')
    if slug == subontology:
        return subontology
    return subontology + '-' + slug


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <subontology>", file=sys.stderr)
        sys.exit(1)

    subontology = sys.argv[1]
    nodes = json.load(sys.stdin)

    # First pass: normalize fields and compute new ids, building a remap table.
    result = []
    id_remap = {}
    for node in nodes:
        normalized = {k: normalize_value(v) for k, v in node.items()}
        new_id = to_id(subontology, normalized['label'])
        if 'id' in node and node['id'] != new_id:
            id_remap[node['id']] = new_id
        normalized['id'] = new_id
        normalized['source'] = 'ai'
        result.append(normalized)

    # Second pass: rewrite any parent_ids that were remapped.
    if id_remap:
        for node in result:
            if 'parent_ids' in node:
                node['parent_ids'] = [id_remap.get(p, p) for p in node['parent_ids']]

    print(json.dumps(result, indent=4))


if __name__ == '__main__':
    main()
