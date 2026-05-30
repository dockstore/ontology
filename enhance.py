#!/usr/bin/env python3
"""Add AI-generated nodes to the EDAM ontology."""

import json
import sys
from utils import add_nodes, load_json


def main():
    nodes = json.load(sys.stdin)

    nodes = add_nodes(nodes, load_json('additions/ai/operation.json'))
    nodes = add_nodes(nodes, load_json('additions/ai/topic.json'))
    nodes = add_nodes(nodes, load_json('additions/ai/data.json'))
    nodes = add_nodes(nodes, load_json('additions/ai/format.json'))

    json.dump(nodes, sys.stdout, indent=4)


if __name__ == '__main__':
    main()
