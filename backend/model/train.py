import os
import numpy as np
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

from model import extract_mfcc, build_model

DATASET_PATH = "data/augmented_final"
LABELS = sorted(os.listdir(DATASET_PATH))  # folder-per-class

X, y = [], []

print("Loading dataset...")

for label_idx, label in enumerate(LABELS):
    label_path = os.path.join(DATASET_PATH, label)

    if not os.path.isdir(label_path):
        continue

    for file in os.listdir(label_path):
        if file.endswith(".wav"):
            file_path = os.path.join(label_path, file)
            mfcc = extract_mfcc(file_path)
            X.append(mfcc)
            y.append(label_idx)

X = np.array(X)
y = to_categorical(y)

# CNN expects 4D input
X = X[..., np.newaxis]

print(f"Dataset loaded: {X.shape}")

# Train / validation split
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Build model
model = build_model(
    input_shape=X.shape[1:],
    num_classes=y.shape[1]
)

print("Training model...")
model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=20,
    batch_size=16
)

# Save model
model.save("models/model.h5")
print("✅ Model saved as models/model.h5")
