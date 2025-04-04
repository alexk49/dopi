import csv
import os
import pprint
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple

from http_client import Client


API_HOST = "api.crossref.org"

# crossref api asks to mailto attribute in user agent
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]

HEADERS = {
    "Content-type": "application/json",
    "User-Agent": f"bulk-doi-checker mailto:{EMAIL_ADDRESS}",
    "Mailto": EMAIL_ADDRESS,
}

LOCK_FILE = "doi_processing.lock"


def get_lock_filepath(present_working_dir: os.PathLike) -> os.PathLike:
    filepath = present_working_dir / LOCK_FILE
    return filepath


def create_lockfile(filepath) -> bool:
    try:
        if filepath.is_file():
            return True

        with open(filepath, "w"):
            pass
        return True
    except Exception as err:
        print(f"error creating {filepath}: {err}")
        return False


def read_csv_data(path_to_csv: str | os.PathLike) -> Tuple[str, str, list]:
    """
    Format of csv should always be:

    hello@email.com
    hostsite-dois-should-resolve-to
    doi
    doi
    >>> email, resolving_host, dois = read_csv_data(filepath)
    """
    with open(path_to_csv, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        email = next(reader)[0]
        host = next(reader)[0]
        dois = [row[0] for row in reader]
    return email, host, dois


def write_results_to_csv(results: list, output_filepath):
    with open(output_filepath, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def write_full_meta_results_to_csv(results: list, output_filepath):
    with open(output_filepath, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0]["full_metadata"]["message"].keys()
        )
        writer.writeheader()

        for index in range(len(results)):
            row = results[index]["full_metadata"]["message"]

            if row != {}:
                writer.writerow(row)


def create_log_filename(file_str: str, ext=".csv"):
    """
    Filenames contain random unique id to avoid any conflicts
    """
    datestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
    unique_id = str(uuid.uuid4())
    filename = file_str + "_" + datestamp + "-" + unique_id + ext
    return filename


def get_resolving_url_for_doi(response_dict: dict):
    try:
        return response_dict["message"]["resource"]["primary"]["URL"]
    except Exception as err:
        print(f"unable to find resolving URL: {err}")


def fetch_dois_data(
    dois: List[str], resolving_host: str = "", full_metadata: bool = True
) -> List[Dict[str, Any]]:
    """
    Fetch metadata for a list of DOIs from the Crossref API.
    """
    results = []

    with Client(host=API_HOST, headers=HEADERS) as client:
        for doi in dois:
            result = process_single_doi(client, doi, resolving_host, full_metadata)
            pprint.pp(result)
            results.append(result)

    return results


def process_single_doi(
    client: Client, doi: str, resolving_host: str, full_metadata: bool
) -> Dict[str, Any]:
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


def validate_resolving_url(
    doi: str, response_dict: Dict, resolving_host: str, result: Dict
) -> Dict:
    """Validate if DOI resolves to the expected host."""
    resolving_url = get_resolving_url_for_doi(response_dict)

    if not resolving_url:
        result["ERRORS"] = "Unable to find resolving URL in metadata"
        return result

    print(f"{doi} resolves to {resolving_url}")

    if resolving_host in resolving_url:
        print(f"{resolving_host} in {resolving_url}, {doi} resolves as expected")
        result.update(
            {"status": "SUCCESS", "resolving_url": resolving_url, "ERRORS": ""}
        )
    else:
        err_msg = (
            f"{resolving_host} NOT in {resolving_url}, {doi} does not resolve correctly"
        )
        print(err_msg)
        result.update(
            {"status": "FAILURE", "resolving_url": resolving_url, "ERRORS": err_msg}
        )
    return result
