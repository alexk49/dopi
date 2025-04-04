import pprint
import sys
from pathlib import Path

from helpers import create_lockfile, fetch_dois_data, get_lock_filepath, create_log_filename, read_csv_data, write_results_to_csv, write_full_meta_results_to_csv


def setup_directories(script_dir):
    QUEUE_DIR = "queue"
    FAILURES_DIR = "failures"
    COMPLETE_DIR = "complete"

    directories = {
        "QUEUE_DIR": script_dir / QUEUE_DIR,
        "FAILURES_DIR": script_dir / FAILURES_DIR,
        "COMPLETE_DIR": script_dir / COMPLETE_DIR,
    }
    
    for dir_path in directories.values():
        dir_path.mkdir(exist_ok=True)
    return directories


def process_csv_file(file, directories):
    """Process a single CSV file with DOIs."""
    try:
        print(f"Processing {file}")
        email, resolving_host, dois = read_csv_data(file)
        results = fetch_dois_data(dois=dois, resolving_host=resolving_host)

        pprint.pp(results)
        
        full_meta_filename = create_log_filename("full_metadata_results")
        full_meta_filepath = directories["COMPLETE_DIR"] / full_meta_filename
        write_full_meta_results_to_csv(results, full_meta_filepath)
        
        for res in results:
            res.pop('full_metadata', None)

        summary_filename = create_log_filename(f"dois_to_{resolving_host}_results")
        summary_filepath = directories["COMPLETE_DIR"] / summary_filename
        write_results_to_csv(results, summary_filepath)
        
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


def process_queue(files, directories):
    """Process all CSV files in the queue directory."""
    for file in files:
        if file.is_file() and file.suffix == ".csv":
            process_csv_file(file, directories)
        else:
            print(f"Invalid file type found at: {file}")
            output_path = directories["FAILURES_DIR"] / file.name
            file.replace(output_path)


def main():
    """
    This should be run as a subprocess by the main app
    """
    script_dir = Path().resolve()
    lock_filepath = get_lock_filepath(script_dir)

    if not create_lockfile(lock_filepath):
        print("UNABLE TO CREATE LOCK FILE EXITING PROGRAM")
        sys.exit(1)

    directories = setup_directories(script_dir)

    try:
        while True:
            queue_dir = directories["QUEUE_DIR"]
            files = sorted(queue_dir.iterdir())
            
            if not files:
                print("No files to process, exiting.")
                break
            
            process_queue(files, directories)
    finally:
        print("Process complete, removing lock file")
        lock_filepath.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
