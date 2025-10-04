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
    if not isinstance(images, list):
        return None
    order = ["extralarge", "large", "medium", "small"]
    by_size = {norm(img.get("size")): norm(img.get("#text")) for img in images}
    for s in order:
        u = by_size.get(s)
        if u:
            return u
    for img in images:
        u = norm(img.get("#text"))
        if u:
            return u
    return None


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


if track_counter:
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, ((a, t), c) in enumerate(track_counter):
        prefix = medals[i] if i < len(medals) else "•"
        lines.append(f"{prefix} **{t}** — {a} · {c}×")
    fields.append({"name": "Top Tracks", "value": "\n".join(lines), "inline": False})

if album_counter:
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, ((ar, al), c) in enumerate(album_counter):
        prefix = medals[i] if i < len(medals) else "•"
        lines.append(f"{prefix} **{al}** — {ar} · {c}×")
    fields.append({"name": "Top Albums", "value": "\n".join(lines), "inline": False})

if artist_counter:
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (a, c) in enumerate(artist_counter):
        prefix = medals[i] if i < len(medals) else "•"
        lines.append(f"{prefix} **{a}** · {c}×")
    fields.append({"name": "Top Artists", "value": "\n".join(lines), "inline": False})

thumb_url = None
if artist_counter:
    top_artist = artist_counter[0][0]
    for r in reversed(rows):
        if r["artist"] == top_artist and r.get("image"):
            thumb_url = r["image"]
            break

if not thumb_url:
    for r in reversed(rows):
        if r.get("image"):
            thumb_url = r["image"]
            break

# Embed 1: Main Summary
summary_embed = {
    "title": "🎧 Weekly Last.fm Report",
    "description": summary,
    "color": 3447003,
    "fields": [f for f in fields if f["name"] in ("Activity")],
}
if thumb_url:
    summary_embed["thumbnail"] = {"url": thumb_url}


def create_list_embed(title: str, field_name: str) -> dict | None:
    """Creates an embed for a list of items."""
    for field in fields:
        if field["name"] == field_name:
            embed = {
                "title": title,
                "color": 3447003,
                "fields": [
                    {"name": field_name, "value": field["value"], "inline": False}
                ],
            }
            # Find a thumbnail
            list_thumb_url = None
            if field_name == "Top Artists" and artist_counter:
                top_list_artist = artist_counter[0][0]
                for row in reversed(rows):
                    if row["artist"] == top_list_artist and row.get("image"):
                        list_thumb_url = row["image"]
                        break
            elif field_name == "Top Albums" and album_counter:
                top_list_artist, top_album = album_counter[0][0]
                for row in reversed(rows):
                    if (
                        row["artist"] == top_list_artist
                        and row["album"] == top_album
                        and row.get("image")
                    ):
                        list_thumb_url = row["image"]
                        break
            elif field_name == "Top Tracks" and track_counter:
                top_list_artist, top_track = track_counter[0][0]
                for row in reversed(rows):
                    if (
                        row["artist"] == top_list_artist
                        and row["track"] == top_track
                        and row.get("image")
                    ):
                        list_thumb_url = row["image"]
                        break

            if list_thumb_url:
                embed["thumbnail"] = {"url": list_thumb_url}

            return embed
    return None


output = {
    "summary_embed": summary_embed,
    "track_embed": create_list_embed("Top Tracks", "Top Tracks"),
    "album_embed": create_list_embed("Top Albums", "Top Albums"),
    "artist_embed": create_list_embed("Top Artists", "Top Artists"),
}


# return [{"json": output}]

# local script
print(json.dumps([{"json": output}]))
