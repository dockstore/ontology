#!/usr/bin/env python3
"""Convert EDAM.owl to a simplified custom JSON representation."""

import json
import re
import sys
import xml.etree.ElementTree as ET

NS = {
    'rdf':      'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs':     'http://www.w3.org/2000/01/rdf-schema#',
    'owl':      'http://www.w3.org/2002/07/owl#',
    'oboInOwl': 'http://www.geneontology.org/formats/oboInOwl#',
    'edam':     'http://edamontology.org/',
}

RDF_ABOUT    = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'
RDF_RESOURCE = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'
DEPRECATED_CLASS_URI = 'http://www.w3.org/2002/07/owl#DeprecatedClass'


def to_slug(uri, label):
    subontology = re.search(r'/([a-z]+)_\d+$', uri).group(1)
    slug = re.sub('-+', '-', re.sub('[^a-z0-9]+', '-', label.lower())).strip('-')
    if (slug == subontology):
        return slug
    return subontology + '-' + slug;

def get_text(cls, name):
    elem = cls.find(name, NS)
    if elem is None:
        return None
    return elem.text

def get_uri(cls):
    return cls.get(RDF_ABOUT)

def get_deprecated(cls):
    return get_text(cls, 'owl:deprecated')

def get_label(cls):
    return get_text(cls, 'rdfs:label')

def get_definition(cls):
    return get_text(cls, 'oboInOwl:hasDefinition')

def get_not_recommended_for_annotation(cls):
    return get_text(cls, 'edam:notRecommendedForAnnotation') == 'true'

def get_parents(cls):
    return [
        sc.get(RDF_RESOURCE)
        for sc in cls.findall('rdfs:subClassOf', NS)
        if sc.get(RDF_RESOURCE) and sc.get(RDF_RESOURCE) != DEPRECATED_CLASS_URI
    ]


def main():
    # Read and parse the EDAM XML representation.
    root = ET.parse(sys.stdin).getroot()

    # Convert the parsed XML into a list of simplified nodes.
    nodes = []
    for cls in root.findall('owl:Class', NS):

        deprecated = get_deprecated(cls)
        uri = get_uri(cls)
        label = get_label(cls)
        definition = get_definition(cls)
        not_recommended_for_annotation = get_not_recommended_for_annotation(cls)
        parents = get_parents(cls)

        if deprecated or not uri or not label or not definition:
            continue

        nodes.append({
            'uri':         uri,
            'label':       label,
            'definition': definition,
            'not_recommended_for_annotation': not_recommended_for_annotation,
            'parents':     parents,
        })

    # Convert the simplified nodes to our custom representation, which uses human-readable IDs.
    # Remove any parent IDs that point at a non-existent parent.
    uri_to_slug = {node['uri']: to_slug(node['uri'], node['label']) for node in nodes}
    uris  = {node['uri'] for node in nodes}
    result = [
        {
            'id':          uri_to_slug[node['uri']],
            'title':       node['label'],
            'description': node['definition'],
            'source':      node['uri'],
            'categorical': not node['not_recommended_for_annotation'],
            'parents':     [uri_to_slug[p] for p in node['parents'] if p in uris],
        }
        for node in nodes
    ]

    # Confirm that there are no duplicate IDs.
    ids = [node['id'] for node in result]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate ids found in result")

    # Output our custom representation in JSON format.
    print(json.dumps(result, indent=4))


if __name__ == '__main__':
    main()
