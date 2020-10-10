"use strict";

document.addEventListener('DOMContentLoaded', function () {
  var LANGUAGE = "fr";
  var searchUrl = function searchUrl(query) {
    return "/search.json?q=" + query;
  };
  var fightUrl = function fightUrl(query) {
    return "/result.json";
  };
  document.querySelectorAll(".pokemon-input.pokemon-name").forEach(function (element) {
    element.addEventListener('input', function (event) {
      searchPokemon(event.target);
    });
  });
  async function searchPokemon(element) {
    var headers = new Headers({ "Accept-Language": LANGUAGE });
    var response = await fetch(searchUrl(element.value), { "headers": headers });
    var data = await response.json();
    var tile = element.closest(".pokemon-choice-tile");
    var searchResult = tile.querySelector(".search-results");
    searchResult.textContent = "";
    data.forEach(function (pokemon) {
      var node = pokemonChoiceNode(pokemon);
      searchResult.append(node);
      installClickPokemonChoice(node);
    });
    adjustSelection(tile);
  }
  function pokemonChoiceNode(pokemon) {
    var fragment = document.querySelector("template.pokemon-choice").content.cloneNode(true);
    var node = fragment.children[0];
    var image = node.querySelector(".pokemon-button-image");
    image.src = pokemon.image;
    image.alt = pokemon.name;
    node.querySelector(".pokemon-button-name").textContent = pokemon.name;
    node.dataset.pokemonId = pokemon.id;
    node.dataset.pokemonName = pokemon.name;
    return node;
  }
  function installClickPokemonChoice(element) {
    element.addEventListener("click", function (event) {
      var tile = this.closest(".pokemon-choice-tile");
      tile.dataset.pokemonId = this.dataset.pokemonId;
      tile.dataset.pokemonName = this.dataset.pokemonName;
      adjustSelection(tile);
    });
  }
  function adjustSelection(tile) {
    var id = tile.dataset.pokemonId;
    tile.querySelectorAll(".search-results .card").forEach(function (choice) {
      choice.classList.remove("has-background-primary");
    });
    var result = tile.querySelector(".search-result[data-pokemon-id=\"" + id + "\"] .card");
    if (result) {
      result.classList.add("has-background-primary");
    }
  }

  var sideElements = {
    "left": document.querySelector('.pokemon-choice-tile[data-side="left"]'),
    "right": document.querySelector('.pokemon-choice-tile[data-side="right"]')
  };
  function getInputForSide(side) {
    var id = parseInt(side.dataset.pokemonId);
    var level = parseInt(side.querySelector(".pokemon-level").value);
    if (id && Number.isInteger(level)) {
      return { "id": id, "level": level };
    }
  }
  document.querySelector(".fight-button").addEventListener("click", async function () {
    var leftInput = getInputForSide(sideElements.left);
    var rightInput = getInputForSide(sideElements.right);
    if (leftInput && rightInput) {
      var data = { "left": leftInput, "right": rightInput };
      console.log(data);
      var response = await fetch(fightUrl(), {
        method: 'GET' //'POST',
        // body: JSON.stringify(data)
      });
      var winner = (await response.json())["winner"];
      document.querySelector(".winner-tile").classList.remove("is-hidden");
      var winnerName = sideElements[winner].dataset.pokemonName;
      var winnerEmoji = { "left": "👈", "right": "👉" }[winner];
      document.querySelector(".winner-name").textContent = winnerName;
      document.querySelector(".winner-emoji").textContent = winnerEmoji;
    }
  });
});