# In n8n this is the input to the node:
# data = _input.all()[0].json

# outside n8n, load from a file for testing:
import json

with open("workflows/lastfm/input.json", "r", encoding="utf-8") as f:
    data = json.load(f)

from collections import Counter
from datetime import datetime
from typing import Any, Dict, List


def norm(x: Any) -> str:
    """Normalize string values by stripping whitespace."""
    return (x or "").strip()


def convert_n8n_object(obj: Any) -> dict:
    """Convert n8n JsProxy objects to Python dictionaries."""
    if isinstance(obj, dict):
        return obj
    try:
        return obj.to_py() if hasattr(obj, "to_py") else {}
    except Exception:
        return {}


def extract_image_url(images: Any) -> str | None:
    """Extract the best available image URL from a list of images."""
    if not images:
        return None

    images_list = [convert_n8n_object(img) for img in images]
    by_size = {
        norm(img.get("size", "")): norm(img.get("#text", "")) for img in images_list
    }

    for size in ["extralarge", "large", "medium", "small"]:
        if url := by_size.get(size):
            return url

    return next(
        (
            norm(img.get("#text", ""))
            for img in images_list
            if norm(img.get("#text", ""))
        ),
        None,
    )


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


# Parse tracks
rows = []
for tr in data.get("recenttracks", {}).get("track", []):
    attr = tr.get("@attr")
    if attr and attr.get("nowplaying") in ("true", True):
        continue

    date_uts = (tr.get("date") or {}).get("uts")
    dt = datetime.fromtimestamp(int(date_uts)) if date_uts else None
    artist = norm((tr.get("artist") or {}).get("#text"))
    track = norm(tr.get("name"))
    album = norm((tr.get("album") or {}).get("#text"))
    image = extract_image_url(tr.get("image"))

    if artist and track:
        rows.append(
            {"artist": artist, "track": track, "album": album, "image": image, "dt": dt}
        )

# Calculate statistics
total_scrobbles = len(rows)
unique_tracks = len({(r["artist"], r["track"]) for r in rows})
unique_artists = len({r["artist"] for r in rows})
track_counter = Counter((r["artist"], r["track"]) for r in rows).most_common(5)
artist_counter = Counter(r["artist"] for r in rows).most_common(5)
album_counter = Counter(
    (r["artist"], r["album"]) for r in rows if r["album"]
).most_common(5)

# Build fields
fields = []
summary = (
    f"**{total_scrobbles}** scrobbles · **{unique_tracks}** unique tracks · **{unique_artists}** unique artists"
    if total_scrobbles
    else "No scrobbles this week."
)
fields.append({"name": "Weekly Summary", "value": summary, "inline": False})

if total_scrobbles > 0:
    scrobbles_by_day = Counter(r["dt"].date() for r in rows if r["dt"])
    if scrobbles_by_day:
        days = (max(scrobbles_by_day) - min(scrobbles_by_day)).days + 1
        avg = total_scrobbles / days if days > 0 else total_scrobbles
        most_active = scrobbles_by_day.most_common(1)[0]
        day_str = most_active[0].strftime("%A")
        fields.append(
            {
                "name": "Activity",
                "value": f"Avg **{avg:.1f}** scrobbles/day · Most active day: **{day_str}** ({most_active[1]} scrobbles)",
                "inline": False,
            }
        )

medals = ["🥇", "🥈", "🥉"]
for name, items, formatter in [
    ("Top Tracks", track_counter, lambda i: f"{i[0][1]} — {i[0][0]} · {i[1]}×"),
    ("Top Albums", album_counter, lambda i: f"{i[0][1]} — {i[0][0]} · {i[1]}×"),
    ("Top Artists", artist_counter, lambda i: f"{i[0]} · {i[1]}×"),
]:
    if items:
        lines = [
            f"{medals[idx] if idx < 3 else '•'} **{formatter(item)}**"
            for idx, item in enumerate(items)
        ]
        fields.append({"name": name, "value": "\n".join(lines), "inline": False})

# Create embeds
summary_embed = {
    "title": "🎧 Weekly Last.fm Report",
    "description": summary,
    "color": 3447003,
    "fields": [f for f in fields if f["name"] == "Activity"],
}

if thumb := find_thumbnail(
    rows, artist=artist_counter[0][0] if artist_counter else None
):
    summary_embed["thumbnail"] = thumb


def create_list_embed(
    title: str,
    field_name: str,
    artist: str = None,
    album: str = None,
    track: str = None,
) -> dict | None:
    """Create an embed for a specific top list."""
    field = next((f for f in fields if f["name"] == field_name), None)
    if not field:
        return None

    embed = {
        "title": title,
        "color": 3447003,
        "fields": [{"name": field_name, "value": field["value"], "inline": False}],
    }

    if thumb := find_thumbnail(rows, artist, album, track):
        embed["thumbnail"] = thumb

    return embed


output = {
    "summary_embed": summary_embed,
    "track_embed": create_list_embed(
        "Top Tracks",
        "Top Tracks",
        artist=track_counter[0][0][0] if track_counter else None,
        track=track_counter[0][0][1] if track_counter else None,
    ),
    "album_embed": create_list_embed(
        "Top Albums",
        "Top Albums",
        artist=album_counter[0][0][0] if album_counter else None,
        album=album_counter[0][0][1] if album_counter else None,
    ),
    "artist_embed": create_list_embed(
        "Top Artists",
        "Top Artists",
        artist=artist_counter[0][0] if artist_counter else None,
    ),
}

# return [{"json": output}]
print(json.dumps([{"json": output}]))
