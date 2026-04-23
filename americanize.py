import re
import sys

# Maps British English roots/forms to American equivalents.
# Keys are the shortest form that captures the spelling difference; all inflections
# that share the same root share the same substitution rule.
british_to_american = {
    # -our -> -or
    "behaviour":  "behavior",
    "colour":     "color",
    "tumour":     "tumor",

    # -ogue -> -og
    "catalogued":  "cataloged",
    "catalogue":  "catalog",
    "catalogui":  "catalogi",

    # -re -> -er
    "centre":     "center",

    # -ae- -> -e- (medical/scientific)
    "gynaecolog": "gynecolog",   # gynaecology, gynaecological
    "haematolog": "hematolog",   # haematology, haematological
    "paediatric": "pediatric",   # paediatrics

    # -yse -> -yze
    "analyse":    "analyze",
    "analysing":  "analyzing",
    "catalyse":   "catalyze",
    "catalysing": "catalyzing",

    # -ise -> -ize
    "anonymisa":  "anonymiza",
    "anonymise":  "anonymize",
    "anonymisi":  "anonymizi",
    "authorisa":  "authoriza",
    "authorise":  "authorize",
    "authorisi":  "authorizi",
    "categorisa": "categoriza",
    "categorise": "categorize",
    "categorisi": "categorizi",
    "characterisa": "characteriza",
    "characterise": "characterize",
    "characterisi": "characterizi",
    "conceptualisa": "conceptualiza",
    "conceptualise": "conceptualize",
    "conceptualisi": "conceptualizi",
    "customisa":  "customiza",
    "customise":  "customize",
    "customisi":  "customizi",
    "digitalisa": "digitaliza",
    "digitalise": "digitalize",
    "digitalisi": "digitalizi",
    "digitisa":   "digitiza",
    "digitise":   "digitize",
    "digitisi":   "digitizi",
    "hybridisa":  "hybridiza",
    "hybridise":  "hybridize",
    "hybridisi":  "hybridizi",
    "immobilisa": "immobiliza",
    "immobilise": "immobilize",
    "immobilisi": "immobilizi",
    "ionisa":     "ioniza",
    "ionise":     "ionize",
    "ionisi":     "ionizi",
    "localisa":   "localiza",
    "localise":   "localize",
    "localisi":   "localizi",
    "maximisa":   "maximiza",
    "maximise":   "maximize",
    "maximisi":   "maximizi",
    "minimisa":   "minimiza",
    "minimise":   "minimize",
    "minimisi":   "minimizi",
    "mobilisa":   "mobiliza",
    "mobilise":   "mobilize",
    "mobilisi":   "mobilizi",
    "normalisa":  "normaliza",
    "normalise":  "normalize",
    "normalisi":  "normalizi",
    "optimisa":   "optimiza",
    "optimise":   "optimize",
    "optimisi":   "optimizi",
    "organisa":   "organiza",
    "organise":   "organize",
    "organisi":   "organizi",
    "parallelisa": "paralleliza",
    "parallelise": "parallelize",
    "parallelisi": "parallelizi",
    "parameterisa": "parameteriza",
    "parameterise": "parameterize",
    "parameterisi": "parameterizi",
    "personalisa": "personaliza",
    "personalise": "personalize",
    "personalisi": "personalizi",
    "prioritisa": "prioritiza",
    "prioritise": "prioritize",
    "prioritisi": "prioritizi",
    "randomisa":  "randomiza",
    "randomise":  "randomize",
    "randomisi":  "randomizi",
    "recognisa":  "recogniza",
    "recognise":  "recognize",
    "recognisi":  "recognizi",
    "serialisa":  "serializa",
    "serialise":  "serialize",
    "serialisi":  "serializi",
    "specialisa": "specializa",
    "specialise": "specialize",
    "specialisi": "specializi",
    "stabilisa":  "stabiliza",
    "stabilise":  "stabilize",
    "stabilisi":  "stabilizi",
    "standardisa": "standardiza",
    "standardise": "standardize",
    "standardisi": "standardizi",
    "summarisa":  "summariza",
    "summarise":  "summarize",
    "summarisi":  "summarizi",
    "unauthorised": "unauthorized",
    "utilisa":    "utiliza",
    "utilise":    "utilize",
    "utilisi":    "utilizi",
    "visualisa":  "visualiza",
    "visualise":  "visualize",
    "visualisi":  "visualizi",

    # doubled -ll in inflected forms (root is the same in both dialects)
    "labell":     "label",
    "modell":     "model",

    # units
    "kilometre":  "kilometer",
    "metre":      "meter",
    "centimetre": "centimeter",
    "millimetre": "millimeter",
    "micrometre": "micrometer",
    "nanometre":  "nanometer",
    "litre":      "liter",
    "decilitre":  "deciliter",
    "millilitre": "milliliter",
    "microlitre": "microliter",

    # miscellaneous
    "ageing":     "aging",
    "maths":      "math",
    "artefact":   "artifact"
}

def _transfer_case(original, replacement):
    """Apply the case pattern of `original` to `replacement`, char by char."""
    result = []
    for i, ch in enumerate(replacement):
        result.append(ch.upper() if original[min(i, len(original) - 1)].isupper() else ch.lower())
    return ''.join(result)

def _make_replacer(british, american):
    def replacer(m):
        word = m.group(0)
        new_root = _transfer_case(word[:len(british)], american)
        return new_root + word[len(british):]
    return replacer

def main():
    content = sys.stdin.read()
    for british, american in british_to_american.items():
        pattern = r'\b' + re.escape(british) + r'\w*'
        content = re.sub(pattern, _make_replacer(british, american), content, flags=re.IGNORECASE)
    sys.stdout.write(content)


if __name__ == "__main__":
    main()
