# Loop over input items and add a new field called 'myNewField' to the JSON of each one
for item in _input.all():
    raw_data = item.json["output"]

# --- 1. Define mappings for titles and colors directly from severity ---
severity_map = {
    "critical": {"color": 15158332},  # Red
    "warning": {"color": 15105570},  # Orange
    "log": {"color": 3066993},  # Green
}

# --- 2. Process the overall status ---
overall_severity = raw_data.get("overall_severity", "log")
status_info = severity_map.get(overall_severity)

# Create the final title, color, and description
final_title = f"{_('Set commute').first().json.time} Commute Status"
final_color = status_info["color"]
final_description = f"**{raw_data.get('overall_summary')}**"

# --- 3. Process each line report to build the 'fields' array ---
final_fields = []
line_reports = raw_data.get("line_reports", [])

for report in line_reports:
    line_name = report.get("line")
    severity = report.get("severity")
    summary = report.get("summary")

    # This logic creates the value string based on the line's severity
    if severity == "log":
        value = "✅ Normal service"
    elif severity == "warning":
        value = f"⚠️ Delays\n{summary}"
    else:
        value = f"❌ Disruption\n{summary}"
    final_fields.append({"name": line_name, "value": value, "inline": False})

# --- 4. Construct the complete final JSON for  the Discord node ---
# This object will be the output of this Code node
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

# --- 5. Return the data for the next node in n8n ---
return [{"json": final_json}]

return _input.all()
