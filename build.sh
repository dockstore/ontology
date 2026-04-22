#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${ROOT_DIR}"

WORK_DIR=${ROOT_DIR}/work
mkdir -p ${WORK_DIR}

EDAM_TAG="1.25-20251112T1620Z-intermediate"
OWL_URL="https://github.com/edamontology/edamontology/releases/download/${EDAM_TAG}/EDAM.owl"
OWL_FILE="${WORK_DIR}/EDAM.owl"
SIMPLIFIED_FILE="${WORK_DIR}/EDAM_simplified.json"

# Get a recent tagged release of the EDAM ontology
echo "Downloading $OWL_FILE from tag ${EDAM_TAG}..."
curl -fsSL -o "${OWL_FILE}" "${OWL_URL}"

# Convert the EDAM XML file to a simplified JSON representation.
python simplify.py < ${OWL_FILE} > ${SIMPLIFIED_FILE}

# Create a file for each subontology of interest using the simplified EDAM JSON representation.
python extract.py < ${SIMPLIFIED_FILE}

echo "Done. JSON files written to ${ROOT_DIR}."
