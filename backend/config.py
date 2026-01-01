import os

BASE_PATH = "data"

DIRS = {
    "raw": os.path.join(BASE_PATH, "raw_data"),
    "clean": os.path.join(BASE_PATH, "clean_data"),
    "quarantine": os.path.join(BASE_PATH, "quarantine"),
    "augmented": os.path.join(BASE_PATH, "augmented_final"),
}

SAMPLE_RATE = 16000

QUALITY_CONFIG = {
    "min_duration": 1.0,
    "max_duration": 10.0,
    "min_snr": 15.0,
    "max_clipping_pct": 1.0
}
