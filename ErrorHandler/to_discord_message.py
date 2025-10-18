import json


def to_discord_message(data: dict):
    """Formats error data from an n8n Error Trigger into a Discord embed."""
    execution = data["execution"]
    error_details = execution["error"]
    workflow = data["workflow"]

    # Set the embed color to red for errors
    error_color = 15158332  # Red

    # Create a clear title and description
    final_title = f"❌ Workflow Error: {workflow.get('name', 'Unknown Workflow')}"
    final_description = "An error was caught during execution. See details below."

    # Build fields with key error information
    final_fields = [
        # Field for Workflow Name and ID
        {
            "name": "Workflow",
            "value": f"{workflow.get('name', 'N/A')} (ID: {workflow.get('id', 'N/A')})",
            "inline": True,
        },
        # Field for the node that failed
        {
            "name": "Failed Node",
            "value": execution.get("lastNodeExecuted", "N/A"),
            "inline": True,
        },
        # Field for the direct link to the failed execution
        {
            "name": "Execution Log",
            "value": f"[Click to view execution]({execution.get('url', '#')})",
            "inline": False,
        },
        # Field for the error message, formatted as a code block
        {
            "name": "Error Message",
            "value": f"```{error_details.get('message', 'No message available.')}```",
            "inline": False,
        },
    ]

    # Add stacktrace if available, truncated to fit Discord's limit
    stacktrace = error_details.get("stack")
    if stacktrace:
        # Truncate stacktrace to prevent hitting Discord's 1024-character limit for field values
        truncated_stack = (
            (stacktrace[:950] + "...") if len(stacktrace) > 950 else stacktrace
        )
        final_fields.append(
            {
                "name": "Stacktrace",
                "value": f"```{truncated_stack}```",
                "inline": False,
            }
        )

        embed = {
            "title": final_title,
            "description": final_description,
            "color": error_color,
            "author": "Error Handler",
            "fields": final_fields,
            "footer": {
                "text": f"Mode: {execution.get('mode', 'N/A')} | Execution ID: {execution.get('id', 'N/A')}"
            },
        }

    return [{"json": {"embed": embed}}]


if __name__ == "__main__":
    import click

    @click.command()
    @click.option(
        "--json-path",
        type=click.Path(exists=True),
        default="ErrorHandler/inputs/to_discord_message.json",
        help="Path to the JSON file containing the input data for the n8n node.",
    )
    def main(json_path):
        """CLI for local testing of the error handler script."""
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
    # In n8n, the script is not run as the main program, and _input is provided.
    data = _input.first().json.to_py()  # pylint: disable=undefined-variable # type: ignore # noqa
    # return to_discord_message(data)
