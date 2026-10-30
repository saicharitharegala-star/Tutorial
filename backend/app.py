import json
import os
from pathlib import Path

import certifi
import pymongo
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from pymongo.errors import PyMongoError


load_dotenv()

app = Flask(__name__)
MONGO_URI = os.getenv("MONGO_URI")
DATA_FILE = Path(__file__).with_name("data.json")


def get_collection():
    """Connect lazily so connection failures can be returned as HTTP errors."""
    if not MONGO_URI:
        raise ConnectionError("The MONGO_URI environment variable is not configured.")

    try:
        client = pymongo.MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
        )
        client.admin.command("ping")
        return client.test["flask_tutorial"]
    except PyMongoError as error:
        raise ConnectionError("Unable to connect to the database.") from error


def read_api_data():
    """Read the current API response from disk on every request."""
    try:
        with DATA_FILE.open("r", encoding="utf-8") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError("The API data file contains invalid JSON.") from error

    if not isinstance(data, list):
        raise ValueError("The API data file must contain a JSON list.")
    return data


@app.route("/submit", methods=["POST"])
def submit():
    form_data = request.get_json(silent=True) or request.form.to_dict()
    if not form_data:
        return jsonify(error="No form data was submitted."), 400

    try:
        get_collection().insert_one(form_data)
    except ConnectionError as error:
        return jsonify(error=str(error)), 503
    except PyMongoError:
        return jsonify(error="The submission could not be saved."), 500

    return jsonify(message="Data submitted successfully"), 201


@app.route("/view")
def view():
    try:
        records = list(get_collection().find({}, {"_id": 0}))
    except ConnectionError as error:
        return jsonify(error=str(error)), 503
    except PyMongoError:
        return jsonify(error="Unable to retrieve data."), 500
    return jsonify(records)


@app.route("/api")
def api():
    """Return the list stored in backend/data.json using file I/O."""
    try:
        return jsonify(read_api_data())
    except ValueError as error:
        return jsonify(error=str(error)), 500
@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    item_name = request.form.get("itemName", "").strip()
    item_description = request.form.get("itemDescription", "").strip()

    if not item_name or not item_description:
        return jsonify(
            error="itemName and itemDescription are required."
        ), 400

    document = {
        "itemName": item_name,
        "itemDescription": item_description,
    }

    try:
        result = get_collection().insert_one(document)
    except ConnectionError as error:
        return jsonify(error=str(error)), 503
    except PyMongoError:
        return jsonify(error="Unable to save the to-do item."), 500

    return jsonify(
        message="To-do item saved successfully.",
        itemId=str(result.inserted_id),
    ), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
