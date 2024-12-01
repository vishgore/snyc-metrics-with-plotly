import os, requests
import pandas as pd

# Get org_id and api_token from environment variables
org_id = os.getenv("SNYK_ORG_ID")
api_token = os.getenv("SNYK_API_TOKEN")


def flatten_dict(data):
    """
    Flattens a nested dictionary recursively, handling arrays and objects.

    Args:
        data (dict): Dictionary to flatten.

    Returns:
        dict: Flattened dictionary with primitive values.
    """
    flattened_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            flattened_data.update(flatten_dict(value))  # Recursive call for sub-dictionaries
        elif isinstance(value, list):
            # Handle arrays by converting them to comma-separated strings
            flattened_data[f"{key}_list"] = ",".join(str(item) for item in value)
        elif isinstance(value, object):  # Handle other objects as strings
            flattened_data[key] = str(value)
        else:
            flattened_data[key] = value
    return flattened_data

url = f"https://api.snyk.io/rest/orgs/{org_id}/issues?version=2024-03-12&limit=50"

payload = {}
headers = {
    'Accept': 'application/vnd.api+json',
    'Authorization': f'token {api_token}'
}

response = requests.request("GET", url, headers=headers, data=payload)

# Check for successful response
if response.status_code == 200:
    data = response.json()
    
    # Extract and flatten issue data
    issues = []
    for issue in data.get("data", []):
        flat_issue_data = flatten_dict(issue["attributes"])
        flat_issue_data["id"] = issue["id"]  # Add the top-level "id"
        issues.append(flat_issue_data)
    
    # Create a pandas DataFrame
    df = pd.DataFrame(issues)
    
    # Write the DataFrame to a CSV file (without index)
    df.to_csv("snyk_issues_flat.csv", index=False)
    print("Snyk issues data (flattened) written to snyk_issues_flat.csv")
else:
    print(f"Error: API request failed with status code {response.status_code}")
