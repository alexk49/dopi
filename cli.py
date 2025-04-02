#!/usr/bin/env python3
import argparse
import csv
import pprint
import os
import sys

from http_client import Client
from typing import List, Tuple


def set_arg_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-rh",
        "-res",
        "--resolving-host",
        type=str,
        help="If passed the script will check the given DOI/s to see if they resolve to the given host URL.",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-dois",
        "--dois",
        type=str,
        help="Pass DOIs separated by comma to be validated.",
    )
    group.add_argument(
        "-d", "-doi", "--doi", type=str, help="Pass single DOI to be validated."
    )
    group.add_argument(
        "-f", "-file", "--file", type=str, help="Pass filepath for csv file of DOIs to be validated. This should contain the DOIs in the first column and nothing else."
    )
    return parser


def get_resolving_url_for_doi(response_dict: dict):
    try:
        return response_dict["message"]["resource"]["primary"]["URL"]
    except Exception as err:
        print(f"unable to find resolving URL: {err}")


EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]

# crossref api asks to mailto attribute in user agent
HEADERS = {
    "Content-type": "application/json",
    "User-Agent": f"bulk-doi-checker mailto:{EMAIL_ADDRESS}",
    "Mailto": EMAIL_ADDRESS,
}

API_HOST = "api.crossref.org"


def read_dois_in_csv(path_to_csv: str) -> list:
    with open(path_to_csv, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        first_row = next(reader)
        dois = [first_row[0]] + [row[0] for row in reader]
    return dois


def check_dois_resolve_to_host(dois: list, resolving_host: str) -> Tuple[List, List]:
    successes = []
    failures = []

    with Client(host=API_HOST, headers=HEADERS) as client:
        for doi in dois:
            url_path = f"/works/{doi}"
            response = client.request(url_path)

            if not response:
                print(f"no resource found for {doi}")
                failures.append(doi)
                continue

            response_dict = client.get_json_dict_from_response(response)

            pprint.pp(response_dict)

            resolving_url = get_resolving_url_for_doi(response_dict)

            print(f"{doi} resolves to {resolving_url}")

            if resolving_host in resolving_url:
                print(f"{resolving_host} in {resolving_url}, doi resolves as expected")
                successes.append(doi)
            else:
                print(
                    f"{resolving_host} NOT in {resolving_url}, doi does not resolve correctly"
                )
                failures.append(doi)
    return successes, failures


def main():
    parser = set_arg_parser()
    args = parser.parse_args()

    if not args.doi and not args.dois and not args.file:
        parser.print_help()
        sys.exit(1)

    if args.doi:
        print("single doi passed to validate")
        dois = [args.doi]

    if args.dois:
        dois = args.dois.split(",")

    if args.file:
        dois = read_dois_in_csv(args.file)

    resolving_host = args.resolving_host

    if resolving_host:
        successes, failures = check_dois_resolve_to_host(
            dois=dois, resolving_host=resolving_host
        )
        print("resolved as expected: ")
        print(successes)

        print("didn't resolve as expected")
        print(failures)


if __name__ == "__main__":
    main()
