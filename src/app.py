import csv
import json
from pathlib import Path

from bottle import default_app, response, request, static_file

from helpers import get_list_from_str, get_lock_filepath, create_log_filename
from submissions import process_queue, setup_directories


# app = Bottle()
app = default_app()

APP_DIR = Path().resolve()
STATIC_DIR = APP_DIR / "src" / "static"

directories = setup_directories(APP_DIR)


@app.route("/static/<filename:path>")
def serve_static(filename: str):
    return static_file(filename, root=STATIC_DIR)


@app.route("/")
def home():
    return static_file("index.html", root=STATIC_DIR)


@app.get("/submit")
def submit():
    return static_file("submit.html", root=STATIC_DIR)


@app.post("/submit")
def post_submit():
    email = request.forms.email
    resolver = request.forms.resolving_host

    dois_text = request.forms.dois_text
    dois_upload = request.forms.dois_upload

    full_meta = request.forms.full_meta

    print(email)
    print(resolver)
    print(dois_text)
    print(dois_upload)
    print(full_meta)

    # TODO validate form submission

    output_filename = create_log_filename(f"checks_to_{resolver}")
    output_path = directories["QUEUE_DIR"] / output_filename

    if dois_text:

        dois_list: list = get_list_from_str(dois_text)

        with open(output_path, mode="w", newline="") as file:
            writer = csv.writer(file)

            writer.writerow([email])
            writer.writerow([resolver])

            for doi in dois_list:
                writer.writerow([doi])

    # check if queue is running, by checking lockfile exists
    lock_filepath = get_lock_filepath(APP_DIR)

    if lock_filepath.is_file():
        print("process already running, file added to the queue dir at %s", output_path)
    else:
        print("starting queue process")
        # process_queue(APP_DIR)

    response.content_type = 'application/json'
    return {'success': True, 'message': 'Thank you, your submission has been added to the queue!'}


def run_app():
    app.run(host="localhost", port=8080, debug=True, reloader=True)


if __name__ == "__main__":
    run_app()
