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
SIMPLIFIED_AMERICANIZED_FILE="${WORK_DIR}/EDAM_simplified_americanized.json"
SIMPLIFIED_CORRECTED_FILE="${WORK_DIR}/EDAM_simplified_corrected.json"

# Get a recent tagged release of the EDAM ontology
echo "Downloading $OWL_FILE from tag ${EDAM_TAG}..."
curl -fsSL -o "${OWL_FILE}" "${OWL_URL}"

# Convert the EDAM XML file to a simplified JSON representation.
echo "Simplifying..."
python3 simplify.py < ${OWL_FILE} > ${SIMPLIFIED_FILE}

# Convert British spellings to American spellings.
echo "Americanizing..."
python3 americanize.py < ${SIMPLIFIED_FILE} > ${SIMPLIFIED_AMERICANIZED_FILE}

# Apply definition corrections (spelling and grammar fixes).
echo "Correcting..."
python3 correct.py < ${SIMPLIFIED_AMERICANIZED_FILE} > ${SIMPLIFIED_CORRECTED_FILE}

# Create a file for each subontology of interest using the simplified+Americanized+corrected EDAM JSON representation.
echo "Extracting..."
python3 extract.py ${GENERATED_DIR} < ${SIMPLIFIED_CORRECTED_FILE}

echo "Done. Ontology JSON files written to ${GENERATED_DIR}."
