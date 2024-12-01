import os
import requests
import json

def call_snyk_api(api_token, org_id, integration_id, url, headers):
  """Calls the Snyk API with the specified URL and headers.

  Args:
      api_token (str): Your Snyk API token.
      org_id (str): The ID of the organization you're working with.
      integration_id (str): The ID of the integration.
      url (str): The URL of the Snyk API endpoint.
      headers (dict): The headers to include in the request.

  Returns:
      requests.Response: The response object containing the API response data.
  """

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response
  except requests.exceptions.RequestException as e:
    print(f"Error calling Snyk API: {e}")
    return None

def get_targets(api_token, org_id, api_version, source_type_name):
  """Retrieves Snyk targets for the specified organization.

  Args:
      api_token (str): Your Snyk API token.
      org_id (str): The ID of the organization you're working with.
      api_version (str): The API version to use.
      source_type_name (str): The name of the source type (e.g., "github").

  Returns:
      list or None: A list of target dictionaries or None if an error occurs.
  """

  url = f"https://api.snyk.io/rest/orgs/{org_id}/targets?version={api_version}&source_types={source_type_name}"
  headers = {
      "accept": "application/vnd.api+json",
      "authorization": f"Token {api_token}"
  }

  response = call_snyk_api(api_token, org_id, None, url, headers)
  if response:
    data = response.json()
    targets = data.get("data", [])
    return [target for target in targets if target["relationships"]["integration"]["data"]["id"] == integration_id]
  else:
    return None

#Read required arguments from environment variables
api_token = os.getenv("SNYK_API_TOKEN")
org_id = os.getenv("SNYK_ORG_ID")
integration_id = os.getenv("SNYK_INTEGRATION_ID")
api_version = os.getenv("SNYK_API_VERSION", "2024-04-29")  # Provide default value
source_type_name = os.getenv("SNYK_SOURCE_TYPE_NAME")

# Check if pull request testing is enabled
response = call_snyk_api(api_token, org_id, None, "https://api.snyk.io/v1/org/{}/integrations/{}/settings".format(org_id, integration_id), {"Authorization": f"token {api_token}", "Content-Type": "application/json; charset=utf-8"})
if response:
  settings = response.json()
  pull_request_test_enabled = settings.get("pullRequestTestEnabled", False)

  if pull_request_test_enabled:
    targets = get_targets(api_token, org_id, api_version, source_type_name)
    if targets:
      print("Targets filtered by integration ID:")
      for target in targets:
        print(target)
    else:
      print("No targets found for the specified source type and integration.")
  else:
    print("Pull request testing is not enabled.")
else:
  print("Error retrieving integration settings.")