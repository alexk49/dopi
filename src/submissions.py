import pprint
import sys
from pathlib import Path

from config import Config
from helpers import (
    create_lockfile,
    fetch_dois_data,
    get_lock_filepath,
    read_full_csv_data,
    write_resolving_host_summary_to_csv,
    write_full_metadata_to_csv,
)


def process_csv_file(file: Path, directories: dict) -> bool:
    """Process a single CSV file with DOIs."""
    try:
        print(f"Processing {file}")
        email, resolving_host, dois = read_full_csv_data(file)
        results = fetch_dois_data(dois=dois, resolving_host=resolving_host)

        pprint.pp(results)

        write_full_metadata_to_csv(results, directories=directories)

        write_resolving_host_summary_to_csv(resolving_host, results, directories=directories)

        # TODO: Email results
        print("Emailing results (TO BE IMPLEMENTED)")

        print(f"{file} has processed successfully, deleting file")
        file.unlink()
        return True
    except Exception as err:
        print(f"Error with file: {file}: {err}")
        output_path = directories["FAILURES_DIR"] / file.name
        file.replace(output_path)
        return False


def process_files(files, directories):
    """Process all CSV files in the queue directory."""
    for file in files:
        if file.is_file() and file.suffix == ".csv":
            process_csv_file(file, directories)
        else:
            print(f"Invalid file type found at: {file}")
            output_path = directories["FAILURES_DIR"] / file.name
            file.replace(output_path)


def process_queue(app_dir=None):
    """
    This should be run as a subprocess by the main app
    """
    if not app_dir:
        script_dir = Path().resolve()
    else:
        script_dir = app_dir

    lock_filepath = get_lock_filepath(script_dir)

    if not create_lockfile(lock_filepath):
        print("UNABLE TO CREATE LOCK FILE EXITING PROGRAM")
        sys.exit(1)

    directories = Config.directories 

    try:
        while True:
            queue_dir = directories["QUEUE_DIR"]
            files = sorted(queue_dir.iterdir())

            if not files:
                print("No files to process, exiting.")
                break

            process_files(files, directories)
    finally:
        print("Process complete, removing lock file")
        lock_filepath.unlink(missing_ok=True)


if __name__ == "__main__":
    process_queue()
