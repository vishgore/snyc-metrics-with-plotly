import dash
from dash import dcc, html
import json
from datetime import datetime, timedelta


def process_data(data):
    """
    Processes the JSON data to extract cumulative counts of created and resolved vulnerabilities.
    """
    min_date = None
    max_date = None
    daily_data = {}  # Define daily_data outside the function

    for issue in data["issues"]:
        if issue is not None:
            # Check for "attributes" and "created_at" keys
            if "attributes" in issue and "created_at" in issue["attributes"]:
                issue_date = datetime.fromisoformat(issue["attributes"]["created_at"])

                # Update min and max dates
                min_date = min_date if min_date and issue_date >= min_date else issue_date
                max_date = max_date if max_date and issue_date <= max_date else issue_date

                # Create entry for the date if it doesn't exist
                daily_data[issue_date] = daily_data.get(issue_date, {"created": 0, "resolved": 0})

                # Increment the appropriate count based on status
                if issue["attributes"]["status"] == "open":
                    daily_data[issue_date]["created"] += 1
                elif issue["attributes"]["status"] == "resolved":
                    if "resolution" in issue["attributes"] and "resolved_at" in issue["attributes"]["resolution"]:
                        resolution_date = datetime.fromisoformat(issue["attributes"]["resolution"]["resolved_at"])
                        daily_data[resolution_date] = daily_data.get(resolution_date, {"created": 0, "resolved": 0})
                        daily_data[resolution_date]["resolved"] += 1

    # Calculate cumulative counts
    cumulative_data = {"created": [], "resolved": []}
    current_date = min_date
    while current_date <= max_date:
        # Initialize counts for the current date (use get to handle missing dates)
        created_count = daily_data.get(current_date, {}).get("created", 0)
        resolved_count = daily_data.get(current_date, {}).get("resolved", 0)

        # Add counts to cumulative data
        cumulative_data["created"].append(created_count)
        cumulative_data["resolved"].append(resolved_count)

        # Increment date for the next iteration
        current_date += timedelta(days=1)

    return cumulative_data, min_date, max_date


# Sample JSON data (replace with your actual file path)
json_file_path = "/Users/vishalgore/.snyk-issues/group/8f69e502-9ba6-43a4-8fdb-2dc6dffe49c6/issues-16-5-2024.json"

# Read JSON data
with open(json_file_path, 'r') as f:
    data = json.load(f)

# Process data to get cumulative counts and dates
cumulative_data, min_date, max_date = process_data(data)

# Format dates for the chart
dates = [date.strftime('%Y-%m-%d') for date in daily_data.fromkeys(range(int((max_date - min_date).days) + 1))]

# Create a Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    dcc.Graph(
        id='vulnerability-status-chart',
        figure={
            'data': [
                {'x': dates, 'y': cumulative_data['created'], 'type': 'line', 'name': 'Created'},
                {'x': dates, 'y': cumulative_data['resolved'], 'type': 'line', 'name': 'Resolved'}
            ],
            'layout': {
                'title': 'Cumulative Vulnerability Status (Created vs. Resolved) Over Time',
                'xaxis': {'title': 'Date'},
                'yaxis': {'title': 'Number of Vulnerabilities (Cumulative)'}
            }
        }
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
