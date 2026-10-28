import json
import os
from urllib.parse import urlparse

from flask import Flask, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_submissions(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_submission(path, submission):
    items = load_submissions(path)
    items.append(submission)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def is_valid_url(url):
    try:
        p = urlparse(url)
    except ValueError:
        return False
    return True


def validate(form):
    errors = []
    if not form["name"]:
        errors.append("Name is required.")
    if not form["reg_no"]:
        errors.append("Registration number is required.")
    if not form["title"]:
        errors.append("Assignment title is required.")
    if not form["url"]:
        errors.append("Submission URL is required.")
    elif not is_valid_url(form["url"]):
        errors.append("Submission URL is invalid. It must start with http:// or https://")
    return errors


def create_app(data_file=None):
    app = Flask(__name__)
    app.config["DATA_FILE"] = data_file or os.path.join(BASE_DIR, "submissions.json")

    @app.route("/", methods=["GET", "POST"])
    def index():
        errors, message, status = [], None, 200
        if request.method == "POST":
            form = {k: request.form.get(k, "").strip()
                    for k in ("name", "reg_no", "title", "url")}
            errors = validate(form)
            if errors:
                status = 400
            else:
                save_submission(app.config["DATA_FILE"], form)
                message = "Submission saved successfully."
        submissions = load_submissions(app.config["DATA_FILE"])
        return render_template("index.html", errors=errors,
                               message=message, submissions=submissions), status

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)