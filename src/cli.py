#!/usr/bin/env python3
import argparse
import os
import pprint
import sys
from pathlib import Path

from helpers import fetch_dois_data, read_dois_from_csv
from submissions import write_full_metadata_to_csv, write_resolving_host_summary_to_csv


def set_arg_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-rh",
        "-res",
        "--resolving-host",
        type=str,
        help="If passed the script will check the given DOI/s to see if they resolve to the given host URL.",
    )
    parser.add_argument(
        "-full",
        "--full-metadata",
        action="store_true",
        help="If passed the full metadata will be queried for",
    )
    parser.add_argument(
        "-w",
        "--write-to-csv",
        action="store_true",
        help="If passed output results will be written to csv",
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
        "-f",
        "-file",
        "--file",
        type=str,
        help="Pass filepath for csv file of DOIs to be validated. This should contain the DOIs in the first column and nothing else.",
    )
    return parser


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
        dois = read_dois_from_csv(args.file)
        print(dois)

    resolving_host = args.resolving_host

    if not resolving_host:
        try:
            resolving_host = os.environ["RESOLVING_HOST"]
        except KeyError:
            pass

    full_metadata = args.full_metadata

    if resolving_host:
        results = fetch_dois_data(dois=dois, resolving_host=resolving_host, full_metadata=full_metadata)
    else:
        results = fetch_dois_data(dois=dois, resolving_host=resolving_host, full_metadata=full_metadata)

    if args.write_to_csv:
        output_dir = Path().resolve() / "complete"

        if full_metadata:
            write_full_metadata_to_csv(results, output_dir)

        if full_metadata and resolving_host:
            write_resolving_host_summary_to_csv(resolving_host=resolving_host, results=results, output_dir=output_dir)

    pprint.pp(results)


if __name__ == "__main__":
    main()
