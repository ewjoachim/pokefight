import flask
import pandas as pd
from fuzzywuzzy import process

from pokefight import magic

app = flask.Flask(__name__)

NUMBER_SEARCH_RESULTS = 3
SEARCH_SCORE_THRESHOLD = 70


@app.route("/")
def home():
    return flask.render_template("index.html")


@app.route("/search/")
def search():
    language = flask.request.headers.get("Accept-Language", "en")

    if language not in magic.SUPPORTED_LANGUAGES:
        language = "en"

    database = list(magic.POKE_DATABASE[language].values())

    pokemon_name = flask.request.args.get("q")

    # We want to match on pokemon name, hence the processor. As far as I understand,
    # the search query is processed the same way so we query with the form:
    # {"name": pokemon_name}
    matches = process.extract(
        {"name": pokemon_name},
        database,
        processor=lambda x: x["name"],
        limit=NUMBER_SEARCH_RESULTS,
    )
    return flask.jsonify(
        [match for match, score in matches if score > SEARCH_SCORE_THRESHOLD]
    )


@app.route("/fight/", methods=["POST"])
def fight():
    data = flask.request.json

    pokemon_left = magic.get_pokemon_row(id=data["left"]["id"])
    pokemon_right = magic.get_pokemon_row(id=data["right"]["id"])

    df = pd.DataFrame(
        data=[[pokemon_left, pokemon_right]],
        columns=["First_pokemon", "Second_pokemon"],
    )
    X = magic.preprocess_test_data(df).values

    if magic.POKEMON_MODEL.predict(X)[0]:
        result = "left"
    else:
        result = "right"

    return flask.jsonify({"winner": result})
