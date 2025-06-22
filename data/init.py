import os
import glob
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
import joblib

# Constants
DATA_DIR = "data"
ROOMS = {
    "A": "datasets-location_A",
    "B": "datasets-location_B",
    "C": "datasets-location_C",
}
MODEL_DIR = "models"

# Column structure
COLUMNS = [
    "EID", "AbsT", "RelT", "NID",
    "Temp", "RelH", "L1", "L2",
    "Occ", "Act", "Door", "Win"
]

FEATURES = ["RelH", "L1", "L2", "Occ", "Act", "Door", "Win"]
TARGET = "Temp"

os.makedirs(MODEL_DIR, exist_ok=True)

def train_knn_model(room_key, folder_path):
    print(f"Processing room {room_key} from {folder_path}")

    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    if not csv_files:
        print(f"No CSV files found for room {room_key}")
        return

    dfs = []
    for file in csv_files:
        df = pd.read_csv(file, header=None, names=COLUMNS)
        dfs.append(df)

    df_all = pd.concat(dfs, ignore_index=True)
    df_all = df_all.dropna(subset=FEATURES + [TARGET])

    X = df_all[FEATURES]
    y = df_all[TARGET]

    if len(X) < 10:
        print(f"Not enough data for room {room_key}, skipping...")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = KNeighborsRegressor(n_neighbors=3)
    model.fit(X_train, y_train)

    model_path = os.path.join(MODEL_DIR, f"knn_model_room_{room_key}.pkl")
    joblib.dump(model, model_path)

    print(f"Model for room {room_key} saved to {model_path}")


def main():
    for room_key, folder in ROOMS.items():
        folder_path = os.path.join(DATA_DIR, folder)
        train_knn_model(room_key, folder_path)


if __name__ == "__main__":
    main()
