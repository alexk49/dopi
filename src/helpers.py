import csv
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

from http_client import Client


def get_list_from_str(dois: str) -> list:
    """
    Convert given str of separated by new lines into a list
    """
    return re.split(r"[\r\n]+", dois)


""" Functions for interacting with CrossRef API """


def fetch_dois_data(dois: List[str], resolving_host: str = "", full_metadata: bool = True) -> List[Dict[str, Any]]:
    """
    Fetch metadata for a list of DOIs from the Crossref API.
    """
    results = []

    with Client() as client:
        for doi in dois:
            result = process_single_doi(client, doi, resolving_host, full_metadata)
            results.append(result)
    return results


def process_single_doi(client: Client, doi: str, resolving_host: str, full_metadata: bool) -> Dict[str, Any]:
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


def get_resolving_url_for_doi(response_dict: dict) -> dict | str:
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


""" Functions for lockfile """


def create_lockfile(filepath: Path) -> bool:
    try:
        if filepath.is_file():
            return True

        with open(filepath, "w"):
            pass
        return True
    except Exception as err:
        print(f"error creating {filepath}: {err}")
        return False


""" Functions for reading csv files """


def read_full_csv_data(path_to_csv: str | os.PathLike) -> Tuple[str, str, list]:
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


def read_dois_from_csv(path_to_csv: str | os.PathLike) -> list:
    """
    CSV should contain dois in first column and nothing else
    >>> dois = read_csv_data(filepath)
    """
    with open(path_to_csv, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        dois = [row[0] for row in reader]
    return dois


""" Functions for writing to csv files """


def add_csv_to_queue(queue_dir: Path, resolver_host: str, email: str, dois: list) -> Path:
    output_filename = create_log_filename(f"checks_to_{resolver_host}")
    output_path = queue_dir / output_filename

    with open(output_path, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([email])
        writer.writerow([resolver_host])

        for doi in dois:
            writer.writerow([doi])
    return output_path


def create_log_filename(file_str: str, ext=".csv") -> str:
    """
    Filenames contain random unique id to avoid any conflicts

    Used to create output filename for csv files
    """
    datestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
    unique_id = str(uuid.uuid4())
    filename = file_str + "_" + datestamp + "-" + unique_id + ext
    return filename


def write_resolving_host_summary_to_csv(
    resolving_host, results: list, output_dir: Path = Path("output"), directories: dict = {}
) -> Path:
    for res in results:
        res.pop("full_metadata", None)

    summary_filename = create_log_filename(f"dois_to_{resolving_host}_results")

    if directories != {}:
        summary_filepath = directories["COMPLETE_DIR"] / summary_filename
    else:
        summary_filepath = output_dir / summary_filename

    with open(summary_filepath, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    return summary_filepath


def write_full_metadata_to_csv(results: list, output_dir: Path = Path("output"), directories: dict = {}) -> None:
    full_meta_filename = create_log_filename("full_metadata_results")

    if directories != {}:
        full_meta_filepath = directories["COMPLETE_DIR"] / full_meta_filename
    else:
        full_meta_filepath = output_dir / full_meta_filename

    with open(full_meta_filepath, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=results[0]["full_metadata"]["message"].keys())
        writer.writeheader()

        for index in range(len(results)):
            row = results[index]["full_metadata"]["message"]

            if row != {}:
                writer.writerow(row)
