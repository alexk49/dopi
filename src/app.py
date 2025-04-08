from pathlib import Path
from bottle import Bottle, static_file

app = Bottle()

APP_DIR = Path().resolve()
STATIC_DIR = APP_DIR / "src" / "static"

@app.route("/static/<filename:path>")
def serve_static(filename: str):
    return static_file(filename, root=STATIC_DIR)


@app.route('/')
def home():
    return static_file('index.html', root=STATIC_DIR)


@app.route('/submit')
def submit():
    return static_file('submit.html', root=STATIC_DIR)


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True, reloader=True)
