# In n8n this is the input to the node:
# data = _input.all()[0].json

# outside n8n, load from a file for testing:
import json

with open("workflows/lastfm/input.json", "r", encoding="utf-8") as f:
    data = json.load(f)

from collections import Counter
from typing import Any, Dict, List


def is_dict(x: Any) -> bool:
    return isinstance(x, dict)


def norm(x: Any) -> str:
    return (x or "").strip()


def first_image(images: Any) -> str | None:
    if not isinstance(images, list):
        return None
    order = ["extralarge", "large", "medium", "small"]
    by_size = {
        norm(img.get("size")): norm(img.get("#text")) for img in images if is_dict(img)
    }
    for s in order:
        u = by_size.get(s)
        if u:
            return u
    for img in images:
        u = norm(img.get("#text")) if is_dict(img) else ""
        if u:
            return u
    return None


def extract_tracks(js: Any) -> List[Dict[str, Any]]:
    tracks: List[Dict[str, Any]] = []
    if is_dict(js):
        container = js.get("recenttracks") if is_dict(js) else None
        t = []
        if is_dict(container):
            t = container.get("track", [])
        elif "track" in js:
            t = js.get("track", [])
        if isinstance(t, dict):
            t = [t]
        if isinstance(t, list):
            tracks.extend([x for x in t if is_dict(x)])
    elif isinstance(js, list):
        for el in js:
            tracks.extend(extract_tracks(el))
    return tracks


# Gather weekly tracks from all inputs; ignore "now playing"
rows: List[Dict[str, Any]] = []

for tr in extract_tracks(data):
    attr = tr.get("@attr") if is_dict(tr) else None
    if is_dict(attr) and attr.get("nowplaying") in ("true", True):
        continue
    artist = norm(
        (tr.get("artist") or {}).get("#text")
        if is_dict(tr.get("artist"))
        else tr.get("artist")
    )
    track = norm(tr.get("name"))
    album = norm(
        (tr.get("album") or {}).get("#text")
        if is_dict(tr.get("album"))
        else tr.get("album")
    )
    image = first_image(tr.get("image"))
    if artist and track:
        rows.append({"artist": artist, "track": track, "album": album, "image": image})

total_scrobbles = len(rows)
unique_tracks = len({(r["artist"], r["track"]) for r in rows})
unique_artists = len({r["artist"] for r in rows})

track_counter = Counter((r["artist"], r["track"]) for r in rows).most_common(5)
artist_counter = Counter(r["artist"] for r in rows).most_common(5)

fields = []
summary = (
    f"**{total_scrobbles}** scrobbles · **{unique_tracks}** unique tracks · **{unique_artists}** unique artists"
    if total_scrobbles
    else "No scrobbles this week."
)
fields.append({"name": "Weekly Summary", "value": summary, "inline": False})

if track_counter:
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, ((a, t), c) in enumerate(track_counter):
        prefix = medals[i] if i < len(medals) else "•"
        lines.append(f"{prefix} **{t}** — {a} · {c}×")
    fields.append({"name": "Top Tracks", "value": "\n".join(lines), "inline": False})

if artist_counter:
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (a, c) in enumerate(artist_counter):
        prefix = medals[i] if i < len(medals) else "•"
        lines.append(f"{prefix} **{a}** · {c}×")
    fields.append({"name": "Top Artists", "value": "\n".join(lines), "inline": False})

thumb_url = None
for r in reversed(rows):
    if r.get("image"):
        thumb_url = r["image"]
        break

embed = {
    "title": "🎧 Weekly Last.fm Report",
    "description": summary,
    "color": 3447003,
    "fields": fields,
    "footer": {"text": "Period: weekly dataset"},
}
if thumb_url:
    embed["thumbnail"] = {"url": thumb_url}

# return [{"json": {"embed": embed}}]

# local script
print([{"json": {"embed": embed}}])
