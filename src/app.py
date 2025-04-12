import csv
from pathlib import Path

from bottle import default_app, response, request, static_file

from validators import validate_form, get_errors
from helpers import get_lock_filepath, create_log_filename
from submissions import setup_directories


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
    """
    Can access individual elements like:
    email = request.forms.email
    """
    result = validate_form(request.forms)
    print(result)

    errors = get_errors(result)

    print(errors)

    if errors:
        return {"success": False, "message": "Invalid form", "errors": errors}

    output_filename = create_log_filename(f"checks_to_{result['resolver']['value']}")
    output_path = directories["QUEUE_DIR"] / output_filename

    with open(output_path, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([result["email"]["value"]])
        writer.writerow([result["resolver"]["value"]])

        for doi in result["dois"]["value"]:
            writer.writerow([doi])

    # check if queue is running, by checking lockfile exists
    lock_filepath = get_lock_filepath(APP_DIR)

    if lock_filepath.is_file():
        print("process already running, file added to the queue dir at %s", output_path)
    else:
        print("starting queue process")
        # process_queue(APP_DIR)

    response.content_type = "application/json"
    return {"success": True, "message": "Thank you, your submission has been added to the queue!", "errors": {}}


def run_app():
    app.run(host="localhost", port=8080, debug=True, reloader=True)


if __name__ == "__main__":
    run_app()
