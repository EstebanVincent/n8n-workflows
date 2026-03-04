import json
from difflib import SequenceMatcher


def fuzzy_search_top_5(memes, query):
    """
    Perform fuzzy search on meme data based on name and description.
    Returns the top 5 best matches.
    """

    def calculate_similarity(text, search_term):
        """Calculate similarity score between text and query using SequenceMatcher."""
        return SequenceMatcher(None, text.lower(), search_term.lower()).ratio()

    def get_match_score(meme_obj, search_term):
        """Calculate overall match score for a meme object."""
        name_score = calculate_similarity(meme_obj["name"], search_term)
        # The description might not exist for all memes
        description = meme_obj.get("description", "")
        description_score = calculate_similarity(description, search_term)

        # Weight name matches higher than description matches
        # Also check for partial matches in both fields
        name_words = meme_obj["name"].lower().split()
        description_words = description.lower().split()
        query_words = search_term.lower().split()

        # Bonus for exact word matches
        name_word_matches = sum(1 for word in query_words if word in name_words)
        description_word_matches = sum(
            1 for word in query_words if word in description_words
        )

        # Combined score with weights
        combined_score = (
            name_score * 0.6  # Name gets higher weight
            + description_score * 0.3  # Description gets lower weight
            + (name_word_matches / len(query_words))
            * 0.1  # Bonus for name word matches
            + (description_word_matches / len(query_words))
            * 0.05  # Small bonus for description word matches
        )

        return combined_score

    # Calculate scores for all memes
    scored_memes = []
    for meme_item in memes:
        score = get_match_score(meme_item, query)
        scored_memes.append((meme_item, score))

    # Sort by score in descending order and return top 5
    scored_memes.sort(key=lambda x: x[1], reverse=True)

    return {"data": [meme_obj for meme_obj, score in scored_memes[:5]]}


if __name__ == "__main__":
    import click

    @click.command()
    @click.option(
        "-q",
        "--query",
        type=str,
        required=True,
        help="Search query for fuzzy matching memes.",
        prompt="Enter your search query",
    )
    @click.option(
        "-m",
        "--memes",
        type=click.Path(exists=True),
        default="ImgflipMemeCreator/inputs/fuzzy_search_top_5.json",
        help="Path to the JSON file containing meme data.",
    )
    def main(query, memes):
        """Fuzzy search for memes."""
        try:
            with open(memes, "r", encoding="utf-8") as f:
                meme_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from the file '{memes}'.")
            return

        results = fuzzy_search_top_5(meme_data, query)
        print(json.dumps(results, indent=2))

    main()  # pylint: disable=no-value-for-parameter
else:
    # In n8n, the script is not run as the main program, and _input is provided.
    data = _items[0]["json"]["data"]  # pylint: disable=undefined-variable # type: ignore # noqa

    # The result of this script will be the output of the n8n node
    result = fuzzy_search_top_5(data[0].data, data[1].output.query)
    # return result
