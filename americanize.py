"""Convert the British spellings in EDAM to American spellings.
Not a general purpose converter, but instead tailored to the content of EDAM.
Written to be compact, correct, and easy to understand, at the expense of
being computationally inefficient.
"""

import re
import sys

# Maps British English roots to American equivalents.
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
    "labelle":    "labele",
    "labelli":    "labeli",
    "modelle":    "modele",
    "modelli":    "modeli",

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
    "artefact":   "artifact",
    "programme":  "program",
}


def _copy_case(source, target):
    result = []
    for target_index, ch in enumerate(target):
        source_index = min(target_index, len(source) - 1)
        if source[source_index].isupper():
            result.append(ch.upper())
        else:
            result.append(ch.lower())
    return ''.join(result)

def _replacer(m):
    word = m.group(0)
    word_lower = word.lower()
    for british, american in british_to_american.items():
        if word_lower.startswith(british):
            new_word = american + word[len(british):]
            return _copy_case(word, new_word)
    return word


def main():
    content = sys.stdin.read()
    americanized = re.sub(r'\b\w+', _replacer, content)
    sys.stdout.write(americanized)

if __name__ == "__main__":
    main()
