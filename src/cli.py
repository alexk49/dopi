#!/usr/bin/env python3
import argparse
import os
import pprint
import subprocess
import sys
from pathlib import Path

from app import run_app
from crossref import fetch_dois_data
from emailer import run_emailer_cli, set_emailer_arg_parser
from helpers import read_full_csv_data
from submissions import write_full_metadata_to_csv, write_resolving_host_summary_to_csv


def set_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=False)

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
        "-cc",
        "--complete-csv",
        type=str,
        help="Pass all data via csv with email, host site and doi all written in csv",
    )
    group.add_argument(
        "-dois",
        "--dois",
        type=str,
        help="Pass DOIs separated by comma to be validated.",
    )
    group.add_argument("-d", "-doi", "--doi", type=str, help="Pass single DOI to be validated.")
    group.add_argument(
        "-f",
        "-file",
        "--file",
        type=str,
        help="Pass filepath for csv file of DOIs to be validated. This should contain the DOIs in the first column and nothing else.",
    )
    group.add_argument(
        "-app",
        "-run",
        "--run-app",
        action="store_true",
        help="Run web application locally",
    )
    group.add_argument(
        "-lpy",
        "--lint-py",
        action="store_true",
        help="Lint python files.",
    )
    group.add_argument(
        "-ljs",
        "--lint-js",
        action="store_true",
        help="Lint javascript files.",
    )
    group.add_argument(
        "-l",
        "--lint",
        action="store_true",
        help="Lint all files",
    )
    group.add_argument(
        "-tpy",
        "--test-py",
        action="store_true",
        help="Run python tests.",
    )
    group.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Run all tests",
    )

    emailer_parser = subparsers.add_parser(
        "emailer", help="Send email, --recipient | --subject | --body | --attachment"
    )
    emailer_args = set_emailer_arg_parser()
    for action in emailer_args._actions:
        if action.option_strings:
            emailer_parser._add_action(action)
    return parser


def run_command(command):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(command)}")
        sys.exit(e.returncode)


def run_py_tests():
    run_command(["python", "-m", "unittest", "discover"])


def run_js_tests():
    run_command(["npm", "test"])


def run_tests():
    run_py_tests()
    run_js_tests()


def run_js_linters():
    run_command(["npx", "eslint", "static/*.js"])
    run_command(["npx", "prettier", "--write", "static/*.js"])


def run_py_linters():
    run_command(["ruff", "check", ".", "--fix"])

    run_command(["ruff", "format", "."])

    run_command(["mypy", "."])


def run_linters():
    run_py_linters()
    run_js_linters()


def main():
    parser = set_arg_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.run_app:
        run_app()
        sys.exit()

    if args.command == "emailer":
        run_emailer_cli(args)
        sys.exit()

    if args.lint_py:
        run_py_linters()
        sys.exit()

    if args.lint_js:
        run_js_linters()
        sys.exit()

    if args.lint:
        run_linters()
        sys.exit()

    if args.test:
        run_tests()
        sys.exit()

    if args.test_py:
        run_py_tests()
        sys.exit()

    resolving_host = args.resolving_host

    if args.complete_csv:
        print("getting email, resolver and dois from csv")
        print(args.complete_csv)
        email, resolving_host, dois = read_full_csv_data(args.complete_csv)
        print(email, resolving_host, dois)

    if args.doi:
        print("single doi passed to validate")
        dois = [args.doi]

    if args.dois:
        dois = args.dois.split(",")

    if args.file:
        dois = read_full_csv_data(args.file)
        print(dois)

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
