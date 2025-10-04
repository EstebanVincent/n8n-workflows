# n8n Code (Python Beta) — Last 2 Weeks Steam Report (strict to given shape; no walrus)

from datetime import datetime, timedelta, timezone


def to_int(x):
    try:
        return int(x)
    except Exception:
        try:
            return int(float(x))
        except Exception:
            return 0


def minutes_to_hours(m):
    return round(to_int(m) / 60.0, 1)


items = _input.all()
first = items[0].json if items else {}

games = (first.get("response") or {}).get("games") or []
games = [g for g in games if to_int(g.get("playtime_2weeks", 0)) > 0]

games.sort(key=lambda g: to_int(g.get("playtime_2weeks", 0)), reverse=True)
top = games[:5]

total_minutes = sum(to_int(g.get("playtime_2weeks", 0)) for g in games)
total_hours = minutes_to_hours(total_minutes)
unique_games = len(games)

today = datetime.now(timezone.utc).date()
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
