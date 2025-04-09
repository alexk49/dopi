from pathlib import Path
from bottle import default_app, request, static_file

# app = Bottle()
app = default_app()

APP_DIR = Path().resolve()
STATIC_DIR = APP_DIR / "src" / "static"


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
    full_meta = request.forms.full_meta

    print(full_meta)
    print(email)
    print(resolver)


def run_app():
    app.run(host="localhost", port=8080, debug=True, reloader=True)


if __name__ == "__main__":
    run_app()
