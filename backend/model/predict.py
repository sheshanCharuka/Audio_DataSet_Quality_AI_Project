import numpy as np
from tensorflow.keras.models import load_model
from model import extract_mfcc

MODEL_PATH = "models/model.h5"
LABELS = ["normal", "abnormal"]  # change to your classes

model = load_model(MODEL_PATH)

def predict_audio(file_path):
    mfcc = extract_mfcc(file_path)
    mfcc = mfcc[np.newaxis, ..., np.newaxis]

    prediction = model.predict(mfcc)
    predicted_label = LABELS[np.argmax(prediction)]
    confidence = float(np.max(prediction))

    return {
        "label": predicted_label,
        "confidence": round(confidence, 3)
    }
