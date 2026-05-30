#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR=${ROOT_DIR}/work
GENERATED_DIR=${ROOT_DIR}/generated

cd "${ROOT_DIR}"
mkdir -p ${WORK_DIR}
mkdir -p ${GENERATED_DIR}

EDAM_TAG="1.25-20251112T1620Z-intermediate"
OWL_URL="https://github.com/edamontology/edamontology/releases/download/${EDAM_TAG}/EDAM.owl"
OWL_FILE="${WORK_DIR}/EDAM.owl"
SIMPLIFIED_FILE="${WORK_DIR}/EDAM_simplified.json"
AMERICANIZED_FILE="${WORK_DIR}/EDAM_americanized.json"
ADJUSTED_FILE="${WORK_DIR}/EDAM_adjusted.json"
ENHANCED_FILE="${WORK_DIR}/EDAM_enhanced.json"

# Get a recent tagged release of the EDAM ontology
echo "Downloading $OWL_FILE from tag ${EDAM_TAG}..."
curl -fsSL -o "${OWL_FILE}" "${OWL_URL}"

# Convert the EDAM XML file to a simplified JSON representation.
echo "Simplifying..."
python3 simplify.py < ${OWL_FILE} > ${SIMPLIFIED_FILE}

# Convert British spellings to American spellings.
echo "Americanizing..."
python3 americanize.py < ${SIMPLIFIED_FILE} > ${AMERICANIZED_FILE}

# Adjust recommended-for-annotation property, make other similar changes.
echo "Adjusting..."
python3 adjust.py < ${AMERICANIZED_FILE} > ${ADJUSTED_FILE}

# Add AI-suggested nodes.
echo "Enhancing..."
python3 enhance.py < ${ADJUSTED_FILE} > ${ENHANCED_FILE}

# Create a file for each subontology of interest using the adjusted, enhanced EDAM JSON representation.
echo "Extracting..."
python3 extract.py ${GENERATED_DIR} < ${ENHANCED_FILE}

echo "Done. Ontology JSON files written to ${GENERATED_DIR}."
