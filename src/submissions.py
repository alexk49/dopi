import pprint
import sys
from multiprocessing import Process
from pathlib import Path

from config import Config
from crossref import fetch_dois_data
from emailer import Emailer
from helpers import (
    create_lockfile,
    read_full_csv_data,
    write_resolving_host_summary_to_csv,
    write_full_metadata_to_csv,
)


def email_summary_csv(recipient: str, filepath: Path) -> None:
    mailer = Emailer(sender_email=Config.EMAIL_ADDRESS, email_password=Config.EMAIL_PASSWORD)

    message_subject = "Results for Doi checks"
    message_body = "Please see attached for the results of your checks"

    message = mailer.create_email_message(
        recipient_email=recipient, message_subject=message_subject, message_body=message_body
    )

    message = mailer.add_attachment(message=message, filepath=filepath)

    mailer.send_email(message)


def process_csv_file(file: Path, directories: dict, email_notification: bool = True) -> bool:
    """Process a single CSV file with DOIs."""
    try:
        print(f"Processing {file}")
        email, resolving_host, dois = read_full_csv_data(file)
        results = fetch_dois_data(dois=dois, resolving_host=resolving_host)

        pprint.pp(results)

        write_full_metadata_to_csv(results, directories=directories)

        summary_filepath = write_resolving_host_summary_to_csv(resolving_host, results, directories=directories)

        if email_notification:
            print("Emailing results")
            email_summary_csv(recipient=email, filepath=summary_filepath)

        print(f"{file} has processed successfully, deleting file")
        file.unlink()
        return True
    except Exception as err:
        print(f"Error with file: {file}: {err}")
        output_path = directories["FAILURES_DIR"] / file.name
        file.replace(output_path)
        return False


def process_files(files: list[Path], directories: dict):
    """Process all CSV files in the queue directory."""
    for file in files:
        if file.is_file() and file.suffix == ".csv":
            process_csv_file(file, directories)
        else:
            print(f"Invalid file type found at: {file}")
            output_path = directories["FAILURES_DIR"] / file.name
            file.replace(output_path)


def process_queue(lock_filepath: Path = Config.LOCK_FILEPATH, directories: dict = Config.directories):
    """
    This should be run as a subprocess by the main app
    """
    if not create_lockfile(lock_filepath):
        print(f"UNABLE TO CREATE LOCK FILE {lock_filepath} EXITING PROGRAM")
        sys.exit(1)

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


def start_queue():
    p = Process(target=process_queue)
    p.daemon = True
    p.start()


if __name__ == "__main__":
    process_queue()
