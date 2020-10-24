import json
import os

import flask
import joblib
import pandas as pd
from fuzzywuzzy import process

app = flask.Flask(__name__)


@app.route("/")
def home():
    return flask.send_file("../index.html")


@app.route("/favicon.ico")
def favicon():
    return flask.send_file("../favicon.ico")


@app.route("/css/<path:subpath>")
def css(subpath):
    return flask.send_from_directory("../css", subpath)


@app.route("/lib/<path:subpath>")
def js(subpath):
    return flask.send_from_directory("../lib", subpath)


@app.route("/search/")
def search():
    return flask.jsonify(
        get_search_results(
            pokemon_name=flask.request.args.get("q"),
            lang=flask.request.headers.get("Accept-Language"),
        )
    )


@app.route("/fight/", methods=["POST"])
def fight():
    data = flask.request.json
    print(flask.request.headers)
    return flask.jsonify(
        {
            "winner": predict_battle_outcome(
                pokemon_id_left=int(data["left"]["id"]),
                pokemon_id_right=int(data["right"]["id"]),
                trained_estimator=POKEMON_MODEL,
            )
        }
    )


def load_database():

    input_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data/pokemon_species.json",
    )
    with open(input_file, "r") as f:
        return json.load(f)


POKE_DATABASE = load_database()


def localized_database(*, lang):
    # Only keep the `lang` names
    for result in POKE_DATABASE:
        result = result.copy()
        result["name"] = result.pop("names")[lang]
        yield result


def get_search_results(*, pokemon_name, lang="en", limit=3):
    if lang not in ["en", "fr"]:
        raise Exception("TODO: Proper lang check?")

    database = list(localized_database(lang=lang))

    # We want to match on pokemon name, hence the processor. As far as I understand,
    # the search query is processed the same way so we query with the form:
    # {"name": pokemon_name}
    matches = process.extract(
        {"name": pokemon_name},
        database,
        processor=lambda x: x["name"],
        limit=limit,
    )
    print([(match["name"], score) for match, score in matches])
    return [match for match, score in matches if score > 70]


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


def get_pokemon_dataset():
    return pd.read_csv("ml/pokemon.csv", index_col=0)


def get_pokemon_model():
    return joblib.load("ml/model.pickle")


POKEMON_DATASET = get_pokemon_dataset()

POKEMON_MODEL = get_pokemon_model()


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


def predict_battle_outcome(
    pokemon_id_left: int, pokemon_id_right: int, trained_estimator
):
    df = pd.DataFrame(
        data=[[pokemon_id_left, pokemon_id_right]],
        columns=["First_pokemon", "Second_pokemon"],
    )
    X = preprocess_test_data(df).values

    if trained_estimator.predict(X)[0]:
        return "left"
    else:
        return "right"
