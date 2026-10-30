
import json
import os
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, jsonify, redirect, render_template, request, url_for


FRONTEND_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(FRONTEND_DIR / "templates"))
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:9000")
BACKEND_DATA_FILE = FRONTEND_DIR.parent / "backend" / "data.json"


def page_context(**extra):
    context = {
        "date": datetime.now().strftime("%A"),
        "time": datetime.now().strftime("%H:%M:%S"),
    }
    context.update(extra)
    return context


@app.route("/")
def home():
    return render_template("index.html", **page_context())


@app.route("/submit", methods=["POST"])
def submit():
    form_data = request.form.to_dict()
    try:
        response = requests.post(
            f"{BACKEND_URL}/submit", data=form_data, timeout=5
        )
        response.raise_for_status()
    except requests.RequestException as error:
        message = "We could not submit your data. Please try again shortly."
        if getattr(error, "response", None) is not None:
            try:
                message = error.response.json().get("error", message)
            except ValueError:
                pass
        return render_template(
            "index.html",
            **page_context(error=message, form_data=form_data),
        ), 502

    return redirect(url_for("success"))


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/api")
def api():
    """Read the backend JSON file for a dynamic JSON API response."""
    try:
        with BACKEND_DATA_FILE.open("r", encoding="utf-8") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        data = []
    except json.JSONDecodeError:
        return jsonify(error="The API data file contains invalid JSON."), 500

    if not isinstance(data, list):
        return jsonify(error="The API data file must contain a JSON list."), 500
    return jsonify(data)


@app.route("/get_data")
def get_data():
    try:
        response = requests.get(f"{BACKEND_URL}/view", timeout=5)
        response.raise_for_status()
        return jsonify(response.json())
    except (requests.RequestException, ValueError):
        return jsonify(error="Unable to retrieve data from the backend."), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
