import json
import pathlib

import requests

BASE_URL = "https://pokeapi.co/api/v2/pokemon-species"
BASE_SPRITE_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"
)


def get_pokemon_sprite_url(*, pokemon_id):
    return f"{BASE_SPRITE_URL}/{pokemon_id}.png"


def fetch_all_species(*, output_file):
    all_species = []
    for pokemon_id in range(1, 151):
        names = requests.get(f"{BASE_URL}/{pokemon_id}").json()["names"]

        all_species.append(
            {
                "pokemon_id": pokemon_id,
                "names": {name["language"]["name"]: name["name"] for name in names},
                "img_url": get_pokemon_sprite_url(pokemon_id=pokemon_id),
            }
        )

    with open(output_file, "w") as f:
        json.dump(all_species, f)


if __name__ == "__main__":
    output_file = pathlib.Path(__file__).parents[1] / "data/pokemon_species.json"
    fetch_all_species(output_file=output_file)
