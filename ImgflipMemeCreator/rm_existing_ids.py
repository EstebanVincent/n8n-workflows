import json


def rm_existing_ids(data: dict) -> list:
    """Filters out memes that already exist in the database and returns new memes."""
    new_memes = data["data"][0]["data"]["memes"]

    # If there's only one data source (no existing memes), return the first 20 new memes
    if len(data["data"]) == 1:
        return [{"json": {"success": 1, "meme": meme}} for meme in new_memes][:20]

    # Get existing meme IDs
    existing_memes = data["data"][1]["data"]
    existing_id = [meme["id"] for meme in existing_memes]

    # Filter out memes that already exist
    didnt_exist_memes = [
        {"json": {"success": 1, "meme": meme}}
        for meme in new_memes
        if int(meme["id"]) not in existing_id
    ]

    # Return up to 20 new memes, or a failure indicator if none exist
    if didnt_exist_memes:
        return didnt_exist_memes[:20]
    return [{"json": {"success": 0}}]


if __name__ == "__main__":
    import click

    @click.command()
    @click.option(
        "--json-path",
        type=click.Path(exists=True),
        default="ImgflipMemeCreator/inputs/rm_existing_ids.json",
        help="Path to the JSON file containing the input data for the n8n node.",
    )
    def main(json_path):
        """CLI for local testing of the rm_existing_ids script."""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from the file '{json_path}'.")
            return

        result = rm_existing_ids(data)
        print(json.dumps(result, indent=2))

    main()  # pylint: disable=no-value-for-parameter
else:
    # In n8n, the script is not run as the main program, and _input is provided.
    data = _items[0]["json"]  # pylint: disable=undefined-variable # type: ignore # noqa
    # return rm_existing_ids(data)
