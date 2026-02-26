import os
import glob

import librosa
import soundfile as sf
import numpy as np
import pandas as pd
import noisereduce as nr

from audiomentations import Compose, AddGaussianNoise, TimeStretch, PitchShift
from config import DIRS, SAMPLE_RATE, QUALITY_CONFIG

# --------------------------------------------------
# CREATE REQUIRED DIRECTORIES
# --------------------------------------------------
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

os.makedirs("reports", exist_ok=True)

# --------------------------------------------------
# AUDIO AUGMENTATION PIPELINE
# --------------------------------------------------
augmenter = Compose([
    TimeStretch(min_rate=0.8, max_rate=1.2, p=0.5),
    PitchShift(min_semitones=-2, max_semitones=2, p=0.5),
    AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=0.3),
])

# --------------------------------------------------
# UTILS
# --------------------------------------------------
def calculate_snr(y: np.ndarray) -> float:
    """Estimate SNR in dB"""
    energy = y ** 2
    noise_floor = np.percentile(energy, 10)
    signal_power = np.mean(energy)

    if noise_floor <= 0:
        return 100.0

    return 10 * np.log10(signal_power / noise_floor)

def clean_audio(y: np.ndarray, sr: int) -> np.ndarray:
    """Noise reduction + trimming"""
    y = nr.reduce_noise(
        y=y,
        sr=sr,
        prop_decrease=0.75,
        stationary=True
    )
    y, _ = librosa.effects.trim(y, top_db=20)
    return y

# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------
def process_audio_pipeline():
    files = glob.glob(os.path.join(DIRS["raw"], "*.wav"))
    report = []

    if not files:
        print("❌ No audio files found in raw_data!")
        return pd.DataFrame(columns=["filename", "status", "duration_sec", "snr_db", "clipping_pct"])

    for filepath in files:
        filename = os.path.basename(filepath)

        try:
            # Load audio
            y, sr = librosa.load(filepath, sr=SAMPLE_RATE, mono=True)

            duration = librosa.get_duration(y=y, sr=sr)
            snr = calculate_snr(y)
            clipping_pct = np.mean(np.abs(y) >= 0.99) * 100

            fails = []

            if duration < QUALITY_CONFIG["min_duration"]:
                fails.append("TooShort")
            if duration > QUALITY_CONFIG["max_duration"]:
                fails.append("TooLong")
            if snr < QUALITY_CONFIG["min_snr"]:
                fails.append("LowSNR")
            if clipping_pct > QUALITY_CONFIG["max_clipping_pct"]:
                fails.append("Clipping")

            # --------------------------------------------------
            # QUARANTINE
            # --------------------------------------------------
            if fails:
                out_name = f"{os.path.splitext(filename)[0]}_{'_'.join(fails)}.wav"
                out_path = os.path.join(DIRS["quarantine"], out_name)
                sf.write(out_path, y, sr)
                status = "Quarantined"

            # --------------------------------------------------
            # CLEAN + AUGMENT
            # --------------------------------------------------
            else:
                y_clean = clean_audio(y, sr)

                # Save clean audio
                sf.write(
                    os.path.join(DIRS["clean"], filename),
                    y_clean,
                    sr
                )

                base = os.path.splitext(filename)[0]

                # Save original clean
                sf.write(
                    os.path.join(DIRS["augmented"], f"{base}_orig.wav"),
                    y_clean,
                    sr
                )

                # Augmented versions
                for i in range(3):
                    y_aug = augmenter(samples=y_clean, sample_rate=sr)
                    sf.write(
                        os.path.join(DIRS["augmented"], f"{base}_aug_{i}.wav"),
                        y_aug,
                        sr
                    )

                status = "Approved"

            # --------------------------------------------------
            # APPEND TO REPORT
            # --------------------------------------------------
            report.append({
                "filename": filename,          # <- Flask expects "filename"
                "status": status,              # <- Flask expects "status"
                "duration_sec": round(duration, 2),
                "snr_db": round(snr, 2),
                "clipping_pct": round(clipping_pct, 2)
            })

        except Exception as e:
            report.append({
                "filename": filename,
                "status": "Error",
                "duration_sec": 0,
                "snr_db": 0,
                "clipping_pct": 0,
                "error": str(e)
            })

    # --------------------------------------------------
    # SAVE REPORT
    # --------------------------------------------------
    df = pd.DataFrame(report)
    df.to_csv("reports/quality_report.csv", index=False)

    return df
