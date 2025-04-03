import csv
import os
import pprint
import uuid
from datetime import datetime
from typing import Any, Dict, List, Tuple

from http_client import Client


API_HOST = "api.crossref.org"

# crossref api asks to mailto attribute in user agent
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]

HEADERS = {
    "Content-type": "application/json",
    "User-Agent": f"bulk-doi-checker mailto:{EMAIL_ADDRESS}",
    "Mailto": EMAIL_ADDRESS,
}



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


def check_dois_resolve_to_host(dois: list, resolving_host: str):
    results = []

    with Client(host=API_HOST, headers=HEADERS) as client:
        for doi in dois:
            url_path = f"/works/{doi}"
            response = client.request(url_path)

            if not response:
                print(f"no resource found for {doi}")
                results.append({"doi": doi, "status": "FAILURE", "resolving_url": "not_found", "errors": "404"})
                continue

            response_dict = client.get_json_dict_from_response(response)

            pprint.pp(response_dict)

            resolving_url = get_resolving_url_for_doi(response_dict)

            print(f"{doi} resolves to {resolving_url}")

            if resolving_host in resolving_url:
                print(f"{resolving_host} in {resolving_url}, {doi} resolves as expected")
                results.append({"doi": doi, "status": "SUCCESS", "resolving_url": resolving_url, "errors": ""})
            else:
                err_msg = f"{resolving_host} NOT in {resolving_url}, {doi} does not resolve correctly"
                print(err_msg)
                results.append({"doi": doi, "status": "FAILURE", "resolving_url": resolving_url, "errors": err_msg})
    return results
