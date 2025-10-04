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
    return (x or "").strip()


def first_image(images: Any) -> str | None:
    """Extract the best available image URL from a list of images."""
    if not images:
        return None

    # Convert images to list of dicts if needed (for n8n compatibility)
    images_list = []
    for img in images:
        if isinstance(img, dict):
            images_list.append(img)
        else:
            # Handle n8n JsProxy objects by using to_py() method
            try:
                converted = img.to_py() if hasattr(img, "to_py") else {}
                images_list.append(converted)
            except Exception:
                images_list.append({})

    by_size = {
        norm(img.get("size", "")): norm(img.get("#text", "")) for img in images_list
    }

    for size in ["extralarge", "large", "medium", "small"]:
        if url := by_size.get(size):
            return url

    fallback = next(
        (
            norm(img.get("#text", ""))
            for img in images_list
            if norm(img.get("#text", ""))
        ),
        None,
    )
    return fallback


# Gather weekly tracks from all inputs; ignore "now playing"
rows: List[Dict[str, Any]] = []

for tr in data.get("recenttracks").get("track", []):
    attr = tr.get("@attr")
    if attr and attr.get("nowplaying") in ("true", True):
        continue
    #
    date_uts = (tr.get("date") or {}).get("uts")
    dt = datetime.fromtimestamp(int(date_uts)) if date_uts else None
    #
    artist = norm((tr.get("artist") or {}).get("#text"))
    track = norm(tr.get("name"))
    album = norm((tr.get("album") or {}).get("#text"))
    image = first_image(tr.get("image"))
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

total_scrobbles = len(rows)
unique_tracks = len({(r["artist"], r["track"]) for r in rows})
unique_artists = len({r["artist"] for r in rows})

track_counter = Counter((r["artist"], r["track"]) for r in rows).most_common(5)
artist_counter = Counter(r["artist"] for r in rows).most_common(5)
album_counter = Counter(
    (r["artist"], r["album"]) for r in rows if r["album"]
).most_common(5)

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
        avg_scrobbles = total_scrobbles / days if days > 0 else total_scrobbles
        most_active_day = scrobbles_by_day.most_common(1)[0]
        day_str = most_active_day[0].strftime("%A")
        stats = f"Avg **{avg_scrobbles:.1f}** scrobbles/day · Most active day: **{day_str}** ({most_active_day[1]} scrobbles)"
        fields.append({"name": "Activity", "value": stats, "inline": False})

medals = ["🥇", "🥈", "🥉"]
if track_counter:
    lines = []
    for i, ((a, t), c) in enumerate(track_counter):
        prefix = medals[i] if i < len(medals) else "•"
        lines.append(f"{prefix} **{t}** — {a} · {c}×")
    fields.append({"name": "Top Tracks", "value": "\n".join(lines), "inline": False})

if album_counter:
    lines = []
    for i, ((ar, al), c) in enumerate(album_counter):
        prefix = medals[i] if i < len(medals) else "•"
        lines.append(f"{prefix} **{al}** — {ar} · {c}×")
    fields.append({"name": "Top Albums", "value": "\n".join(lines), "inline": False})

if artist_counter:
    lines = []
    for i, (a, c) in enumerate(artist_counter):
        prefix = medals[i] if i < len(medals) else "•"
        lines.append(f"{prefix} **{a}** · {c}×")
    fields.append({"name": "Top Artists", "value": "\n".join(lines), "inline": False})


def find_thumbnail(
    artist_name: str = None, album_name: str = None, track_name: str = None
) -> str | None:
    """Find a thumbnail URL matching the given criteria, or return any available image."""

    for r in reversed(rows):
        if artist_name and r["artist"] != artist_name:
            continue
        if album_name and r.get("album") != album_name:
            continue
        if track_name and r["track"] != track_name:
            continue
        if r.get("image"):
            return r["image"]

    return None


thumb_url = (
    find_thumbnail(artist_name=artist_counter[0][0])
    if artist_counter
    else find_thumbnail()
)

# Embed 1: Main Summary
summary_embed = {
    "title": "🎧 Weekly Last.fm Report",
    "description": summary,
    "color": 3447003,
    "fields": [f for f in fields if f["name"] in ("Activity")],
}
if thumb_url:
    summary_embed["thumbnail"] = thumb_url


def create_list_embed(title: str, field_name: str) -> dict | None:
    """Creates an embed for a list of items."""
    field = next((f for f in fields if f["name"] == field_name), None)
    if not field:
        return None

    embed = {
        "title": title,
        "color": 3447003,
        "fields": [{"name": field_name, "value": field["value"], "inline": False}],
    }

    # Find thumbnail based on the top item
    thumb_map = {
        "Top Artists": (artist_counter[0][0], None, None)
        if artist_counter
        else (None, None, None),
        "Top Albums": (album_counter[0][0][0], album_counter[0][0][1], None)
        if album_counter
        else (None, None, None),
        "Top Tracks": (track_counter[0][0][0], None, track_counter[0][0][1])
        if track_counter
        else (None, None, None),
    }

    if field_name in thumb_map:
        art, alb, trk = thumb_map[field_name]
        if thumb := find_thumbnail(artist_name=art, album_name=alb, track_name=trk):
            embed["thumbnail"] = thumb

    return embed


output = {
    "summary_embed": summary_embed,
    "track_embed": create_list_embed("Top Tracks", "Top Tracks"),
    "album_embed": create_list_embed("Top Albums", "Top Albums"),
    "artist_embed": create_list_embed("Top Artists", "Top Artists"),
}


# return [{"json": output}]

# local script
print(json.dumps([{"json": output}]))
