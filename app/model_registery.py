
import os
import joblib

MODEL_DIR = "models"
ROOMS = ["A", "B", "C"]

model_registry = {}

def load_models():
    for room in ROOMS:
        model_path = os.path.join(MODEL_DIR, f"knn_model_room_{room}.pkl")
        if os.path.exists(model_path):
            model_registry[room] = joblib.load(model_path)
        else:
            print(f"Model file for room {room} not found: {model_path}")