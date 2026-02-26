from flask import Flask, jsonify, request
import os
import glob
from audio_utils import process_audio_pipeline
from config import DIRS
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# -------------------------------
# HOME ROUTE
# -------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Flask Audio Backend Running Successfully"
    })


# -------------------------------
# AUDIO PROCESSING ROUTE
# -------------------------------
@app.route("/process", methods=["POST"])
def process_audio():
    df = process_audio_pipeline()
    
    if "status" not in df.columns:
        return jsonify({
            "error": "status column missing in DataFrame",
            "columns_found": list(df.columns)
        }), 500

    return jsonify({
        "total_files": len(df),
        "approved": int((df["status"] == "Approved").sum()),
        "quarantined": int((df["status"] == "Quarantined").sum())
    })



# -------------------------------
# DATASET STATISTICS ROUTE
# -------------------------------
@app.route("/stats")
def stats():
    # Basic counts
    counts = {k: len(os.listdir(v)) for k, v in DIRS.items()}

    raw_count = counts.get("raw", 0)
    clean_count = counts.get("clean", 0)
    quarantine_count = counts.get("quarantine", 0)
    augmented_count = counts.get("augmented", 0)

    # Percentages
    clean_pct = round((clean_count / raw_count) * 100, 2) if raw_count > 0 else 0
    quarantine_pct = round((quarantine_count / raw_count) * 100, 2) if raw_count > 0 else 0

    # Top failure reasons
    quarantine_files = glob.glob(os.path.join(DIRS["quarantine"], "*.wav"))
    failure_reasons = []
    for f in quarantine_files:
        fname = os.path.basename(f)
        parts = fname.split("_")[1:]  # skip original file name
        parts = [p.replace(".wav", "") for p in parts]
        failure_reasons.extend(parts)
    
    reason_counts = {}
    for r in failure_reasons:
        reason_counts[r] = reason_counts.get(r, 0) + 1
    top_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return jsonify({
        "raw_files": raw_count,
        "clean_files": clean_count,
        "clean_pct": clean_pct,
        "quarantined_files": quarantine_count,
        "quarantine_pct": quarantine_pct,
        "augmented_files": augmented_count,
        "top_failure_reasons": top_reasons
    })


if __name__ == "__main__":
    for d in DIRS.values():
        os.makedirs(d, exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    app.run(debug=True)


# -------------------------------
# APP ENTRY POINT
# -------------------------------

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
