document.addEventListener('DOMContentLoaded', () => {
  const LANGUAGE = "fr";
  const searchUrl = (query) => `/search/?q=${query}`
  const fightUrl = (query) => `/fight/`
  document.querySelectorAll(".pokemon-input.pokemon-name").forEach((element) => {
    element.addEventListener('input', (event) => {
      searchPokemon(event.target)
    })
    searchPokemon(element)

  })
  async function searchPokemon(element) {
    const headers = new Headers({ "Accept-Language": LANGUAGE });
    const response = await fetch(searchUrl(element.value), { "headers": headers });
    const data = await response.json();
    const tile = element.closest(".pokemon-choice-tile");
    const searchResult = tile.querySelector(".search-results");
    searchResult.textContent = ""
    data.forEach((pokemon) => {
      const node = pokemonChoiceNode(pokemon);
      searchResult.append(node);
      installClickPokemonChoice(node);
    });
    adjustSelection(tile);
  }
  function pokemonChoiceNode(pokemon) {
    const fragment = document.querySelector("template.pokemon-choice").content.cloneNode(true);
    const node = fragment.children[0]
    const image = node.querySelector(".pokemon-button-image")
    image.src = pokemon.img_url;
    image.alt = pokemon.name;
    node.querySelector(".pokemon-button-name").textContent = pokemon.name;
    node.dataset.pokemonId = pokemon.pokemon_id;
    node.dataset.pokemonName = pokemon.name;
    return node;
  }
  function installClickPokemonChoice(element) {
    element.addEventListener("click", function (event) {
      const tile = this.closest(".pokemon-choice-tile");
      tile.dataset.pokemonId = this.dataset.pokemonId;
      tile.dataset.pokemonName = this.dataset.pokemonName;
      tile.querySelector(".pokemon-input").value = tile.dataset.pokemonName;
      adjustSelection(tile);
    })
  }
  function adjustSelection(tile) {
    const id = tile.dataset.pokemonId;
    tile.querySelectorAll(".search-results .card").forEach((choice) => {
      choice.classList.remove("has-background-primary")
    });
    const result = tile.querySelector(`.search-result[data-pokemon-id="${id}"] .card`);
    if (result) {
      result.classList.add("has-background-primary");
    }
  }

  const sideElements = {
    "left": document.querySelector('.pokemon-choice-tile[data-side="left"]'),
    "right": document.querySelector('.pokemon-choice-tile[data-side="right"]'),
  }
  function getInputForSide(side) {
    const id = parseInt(side.dataset.pokemonId);
    if (id) {
      return { "id": id };
    }
  }
  document.querySelector(".fight-button").addEventListener("click", async function () {
    const leftInput = getInputForSide(sideElements.left);
    const rightInput = getInputForSide(sideElements.right);
    if (leftInput && rightInput) {
      const data = { "left": leftInput, "right": rightInput };
      const response = await fetch(fightUrl(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      const winner = (await response.json())["winner"];
      document.querySelector(".winner-tile").classList.remove("is-hidden");
      const winnerName = sideElements[winner].dataset.pokemonName;
      const winnerEmoji = { "left": "👈", "right": "👉" }[winner];
      document.querySelector(".winner-name").textContent = winnerName;
      document.querySelector(".winner-emoji").textContent = winnerEmoji;
    }
  })
});
