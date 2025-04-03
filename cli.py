#!/usr/bin/env python3
import argparse
import sys

from helpers import check_dois_resolve_to_host, read_csv_data


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
        dois = read_csv_data(args.file)

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
