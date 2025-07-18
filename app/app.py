from flask import Flask, render_template, send_from_directory
import pandas as pd
import os

app = Flask(__name__)
#app.config["IMAGE_FOLDER"] = image_path  # full folder path from earlier

CSV_FILE = None
IMAGE_DIR = None
records = []

def init_app(csv_path, image_path):
    global CSV_FILE, IMAGE_DIR, records
    CSV_FILE = csv_path
    IMAGE_DIR = image_path

    print(f"Reading CSV from: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE, sep=",")  # Make sure it's using commas
    print(f"Loaded DataFrame shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")

    # Ensure "Frame" column exists
    if "Frame" in df.columns:
        df["image_path"] = df["Frame"].apply(
            lambda name: f"/images/{name.strip()}" if pd.notna(name) and name.strip() != "" else None
        )
    else:
        print("ERROR: 'Frame' column missing")
        df["image_path"] = None

    records = df.to_dict(orient="records")
    print("Parsed records:", records)

@app.route("/")
def index():
    print('in index!!')
    for i in records:
        
        return render_template("index.html", records=records)

@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

@app.route("/ping")
def ping():
    return "pong"

def run_flask_viewer(csv_path, image_path):
    init_app(csv_path, image_path)
    app.run(debug=False, host="0.0.0.0", port=5000)
