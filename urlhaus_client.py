# urlhaus_client.py
# This file contains one reusable function for URLHaus lookups.

import os

import requests
from dotenv import load_dotenv

from url_utils import normalize_url


# Load variables from the local .env file.
load_dotenv()

# URLHaus endpoint for looking up one URL.
URLHAUS_API_URL = "https://urlhaus-api.abuse.ch/v1/url/"


def lookup_urlhaus(url):
    """
    Look up one URL in URLHaus.

    Returns a small dictionary that says whether the URL was found,
    not found, or whether the lookup failed.
    """

    # Normalize the URL before requesting it.
    normalized_url = normalize_url(url)

    # Read the secret without printing it.
    api_key = os.getenv("URLHAUS_API_KEY")

    # Return a controlled error instead of crashing the pipeline.
    if not api_key:
        return {
            "provider": "urlhaus",
            "normalized_url": normalized_url,
            "found": False,
            "url_status": None,
            "tags": [],
            "error_message": "URLHAUS_API_KEY is missing."
        }

    try:
        # Make the API request.
        response = requests.post(
            URLHAUS_API_URL,
            headers={"Auth-Key": api_key},
            data={"url": normalized_url},
            timeout=15
        )

        # Turn HTTP errors, such as 403 or 500, into Python errors.
        response.raise_for_status()

        # Convert JSON text from URLHaus into a Python dictionary.
        result = response.json()

        # A normal no-results response is not an error.
        if result.get("query_status") == "no_results":
            return {
                "provider": "urlhaus",
                "normalized_url": normalized_url,
                "found": False,
                "url_status": None,
                "tags": [],
                "error_message": None
            }

        # A matching record is evidence for review.
        return {
            "provider": "urlhaus",
            "normalized_url": normalized_url,
            "found": True,
            "url_status": result.get("url_status"),
            "tags": result.get("tags", []),
            "error_message": None
        }

    except requests.RequestException as error:
        # Network, timeout, and HTTP errors arrive here.
        return {
            "provider": "urlhaus",
            "normalized_url": normalized_url,
            "found": False,
            "url_status": None,
            "tags": [],
            "error_message": str(error)
        }