from pathlib import Path

from helpers import check_dois_resolve_to_host, create_log_filename, read_csv_data, write_results_to_csv


LOCK_FILE = "doi_processing.lock"
QUEUE_DIR = "queue"
FAILURES_DIR = "failures"
COMPLETE_DIR = "complete"
SCRIPT_DIR = Path().resolve()


def main():
    lock_filepath = SCRIPT_DIR / LOCK_FILE

    queue_dir_path = Path().resolve() / QUEUE_DIR
    failures_dir_path = Path().resolve() / FAILURES_DIR
    complete_dir_path = Path().resolve() / COMPLETE_DIR

    queue_dir_path.mkdir(exist_ok=True)
    failures_dir_path.mkdir(exist_ok=True)
    complete_dir_path.mkdir(exist_ok=True)

    while True:

        files = sorted(queue_dir_path.iterdir())

        if not files:
            break

        for file in files:
            if file.is_file() and file.suffix == ".csv":
                try:
                    print(file)
                    email, resolving_host, dois = read_csv_data(file)
                    print(email)
                    print(resolving_host)
                    print(dois)

                    print(f"processing {file}")
                    results = check_dois_resolve_to_host(dois=dois, resolving_host=resolving_host)

                    print(f"got results: {results}")

                    output_filename = create_log_filename(f"dois_to_{resolving_host}_results")
                    output_filepath = complete_dir_path / output_filename

                    print(f"writing results to csv at {output_filename}")
                    write_results_to_csv(results, output_filepath)

                    # TODO
                    print("emailing results (TO BE IMPLEMENTED)")

                    print(f"{file} has processed successfully, deleting file")
                    file.unlink()
                except Exception as err:
                    print(f"error with file: {file}: {err}")
                    output_path = failures_dir_path / file.name
                    file.replace(output_path)
            else:
                print(f"invalid file type found at: {file}")
                output_path = failures_dir_path / file.name
                file.replace(output_path)


    print("process complete removing lock file")
    lock_filepath.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
