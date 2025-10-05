# In n8n this is the input to the node:
# data = _input.all()[0].json["data"]

# outside n8n, load from a file for testing:
import json
from difflib import SequenceMatcher

with open("workflows/imgflip/memes.json", "r", encoding="utf-8") as f:
    data = json.load(f)


def fuzzy_search_top_5(meme_data, search_query):
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
        description_score = calculate_similarity(meme_obj["description"], search_term)

        # Weight name matches higher than description matches
        # Also check for partial matches in both fields
        name_words = meme_obj["name"].lower().split()
        description_words = meme_obj["description"].lower().split()
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
    for meme_item in meme_data:
        score = get_match_score(meme_item, search_query)
        scored_memes.append((meme_item, score))

    # Sort by score in descending order and return top 5
    scored_memes.sort(key=lambda x: x[1], reverse=True)

    return [meme_obj for meme_obj, score in scored_memes[:5]]
