# My n8n Self-Hosted Workflows

This repository is for managing the workflows of my self-hosted n8n community edition instance.

## Overview

-   **Host:** The n8n instance is running as a Docker image on a Raspberry Pi 4.
-   **Purpose:** This repository allows me to version my workflows, particularly the Python code nodes and prompts. It enables me to use a full-featured IDE for development instead of the n8n web-based editor.

## Repository Structure

Each top-level folder in this repository corresponds to a specific n8n workflow. Inside each folder, you will find:

-   Python scripts used in **Code** nodes.
-   A `.n8n` sub-folder containing the workflow's JSON file.
-   Input examples (`.json` files) for testing Python scripts locally.
-   Prompts (`.md` files) for AI nodes.

## Python Development Workflow

To facilitate both local development and execution within n8n, I use a system based on the `click` package for my Python scripts.

The core logic is wrapped in a function. The script then uses a conditional block:

-   `if __name__ == "__main__":`: This block is for local execution. It uses `click` to create a command-line interface, allowing me to pass arguments and test the script from my terminal.
-   `else:`: This block is for execution within the n8n environment. It retrieves data from the n8n `_input` variable and calls the core logic function. The final `return` statement, which passes the result back to the n8n workflow, is commented out during local development.

This setup allows for easy testing and development locally, and with a minor change (uncommenting one line), the code is ready for production in n8n.

### Example Python Node

Here is an example of the structure used in the Python scripts:

```python
# Your core logic is in a function
def my_function(param1, param2):
    # ... processing ...
    return {"result": f"{param1} and {param2} processed"}

# This block is for local execution with 'click'
if __name__ == "__main__":
    import click
    import json

    @click.command()
    @click.option("--param1", required=True, help="First parameter.")
    @click.option("--param2", required=True, help="Second parameter.")
    def main(param1, param2):
        """A CLI to run the script locally."""
        output = my_function(param1, param2)
        print(json.dumps(output, indent=2))

    main()

# This block is for n8n execution
else:
    # In n8n, the script is not run as the main program.
    # '_input' is a global variable provided by the n8n environment.
    # We assume the input data is available in the first item's JSON.
    data = _input.first().json

    # Extract parameters from the n8n input
    p1 = data.get("parameter_one")
    p2 = data.get("parameter_two")

    # The result of this script will be the output of the n8n node.
    result = my_function(p1, p2)

    # To use in n8n, uncomment the following line:
    # return result
```
