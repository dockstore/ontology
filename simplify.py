#!/usr/bin/env python3
"""Convert EDAM.owl to a simplified custom JSON representation."""

import json
import re
import sys
import xml.etree.ElementTree as ElementTree

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
    """Convert the EDAM URI and label to a text "slug" which will be used as
    a human-readable ID and is composed of lowercase alphanumeric characters
    and non-consecutive internal dashes.
    """

    # Determine the EDAM subontology, which we'll use as the prefix of the slug.
    # EDAM uris are of the following form:
    #   http://edamontology.org/{subontology}_{four-digit-id}
    # Example: http://edamontology.org/data_0842
    subontology = re.search(r'/([a-z]+)_\d+$', uri).group(1)
    # Generate the main slug by converting non-alphanumerics to dashes
    # and then deleting consecutive, leading, and trailing dashes.
    slug = re.sub('-+', '-', re.sub('[^a-z0-9]+', '-', label.lower())).strip('-')
    if (slug == subontology):
        return subontology
    return subontology + '-' + slug

def get_text(xml, name):
    elem = xml.find(name, NS)
    if elem is None:
        return None
    return elem.text

def get_uri(xml):
    return xml.get(RDF_ABOUT)

def get_deprecated(xml):
    return get_text(xml, 'owl:deprecated')

def get_label(xml):
    return get_text(xml, 'rdfs:label')

def get_definition(xml):
    return get_text(xml, 'oboInOwl:hasDefinition')

def get_not_recommended_for_annotation(xml):
    return get_text(xml, 'edam:notRecommendedForAnnotation') == 'true'

def get_parent_uris(xml):
    return [
        sc.get(RDF_RESOURCE)
        for sc in xml.findall('rdfs:subClassOf', NS)
        if sc.get(RDF_RESOURCE) and sc.get(RDF_RESOURCE) != DEPRECATED_CLASS_URI
    ]


def main():
    # Read and parse the EDAM XML representation.
    root = ElementTree.parse(sys.stdin).getroot()

    # Convert the parsed XML into a list of simplified nodes.
    nodes = []
    for xml in root.findall('owl:Class', NS):
        deprecated = get_deprecated(xml)
        uri = get_uri(xml)
        label = get_label(xml)
        definition = get_definition(xml)
        not_recommended_for_annotation = get_not_recommended_for_annotation(xml)
        parent_uris = get_parent_uris(xml)

        if deprecated or not uri or not label or not definition:
            continue

        nodes.append({
            'uri':         uri,
            'label':       label,
            'definition':  definition,
            'not_recommended_for_annotation': not_recommended_for_annotation,
            'parent_uris': parent_uris,
        })

    # Convert the simplified nodes to our custom representation, which uses human-readable IDs.
    # Remove any parent IDs that point at a non-existent parent.
    uri_to_id = {node['uri']: to_slug(node['uri'], node['label']) for node in nodes}
    result = [
        {
            'id':          uri_to_id[node['uri']],
            'label':       node['label'],
            'definition':  node['definition'],
            'source':      node['uri'],
            'recommended_for_annotation': not node['not_recommended_for_annotation'],
            'parent_ids':  [uri_to_id[p] for p in node['parent_uris'] if p in uri_to_id],
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
