import json
from datetime import datetime, timedelta


def minutes_to_hours(m: int | float) -> float:
    """Converts minutes to hours, rounded to one decimal place."""
    return round(m / 60.0, 1)


def to_discord_message(data: dict):
    """Creates a Discord message embed from Steam playtime data."""
    games = data.get("response", {}).get("games", [])
    games.sort(key=lambda g: g.get("playtime_2weeks", 0), reverse=True)
    top = games[:5]

    total_minutes = sum(g.get("playtime_2weeks", 0) for g in games)
    total_hours = minutes_to_hours(total_minutes)
    unique_games = len(games)

    today = datetime.now(ZoneInfo("Europe/Paris")).date()
    start_date = today - timedelta(days=14)
    date_range = f"{start_date.isoformat()} → {today.isoformat()}"

    medals = ["🥇", "🥈", "🥉"]
    fields = []
    for i, g in enumerate(top):
        prefix = medals[i] if i < len(medals) else "•"
        fields.append(
            {
                "name": f"{prefix} {g.get('name', 'Unknown')}",
                "value": f"**{minutes_to_hours(g.get('playtime_2weeks', 0))} h** in the last 2 weeks  ·  Lifetime: {minutes_to_hours(g.get('playtime_forever', 0))} h",
                "inline": False,
            }
        )

    desc = (
        (f"**{total_hours} h** across **{unique_games}** game(s) in the last 2 weeks.")
        if unique_games
        else "No playtime recorded in the last 2 weeks."
    )

    embed = {
        "title": "🎮 Last 2 Weeks Steam Report",
        "description": desc,
        "color": 3066993,
        "fields": fields,
        "footer": {"text": f"Period: {date_range}"},
    }

    return [{"json": {"embed": embed}}]


if __name__ == "__main__":
    from zoneinfo import ZoneInfo

    import click

    @click.command()
    @click.option(
        "--json-path",
        type=click.Path(exists=True),
        default="WeeklySteam/inputs/to_discord_message.json",
        help="Path to the JSON file containing the input data for the n8n node.",
    )
    def main(json_path):
        """CLI for local testing of the create_embed script."""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from the file '{json_path}'.")
            return

        result = to_discord_message(data)
        print(json.dumps(result, indent=2))

    main()  # pylint: disable=no-value-for-parameter
else:
    # In n8n, the script is not run as the main program, and _items is provided.
    from zoneinfo import ZoneInfo
    data = _items[0]["json"]  # pylint: disable=undefined-variable # type: ignore # noqa
    # return to_discord_message(data)
