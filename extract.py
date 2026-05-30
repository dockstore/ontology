#!/usr/bin/env python3
"""Extract a file for each of the subontologies that we will use to automatically categorize Dockstore entries."""

import json
import sys
from utils import add_prefix_to_ids, extract_subtree, write_json


def get_generated_dir():
    if len(sys.argv) <= 1:
       print(f'Usage: {sys.argv[0]} <generated_dir>', file=sys.stderr)
       sys.exit(1)
    return sys.argv[1]


def main():
    generated_dir = get_generated_dir()
    nodes = json.load(sys.stdin)

    # Extract and write the operation subontology.
    write_json(extract_subtree(nodes, 'operation'), f'{generated_dir}/operation.json')

    # Extract and write the topic subontology.
    write_json(extract_subtree(nodes, 'topic'), f'{generated_dir}/topic.json')

    # Extract the data subontology, then write versions of it for both inputs and outputs.
    data = extract_subtree(nodes, 'data')
    write_json(add_prefix_to_ids(data, 'input-'), f'{generated_dir}/input-data.json')
    write_json(add_prefix_to_ids(data, 'output-'), f'{generated_dir}/output-data.json')

    # Extract the format subontology, then write versions of it for both inputs and outputs.
    format = extract_subtree(nodes, 'format')
    write_json(add_prefix_to_ids(format, 'input-'), f'{generated_dir}/input-format.json')
    write_json(add_prefix_to_ids(format, 'output-'), f'{generated_dir}/output-format.json')


if __name__ == '__main__':
    main()
