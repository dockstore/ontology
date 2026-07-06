#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR=${ROOT_DIR}/work
GENERATED_DIR=${ROOT_DIR}/generated

cd "${ROOT_DIR}"
mkdir -p ${WORK_DIR}
mkdir -p ${GENERATED_DIR}
rm -f ${GENERATED_DIR}/*

# For reasons not yet understood, the previously-linked EDAM file, which was present in the release assets, disappeared.
# So, in the future, link to said file via the "raw" link, as below.
OWL_URL="https://raw.githubusercontent.com/edamontology/edamontology/refs/tags/1.25-20251112T1620Z-intermediate/EDAM_dev.owl"
OWL_FILE="${WORK_DIR}/EDAM.owl"
SIMPLIFIED_FILE="${WORK_DIR}/EDAM_simplified.json"
CORRECTED_FILE="${WORK_DIR}/EDAM_corrected.json"
AMERICANIZED_FILE="${WORK_DIR}/EDAM_americanized.json"
ADJUSTED_FILE="${WORK_DIR}/EDAM_adjusted.json"
ENHANCED_FILE="${WORK_DIR}/EDAM_enhanced.json"

# Get a recent tagged release of the EDAM ontology
echo "Downloading $OWL_FILE from ${OWL_URL}..."
curl -fsSL -o "${OWL_FILE}" "${OWL_URL}"

# Convert the EDAM XML file to a simplified JSON representation.
echo "Simplifying..."
python3 simplify.py < ${OWL_FILE} > ${SIMPLIFIED_FILE}

# Apply definition corrections (spelling and grammar fixes).
echo "Correcting..."
python3 correct.py < ${SIMPLIFIED_FILE} > ${CORRECTED_FILE}

# Convert British spellings to American spellings.
echo "Americanizing..."
python3 americanize.py < ${CORRECTED_FILE} > ${AMERICANIZED_FILE}

# Adjust recommended-for-annotation property, remove unwanted portions of ontology, etc.
echo "Adjusting..."
python3 adjust.py < ${AMERICANIZED_FILE} > ${ADJUSTED_FILE}

# Add AI-suggested nodes.
echo "Enhancing..."
python3 enhance.py < ${ADJUSTED_FILE} > ${ENHANCED_FILE}

# Create a file for each subontology of interest.
echo "Extracting..."
python3 extract.py ${GENERATED_DIR} < ${ENHANCED_FILE}

# Create a Zip archive of the subontology files.
cd ${GENERATED_DIR}
zip ontologies.zip *.json

echo "Done. Ontology JSON files written to ${GENERATED_DIR}."
