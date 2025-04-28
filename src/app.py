from bottle import default_app, response, request, static_file

from config import Config
from helpers import add_csv_to_queue
from submissions import start_queue
from validators import validate_form, get_errors


app = default_app()


@app.route("/static/<filename:path>")
def serve_static(filename: str):
    return static_file(filename, root=Config.STATIC_DIR)


@app.route("/complete/<filename:path>")
def download_complete_file(filename: str):
    return static_file(filename, root=Config.directories["COMPLETE_DIR"], download=filename)


@app.get("/")
def home():
    return static_file("index.html", root=Config.STATIC_DIR)


@app.get("/queue")
def queue_count():
    queue_dir = Config.directories["QUEUE_DIR"]
    queue_count = len(list(queue_dir.glob("*.csv")))
    response.content_type = "application/json"
    return {"queue_count": str(queue_count)}


@app.get("/completed")
def completed():
    completed_dir = Config.directories["COMPLETE_DIR"]
    completed_files = list(completed_dir.glob("*.csv"))
    filenames = [file.name for file in completed_files]
    response.content_type = "application/json"
    return {"completed": filenames}


@app.post("/submit")
def post_submit():
    result = validate_form(request.forms)
    errors = get_errors(result)

    if errors:
        return {"success": False, "message": "Invalid form", "errors": errors}

    output_path = add_csv_to_queue(
        queue_dir=Config.directories["QUEUE_DIR"],
        resolver_host=result["resolver"]["value"],
        email=result["email"]["value"],
        dois=result["dois"]["value"],
    )

    # check if queue is running, by checking lockfile exists
    if Config.LOCK_FILEPATH.is_file():
        print("process already running, file added to the queue dir at %s", output_path)
    else:
        print("starting queue process")
        start_queue()

    response.content_type = "application/json"
    return {"success": True, "message": "Thank you, your submission has been added to the queue!", "errors": {}}


def run_app():
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, reloader=Config.DEBUG)


if __name__ == "__main__":
    run_app()
