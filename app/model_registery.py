import os
import joblib

MODEL_DIR = "models"
ROOMS = ["A", "B", "C"]
KNN_MODEL_TEMPLATE = "knn_model_room_{}.pkl"
RF_MODEL_TEMPLATE = "random_forest_model_room_{}.pkl"

model_registry = {}

def load_models():
    for room in ROOMS:
        knn_path = os.path.join(MODEL_DIR, KNN_MODEL_TEMPLATE.format(room))
        if os.path.exists(knn_path):
            model_registry[f"knn_{room}"] = joblib.load(knn_path)
            print(f"KNN model for room {room} loaded.")
        else:
            print(f"KNN model file for room {room} not found: {knn_path}")

        rf_path = os.path.join(MODEL_DIR, RF_MODEL_TEMPLATE.format(room))
        if os.path.exists(rf_path):
            model_registry[f"rf_{room}"] = joblib.load(rf_path)
            print(f"Random Forest model for room {room} loaded.")
        else:
            print(f"Random Forest model file for room {room} not found: {rf_path}")
