import csv
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple


def generate_csrf_token():
    return os.urandom(16).hex()


def get_list_from_str(dois: str) -> list:
    """
    Convert given str of separated by new lines into a list
    """
    return re.split(r"[\r\n]+", dois)


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
