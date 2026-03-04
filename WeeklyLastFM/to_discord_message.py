import json
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List


def extract_image_url(images: Any) -> str | None:
    """Extract the best available image URL from a list of images."""
    if not images:
        return None

    by_size = {img["size"]: img["#text"] for img in images}

    for size in ["extralarge", "large", "medium", "small"]:
        if url := by_size.get(size):
            return url
    return None


def find_thumbnail(
    rows: List[Dict], artist: str = None, album: str = None, track: str = None
) -> str | None:
    """Find a thumbnail URL matching the given criteria."""
    for r in reversed(rows):
        if artist and r["artist"] != artist:
            continue
        if album and r.get("album") != album:
            continue
        if track and r["track"] != track:
            continue
        if r.get("image"):
            return r["image"]
    return None


def to_discord_message(data: dict):
    """Creates a Discord message embed from Last.fm scrobble data."""
    # Parse tracks
    rows = []
    for tr in data["recenttracks"]["track"]:
        attr = tr.get("@attr")
        if attr and attr.get("nowplaying"):
            continue

        date_uts = tr["date"]["uts"]
        dt = datetime.fromtimestamp(int(date_uts)) if date_uts else None
        artist = tr["artist"]["#text"]
        track = tr["name"]
        album = tr["album"]["#text"]
        image = extract_image_url(tr["image"])

        if artist and track:
            rows.append(
                {
                    "artist": artist,
                    "track": track,
                    "album": album,
                    "image": image,
                    "dt": dt,
                }
            )

    # Calculate statistics
    total_scrobbles = len(rows)
    unique_tracks = len({(r["artist"], r["track"]) for r in rows})
    unique_artists = len({r["artist"] for r in rows})
    unique_albums = len({r["album"] for r in rows})
    track_counter = Counter((r["artist"], r["track"]) for r in rows).most_common(5)
    artist_counter = Counter(r["artist"] for r in rows).most_common(5)
    album_counter = Counter(
        (r["artist"], r["album"]) for r in rows if r["album"]
    ).most_common(5)

    # Build fields
    summary = (
        f"**{total_scrobbles}** scrobbles · **{unique_tracks}** Tracks · **{unique_artists}** Artists · **{unique_albums}** Albums"
        if total_scrobbles
        else "No scrobbles this week."
    )

    today = datetime.now(ZoneInfo("Europe/Paris")).date()
    start_date = today - timedelta(days=7)
    date_range = f"{start_date.isoformat()} → {today.isoformat()}"

    # Create embeds
    summary_embed = {
        "title": "Weekly Last.fm Report",
        "description": summary,
        "color": 3447003,
        "fields": [],
        "footer": {"text": f"{date_range}"},
    }

    if total_scrobbles > 0:
        scrobbles_by_day = Counter(r["dt"].date() for r in rows if r["dt"])
        if scrobbles_by_day:
            days = (max(scrobbles_by_day) - min(scrobbles_by_day)).days + 1
            avg = total_scrobbles / days if days > 0 else total_scrobbles
            most_active = scrobbles_by_day.most_common(1)[0]
            day_str = most_active[0].strftime("%A")
            summary_embed["fields"].append(
                {
                    "name": "Activity",
                    "value": f"Avg **{avg:.1f}** scrobbles/day · Most active day: **{day_str}** ({most_active[1]} scrobbles)",
                    "inline": False,
                }
            )

    def create_artist_embed(items: list, thumb_artist: str = None) -> dict | None:
        """Create embed for top artists with individual fields."""
        if not items:
            return None

        embed = {
            "title": "Top Artists",
            "color": 3447003,
            "fields": [
                {"name": artist, "value": f"{count} scrobbles", "inline": False}
                for artist, count in items
            ],
        }

        if thumb := find_thumbnail(rows, artist=thumb_artist):
            embed["image"] = thumb

        return embed

    def create_track_album_embed(
        title: str,
        items: list,
        thumb_artist: str = None,
        thumb_album: str = None,
        thumb_track: str = None,
    ) -> dict | None:
        """Create embed for tracks/albums with individual fields."""
        if not items:
            return None

        embed = {"title": title, "color": 3447003, "fields": []}

        for (artist, name), count in items:
            embed["fields"].append(
                {
                    "name": name,
                    "value": f"{artist}\n{count} scrobbles",
                    "inline": False,
                }
            )

        if thumb := find_thumbnail(
            rows, artist=thumb_artist, album=thumb_album, track=thumb_track
        ):
            embed["image"] = thumb

        return embed

    output = {
        "summary_embed": summary_embed,
        "track_embed": create_track_album_embed(
            "Top Tracks",
            track_counter,
            thumb_artist=track_counter[0][0][0] if track_counter else None,
            thumb_track=track_counter[0][0][1] if track_counter else None,
        ),
        "album_embed": create_track_album_embed(
            "Top Albums",
            album_counter,
            thumb_artist=album_counter[0][0][0] if album_counter else None,
            thumb_album=album_counter[0][0][1] if album_counter else None,
        ),
        "artist_embed": create_artist_embed(
            artist_counter,
            thumb_artist=artist_counter[0][0] if artist_counter else None,
        ),
    }

    return [{"json": output}]


if __name__ == "__main__":
    from zoneinfo import ZoneInfo

    import click

    @click.command()
    @click.option(
        "--json-path",
        type=click.Path(exists=True),
        default="WeeklyLastFM/inputs/to_discord_message.json",
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