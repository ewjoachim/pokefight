import json
import os

from fuzzywuzzy import process


def load_all_results(*, lang):
    input_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data/pokemon_species.json",
    )

    with open(input_file, "r") as f:
        all_results = json.load(f)

    # Only keep the `lang` names
    for result in all_results:
        names = result.pop("names")
        result["name"] = names[lang]

    return all_results


def get_search_results(*, pokemon_name, lang="en", limit=5):
    if lang not in ["en", "fr"]:
        raise Exception("TODO: Proper lang check?")

    all_results = load_all_results(lang=lang)

    # We want to match on pokemon name, hence the processor. As far as I understand,
    # the search query is processed the same way so we query with the form:
    # {"name": pokemon_name}
    matches = process.extract(
        {"name": pokemon_name},
        all_results,
        processor=lambda x: x["name"],
        limit=limit,
    )
    # TODO: Remove matches below a threshold score?
    return [match for match, score in matches]
