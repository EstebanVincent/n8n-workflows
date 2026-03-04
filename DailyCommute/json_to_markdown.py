# n8n Code (Python Beta) — aggregate all inputs into one Markdown
import html
import json
import re


def strip_html(x: str) -> str:
    if not isinstance(x, str):
        return ""
    # unescape entities then remove tags and trim spaces / collapse whitespace
    x = html.unescape(x)
    x = re.sub(r"<[^>]+>", "", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


def first(obj, *path, default=None):
    """Safe nested get with optional list indexes/keys."""
    cur = obj
    for p in path:
        try:
            if isinstance(p, int):
                cur = (cur or [])[p]
            else:
                cur = (cur or {}).get(p)
        except Exception:
            return default
        if cur is None:
            return default
    return cur if cur is not None else default


def line_title(payload: dict) -> str:
    """Extracts a title for a transport line from the data payload."""
    # 1) Preferred: line_reports[0].line.name (as user noted)
    t = first(payload, "line_reports", 0, "line", "name")
    if t:
        return t
    # 2) Try impacted_objects -> pt_object.line/name
    dis = first(payload, "disruptions", default=[]) or []
    for d in dis:
        # RER/Metro often exposes both pt_object.name ("RER B") and pt_object.line.name/code
        t = (
            first(d, "impacted_objects", 0, "pt_object", "name")
            or first(d, "impacted_objects", 0, "pt_object", "line", "name")
            or first(d, "impacted_objects", 0, "pt_object", "line", "code")
        )
        if t:
            return t
    return "Unknown line"


def json_to_markdown(data: dict):
    """Creates a Markdown report from a list of disruption data items."""
    sections = []

    for item in data["data"]:
        title = line_title(item)
        disruptions = item["disruptions"]

        sections.append(f"# {title}")

        if not disruptions:
            sections.append("_No disruptions reported._")
            continue

        for idx, d in enumerate(disruptions, 1):
            tags_list = d.get("tags") or []
            # Skip disruptions tagged "Ascenseur"
            if any(str(t).strip().lower() == "ascenseur" for t in tags_list):
                continue
            status = d.get("status") or "-"
            tags = ", ".join([str(t) for t in tags_list]) or "-"
            cause = d.get("cause") or "-"
            category = d.get("category") or "-"
            sev = d.get("severity") or {}
            sev_name = sev.get("name") or "-"
            sev_eff = sev.get("effect") or "-"

            msgs = []
            for m in d.get("messages") or []:
                txt = strip_html(m.get("text", ""))
                if txt and txt not in msgs:
                    msgs.append(txt)

            sections.append(f"## Disruption {idx}")
            sections.append(f"- **Status:** {status}")
            sections.append(f"- **Category:** {category}")
            sections.append(f"- **Cause:** {cause}")
            sections.append(f"- **Tags:** {tags}")
            sections.append(f"- **Severity:** {sev_name} ({sev_eff})")
            if msgs:
                sections.append("- **Messages:**")
                sections.extend([f"  - {m}" for m in msgs])
            else:
                sections.append("- **Messages:** -")

    return [{"json": {"markdown": "".join(sections)}}]


if __name__ == "__main__":
    import click

    @click.command()
    @click.option(
        "--json-path",
        type=click.Path(exists=True),
        default="DailyCommute/inputs/json_to_markdown.json",
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

        result = json_to_markdown(data)
        print(json.dumps(result, indent=2))

    main()  # pylint: disable=no-value-for-parameter
else:
    # In n8n, the script is not run as the main program, and _items is provided.
    data = _items[0]["json"]  # pylint: disable=undefined-variable # type: ignore # noqa
    # return json_to_markdown(data)
