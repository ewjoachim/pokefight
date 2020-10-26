import json
import os

import joblib
import pandas as pd

SUPPORTED_LANGUAGES = ["en", "fr"]


def get_pokemon_dataset():
    return pd.read_csv("ml/pokemon.csv", index_col=0)


def get_pokemon_model():
    return joblib.load("ml/model.pickle")


POKEMON_DATASET = get_pokemon_dataset()

POKEMON_MODEL = get_pokemon_model()


def dummify(type_series, prefix):
    # we need to give our classifier data with the same columns as the data it has learned on
    # in particular, we need to have all type columns present, even if they are not in the test set
    # that's why we extract all the types from the trainset, and fill the missing columns with zeros
    type_columns = sorted(
        prefix + "_" + tc for tc in POKEMON_DATASET["Type 1"].unique()
    )
    dummies = pd.get_dummies(type_series.iloc[:, 0], prefix=prefix).add(
        pd.get_dummies(type_series.iloc[:, 1], prefix=prefix), fill_value=0
    )
    missing_cols = set(type_columns) - set(dummies.columns)
    for c in missing_cols:
        dummies[c] = 0
    return dummies[type_columns]


def preprocess_test_data(battles_test):
    # we need to apply all the preprocessing steps we applied on our training data
    # 1°) joining data about battle outcomes and pokemons
    df_test = battles_test.join(POKEMON_DATASET, on="First_pokemon").join(
        POKEMON_DATASET, on="Second_pokemon", rsuffix="_opponent"
    )
    # 2°) encoding the winner as int (1 if First_pokemon wins, 0 else)
    if "Winner" in df_test.columns:
        df_test["label"] = (df_test["First_pokemon"] == df_test["Winner"]).astype(int)
        df_test = df_test.drop(columns=["Winner"])
    # 3°) dropping useless columns
    df_test = df_test.drop(
        [
            "First_pokemon",
            "Second_pokemon",
            "Name",
            "Name_opponent",
            "Generation",
            "Generation_opponent",
        ],
        axis=1,
    )
    # 4°) encoding boleans as int
    df_test["Legendary"] = df_test["Legendary"].astype(int)
    df_test["Legendary_opponent"] = df_test["Legendary_opponent"].astype(int)
    # 5°) one-hot encoding of categorical columns
    types = dummify(df_test[["Type 1", "Type 2"]], prefix="Type")
    types_opponents = dummify(
        df_test[["Type 1_opponent", "Type 2_opponent"]], prefix="Opponent_Type"
    )
    return pd.concat((df_test, types, types_opponents), axis=1).drop(
        ["Type 1", "Type 2", "Type 1_opponent", "Type 2_opponent"], axis=1
    )


def get_pokemon_row(id):
    name_en = POKE_DATABASE["en"][id]["name"]
    return POKEMON_DATASET.index[POKEMON_DATASET["Name"] == name_en][0]


def load_database():

    input_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data/pokemon_species.json",
    )
    with open(input_file, "r") as f:
        database_all_languages = json.load(f)

    database = {}
    for language in SUPPORTED_LANGUAGES:
        database[language] = {
            pokemon["pokemon_id"]: {
                "pokemon_id": pokemon["pokemon_id"],
                "name": pokemon["names"][language],
                "img_url": pokemon["img_url"],
            }
            for pokemon in database_all_languages
        }
    return database


POKE_DATABASE = load_database()
