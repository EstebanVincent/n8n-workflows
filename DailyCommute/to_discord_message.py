import json


def to_discord_message(data: dict, commute_time: str) -> list:
    raw_data = data.get("output", {})

    # Define mappings for titles and colors directly from severity
    severity_map = {
        "critical": {"color": 15158332},  # Red
        "warning": {"color": 15105570},  # Orange
        "log": {"color": 3066993},  # Green
    }

    # Process the overall status
    overall_severity = raw_data.get("overall_severity", "log")
    status_info = severity_map.get(overall_severity, severity_map["log"])

    # Create the final title, color, and description
    final_title = f"{commute_time} Commute Status"
    final_color = status_info["color"]
    final_description = f"**{raw_data.get('overall_summary', 'No summary available')}**"

    # Process each line report to build the 'fields' array
    final_fields = []
    line_reports = raw_data.get("line_reports", [])

    for report in line_reports:
        line_name = report.get("line", "Unknown Line")
        severity = report.get("severity")
        summary = report.get("summary", "")

        # This logic creates the value string based on the line's severity
        if severity == "log":
            value = "✅ Normal service"
        elif severity == "warning":
            value = f"⚠️ Delays\n{summary}"
        else:
            value = f"❌ Disruption\n{summary}"
        final_fields.append({"name": line_name, "value": value, "inline": False})

    # Construct the complete final JSON for the Discord node
    final_json = {
        "embed": {
            "title": final_title,
            "description": final_description,
            "color": final_color,
            "author": "Commute Assistant",
            "fields": final_fields,
            "footer": {"text": "Legend: ✅ Normal • ⚠️ Delays • ❌ Disruption"},
        }
    }

    return [{"json": final_json}]


if __name__ == "__main__":
    import click

    @click.command()
    @click.option(
        "--json-path",
        type=click.Path(exists=True),
        default="DailyCommute/inputs/to_discord_message.json",
        help="Path to the JSON file containing the input data for the n8n node.",
    )
    @click.option(
        "--commute-time",
        type=str,
        default="Morning",
        help="The time of day for the commute (e.g., 'Morning', 'Evening').",
    )
    def main(json_path, commute_time):
        """CLI for local testing of the to_discord_message script."""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from the file '{json_path}'.")
            return

        result = to_discord_message(data, commute_time)
        print(json.dumps(result, indent=2))

    main()  # pylint: disable=no-value-for-parameter
else:
    # In n8n, the script is not run as the main program, and _input is provided.
    data = _input.first().json.to_py()  # pylint: disable=undefined-variable # type: ignore # noqa
    commute_time = _("Set commute").first().json.time  # pylint: disable=undefined-variable # type: ignore # noqa
    # return to_discord_message(data, commute_time)
