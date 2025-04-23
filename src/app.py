from bottle import default_app, response, request, static_file

from config import Config
from validators import validate_form, get_errors
from helpers import add_csv_to_queue, get_lock_filepath 


# app = Bottle()
app = default_app()


@app.route("/static/<filename:path>")
def serve_static(filename: str):
    return static_file(filename, root=Config.STATIC_DIR)


@app.route("/")
def home():
    return static_file("index.html", root=Config.STATIC_DIR)


@app.get("/submit")
def submit():
    return static_file("submit.html", root=Config.STATIC_DIR)


@app.post("/submit")
def post_submit():
    result = validate_form(request.forms)
    errors = get_errors(result)
    print(result)
    print(errors)

    if errors:
        return {"success": False, "message": "Invalid form", "errors": errors}

    output_path = add_csv_to_queue(queue_dir=Config.directories["QUEUE_DIR"], resolver_host=result["resolver"]["value"], email=result["email"]["value"], dois=result["dois"]["value"])

    # check if queue is running, by checking lockfile exists
    lock_filepath = get_lock_filepath(Config.APP_DIR)

    if lock_filepath.is_file():
        print("process already running, file added to the queue dir at %s", output_path)
    else:
        print("starting queue process")
        # process_queue(APP_DIR)

    response.content_type = "application/json"
    return {"success": True, "message": "Thank you, your submission has been added to the queue!", "errors": {}}


def run_app():
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, reloader=Config.DEBUG)


if __name__ == "__main__":
    run_app()
