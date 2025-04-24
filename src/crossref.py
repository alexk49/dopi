from typing import Any

from http_client import Client


""" Functions for interacting with CrossRef API """


def fetch_dois_data(dois: list[str], resolving_host: str = "", full_metadata: bool = True) -> list[dict[str, Any]]:
    """
    Fetch metadata for a list of DOIs from the Crossref API.
    """
    results = []

    with Client() as client:
        for doi in dois:
            result = process_single_doi(client, doi, resolving_host, full_metadata)
            results.append(result)
    return results


def process_single_doi(client: Client, doi: str, resolving_host: str, full_metadata: bool) -> dict[str, Any]:
    """Process a single DOI and return its result dictionary."""
    # default failure template
    result = {
        "doi": doi,
        "status": "FAILURE",
        "resolving_url": "not_found",
        "ERRORS": "",
        "full_metadata": {"message": {}},
    }

    url_path = f"/works/{doi}"
    response = client.request(url_path)
    response_data = client.get_response_data(response)

    if not response_data or ("Resource not found." in response_data):
        result["ERRORS"] = response_data
        return result

    response_dict = client.get_json_dict_from_response(response_data)

    if isinstance(response_dict, str):
        result["ERRORS"] = response_dict
        return result

    print(f"Received data for DOI {doi}")

    if resolving_host:
        result = validate_resolving_url(doi, response_dict, resolving_host, result)

    if full_metadata:
        result["full_metadata"] = response_dict

    return result


def get_resolving_url_for_doi(response_dict: dict) -> str:
    try:
        return response_dict["message"]["resource"]["primary"]["URL"]
    except Exception as err:
        err_msg = f"unable to find resolving URL: {err}"
        print(err_msg)
        return ""


def validate_resolving_url(doi: str, response_dict: dict, resolving_host: str, result: dict) -> dict:
    """Validate if DOI resolves to the expected host."""
    resolving_url = get_resolving_url_for_doi(response_dict)

    if not resolving_url:
        result["ERRORS"] = "Unable to find resolving URL in metadata"
        return result

    print(f"{doi} resolves to {resolving_url}")

    if resolving_host in resolving_url:
        print(f"{resolving_host} in {resolving_url}, {doi} resolves as expected")
        result.update({"status": "SUCCESS", "resolving_url": resolving_url, "ERRORS": ""})
    else:
        err_msg = f"{resolving_host} NOT in {resolving_url}, {doi} does not resolve correctly"
        print(err_msg)
        result.update({"status": "FAILURE", "resolving_url": resolving_url, "ERRORS": err_msg})
    return result
